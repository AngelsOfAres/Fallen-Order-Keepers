from discord_slash import cog_ext
from discord.ext import commands
import discord
import requests
import imageio.v2 as imageio
from discord import File
import random
from discord_slash.utils.manage_components import create_select, create_select_option, create_actionrow, wait_for_component, create_button
from discord_slash.model import ButtonStyle
from discord.utils import get
from discord_slash import ComponentContext
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageOps
import asyncio
import json
import base64
from client import client
from txns import algod_client, fallen_order_main, fallen_order_manager, fallen_order_accessories, get_balance, send_assets, get_main_char, logs_payment, send_potion, edit_hatchet, edit_metadata
from kinship_pots_wl import kinship_potions_edited
from all_potions_wl import kinship_potions_full
from embeds import embedNoOptEXP

class BuyPotionCog(commands.Cog):
    @cog_ext.cog_slash(name="buy-kinship-potion", description="Purchase a Kinship Potion for ORDER, EXP, and Oak Logs!")
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def purchase_potion(self, ctx):
        wallet, main_character, equipped_hatchet = await get_main_char(str(ctx.author.id))
        if wallet == '':
            embedNoReg = discord.Embed(
                title="Click Here To Register!",
                url="https://app.fallenorder.xyz",
                description=f"Please verify your wallet via our website to continue..\nEnsure you copy your user id below for the verification process:\nUser ID: {ctx.author.id}",
                color=0xFF1C0A,
            )
            await ctx.send(embed=embedNoReg, hidden=True)
            return
        balance_order = await get_balance(wallet, 811718424)
        balance_exp = await get_balance(wallet, 811721471)
        balance_logs = await get_balance(wallet, 1064863037)
        if balance_logs == -1:
            embedNoOpt = discord.Embed(
                title=f"You are not opted into Oak Logs!",
                description=f"Please [click here](https://www.randgallery.com/algo-collection/?address=1064863037) to opt in and try again...",
                color=0xFF0000
            )
            await ctx.send(embed=embedNoOpt)
            return
        if balance_order == -1:
            embedNoOpt = discord.Embed(
                title=f"You are not opted into $ORDER!",
                description=f"Please [click here](https://www.randgallery.com/algo-collection/?address=811718424) to opt in and try again...",
                color=0xFF0000
            )
            await ctx.send(embed=embedNoOpt)
            return
        if balance_exp == -1:
            embedNoOpt = discord.Embed(
                title=f"You are not opted into $EXP",
                description=f"Please [click here](https://www.randgallery.com/algo-collection/?address=811721471) to opt in and try again...",
                color=0xFF0000
            )
            await ctx.send(embed=embedNoOpt)
            return
        if main_character == 0:
            embedNoMain = discord.Embed(
                title="You do not have a Main character assigned!",
                description=f"You may select your main by using /main-character",
                color=0xFF1C0A,
            )
            await ctx.send(embed=embedNoMain)
            return
        if balance_exp < 1000 or balance_order < 5 or balance_logs < 10:
            embedLowBalance = discord.Embed(
                title="You do not have enough supplies!",
                description=f"Kinship Potions cost:\n\n5 $ORDER + 1000 $EXP + 10 Oak Logs",
                color=0xFF1C0A,
            )
            await ctx.send(embed=embedLowBalance)
            return
        chosen_potion = random.choice(kinship_potions_edited)
        metadata_api = f"https://mainnet-idx.algonode.cloud/v2/transactions?tx-type=acfg&asset-id={chosen_potion}"
        response = requests.get(metadata_api)
        if response.status_code == 200:
            data = response.json()
        else:
            print("Error fetching data from API")
        potion_name = data["transactions"][-1]["asset-config-transaction"]["params"]["name"]
        embedConfirmPurchase = discord.Embed(
                title=f"⚠️ CLICK HERE TO OPT IN! ⚠️",
                url=f"https://www.randgallery.com/algo-collection/?address={chosen_potion}",
                description=f"Selected Potion: {potion_name}\n\nCost: 5 $ORDER + 1000 $EXP + 10 Oak Logs\n\nPress confirm ONLY after you have successfully opted in!!\n\nAsset ID:",
                color=0xFFFB0A
            )
        embedConfirmPurchase.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        embedConfirmPurchase.set_footer(text=f"{chosen_potion}")
        action_row = create_actionrow(
                            create_button(style=ButtonStyle.green, label="Confirm", custom_id="confirm"),
                            create_button(style=ButtonStyle.red, label="Cancel", custom_id="cancel")
                        )
        message = await ctx.send(embed=embedConfirmPurchase, components=[action_row])
        try:
            while True:
                interaction: ComponentContext = await wait_for_component(client, components=action_row, timeout=150.0)
                interaction_author_id = interaction.author.id
                if interaction_author_id == ctx.author.id:
                    await interaction.defer(edit_origin=True)
                    action = interaction.custom_id
                    if action == "cancel":
                        await message.delete()
                        return
                    elif action == 'confirm':
                        await message.edit(embed=embedConfirmPurchase, components=[])
                        balance_potion = await get_balance(wallet, chosen_potion)
                        if balance_potion == -1:
                            embedConfirmPurchase = discord.Embed(
                                title=f"Your opt in did not go through!",
                                description=f"Try /buy-kinship-potion again and we will randomize a new potion for you...",
                                color=0xFFFB0A
                            )
                            await message.edit(embed=embedConfirmPurchase)
                            return
                        await send_assets("Kinship Potion Purchase. " + str(ctx.author.name), wallet, fallen_order_main, 811718424, "ORDER", 5)
                        await send_assets("Kinship Potion Purchase. " + str(ctx.author.name), wallet, fallen_order_main, 811721471, "EXP", 1000)
                        await logs_payment(wallet, 1064863037, 10)
                        await send_potion(wallet, chosen_potion)
                        kinship_potions_edited.remove(chosen_potion)
                        with open('kinship_pots_wl.py', 'w') as f:
                            f.write(f"kinship_potions_edited = {kinship_potions_edited}")
                    break
                else:
                    embedWrongUpgrade = discord.Embed(
                        title=f"This is not your Kinship Potion purchase!",
                        color=0xFF0000
                    )
                    await interaction.send(embed=embedWrongUpgrade, hidden=True)
                    continue
        except asyncio.TimeoutError:
            embedTimeout = discord.Embed(
                    title=f"Woops! You took too long to respond...",
                    description=f"Ending {ctx.author.name}'s Kinship Potion purchase..",
                    color=0xFF0000
                )
            await message.edit(embed=embedTimeout, components=[])
            await asyncio.sleep(10)
            await message.delete()
            return
        
        embedConfirmPurchase2 = discord.Embed(
                title=f"Successfully Purchased Kinship Potion!",
                url=f"https://nftexplorer.app/asset/{chosen_potion}",
                description=f"Kinship Potion: {potion_name}\n\nNew Balances\n{balance_order - 5} $ORDER\n{balance_exp - 1000} $EXP\n{balance_logs - 10} Oak Logs",
                color=0x28FF0A
            )
        embedConfirmPurchase2.set_footer(text="Let's get this bad boy fueled up!\n\n*You may use /absorb-kinship to absorb Kinship from your main character to your new potion*")
        embedConfirmPurchase2.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        await message.edit(embed=embedConfirmPurchase2)
        
    @purchase_potion.error
    async def purchase_potion_error(self, ctx, error):
        embedNotAllowed = discord.Embed(
                    title=f"One purchase every 20 seconds!",
                    color=0xFF0000
                )
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(embed=embedNotAllowed, hidden=True)


class AbsorbKinshipCog(commands.Cog):
    @cog_ext.cog_slash(name="absorb-kinship", description="Absorb 50% Of Your Main Character's Kinship Into Your Kinship Potion!")
    async def absorb_kinship(self, ctx):
        potion_image = "https://ipfs.algonft.tools/ipfs/QmZnp2Hy8GK4r88HXRfD821cJnHJsBMGsVAyiY7pC3irMu"
        embedAbsorbInProgress = discord.Embed(
                title=f"⚗️ Kinship Absorb ⚗️",
                description=f"{ctx.author.name} initiating Absorb...",
                color=0xFF0000
            )
        embedAbsorbInProgress.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        message = await ctx.send(embed=embedAbsorbInProgress)
        wallet, main_character, equipped_hatchet = await get_main_char(str(ctx.author.id))
        if wallet == '':
            embedNoReg = discord.Embed(
                title="Click Here To Register!",
                url="https://app.fallenorder.xyz",
                description=f"Please verify your wallet via our website to continue..\nEnsure you copy your user id below for the verification process:\nUser ID: {ctx.author.id}",
                color=0xFF1C0A,
            )
            await ctx.send(embed=embedNoReg, hidden=True)
            return
        if main_character == 0:
            embedNoMain = discord.Embed(
                title="You do not have a Main character assigned!",
                description=f"You may select your main by using /main-character",
                color=0xFF1C0A,
            )
            await ctx.send(embed=embedNoMain)
            return
        balance_exp = await get_balance(wallet, 811721471)
        if balance_exp == -1:
            await message.edit(embed=embedNoOptEXP)
            return
        if balance_exp < 25:
            embedNoEXP = discord.Embed(
                title=f"Awwww...{ctx.author.name} does not own enough $EXP to Absorb!",
                description=f"Absorb costs 1 Oak Log + 25 $EXP\n\nYour Balance: {balance_exp}",
                color=0xFF0000
            )
            embedNoEXP.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
            await message.edit(embed=embedNoEXP)
            return
        balance_logs = await get_balance(wallet, 1064863037)
        if balance_logs == -1:
            embedNoOpt = discord.Embed(
                title=f"You are not opted into Oak Logs!",
                description=f"Please [click here](https://www.randgallery.com/algo-collection/?address=1064863037) to opt in and try again...",
                color=0xFF0000
            )
            embedNoOpt.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
            await message.edit(embed=embedNoOpt)
            return
        if balance_logs < 1:
            embedNoEXP = discord.Embed(
                title=f"Awwww...{ctx.author.name} does not own enough Oak Logs to Absorb!",
                description=f"Absorb costs 1 Oak Log + 25 $EXP\n\nYour Balance: {balance_logs}",
                color=0xFF0000
            )
            embedNoEXP.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
            await message.edit(embed=embedNoEXP)
            return
        potions = []
        account_info = algod_client.account_info(wallet)
        assets = account_info.get("assets", [])
        for asset in assets:
            if asset["amount"] > 0 and asset["asset-id"] in kinship_potions_full:
                metadata_api = f"https://mainnet-idx.algonode.cloud/v2/transactions?tx-type=acfg&asset-id={asset['asset-id']}"
                response = requests.get(metadata_api)
                if response.status_code == 200:
                    data = response.json()
                else:
                    print("Error fetching data from API")
                asset_info = algod_client.asset_info(asset['asset-id'])
                potions.append([asset_info['index'], asset_info["params"]['name']])
        if potions == []:
            embedNoPots = discord.Embed(
                title=f"Awwww...{ctx.author.name} does not own any Kinship Potions!",
                description=f"Use /buy-kinship-potion to purchase a potion...",
                color=0xFF0000
            )
            embedNoPots.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
            await message.edit(embed=embedNoPots)
            return
        select_options = [create_select_option(label=potion[1], value=str(potion[0])) for potion in potions]
        select = create_select(options=select_options, placeholder="Select the potion to Absorb into", min_values=1, max_values=1)
        action_row = create_actionrow(select)
        await message.edit(embed=embedAbsorbInProgress, components=[action_row])
        try:
            while True:
                interaction: ComponentContext = await wait_for_component(client, components=action_row, timeout=30.0)
                interaction_author_id = interaction.author.id
                if interaction_author_id == ctx.author.id:
                    await interaction.defer(edit_origin=True)
                    chosen_potion = int(interaction.selected_options[0])
                    break
                else:
                    embedWrongUpgrade = discord.Embed(
                        title=f"This is not your Kinship Absorb!",
                        color=0xFF0000
                    )
                    await interaction.send(embed=embedWrongUpgrade, hidden=True)
                    continue
        except asyncio.TimeoutError:
            embedTimeout = discord.Embed(
                    title=f"Woops! You took too long to respond...",
                    description=f"Ending {ctx.author.name}'s kinship absorb..",
                    color=0xFF0000
                )
            await message.edit(embed=embedTimeout, components=[])
            await asyncio.sleep(10)
            await message.delete()
            return
        main_character_data = f"https://mainnet-idx.algonode.cloud/v2/transactions?tx-type=acfg&asset-id={main_character}&address={fallen_order_manager}"
        response = requests.get(main_character_data)
        if response.status_code == 200:
            data = response.json()
        else:
            print("Error fetching data from API")
        metadata_decoded = json.loads((base64.b64decode((data["transactions"][0]["note"]).encode('utf-8'))).decode('utf-8'))
        fallen_name = metadata_decoded.get("properties", {}).get("Name", "None")
        kinship = int(metadata_decoded["properties"]["Kinship"])
        if kinship < 0:
            embedNoKinshipChar = discord.Embed(
                title=f"This character has 0 Kinship!",
                description=f"Please select a main character with Kinship available",
                color=0xFF0000
            )
            embedNoKinshipChar.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
            await message.edit(embed=embedNoKinshipChar)
            return
        potion_data = f"https://mainnet-idx.algonode.cloud/v2/transactions?tx-type=acfg&asset-id={chosen_potion}&address={fallen_order_accessories}"
        response2 = requests.get(potion_data)
        if response2.status_code == 200:
            data2 = response2.json()
        else:
            print("Error fetching data from API")
        metadata_decoded2 = json.loads((base64.b64decode((data2["transactions"][0]["note"]).encode('utf-8'))).decode('utf-8'))
        asset_info = algod_client.asset_info(chosen_potion)
        potion_name = asset_info["params"]['name']
        potion_kinship = int(metadata_decoded2["properties"]["Kinship"])
        metadata_decoded["properties"]["Kinship"] = 0
        metadata_decoded2["properties"]["Kinship"] = potion_kinship + int(kinship/2)
        metadata_encoded1 = json.dumps(metadata_decoded)
        metadata_encoded2 = json.dumps(metadata_decoded2)
        asset_info_fallen = algod_client.asset_info(main_character)
        fallen_image_1_ipfs = asset_info_fallen["params"]["url"]
        fallen_image_1_url = "https://ipfs.algonft.tools/ipfs/" + (fallen_image_1_ipfs).replace("ipfs://", "")
        response1 = requests.get(fallen_image_1_url)
        image1 = Image.open(BytesIO(response1.content))
        response2 = requests.get(potion_image)
        image2 = Image.open(BytesIO(response2.content))
        transparent_image = Image.new('RGBA', (image1.width + image2.width, max(image1.height, image2.height)), color=(0, 0, 0, 0))
        transparent_image.paste(image1, (0, 0))
        transparent_image.paste(image2, (image1.width, 0))
        buffer = BytesIO()
        transparent_image.save(buffer, format='PNG')
        buffer.seek(0)
        image_file = File(buffer, filename='transparent_image.png')
        embedAbsorbConfirm = discord.Embed(
                title=f"⚠️ Confirm Kinship Absorb! ⚠️",
                description=f"{fallen_name}'s {kinship} Kinship will been Asborbed into {potion_name}!\n\nPotion Kinship: {potion_kinship} -> {potion_kinship + int(kinship/2)}\n\nBalance: {balance_exp} $EXP | {balance_logs} Oak Logs\nCost: 25 $EXP + 1 Oak Log",
                color=0xFCE303
            )
        embedAbsorbConfirm.set_image(url="attachment://transparent_image.png")
        embedAbsorbConfirm.set_footer(text=f"CONFIRM DETAILS ABOVE BEFORE CLICKING!")
        embedAbsorbConfirm.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        action_row = create_actionrow(
                            create_button(style=ButtonStyle.green, label="Confirm", custom_id="confirm"),
                            create_button(style=ButtonStyle.red, label="Cancel", custom_id="cancel")
                        )
        await message.edit(file=image_file, embed=embedAbsorbConfirm, components=[action_row])
        while True:
            try:
                interaction: ComponentContext = await wait_for_component(client, components=action_row, timeout=20.0)
                interaction_author_id = interaction.author.id
                if interaction_author_id == ctx.author.id:
                    await interaction.defer(edit_origin=True)
                    action = interaction.custom_id
                    if action == "cancel":
                        await message.delete()
                        return
                    elif action == 'confirm':
                        embedAbsorbConfirm.set_footer(text=f"Please wait while I update your metadata...⏳")
                        await message.edit(embed=embedAbsorbConfirm, components=[])
                        await send_assets("Kinship Absorb. " + str(ctx.author.name), wallet, fallen_order_main, 811721471, "EXP", 25)
                        await logs_payment(wallet, 1064863037, 1)
                        await edit_metadata(main_character, metadata_encoded1)
                        await edit_hatchet(chosen_potion, metadata_encoded2)
                    break

                else:
                    embedWrongUpgrade = discord.Embed(
                        title=f"This is not your Kinship Absorb!",
                        color=0xFF0000
                    )
                    await interaction.send(embed=embedWrongUpgrade, hidden=True)
                    continue
            except asyncio.TimeoutError:
                embedTimeout = discord.Embed(
                        title=f"Woops! You took too long to respond...",
                        description=f"Ending {ctx.author.name}'s Kinship Absorb..",
                        color=0xFF0000
                    )
                await message.edit(embed=embedTimeout, components=[])
                await asyncio.sleep(10)
                await message.delete()
                return
        embedAbsorbComplete = discord.Embed(
            title=f"⚗️ Kinship Absorb Successful! ⚗️",
            url=f"https://www.randgallery.com/algo-collection/?address={chosen_potion}",
            description=f"{fallen_name}'s {kinship} Kinship has been Asborbed into {potion_name}!\n\nNew Potion Kinship: {potion_kinship + int(kinship/2)}\n\nNew Balance: {balance_exp - 25} $EXP | {balance_logs - 1} Oak Logs\nPaid: 25 $EXP + 1 Oak Log",
            color=0x28FF0A
        )
        embedAbsorbComplete.set_image(url="attachment://transparent_image.png")
        embedAbsorbComplete.set_footer(text=f"All juiced up!\n\nMaster, it was an honor to serve my Kinship to you")
        embedAbsorbComplete.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        await message.edit(file=image_file, embed=embedAbsorbComplete)
        
    @absorb_kinship.error
    async def absorb_kinship_error(self, ctx, error):
        embedNotAllowed = discord.Embed(
                    title=f"One Kinship Absorb every 20 seconds!",
                    color=0xFF0000
                )
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(embed=embedNotAllowed, hidden=True)


class UseKinshipPotionCog(commands.Cog):
    @cog_ext.cog_slash(name="use-kinship-potion", description="Transfer Kinship From A Potion To Your Main Character!")
    async def use__kinship_potion(self, ctx):
        potion_image = "https://ipfs.algonft.tools/ipfs/QmZnp2Hy8GK4r88HXRfD821cJnHJsBMGsVAyiY7pC3irMu"
        embedAbsorbInProgress = discord.Embed(
                title=f"⚗️ Kinship Potion Use ⚗️",
                description=f"{ctx.author.name} initiating Absorb...",
                color=0xFF0000
            )
        embedAbsorbInProgress.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        message = await ctx.send(embed=embedAbsorbInProgress)
        wallet, main_character, equipped_hatchet = await get_main_char(str(ctx.author.id))
        if wallet == '':
            embedNoReg = discord.Embed(
                title="Click Here To Register!",
                url="https://app.fallenorder.xyz",
                description=f"Please verify your wallet via our website to continue..\nEnsure you copy your user id below for the verification process:\nUser ID: {ctx.author.id}",
                color=0xFF1C0A,
            )
            await ctx.send(embed=embedNoReg, hidden=True)
            return
        if main_character == 0:
            embedNoMain = discord.Embed(
                title="You do not have a Main character assigned!",
                description=f"You may select your main by using /main-character",
                color=0xFF1C0A,
            )
            await ctx.send(embed=embedNoMain)
            return
        balance_exp = await get_balance(wallet, 811721471)
        if balance_exp == -1:
            await message.edit(embed=embedNoOptEXP)
            return
        if balance_exp < 25:
            embedNoEXP = discord.Embed(
                title=f"Awwww...{ctx.author.name} does not own enough $EXP to use Kinship Potion!",
                description=f"Kinship potion use costs 25 $EXP\n\nYour Balance: {balance_exp}",
                color=0xFF0000
            )
            embedNoEXP.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
            await message.edit(embed=embedNoEXP)
            return
        potions = []
        account_info = algod_client.account_info(wallet)
        assets = account_info.get("assets", [])
        for asset in assets:
            if asset["amount"] > 0 and asset["asset-id"] in kinship_potions_full:
                metadata_api = f"https://mainnet-idx.algonode.cloud/v2/transactions?tx-type=acfg&asset-id={asset['asset-id']}"
                response = requests.get(metadata_api)
                if response.status_code == 200:
                    data = response.json()
                else:
                    print("Error fetching data from API")
                asset_info = algod_client.asset_info(asset['asset-id'])
                potions.append([asset_info['index'], asset_info["params"]['name']])
        if potions == []:
            embedNoPots = discord.Embed(
                title=f"Awwww...{ctx.author.name} does not own any Kinship Potions!",
                description=f"Use /buy-kinship-potion to purchase a potion...",
                color=0xFF0000
            )
            embedNoPots.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
            await message.edit(embed=embedNoPots)
            return
        select_options = [create_select_option(label=potion[1], value=str(potion[0])) for potion in potions]
        select = create_select(options=select_options, placeholder="Select the potion you want to use", min_values=1, max_values=1)
        action_row = create_actionrow(select)
        await message.edit(embed=embedAbsorbInProgress, components=[action_row])
        try:
            while True:
                interaction: ComponentContext = await wait_for_component(client, components=action_row, timeout=30.0)
                interaction_author_id = interaction.author.id
                if interaction_author_id == ctx.author.id:
                    await interaction.defer(edit_origin=True)
                    chosen_potion = int(interaction.selected_options[0])
                    break
                else:
                    embedWrongUpgrade = discord.Embed(
                        title=f"This is not your kinship potion use!",
                        color=0xFF0000
                    )
                    await interaction.send(embed=embedWrongUpgrade, hidden=True)
                    continue
        except asyncio.TimeoutError:
            embedTimeout = discord.Embed(
                    title=f"Woops! You took too long to respond...",
                    description=f"Ending {ctx.author.name}'s kinship potion use..",
                    color=0xFF0000
                )
            await message.edit(embed=embedTimeout, components=[])
            await asyncio.sleep(10)
            await message.delete()
            return
        main_character_data = f"https://mainnet-idx.algonode.cloud/v2/transactions?tx-type=acfg&asset-id={main_character}&address={fallen_order_manager}"
        response = requests.get(main_character_data)
        if response.status_code == 200:
            data = response.json()
        else:
            print("Error fetching data from API")
        metadata_decoded = json.loads((base64.b64decode((data["transactions"][0]["note"]).encode('utf-8'))).decode('utf-8'))
        fallen_name = metadata_decoded.get("properties", {}).get("Name", "None")
        kinship = int(metadata_decoded["properties"]["Kinship"])
        if kinship < 0:
            embedNoKinshipChar = discord.Embed(
                title=f"This character has 0 Kinship!",
                description=f"Please select a main character with Kinship available",
                color=0xFF0000
            )
            embedNoKinshipChar.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
            await message.edit(embed=embedNoKinshipChar)
            return
        potion_data = f"https://mainnet-idx.algonode.cloud/v2/transactions?tx-type=acfg&asset-id={chosen_potion}&address={fallen_order_accessories}"
        response2 = requests.get(potion_data)
        if response2.status_code == 200:
            data2 = response2.json()
        else:
            print("Error fetching data from API")
        metadata_decoded2 = json.loads((base64.b64decode((data2["transactions"][0]["note"]).encode('utf-8'))).decode('utf-8'))
        asset_info = algod_client.asset_info(chosen_potion)
        potion_name = asset_info["params"]['name']
        potion_kinship = int(metadata_decoded2["properties"]["Kinship"])
        new_kinship = kinship + potion_kinship
        metadata_decoded["properties"]["Kinship"] = new_kinship
        metadata_decoded2["properties"]["Kinship"] = 0
        metadata_encoded1 = json.dumps(metadata_decoded)
        metadata_encoded2 = json.dumps(metadata_decoded2)
        asset_info_fallen = algod_client.asset_info(main_character)
        fallen_image_1_ipfs = asset_info_fallen["params"]["url"]
        fallen_image_1_url = "https://ipfs.algonft.tools/ipfs/" + (fallen_image_1_ipfs).replace("ipfs://", "")
        response1 = requests.get(fallen_image_1_url)
        image1 = Image.open(BytesIO(response1.content))
        response2 = requests.get(potion_image)
        image2 = Image.open(BytesIO(response2.content))
        transparent_image = Image.new('RGBA', (image1.width + image2.width, max(image1.height, image2.height)), color=(0, 0, 0, 0))
        transparent_image.paste(image1, (0, 0))
        transparent_image.paste(image2, (image1.width, 0))
        buffer = BytesIO()
        transparent_image.save(buffer, format='PNG')
        buffer.seek(0)
        image_file = File(buffer, filename='transparent_image.png')
        embedAbsorbConfirm = discord.Embed(
                title=f"⚠️ Confirm Kinship Absorb! ⚠️",
                description=f"{potion_name}'s {potion_kinship} Kinship will be Asborbed into {fallen_name}!\n\n{fallen_name}'s New Kinship: {new_kinship}\n\nBalance: {balance_exp} $EXP\nCost: 25 $EXP",
                color=0xFCE303
            )
        embedAbsorbConfirm.set_image(url="attachment://transparent_image.png")
        embedAbsorbConfirm.set_footer(text=f"CONFIRM DETAILS ABOVE BEFORE CLICKING!")
        embedAbsorbConfirm.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        action_row = create_actionrow(
                            create_button(style=ButtonStyle.green, label="Confirm", custom_id="confirm"),
                            create_button(style=ButtonStyle.red, label="Cancel", custom_id="cancel")
                        )
        await message.edit(file=image_file, embed=embedAbsorbConfirm, components=[action_row])
        while True:
            try:
                interaction: ComponentContext = await wait_for_component(client, components=action_row, timeout=20.0)
                interaction_author_id = interaction.author.id
                if interaction_author_id == ctx.author.id:
                    await interaction.defer(edit_origin=True)
                    action = interaction.custom_id
                    if action == "cancel":
                        await message.delete()
                        return
                    elif action == 'confirm':
                        embedAbsorbConfirm.set_footer(text=f"Please wait while I update your metadata...⏳")
                        await message.edit(embed=embedAbsorbConfirm, components=[])
                        await send_assets("Kinship Absorb. " + str(ctx.author.name), wallet, fallen_order_main, 811721471, "EXP", 25)
                        await edit_metadata(main_character, metadata_encoded1)
                        await edit_hatchet(chosen_potion, metadata_encoded2)
                    break

                else:
                    embedWrongUpgrade = discord.Embed(
                        title=f"This is not your Kinship potion use Absorb!",
                        color=0xFF0000
                    )
                    await interaction.send(embed=embedWrongUpgrade, hidden=True)
                    continue
            except asyncio.TimeoutError:
                embedTimeout = discord.Embed(
                        title=f"Woops! You took too long to respond...",
                        description=f"Ending {ctx.author.name}'s Kinship potion use..",
                        color=0xFF0000
                    )
                await message.edit(embed=embedTimeout, components=[])
                await asyncio.sleep(10)
                await message.delete()
                return
        embedAbsorbComplete = discord.Embed(
            title=f"⚗️ Kinship Potion Use Successful! ⚗️",
            url=f"https://www.randgallery.com/algo-collection/?address={main_character}",
            description=f"{fallen_name} gulps that {potion_kinship} Kinship Potion down...\n*That Kinship was tasty boss!*\n\n{fallen_name}'s New Kinship: {new_kinship}\n\nNew Balance: {balance_exp - 25} $EXP\nPaid: 25 $EXP",
            color=0x28FF0A
        )
        embedAbsorbComplete.set_image(url="attachment://transparent_image.png")
        embedAbsorbComplete.set_footer(text=f"I'm Feelin' The Love Today, Master {ctx.author.name}!")
        embedAbsorbComplete.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        await message.edit(file=image_file, embed=embedAbsorbComplete)
        
    @use__kinship_potion.error
    async def use__kinship_potion_error(self, ctx, error):
        embedNotAllowed = discord.Embed(
                    title=f"One Kinship potion usage every 20 seconds!",
                    color=0xFF0000
                )
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(embed=embedNotAllowed, hidden=True)

def setup(client: client):
    client.add_cog(BuyPotionCog(client))
    client.add_cog(AbsorbKinshipCog(client))
    client.add_cog(UseKinshipPotionCog(client))