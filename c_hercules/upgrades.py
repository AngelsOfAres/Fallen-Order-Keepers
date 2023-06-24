from discord_slash import cog_ext
from discord.ext import commands
import discord
import requests
import imageio.v2 as imageio
import random
from datetime import datetime, timedelta
from discord_slash.utils.manage_components import create_select, create_select_option, create_actionrow, create_button, wait_for_component
import json
from discord_slash.model import ButtonStyle
import base64
from discord_slash import ComponentContext
import asyncio
import pytz
from client import client
from txns import fallen_order_main, algod_client, get_wallet, edit_metadata, get_balance, send_assets, fallen_order_manager, get_kinship_subs, update_kinsubs
from embeds import embedWrongChannelBoost, embedNoOptEXP, embedErr, embedNotKinshipChannel
from whitelist import fo_rank1, fo_rank2, fo_rank3, fo_rank4, fo_rank5

kinship_on = False
utc = pytz.timezone('UTC')
now_datetime = datetime.now(utc)

class StatBoostCog(commands.Cog):
    @cog_ext.cog_slash(name="boost", description="Allocate Your Character's Available Points!")
    @commands.cooldown(1, 30, commands.BucketType.guild)
    async def upgrade_character(self, ctx):
        if ctx.channel.id != 1082157256679882862:
            await ctx.send(embed=embedWrongChannelBoost, hidden=True)
            return
        embedUpgradeInProgress = discord.Embed(
                title=f"🧙‍♂️ Initiating Upgrade... 🧙‍♂️",
                description=f"{ctx.author.name} gathers their Fallen Order to boost their stats...",
                color=0xFCE303
            )
        embedUpgradeInProgress.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        embedUpgradeInProgress.set_footer(text=f"Select your Fallen Order below:")
        message = await ctx.send(embed=embedUpgradeInProgress)
        wallet, name, won, lost, expwon, explost, lastdrip, drip_exp = await get_wallet(str(ctx.author.id))
        if wallet == '':
            embedNoReg = discord.Embed(
                title="Click Here To Register!",
                url="https://app.fallenorder.xyz",
                description=f"Please verify your wallet via our website to continue..\nEnsure you copy your user id below for the verification process:\nUser ID: {ctx.author.id}",
                color=0xFF1C0A,
            )
            await message.edit(embed=embedNoReg, hidden=True)
            return
        balance_exp = await get_balance(wallet, 811721471)
        if balance_exp == -1:
            await message.edit(embed=embedNoOptEXP)
            return
        if balance_exp < 25:
            embedNoEXP = discord.Embed(title=f"Woops! You do not own enough $EXP!", description=f"Character stat changes cost 25 $EXP...", color=0xFF0000)
            embedNoEXP.set_thumbnail(url="https://s3.amazonaws.com/algorand-wallet-mainnet-thumbnails/prism-images/media/assets-logo-png/2022/10/11/a26da3af714a40e8bad2b29a6dfc4655.png--resize--w__200--q__70.webp")   
            await message.edit(embed=embedNoEXP)
            return
        fallen_assets = []
        account_info = algod_client.account_info(wallet)
        assets = account_info.get("assets", [])
        count = 0
        for asset in assets:
            if count == 25:
                break
            if asset["amount"] > 0 and (asset["asset-id"] in fo_rank1 or asset["asset-id"] in fo_rank2 or asset["asset-id"] in fo_rank3 or asset["asset-id"] in fo_rank4 or asset["asset-id"] in fo_rank5):
                metadata_api = f"https://mainnet-idx.algonode.cloud/v2/transactions?tx-type=acfg&asset-id={asset['asset-id']}&address={fallen_order_manager}"
                response = requests.get(metadata_api)
                if response.status_code == 200:
                    data = response.json()
                else:
                    print("Error fetching data from API")
                metadata_decoded = json.loads((base64.b64decode((data["transactions"][0]["note"]).encode('utf-8'))).decode('utf-8'))
                fallen_name = metadata_decoded.get("properties", {}).get("Name", "None")
                asset_info = algod_client.asset_info(asset['asset-id'])
                fallen_assets.append([asset_info['params']['unit-name'], asset_info['index'], fallen_name])
                count += 1
        
        if fallen_assets == []:
            embedNoFO = discord.Embed(
                title=f"Awwww...{ctx.author.name} does not own any Fallen Order!",
                description=f"[Click Here To Shuffle!](https://algoxnft.com/shuffle/902)",
                color=0xFF0000
            )
            embedNoFO.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
            await message.edit(embed=embedNoFO)
            return
        
        select_options = [create_select_option(label=fallen[0] + " - " + fallen[2], value=str(fallen[1])) for fallen in fallen_assets]
        select = create_select(options=select_options, placeholder="Select the character you want to upgrade", min_values=1, max_values=1)
        action_row = create_actionrow(select)

        await message.edit(embed=embedUpgradeInProgress, components=[action_row])
        try:
            while True:
                interaction: ComponentContext = await wait_for_component(client, components=action_row, timeout=30.0)
                interaction_author_id = interaction.author.id

                if interaction_author_id == ctx.author.id:
                    await interaction.defer(edit_origin=True)
                    chosen_fallen = interaction.selected_options[0]
                    break
                else:
                    embedWrongUpgrade = discord.Embed(
                        title=f"This is not your upgrade!",
                        description=f"{ctx.author.name} is currently upgrading..",
                        color=0xFF0000
                    )
                    await interaction.send(embed=embedWrongUpgrade, hidden=True)
                    continue
        except asyncio.TimeoutError:
            embedTimeout = discord.Embed(
                    title=f"Woops! You took too long to respond...",
                    description=f"Ending {ctx.author.name}'s upgrade..",
                    color=0xFF0000
                )
            await message.edit(embed=embedTimeout, components=[])
            await asyncio.sleep(10)
            await message.delete()
            return

        metadata_api = f"https://mainnet-idx.algonode.cloud/v2/transactions?tx-type=acfg&asset-id={chosen_fallen}&address={fallen_order_manager}"
        response = requests.get(metadata_api)
        if response.status_code == 200:
            data = response.json()
        else:
            print("Error fetching data from API")
        metadata_decoded = json.loads((base64.b64decode((data["transactions"][0]["note"]).encode('utf-8'))).decode('utf-8'))
        attack = int(metadata_decoded["properties"]["ATK"])
        defense = int(metadata_decoded["properties"]["DEF"])
        abilitypower = int(metadata_decoded["properties"]["AP"])
        points_available = int(metadata_decoded["properties"]["Points"])
        level = metadata_decoded["properties"]["Level"]
        hitpoints = metadata_decoded["properties"]["HP"]
        total_points = points_available + attack + defense + abilitypower
        asset_info = algod_client.asset_info(chosen_fallen)
        fallen_image_url = asset_info["params"]["url"]
        fallen_image = "https://ipfs.algonft.tools/ipfs/" + (fallen_image_url).replace("ipfs://", "")
        fallen_name = metadata_decoded.get("properties", {}).get("Name", asset_info['params']['unit-name'])

        embedDisplayChar = discord.Embed(
                title=f"🧙‍♂️ Stats Upgrade - {fallen_name} - {ctx.author.name} 🧙‍♂️",
                color=0xFCE303
            )
        embedDisplayChar.add_field(name=f"Level | HP", value=f"{level} | {hitpoints}", inline=False)   
        embedDisplayChar.add_field(name=f"ATK | DEF | AP", value=f"{attack} | {defense} | {abilitypower}", inline=False)
        embedDisplayChar.set_image(url=fallen_image)
        embedDisplayChar.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        embedDisplayChar.set_footer(text=f"Your character currently has a total of {total_points} Points!\n\nEnter your new desired ATK DEF AP\n\nSample:\n250 200 300")

        await message.edit(embed=embedDisplayChar, components=[])

        embedWrongInputs = discord.Embed(
                title=f"Oops! Invalid Input!",
                description=f"Please send all 3 values in one single message separated by a space as follows:\n258 330 165",
                color=0xFCE303
            )

        def check(m):
            return m.author == interaction.author

        try:
            response = await client.wait_for("message", check=check, timeout=60.0)
        except asyncio.TimeoutError:
            embedTimeout = discord.Embed(
                    title=f"Woops! You took too long to respond...",
                    description=f"Ending {ctx.author.name}'s upgrade..",
                    color=0xFF0000
                )
            await message.edit(embed=embedTimeout, components=[])
            await asyncio.sleep(10)
            await message.delete()
            return
        await asyncio.sleep(1)
        await response.delete()
        try:
            input_value1 = [response.content]
        except ValueError:
            await message.edit(embed=embedWrongInputs)
            await asyncio.sleep(10)
            await message.delete()
            return
        
        input_value = [int(x) for x in input_value1[0].split()]
        total_input = input_value[0] + input_value[1] + input_value[2]
        if input_value[0] < 0 or input_value[1] < 0 or input_value[2] < 0 or total_input == 0:
            embedWrongInputs2 = discord.Embed(
                title=f"You can not use all zeroes or negative values!",
                description=f"Your Input: {input_value[0]} ATK | {input_value[1]} DEF | {input_value[2]} AP\n\nCurrent Points: {total_points}",
                color=0xFF0000
            )
            await message.edit(embed=embedWrongInputs2)
            await asyncio.sleep(10)
            await message.delete()
            return
        
        if total_input <= total_points:
            points_remaining = total_points - total_input
            new_atk = int(input_value[0])
            new_def = int(input_value[1])
            new_ap = int(input_value[2])
            metadata_decoded["properties"]["Points"] = points_remaining
            metadata_decoded["properties"]["ATK"] = new_atk
            metadata_decoded["properties"]["DEF"] = new_def
            metadata_decoded["properties"]["AP"] = new_ap
            metadata_encoded = json.dumps(metadata_decoded)
            
        else:
            embedWrongInputs2 = discord.Embed(
                title=f"Your character does not have {total_input} points available!",
                description=f"Your Input: {input_value[0]} ATK | {input_value[1]} DEF | {input_value[2]} AP\n\nCurrent Points: {points_available}",
                color=0xFF0000
            )
            await message.edit(embed=embedWrongInputs2)
            await asyncio.sleep(10)
            await message.delete()
            return
        
        embedConfirmUpgrade = discord.Embed(
                title=f"⚠️ Confirm Stat Boost ⚠️",
                description=f"Ensure All Details Below Are Correct:",
                color=0xFCE303
            )
        embedConfirmUpgrade.add_field(name=f"Level | HP", value=f"{level} | {hitpoints}", inline=False)   
        embedConfirmUpgrade.add_field(name=f"ATK | DEF | AP", value=f"{new_atk} | {new_def} | {new_ap}", inline=False)
        embedConfirmUpgrade.set_image(url=fallen_image)
        embedConfirmUpgrade.set_footer(text=f"Your stat changes will cost 25 $EXP!")
        embedConfirmUpgrade.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")

        action_row = create_actionrow(
                            create_button(style=ButtonStyle.green, label="Confirm", custom_id="confirm"),
                            create_button(style=ButtonStyle.red, label="Cancel", custom_id="cancel")
                        )

        await message.edit(embed=embedConfirmUpgrade, components=[action_row])
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
                    embedConfirmUpgrade.set_footer(text=f"Please wait while I update your metadata...⏳")
                    await message.edit(embed=embedConfirmUpgrade, components=[])
                    await send_assets("Character Stat Edit. " + str(ctx.author.name), wallet, fallen_order_main, 811721471, "EXP", 25)
                    await edit_metadata(chosen_fallen, metadata_encoded)

            else:
                embedWrongUpgrade = discord.Embed(
                    title=f"This is not your stat boost!",
                    description=f"{ctx.author.name} is currently upgrading..",
                    color=0xFF0000
                )
                await interaction.send(embed=embedWrongUpgrade, hidden=True)
        except asyncio.TimeoutError:
            embedTimeout = discord.Embed(
                    title=f"Woops! You took too long to respond...",
                    description=f"Ending {ctx.author.name}'s game..",
                    color=0xFF0000
                )
            await message.edit(embed=embedTimeout, components=[])
            await asyncio.sleep(10)
            await message.delete()
            return

        embedUpgradeDone = discord.Embed(
                title=f"Your Fallen Order character has been upgraded successfully!",
                url=f"https://nftexplorer.app/asset/{chosen_fallen}",
                description=f"You have {points_remaining} Points available for use on your character",
                color=0x28FF0A
            )
        embedUpgradeDone.add_field(name=f"Level | HP", value=f"{level} | {hitpoints}", inline=False)   
        embedUpgradeDone.add_field(name=f"ATK | DEF | AP", value=f"{new_atk} | {new_def} | {new_ap}", inline=False)
        embedUpgradeDone.set_image(url=fallen_image)
        embedUpgradeDone.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        
        embedUpgradeDone.set_footer(text=f"Thank you, Master {ctx.author.name}! My new stats suit me!")
        await message.edit(embed=embedUpgradeDone, components=[])
    
    @upgrade_character.error
    async def upgrade_character_error(self, ctx, error):
        embedNotAllowed = discord.Embed(
                    title=f"Please wait 30sec before this command becomes available again!",
                    color=0xFF0000
                )
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(embed=embedNotAllowed, hidden=True)


class AddPointsCog(commands.Cog):
    @cog_ext.cog_slash(name="use-booster", description="Use Stat Booster $BOOST to add points to your Character's Points trait!")
    @commands.cooldown(1, 30, commands.BucketType.guild)
    async def add_points(self, ctx):
        if ctx.channel.id != 1082157256679882862:
            await ctx.send(embed=embedWrongChannelBoost, hidden=True)
            return
        embedUpgradeInProgress = discord.Embed(
                title=f"🧙‍♂️ Initiating Upgrade... 🧙‍♂️",
                description=f"{ctx.author.name} gathers their Fallen Order to boost their Points...",
                color=0xFCE303
            )
        embedUpgradeInProgress.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        message = await ctx.send(embed=embedUpgradeInProgress)
        wallet, name, won, lost, expwon, explost, lastdrip, drip_exp = await get_wallet(str(ctx.author.id))
        if wallet == '':
            embedNoReg = discord.Embed(
                title="Click Here To Register!",
                url="https://app.fallenorder.xyz",
                description=f"Please verify your wallet via our website to continue..\nEnsure you copy your user id below for the verification process:\nUser ID: {ctx.author.id}",
                color=0xFF1C0A,
            )
            await message.edit(embed=embedNoReg, hidden=True)
            return
        balance_boost = await get_balance(wallet, 815771120)
        if balance_boost < 1:
            embedNoOptBoost = discord.Embed(title=f"Woops! You do not own any Stat Boosters ($BOOST)!", description=f"You may gain $BOOST NFTs from leveling characters up or purchasing them from other players on the secondary market", color=0xFF0000)
            embedNoOptBoost.set_image(url="https://nft-media.algoexplorerapi.io/images/bafybeibdnf2qn7a3w5ckxecv4svykpntufjkqh2zank6kx6mn2idik2nz4")
            await message.edit(embed=embedNoOptBoost)
            return
        fallen_assets = []
        account_info = algod_client.account_info(wallet)
        assets = account_info.get("assets", [])
        count = 0
        for asset in assets:
            if count == 25:
                break
            if asset["amount"] > 0 and (asset["asset-id"] in fo_rank1 or asset["asset-id"] in fo_rank2 or asset["asset-id"] in fo_rank3 or asset["asset-id"] in fo_rank4 or asset["asset-id"] in fo_rank5):
                metadata_api = f"https://mainnet-idx.algonode.cloud/v2/transactions?tx-type=acfg&asset-id={asset['asset-id']}&address={fallen_order_manager}"
                response = requests.get(metadata_api)
                if response.status_code == 200:
                    data = response.json()
                else:
                    print("Error fetching data from API")
                metadata_decoded = json.loads((base64.b64decode((data["transactions"][0]["note"]).encode('utf-8'))).decode('utf-8'))
                asset_info = algod_client.asset_info(asset['asset-id'])
                fallen_name = metadata_decoded.get("properties", {}).get("Name", asset_info['params']['unit-name'])
                fallen_assets.append([asset_info['params']['unit-name'], asset_info['index'], fallen_name])
                count += 1
        
        if fallen_assets == []:
            embedNoFO = discord.Embed(
                title=f"Awwww...{ctx.author.name} does not own any Fallen Order!",
                description=f"[Click Here To Shuffle!](https://algoxnft.com/shuffle/902)",
                color=0xFF0000
            )
            embedNoFO.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
            await message.edit(embed=embedNoFO)
            return
        
        select_options = [create_select_option(label=fallen[0] + " - " + fallen[2], value=str(fallen[1])) for fallen in fallen_assets]
        select = create_select(options=select_options, placeholder="Select the character you want to add Points to", min_values=1, max_values=1)
        action_row = create_actionrow(select)
        await message.edit(embed=embedUpgradeInProgress, components=[action_row])
        try:
            while True:
                interaction: ComponentContext = await wait_for_component(client, components=action_row, timeout=30.0)
                interaction_author_id = interaction.author.id
                if interaction_author_id == ctx.author.id:
                    await interaction.defer(edit_origin=True)
                    chosen_fallen = interaction.selected_options[0]
                    break
                else:
                    embedWrongUpgrade = discord.Embed(
                        title=f"This is not your upgrade!",
                        description=f"{ctx.author.name} is currently boosting..",
                        color=0xFF0000
                    )
                    await interaction.send(embed=embedWrongUpgrade, hidden=True)
                    continue
        except asyncio.TimeoutError:
            embedTimeout = discord.Embed(
                    title=f"Woops! You took too long to respond...",
                    description=f"Ending {ctx.author.name}'s point boost..",
                    color=0xFF0000
                )
            await message.edit(embed=embedTimeout, components=[])
            await asyncio.sleep(10)
            await message.delete()
            return
        metadata_api = f"https://mainnet-idx.algonode.cloud/v2/transactions?tx-type=acfg&asset-id={chosen_fallen}&address={fallen_order_manager}"
        response = requests.get(metadata_api)
        if response.status_code == 200:
            data = response.json()
        else:
            print("Error fetching data from API")
        metadata_decoded = json.loads((base64.b64decode((data["transactions"][0]["note"]).encode('utf-8'))).decode('utf-8'))
        points_available = int(metadata_decoded["properties"]["Points"])
        asset_info = algod_client.asset_info(chosen_fallen)
        fallen_image_url = asset_info["params"]["url"]
        fallen_image = "https://ipfs.algonft.tools/ipfs/" + (fallen_image_url).replace("ipfs://", "")
        fallen_name = metadata_decoded.get("properties", {}).get("Name", asset_info['params']['unit-name'])
        metadata_decoded["properties"]["Points"] = points_available + 50
        metadata_encoded = json.dumps(metadata_decoded)

        embedDisplayChar = discord.Embed(
                title=f"⚠️ Confirm Points Boost - {ctx.author.name} ⚠️",
                description=f"Current Points - {points_available}\n\nNew Points - {points_available + 50}",
                color=0xFCE303
            )
        embedDisplayChar.set_image(url=fallen_image)
        embedDisplayChar.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        embedDisplayChar.set_footer(text=f"\nCost: 1 Stat Booster $BOOST\n\nAre you sure you want to add 50 Points to {fallen_name}?")

        action_row = create_actionrow(
                            create_button(style=ButtonStyle.green, label="Confirm", custom_id="confirm"),
                            create_button(style=ButtonStyle.red, label="Cancel", custom_id="cancel")
                        )

        await message.edit(embed=embedDisplayChar, components=[action_row])
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
                    embedDisplayChar.set_footer(text=f"Please wait while I update your metadata...⏳")
                    await message.edit(embed=embedDisplayChar, components=[])
                    await send_assets("Stat Booster Used. " + str(ctx.author.name), wallet, fallen_order_main, 815771120, "BOOST", 1)
                    await edit_metadata(chosen_fallen, metadata_encoded)

            else:
                embedWrongUpgrade = discord.Embed(
                    title=f"This is not your Points boost!",
                    description=f"{ctx.author.name} is currently adding Points..",
                    color=0xFF0000
                )
                await interaction.send(embed=embedWrongUpgrade, hidden=True)
        except asyncio.TimeoutError:
            embedTimeout = discord.Embed(
                    title=f"Woops! You took too long to respond...",
                    description=f"Ending {ctx.author.name}'s points addition..",
                    color=0xFF0000
                )
            await message.edit(embed=embedTimeout, components=[])
            await asyncio.sleep(10)
            await message.delete()
            return

        embedUpgradeDone = discord.Embed(
                title=f"Your Fallen Order character received 50 Points!",
                url=f"https://nftexplorer.app/asset/{chosen_fallen}",
                description=f"You now have {points_available + 50} Points available on your character",
                color=0x28FF0A
            )
        embedUpgradeDone.set_image(url=fallen_image)
        embedUpgradeDone.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        
        embedUpgradeDone.set_footer(text=f"Thank you, Master {ctx.author.name}! My Points will come in handy!")
        await message.edit(embed=embedUpgradeDone, components=[])
        
    @add_points.error
    async def add_points_error(self, ctx, error):
        embedNotAllowed = discord.Embed(
                    title=f"Please wait 30sec before this command becomes available again!",
                    color=0xFF0000
                )
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(embed=embedNotAllowed, hidden=True)


class AddNameCog(commands.Cog):
    @cog_ext.cog_slash(name="rename", description="Name your Characters!")
    @commands.cooldown(1, 60, commands.BucketType.guild)
    async def add_name(self, ctx):
        if ctx.channel.id != 1082157256679882862:
            await ctx.send(embed=embedWrongChannelBoost, hidden=True)
            return
        embedUpgradeInProgress = discord.Embed(
                title=f"🧙‍♂️ Initiating Rename... 🧙‍♂️",
                description=f"{ctx.author.name} gathers their Fallen Order to rename them...",
                color=0xFCE303
            )
        embedUpgradeInProgress.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        message = await ctx.send(embed=embedUpgradeInProgress)
        wallet, name, won, lost, expwon, explost, lastdrip, drip_exp = await get_wallet(str(ctx.author.id))
        if wallet == '':
            embedNoReg = discord.Embed(
                title="Click Here To Register!",
                url="https://app.fallenorder.xyz",
                description=f"Please verify your wallet via our website to continue..\nEnsure you copy your user id below for the verification process:\nUser ID: {ctx.author.id}",
                color=0xFF1C0A,
            )
            await message.edit(embed=embedNoReg, hidden=True)
            return
        balance_exp = await get_balance(wallet, 811721471)
        if balance_exp == -1:
            await message.edit(embed=embedNoOptEXP)
            return
        if balance_exp < 100:
            embedNoEXP = discord.Embed(title=f"Woops! You do not own enough $EXP!", description=f"Renaming a character costs 100 $EXP...", color=0xFF0000)
            embedNoEXP.set_thumbnail(url="https://s3.amazonaws.com/algorand-wallet-mainnet-thumbnails/prism-images/media/assets-logo-png/2022/10/11/a26da3af714a40e8bad2b29a6dfc4655.png--resize--w__200--q__70.webp")   
            await message.edit(embed=embedNoEXP)
            return
        fallen_assets = []
        account_info = algod_client.account_info(wallet)
        assets = account_info.get("assets", [])
        count = 0
        for asset in assets:
            if count == 25:
                break
            if asset["amount"] > 0 and (asset["asset-id"] in fo_rank1 or asset["asset-id"] in fo_rank2 or asset["asset-id"] in fo_rank3 or asset["asset-id"] in fo_rank4 or asset["asset-id"] in fo_rank5):
                metadata_api = f"https://mainnet-idx.algonode.cloud/v2/transactions?tx-type=acfg&asset-id={asset['asset-id']}&addres={fallen_order_manager}"
                response = requests.get(metadata_api)
                if response.status_code == 200:
                    data = response.json()
                else:
                    print("Error fetching data from API")
                metadata_decoded = json.loads((base64.b64decode((data["transactions"][0]["note"]).encode('utf-8'))).decode('utf-8'))
                asset_info = algod_client.asset_info(asset['asset-id'])
                fallen_name = metadata_decoded.get("properties", {}).get("Name", "None")
                fallen_assets.append([asset_info['params']['unit-name'], asset_info['index'], fallen_name])
                count += 1
        
        if fallen_assets == []:
            embedNoFO = discord.Embed(
                title=f"Awwww...{ctx.author.name} does not own any Fallen Order!",
                description=f"[Click Here To Shuffle!](https://algoxnft.com/shuffle/902)",
                color=0xFF0000
            )
            embedNoFO.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
            await message.edit(embed=embedNoFO)
            return
        
        select_options = [create_select_option(label=fallen[0] + " - " + fallen[2], value=str(fallen[1])) for fallen in fallen_assets]
        select = create_select(options=select_options, placeholder="Select the character you want to rename", min_values=1, max_values=1)
        action_row = create_actionrow(select)
        await message.edit(embed=embedUpgradeInProgress, components=[action_row])
        try:
            while True:
                interaction: ComponentContext = await wait_for_component(client, components=action_row, timeout=30.0)
                interaction_author_id = interaction.author.id
                if interaction_author_id == ctx.author.id:
                    await interaction.defer(edit_origin=True)
                    chosen_fallen = interaction.selected_options[0]
                    break
                else:
                    embedWrongUpgrade = discord.Embed(
                        title=f"This is not your character rename!",
                        description=f"{ctx.author.name} is currently renaming their character..",
                        color=0xFF0000
                    )
                    await interaction.send(embed=embedWrongUpgrade, hidden=True)
                    continue
        except asyncio.TimeoutError:
            embedTimeout = discord.Embed(
                    title=f"Woops! You took too long to respond...",
                    description=f"Ending {ctx.author.name}'s character rename..",
                    color=0xFF0000
                )
            await message.edit(embed=embedTimeout, components=[])
            await asyncio.sleep(10)
            await message.delete()
            return

        metadata_api = f"https://mainnet-idx.algonode.cloud/v2/transactions?tx-type=acfg&asset-id={chosen_fallen}&address={fallen_order_manager}"
        response = requests.get(metadata_api)
        if response.status_code == 200:
            data = response.json()
        else:
            print("Error fetching data from API")
        metadata_decoded = json.loads((base64.b64decode((data["transactions"][0]["note"]).encode('utf-8'))).decode('utf-8'))
        asset_info = algod_client.asset_info(chosen_fallen)
        fallen_image_url = asset_info["params"]["url"]
        fallen_image = "https://ipfs.algonft.tools/ipfs/" + (fallen_image_url).replace("ipfs://", "")
        fallen_name = metadata_decoded.get("properties", {}).get("Name", "None")

        embedDisplayChar = discord.Embed(
                title=f"🧙‍♂️ Character Rename - {ctx.author.name} 🧙‍♂️",
                description=f"Current Name: {fallen_name}",
                color=0xFCE303
            )
        embedDisplayChar.set_image(url=fallen_image)
        embedDisplayChar.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        embedDisplayChar.set_footer(text=f"Please enter the name you want to give your character:\n*max 16 characters*\n\nSample:\nFallen Mage")

        await message.edit(embed=embedDisplayChar, components=[])

        embedWrongInputs = discord.Embed(
                title=f"Oops! Invalid Input!",
                description=f"Please send the name in one single message...",
                color=0xFCE303
            )

        def check(m):
            return m.author == interaction.author

        try:
            response = await client.wait_for("message", check=check, timeout=60.0)
        except asyncio.TimeoutError:
            embedTimeout = discord.Embed(
                    title=f"Woops! You took too long to respond...",
                    description=f"Ending {ctx.author.name}'s upgrade..",
                    color=0xFF0000
                )
            await message.edit(embed=embedTimeout, components=[])
            await asyncio.sleep(10)
            await message.delete()
            return
        await asyncio.sleep(1)
        await response.delete()
        try:
            input_value1 = [response.content]
        except ValueError:
            await message.edit(embed=embedWrongInputs)
            await asyncio.sleep(10)
            await message.delete()
            return
        metadata_decoded["properties"]["Name"] = input_value1[0]
        metadata_encoded = json.dumps(metadata_decoded)
        if len(input_value1[0]) > 16 or "\\" in metadata_encoded:
            embedWrongInputs2 = discord.Embed(
                title=f"You can not use emojis or more than 16 characters!",
                description=f"Your Input: {input_value1[0]}",
                color=0xFF0000
            )
            await message.edit(embed=embedWrongInputs2)
            await asyncio.sleep(10)
            await message.delete()
            return
        
        embedConfirmUpgrade = discord.Embed(
                title=f"⚠️ Confirm Character Rename ⚠️",
                description=f"Ensure All Details Below Are Correct:",
                color=0xFCE303
            )
        embedConfirmUpgrade.add_field(name=f"Previous Name", value=f"{fallen_name}", inline=False)
        embedConfirmUpgrade.add_field(name=f"New Name", value=f"{input_value1[0]}", inline=False)
        embedConfirmUpgrade.set_image(url=fallen_image)
        embedConfirmUpgrade.set_footer(text=f"Renaming will cost 100 $EXP!")
        embedConfirmUpgrade.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        action_row = create_actionrow(
                            create_button(style=ButtonStyle.green, label="Confirm", custom_id="confirm"),
                            create_button(style=ButtonStyle.red, label="Cancel", custom_id="cancel")
                        )

        await message.edit(embed=embedConfirmUpgrade, components=[action_row])
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
                    embedConfirmUpgrade.set_footer(text=f"Please wait while I update your metadata...⏳")
                    await message.edit(embed=embedConfirmUpgrade, components=[])
                    await send_assets("Character Rename. " + str(ctx.author.name), wallet, fallen_order_main, 811721471, "EXP", 100)
                    await edit_metadata(chosen_fallen, metadata_encoded)

            else:
                embedWrongUpgrade = discord.Embed(
                    title=f"This is not your character rename!",
                    description=f"{ctx.author.name} is currently renaming..",
                    color=0xFF0000
                )
                await interaction.send(embed=embedWrongUpgrade, hidden=True)
        except asyncio.TimeoutError:
            embedTimeout = discord.Embed(
                    title=f"Woops! You took too long to respond...",
                    description=f"Ending {ctx.author.name}'s character rename..",
                    color=0xFF0000
                )
            await message.edit(embed=embedTimeout, components=[])
            await asyncio.sleep(10)
            await message.delete()
            return

        embedUpgradeDone = discord.Embed(
                title=f"Your Fallen Order character has been renamed successfully!",
                url=f"https://nftexplorer.app/asset/{chosen_fallen}",
                color=0x28FF0A
            )
        embedUpgradeDone.add_field(name=f"New Name", value=f"{input_value1[0]}", inline=False)
        embedUpgradeDone.set_image(url=fallen_image)
        embedUpgradeDone.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        embedUpgradeDone.set_footer(text=f"Thank you, Master {ctx.author.name}! I love my new name!")
        await message.edit(embed=embedUpgradeDone, components=[])
        
    @add_name.error
    async def add_name_error(self, ctx, error):
        embedNotAllowed = discord.Embed(
                    title=f"Please wait 30sec before this command becomes available again!",
                    color=0xFF0000
                )
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(embed=embedNotAllowed, hidden=True)


class AddAbilityCog(commands.Cog):
    @cog_ext.cog_slash(name="swap-ability", description="Adjust Your Character's Abilities and Ultimate!")
    @commands.cooldown(1, 30, commands.BucketType.guild)
    async def add_ability(self, ctx):
        if ctx.channel.id != 1082157256679882862:
            await ctx.send(embed=embedWrongChannelBoost, hidden=True)
            return
        embedUpgradeInProgress = discord.Embed(
                title=f"🧙‍♂️ Initiating Ability Swap... 🧙‍♂️",
                description=f"{ctx.author.name} gathers their Fallen Order to swap their abilities...",
                color=0xFCE303
            )
        embedUpgradeInProgress.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        message = await ctx.send(embed=embedUpgradeInProgress)
        wallet, name, won, lost, expwon, explost, lastdrip, drip_exp = await get_wallet(str(ctx.author.id))
        if wallet == '':
            embedNoReg = discord.Embed(
                title="Click Here To Register!",
                url="https://app.fallenorder.xyz",
                description=f"Please verify your wallet via our website to continue..\nEnsure you copy your user id below for the verification process:\nUser ID: {ctx.author.id}",
                color=0xFF1C0A,
            )
            await message.edit(embed=embedNoReg, hidden=True)
            return
        balance_exp = await get_balance(wallet, 811721471)
        if balance_exp == -1:
            await message.edit(embed=embedNoOptEXP)
            return
        if balance_exp < 25:
            embedNoEXP = discord.Embed(title=f"Woops! You do not own enough $EXP!", description=f"Ability swapping costs 25 $EXP...", color=0xFF0000)
            embedNoEXP.set_thumbnail(url="https://s3.amazonaws.com/algorand-wallet-mainnet-thumbnails/prism-images/media/assets-logo-png/2022/10/11/a26da3af714a40e8bad2b29a6dfc4655.png--resize--w__200--q__70.webp")   
            await message.edit(embed=embedNoEXP)
            return
        fallen_assets = []
        account_info = algod_client.account_info(wallet)
        assets = account_info.get("assets", [])
        count = 0
        for asset in assets:
            if count == 25:
                break
            if asset["amount"] > 0 and (asset["asset-id"] in fo_rank1 or asset["asset-id"] in fo_rank2 or asset["asset-id"] in fo_rank3 or asset["asset-id"] in fo_rank4 or asset["asset-id"] in fo_rank5):
                metadata_api = f"https://mainnet-idx.algonode.cloud/v2/transactions?tx-type=acfg&asset-id={asset['asset-id']}&address={fallen_order_manager}"
                response = requests.get(metadata_api)
                if response.status_code == 200:
                    data = response.json()
                else:
                    print("Error fetching data from API")
                metadata_decoded = json.loads((base64.b64decode((data["transactions"][0]["note"]).encode('utf-8'))).decode('utf-8'))
                asset_info = algod_client.asset_info(asset['asset-id'])
                fallen_name = metadata_decoded.get("properties", {}).get("Name", "None")
                fallen_assets.append([asset_info['params']['unit-name'], asset_info['index'], fallen_name])
                count += 1
        
        if fallen_assets == []:
            embedNoFO = discord.Embed(
                title=f"Awwww...{ctx.author.name} does not own any Fallen Order!",
                description=f"[Click Here To Shuffle!](https://algoxnft.com/shuffle/902)",
                color=0xFF0000
            )
            embedNoFO.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
            await message.edit(embed=embedNoFO)
            return
        select_options = [create_select_option(label=fallen[0] + " - " + fallen[2], value=str(fallen[1])) for fallen in fallen_assets]
        select = create_select(options=select_options, placeholder="Select the character you want to edit", min_values=1, max_values=1)
        action_row = create_actionrow(select)
        await message.edit(embed=embedUpgradeInProgress, components=[action_row])
        try:
            while True:
                interaction: ComponentContext = await wait_for_component(client, components=action_row, timeout=30.0)
                interaction_author_id = interaction.author.id
                if interaction_author_id == ctx.author.id:
                    await interaction.defer(edit_origin=True)
                    chosen_fallen = interaction.selected_options[0]
                    break
                else:
                    embedWrongUpgrade = discord.Embed(
                        title=f"This is not your ability swap!",
                        description=f"{ctx.author.name} is currently swapping abilities..",
                        color=0xFF0000
                    )
                    await interaction.send(embed=embedWrongUpgrade, hidden=True)
                    continue
        except asyncio.TimeoutError:
            embedTimeout = discord.Embed(
                    title=f"Woops! You took too long to respond...",
                    description=f"Ending {ctx.author.name}'s ability swap..",
                    color=0xFF0000
                )
            await message.edit(embed=embedTimeout, components=[])
            await asyncio.sleep(10)
            await message.delete()
            return
        metadata_api = f"https://mainnet-idx.algonode.cloud/v2/transactions?tx-type=acfg&asset-id={chosen_fallen}&address={fallen_order_manager}"
        response = requests.get(metadata_api)
        if response.status_code == 200:
            data = response.json()
        else:
            print("Error fetching data from API")
        metadata_decoded = json.loads((base64.b64decode((data["transactions"][0]["note"]).encode('utf-8'))).decode('utf-8'))
        asset_info = algod_client.asset_info(chosen_fallen)
        fallen_image_url = asset_info["params"]["url"]
        fallen_image = "https://ipfs.algonft.tools/ipfs/" + (fallen_image_url).replace("ipfs://", "")
        fallen_name = metadata_decoded.get("properties", {}).get("Name", asset_info['params']['unit-name'])
        current_ability_1 = metadata_decoded.get("properties", {}).get("Ability 1", "None")
        current_ability_2 = metadata_decoded.get("properties", {}).get("Ability 2", "None")
        current_ability_3 = metadata_decoded.get("properties", {}).get("Ability 3", "None")
        current_ultimate = metadata_decoded.get("properties", {}).get("Ultimate", "None")

        embedDisplayChar = discord.Embed(
                title=f"🧙‍♂️ Ability Swap - {ctx.author.name} 🧙‍♂️",
                description=f"Character: {fallen_name}",
                color=0xFCE303
            )
        embedDisplayChar.set_image(url=fallen_image)
        embedDisplayChar.add_field(name=f"Ability 1 | Ability 2 | Ability 3", value=f"{current_ability_1} | {current_ability_2} | {current_ability_3}", inline=False)
        embedDisplayChar.add_field(name=f"Ultimate", value=f"{current_ultimate}", inline=False)
        embedDisplayChar.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        embedDisplayChar.set_footer(text=f"Please select the ability you want to equip:")
        select_options = [  create_select_option(label="Ability 1", value="Ability 1"),
                                create_select_option(label="Ability 2", value="Ability 2"),
                                create_select_option(label="Ability 3", value="Ability 3"),
                                create_select_option(label="Ultimate", value="Ultimate")
                            ]
        select = create_select(options=select_options, placeholder="Select Ability Slot To Swap", min_values=1, max_values=1)
        action_row = create_actionrow(select)
        await message.edit(embed=embedDisplayChar, components=[action_row])
        try:
            while True:
                interaction: ComponentContext = await wait_for_component(client, components=action_row, timeout=30.0)
                interaction_author_id = interaction.author.id
                if interaction_author_id == ctx.author.id:
                    await interaction.defer(edit_origin=True)
                    ability = interaction.selected_options[0]
                    if ability == "Ability 1":
                        current_ability = current_ability_1
                    elif ability == "Ability 2":
                        current_ability = current_ability_2
                    elif ability == "Ability 3":
                        current_ability = current_ability_3
                    elif ability == "Ultimate":
                        current_ability = current_ultimate
                    else:
                        await message.delete()
                        return
                    break
                else:
                    embedWrongUpgrade = discord.Embed(
                        title=f"This is not your ability swap!",
                        description=f"{ctx.author.name} is currently swapping abilities..",
                        color=0xFF0000
                    )
                    await interaction.send(embed=embedWrongUpgrade, hidden=True)
                    continue
        except asyncio.TimeoutError:
            embedTimeout = discord.Embed(
                    title=f"Woops! You took too long to respond...",
                    description=f"Ending {ctx.author.name}'s ability swap..",
                    color=0xFF0000
                )
            await message.edit(embed=embedTimeout, components=[])
            await asyncio.sleep(10)
            await message.delete()
            return
        basic_1 = "Slash"
        basic_2 = "Fury"
        basic_3 = "Fireball"
        basic_4 = "Arcane Nova"
        basic_5 = "Retribution"
        basic_6 = "Eclipse"
        basic_7 = "Soul Surge"
        basic_8 = "Purify"
        ultimate_1 = "Death Blow"
        ultimate_2 = "Divine Aura"
        ultimate_3 = "Mirage"
        ultimate_4 = "Pestilence"
        ultimate_5 = "Molten Rage"
        if ability == "Ultimate":
            select_options = [  create_select_option(label=ultimate_1, value=ultimate_1),
                                create_select_option(label=ultimate_2, value=ultimate_2),
                                create_select_option(label=ultimate_3, value=ultimate_3),
                                create_select_option(label=ultimate_4, value=ultimate_4),
                                create_select_option(label=ultimate_5, value=ultimate_5),
                            ]
        else:
            select_options = [  create_select_option(label=basic_1, value=basic_1),
                                create_select_option(label=basic_2, value=basic_2),
                                create_select_option(label=basic_3, value=basic_3),
                                create_select_option(label=basic_4, value=basic_4),
                                create_select_option(label=basic_5, value=basic_5),
                                create_select_option(label=basic_6, value=basic_6),
                                create_select_option(label=basic_7, value=basic_7),
                                create_select_option(label=basic_8, value=basic_8)
                            ]
        select = create_select(options=select_options, placeholder="Select New Ability", min_values=1, max_values=1)
        action_row = create_actionrow(select)
        await message.edit(embed=embedDisplayChar, components=[action_row])
        try:
            while True:
                interaction: ComponentContext = await wait_for_component(client, components=action_row, timeout=30.0)
                interaction_author_id = interaction.author.id
                if interaction_author_id == ctx.author.id:
                    await interaction.defer(edit_origin=True)
                    chosen_ability = interaction.selected_options[0]
                    if ability == "Ability 1":
                        current_ability_1 = chosen_ability
                    elif ability == "Ability 2":
                        current_ability_2 = chosen_ability
                    elif ability == "Ability 3":
                        current_ability_3 = chosen_ability
                    elif ability == "Ultimate":
                        current_ultimate = chosen_ability
                    else:
                        await message.delete()
                        return
                    break
                else:
                    embedWrongUpgrade = discord.Embed(
                        title=f"This is not your ability swap!",
                        description=f"{ctx.author.name} is currently swapping abilities..",
                        color=0xFF0000
                    )
                    await interaction.send(embed=embedWrongUpgrade, hidden=True)
                    continue
        except asyncio.TimeoutError:
            embedTimeout = discord.Embed(
                    title=f"Woops! You took too long to respond...",
                    description=f"Ending {ctx.author.name}'s ability swap..",
                    color=0xFF0000
                )
            await message.edit(embed=embedTimeout, components=[])
            await asyncio.sleep(10)
            await message.delete()
            return
        
        metadata_decoded["properties"][ability] = chosen_ability
        metadata_encoded = json.dumps(metadata_decoded)
        
        embedConfirmUpgrade = discord.Embed(
                title=f"⚠️ Confirm Ability Swap ⚠️",
                description=f"Ensure All Details Below Are Correct:",
                color=0xFCE303
            )
        embedConfirmUpgrade.add_field(name=f"Previous {ability}", value=f"{current_ability}", inline=False)
        embedConfirmUpgrade.add_field(name=f"New {ability}", value=f"{chosen_ability}", inline=False)
        embedConfirmUpgrade.set_image(url=fallen_image)
        embedConfirmUpgrade.set_footer(text=f"Ability swap will cost 25 $EXP!")
        embedConfirmUpgrade.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")

        action_row = create_actionrow(
                            create_button(style=ButtonStyle.green, label="Confirm", custom_id="confirm"),
                            create_button(style=ButtonStyle.red, label="Cancel", custom_id="cancel")
                        )

        await message.edit(embed=embedConfirmUpgrade, components=[action_row])
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
                    embedConfirmUpgrade.set_footer(text=f"Please wait while I update your metadata...⏳")
                    await message.edit(embed=embedConfirmUpgrade, components=[])
                    await send_assets("Character Rename. " + str(ctx.author.name), wallet, fallen_order_main, 811721471, "EXP", 25)
                    await edit_metadata(chosen_fallen, metadata_encoded)

            else:
                embedWrongUpgrade = discord.Embed(
                    title=f"This is not your character ability swap!",
                    color=0xFF0000
                )
                await interaction.send(embed=embedWrongUpgrade, hidden=True)
        except asyncio.TimeoutError:
            embedTimeout = discord.Embed(
                    title=f"Woops! You took too long to respond...",
                    description=f"Ending {ctx.author.name}'s character ability swapping..",
                    color=0xFF0000
                )
            await message.edit(embed=embedTimeout, components=[])
            await asyncio.sleep(10)
            await message.delete()
            return

        embedUpgradeDone = discord.Embed(
                title=f"Your Fallen Order character's abilities have been swapped!",
                url=f"https://nftexplorer.app/asset/{chosen_fallen}",
                color=0x28FF0A
            )
        embedUpgradeDone.add_field(name=f"Ability 1 | Ability 2 | Ability 3", value=f"{current_ability_1} | {current_ability_2} | {current_ability_3}", inline=False)
        embedUpgradeDone.add_field(name=f"Ultimate", value=f"{current_ultimate}", inline=False)
        embedUpgradeDone.set_image(url=fallen_image)
        embedUpgradeDone.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        embedUpgradeDone.set_footer(text=f"Thank you, Master {ctx.author.name}! Ready to kick ass with my new abilities!")
        await message.edit(embed=embedUpgradeDone, components=[])
        
    @add_ability.error
    async def add_ability_error(self, ctx, error):
        embedNotAllowed = discord.Embed(
                    title=f"Please wait 30sec before this command becomes available again!",
                    color=0xFF0000
                )
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(embed=embedNotAllowed, hidden=True)


class KinshipCog(commands.Cog):
    @cog_ext.cog_slash(name="kinship", description="Add 1 Kinship Point To Your Fallen Order! (Once Per 24H)")
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def add_kinship(self, ctx):
        if ctx.channel.id != 1081221312011309127:
            await ctx.send(embed=embedNotKinshipChannel)
            return        
        embedKinshipInProgress = discord.Embed(
                title=f"🧙‍♂️ Kinship Ritual In Progress... 🧙‍♂️",
                description=f"{ctx.author.name} gathers their Fallen Order to cast a kinship ritual...",
                color=0xFCE303
            )
        embedKinshipInProgress.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        embedKinshipInProgress.set_footer(text=f"The earth starts to rumble and the skies fill with dark clouds and thunder ⚡")
        message = await ctx.send(embed=embedKinshipInProgress)
        wallet, name, won, lost, expwon, explost, lastdrip, drip_exp = await get_wallet(str(ctx.author.id))
        if wallet == '':
            embedNoReg = discord.Embed(
                title="Click Here To Register!",
                url="https://app.fallenorder.xyz",
                description=f"Please verify your wallet via our website to continue..\nEnsure you copy your user id below for the verification process:\nUser ID: {ctx.author.id}",
                color=0xFF1C0A,
            )
            await message.edit(embed=embedNoReg)
            return
        fallen_assets = []
        account_info = algod_client.account_info(wallet)
        assets = account_info.get("assets", [])
        for asset in assets:
            if asset["amount"] > 0 and (asset["asset-id"] in fo_rank1 or asset["asset-id"] in fo_rank2 or asset["asset-id"] in fo_rank3 or asset["asset-id"] in fo_rank4 or asset["asset-id"] in fo_rank5):
                fallen_assets.append(asset['asset-id'])        
        if fallen_assets == []:
            embedNoFO = discord.Embed(
                title=f"Awwww...{ctx.author.name} does not own any Fallen Order!",
                description=f"[Click Here To Shuffle!](https://algoxnft.com/shuffle/902)",
                color=0xFF0000
            )
            embedNoFO.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
            await message.edit(embed=embedNoFO)
            return
        embedKinshipDone = discord.Embed(
                title=f"All of your characters have already casted a kinship ritual in the past 24 hours!",
                color=0xFF0000
            )
        embedKinshipDone.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        embedKinshipDone.set_footer(text="Please return at the next available Kinship interval!\n\n*Reminder*\nWe now have Auto-Kinship subscriptions available for your convenience!\nUse /auto-kinship to view details", icon_url="https://s3.amazonaws.com/algorand-wallet-mainnet-thumbnails/prism-images/media/asset_verification_requests_logo_png/2022/06/22/d2c56a8e61244bd78017e38180d15c91.png--resize--w__200--q__70.webp")
        final_data = []
        for fallen in fallen_assets:
            metadata_api = f"https://mainnet-idx.algonode.cloud/v2/transactions?tx-type=acfg&asset-id={fallen}&address={fallen_order_manager}"
            response = requests.get(metadata_api)
            if response.status_code == 200:
                data = response.json()
            else:
                print("Error fetching data from API")
            utc = pytz.timezone('UTC')
            now_datetime = datetime.now(utc)
            kinships = []
            counter = 0
            while len(data["transactions"]) > counter:
                kinships.append((json.loads((base64.b64decode((data["transactions"][counter]["note"]).encode('utf-8'))).decode('utf-8')))["properties"]["Kinship"])
                counter += 1
            flag = True
            flag_count = 1
            kinship_found = False
            metadata_decoded = json.loads((base64.b64decode((data["transactions"][0]["note"]).encode('utf-8'))).decode('utf-8'))
            while flag and flag_count < len(kinships):
                if kinships[flag_count-1] != kinships[flag_count]:
                    confirmed_round = data["transactions"][flag_count-1]["confirmed-round"]
                    duration = now_datetime - ((datetime.fromtimestamp((algod_client.block_info(confirmed_round))["block"]["ts"])).astimezone(utc))
                    hours_since = round(duration.total_seconds() / 3600, 2)
                    time_left = timedelta(hours=24) - duration
                    seconds = time_left.total_seconds()
                    flag = False
                    kinship_found = True
                flag_count += 1
            if not kinship_found:
                duration = 0
                hours_since = 100
                time_left = timedelta(hours=24)
                seconds = time_left.total_seconds()
            kinship = kinships[flag_count-2]
            asset_info = algod_client.asset_info(fallen)
            fallen_name = metadata_decoded.get("properties", {}).get("Name", asset_info['params']['unit-name'])
            if seconds < 0:
                timer = "Ready!"
            else:
                timer = ((datetime.utcfromtimestamp(seconds)).strftime('%HH %MM %SS')).lstrip('0')
            if timer.startswith("H "):
                dt = timer[2:]
            else:
                dt = timer
            if hours_since >= 24:
                new_kinship = int(kinship) + 1
                metadata_decoded["properties"]["Kinship"] = new_kinship
                metadata_encoded = json.dumps(metadata_decoded)
                final_data.append([fallen_name, new_kinship])
                await edit_metadata(fallen, metadata_encoded)
            else:
                embedKinshipDone.add_field(name=f"{fallen_name} - {dt}", value=f"-----", inline=False)
        if final_data == []:
            await message.edit(embed=embedKinshipDone)
            embedKinshipDone.clear_fields()
            return  
        embedKinshipAdded = discord.Embed(
                title=f"Kinship Ritual Successful!",
                description=f"The following {len(final_data)} Fallen Order characters were boosted",
                color=0xFCE303
            )
        count = 0
        while count < 25 and count < len(final_data):
            for tx in final_data:
                embedKinshipAdded.add_field(name=f"🔥 {tx[0]} upgraded to {tx[1]} Kinship! 🔥", value=f"-", inline=False)
                count += 1
        embedKinshipAdded.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        embedKinshipAdded.set_footer(text=f"Thank you, Master {ctx.author.name}! Don't forget to cast our next ritual in 24H! ⏳\n\n*Reminder*\nWe now have Auto-Kinship subscriptions available for your convenience!\nUse /auto-kinship to view details")
        await message.edit(embed=embedKinshipAdded)
        embedKinshipDone.clear_fields()
        embedKinshipAdded.clear_fields()
        return
        
    @add_kinship.error
    async def add_kinship_error(self, ctx, error):
        embedNotAllowed = discord.Embed(
                    title=f"Please wait 30sec before this command becomes available again!",
                    color=0xFF0000
                )
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(embed=embedNotAllowed, hidden=True)
        
class LevelUpCog(commands.Cog):
    @cog_ext.cog_slash(name="levelup", description="Add 1 Level Point To Your Fallen Order and get a Stat Booster!")
    @commands.cooldown(1, 30, commands.BucketType.guild)
    async def level_character(self, ctx):
        if ctx.channel.id != 1082157256679882862:
            await ctx.send(embed=embedWrongChannelBoost, hidden=True)
            return
        level_up_cost_order = [100,120,140,160,180,200,220,240,260,280,300,320,340,360,380,400,420,440,460,480,500]
        level_up_cost_exp = [1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000, 11000, 12000, 13000, 14000, 15000, 16000, 17000, 18000, 19000, 20000]
        embedLevelUpInProgress = discord.Embed(
                title=f"🧙‍♂️ Initiating Level Up... 🧙‍♂️",
                description=f"{ctx.author.name} gathers their Fallen Order to boost their level...",
                color=0xFCE303
            )
        embedLevelUpInProgress.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        message = await ctx.send(embed=embedLevelUpInProgress)
        wallet, name, won, lost, expwon, explost, lastdrip, drip_exp = await get_wallet(str(ctx.author.id))
        if wallet == '':
            embedNoReg = discord.Embed(
                title="Click Here To Register!",
                url="https://app.fallenorder.xyz",
                description=f"Please verify your wallet via our website to continue..\nEnsure you copy your user id below for the verification process:\nUser ID: {ctx.author.id}",
                color=0xFF1C0A,
            )
            await message.edit(embed=embedNoReg)
            return
        balance_boost = await get_balance(wallet, 815771120)
        if balance_boost == -1:
            embedNoOptBoost = discord.Embed(title=f"Woops! You must first opt into Stat Booster to receive it after your level up!", description=f"[Click Here To Opt In...](https://www.randgallery.com/algo-collection/?address=815771120)", color=0xFF0000)
            embedNoOptBoost.set_image(url="https://nft-media.algoexplorerapi.io/images/bafybeibdnf2qn7a3w5ckxecv4svykpntufjkqh2zank6kx6mn2idik2nz4")
            await message.edit(embed=embedNoOptBoost)
            return
        fallen_assets = []
        account_info = algod_client.account_info(wallet)
        assets = account_info.get("assets", [])
        count = 0
        for asset in assets:
            if count == 25:
                break
            if asset["amount"] > 0 and (asset["asset-id"] in fo_rank1 or asset["asset-id"] in fo_rank2 or asset["asset-id"] in fo_rank3 or asset["asset-id"] in fo_rank4 or asset["asset-id"] in fo_rank5):
                metadata_api = f"https://mainnet-idx.algonode.cloud/v2/transactions?tx-type=acfg&asset-id={asset['asset-id']}&address={fallen_order_manager}"
                response = requests.get(metadata_api)
                if response.status_code == 200:
                    data = response.json()
                else:
                    print("Error fetching data from API")
                metadata_decoded = json.loads((base64.b64decode((data["transactions"][0]["note"]).encode('utf-8'))).decode('utf-8'))
                asset_info = algod_client.asset_info(asset['asset-id'])
                fallen_name = metadata_decoded.get("properties", {}).get("Name", "None")
                fallen_assets.append([asset_info['params']['unit-name'], asset_info['index'], fallen_name])
                count += 1
        
        if fallen_assets == []:
            embedNoFO = discord.Embed(
                title=f"Awwww...{ctx.author.name} does not own any Fallen Order!",
                description=f"[Click Here To Shuffle!](https://algoxnft.com/shuffle/902)",
                color=0xFF0000
            )
            embedNoFO.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
            await message.edit(embed=embedNoFO)
            return
        
        select_options = [create_select_option(label=fallen[0] + " - " + fallen[2], value=str(fallen[1])) for fallen in fallen_assets]
        select = create_select(options=select_options, placeholder="Select the character you want to upgrade", min_values=1, max_values=1)
        action_row = create_actionrow(select)
        await message.edit(embed=embedLevelUpInProgress, components=[action_row])
        try:
            while True:
                interaction: ComponentContext = await wait_for_component(client, components=action_row, timeout=30.0)
                interaction_author_id = interaction.author.id

                if interaction_author_id == ctx.author.id:
                    await interaction.defer(edit_origin=True)
                    chosen_fallen = interaction.selected_options[0]
                    break
                else:
                    embedWrongUpgrade = discord.Embed(
                        title=f"This is not your level up!",
                        description=f"{ctx.author.name} is currently leveling..",
                        color=0xFF0000
                    )
                    await interaction.send(embed=embedWrongUpgrade, hidden=True)
                    continue
        except asyncio.TimeoutError:
            embedTimeout = discord.Embed(
                    title=f"Woops! You took too long to respond...",
                    description=f"Ending {ctx.author.name}'s level up..",
                    color=0xFF0000
                )
            await message.edit(embed=embedTimeout, components=[])
            await asyncio.sleep(10)
            await message.delete()
            return

        metadata_api = f"https://mainnet-idx.algonode.cloud/v2/transactions?tx-type=acfg&asset-id={chosen_fallen}&address={fallen_order_manager}"
        response = requests.get(metadata_api)
        if response.status_code == 200:
            data = response.json()
        else:
            print("Error fetching data from API")
        metadata_decoded = (json.loads((base64.b64decode((data["transactions"][0]["note"]).encode('utf-8'))).decode('utf-8')))
        level = metadata_decoded["properties"]["Level"]
        asset_info = algod_client.asset_info(chosen_fallen)
        fallen_image_url = asset_info["params"]["url"]
        fallen_image = "https://ipfs.algonft.tools/ipfs/" + (fallen_image_url).replace("ipfs://", "")
        fallen_name = metadata_decoded.get("properties", {}).get("Name", asset_info['params']['unit-name'])
        new_level = int(level) + 1
        metadata_decoded["properties"]["Level"] = new_level
        kinship = metadata_decoded["properties"]["Kinship"]
        attack = metadata_decoded["properties"]["ATK"]
        defense = metadata_decoded["properties"]["DEF"]
        abilitypower = metadata_decoded["properties"]["AP"]
        hitpoints = metadata_decoded["properties"]["HP"]
        new_hp = int(hitpoints) + 500
        metadata_decoded["properties"]["HP"] = new_hp
        metadata_encoded = json.dumps(metadata_decoded)
        balance_order = await get_balance(wallet, 811718424)
        balance_exp = await get_balance(wallet, 811721471)
        cost_order = level_up_cost_order[int(level)]
        cost_exp =  level_up_cost_exp[int(level)]
        if balance_order < cost_order or balance_exp < cost_exp:
            embedNoLevelUp = discord.Embed(
                title=f"Woops! You don't have that much $ORDER/$EXP",
                description=f"Leveling up from {level} to {new_level} costs {cost_order} $ORDER and {cost_exp} $EXP",
                color=0xFF0000
            )
            embedNoLevelUp.set_footer(text=f"Your Current Balance: {balance_order} $ORDER | {balance_exp} $EXP")
            await message.edit(embed=embedNoLevelUp, components=[])
            await asyncio.sleep(10)
            await message.delete()
            return
        
        embedConfirmUpgrade = discord.Embed(
                title=f"⚠️ Confirm Level Up ⚠️",
                description=f"Level {level} > New Level {new_level}",
                color=0xFCE303
            )
        embedConfirmUpgrade.add_field(name=f"New Level | HP | Kinship", value=f"{new_level} | {new_hp} | {kinship}", inline=False)   
        embedConfirmUpgrade.add_field(name=f"ATK | DEF | AP", value=f"{attack} | {defense} | {abilitypower}", inline=False)
        embedConfirmUpgrade.set_image(url=fallen_image)
        embedConfirmUpgrade.set_footer(text=f"Confirm Level Up?\n\nCost: {cost_order} $ORDER | {cost_exp} $EXP")
        embedConfirmUpgrade.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        action_row = create_actionrow(
                            create_button(style=ButtonStyle.green, label="Confirm", custom_id="confirm"),
                            create_button(style=ButtonStyle.red, label="Cancel", custom_id="cancel")
                        )
        await message.edit(embed=embedConfirmUpgrade, components=[action_row])
        try:
            interaction: ComponentContext = await wait_for_component(client, components=action_row, timeout=30.0)
            interaction_author_id = interaction.author.id

            if interaction_author_id == ctx.author.id:
                await interaction.defer(edit_origin=True)
                action = interaction.custom_id
                if action == "cancel":
                    await message.delete()
                    return
                elif action == 'confirm':
                    embedConfirmUpgrade.set_footer(text=f"{fallen_name} level up in progress...please wait while I update your metadata ⏳")
                    await message.edit(embed=embedConfirmUpgrade, components=[])
                    await send_assets(str(ctx.author.name), wallet, fallen_order_main, 811718424, "ORDER", cost_order)
                    await send_assets(str(ctx.author.name), wallet, fallen_order_main, 811721471, "EXP", cost_exp)
                    txid = await send_assets("Level Up - The Order", fallen_order_main, wallet, 815771120, "BOOST", 1)
                    await edit_metadata(chosen_fallen, metadata_encoded)
            else:
                embedWrongUpgrade = discord.Embed(
                    title=f"This is not your level up!",
                    description=f"{ctx.author.name} is currently leveling..",
                    color=0xFF0000
                )
                await interaction.send(embed=embedWrongUpgrade, hidden=True)
        except asyncio.TimeoutError:
            embedTimeout = discord.Embed(
                    title=f"Woops! You took too long to respond...",
                    description=f"Ending {ctx.author.name}'s level up..",
                    color=0xFF0000
                )
            await message.edit(embed=embedTimeout, components=[])
            await asyncio.sleep(10)
            await message.delete()
            return        
        embedLevelUpDone = discord.Embed(
                title=f"🧙 LEVEL UP COMPLETE! 🧙‍♀️",
                url=f"https://nftexplorer.app/asset/{chosen_fallen}",
                description=f"Level {level} > New Level {new_level}",
                color=0x28FF0A
            )
        embedLevelUpDone.add_field(name=f"Level | HP | Kinship", value=f"{new_level} | {new_hp} | {kinship}", inline=False)   
        embedLevelUpDone.add_field(name=f"ATK | DEF | AP", value=f"{attack} | {defense} | {abilitypower}", inline=False)
        embedLevelUpDone.set_image(url=fallen_image)
        embedLevelUpDone.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        embedLevelUpDone.set_footer(text=f"Thank you, Master {ctx.author.name}! I grow stronger by the day! 💪🏻")
        embedBoosterSent = discord.Embed(
                title=f"🔥 <@{ctx.author.id}> Received 1 Stat Booster! 🔥",
                url=f"https://algoexplorer.io/tx/{txid}",
                description=f"Congratulations!",
                color=0x28FF0A
            )
        embedBoosterSent.set_image(url="https://nft-media.algoexplorerapi.io/images/bafybeibdnf2qn7a3w5ckxecv4svykpntufjkqh2zank6kx6mn2idik2nz4")
        embedBoosterSent.set_footer(text="$BOOST can be used to add Points to your character at any time.\nYou may also choose to keep it, trade it, or sell it as with any other NFT")
        await message.edit(embed=embedLevelUpDone, components=[])
        await asyncio.sleep(3)
        await ctx.send(embed=embedBoosterSent)

    @level_character.error
    async def level_up_error(self, ctx, error):
        embedNotAllowed = discord.Embed(
                    title=f"Please wait 30sec before this command becomes available again!",
                    color=0xFF0000
                )
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(embed=embedNotAllowed, hidden=True)

class SubKinshipCog(commands.Cog):
    @cog_ext.cog_slash(name="subscribe-kinship", description="Subscribe To Auto-Kinship Delivered Daily On Time Without Worry!", options=[
                    {
                        "name": "amount",
                        "description": "Number Of Kinship Units To Add",
                        "type": 4,
                        "required": True
                    }
                ])
    async def sub_kinship(self, ctx, amount):
        if amount < 5:
            embedNoZero = discord.Embed(
                title="Minimum cost per Kinships Unit is 5 $EXP!",
                description=f"Please enter a non-zero amount of units to add..",
                color=0xFF0000,
            )
            await ctx.send(embed=embedNoZero, hidden=True)
            return
        cost = amount*5
        kinship_data = await get_kinship_subs(str(ctx.author.id))
        name = kinship_data[0]
        wallet = kinship_data[1]
        units_available = kinship_data[2]
        balance = await get_balance(wallet, 811721471)
        if balance == -1:
            await ctx.send(embed=embedNoOptEXP)
            return
        if balance < cost:
            await ctx.send(embed=embedErr)
            return
        if wallet == '':
            embedNoReg = discord.Embed(
                title="Click Here To Register!",
                url="https://app.fallenorder.xyz",
                description=f"Please verify your wallet via our website to continue..\nEnsure you copy your user id below for the verification process:\nUser ID: {ctx.author.id}",
                color=0xFF1C0A,
            )
            await message.edit(embed=embedNoReg)
            return
        embedSubscribeInProgress = discord.Embed(
                title=f"🧙‍♂️ Kinship Subscription In Progress... 🧙‍♂️",
                description=f"{ctx.author.name} gathers their Fallen Order to auto-subscribe them to Kinship",
                color=0xFCE303
            )
        embedSubscribeInProgress.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        embedSubscribeInProgress.set_footer(text=f"Balance: {balance} $EXP\nTotal Cost: {cost} $EXP")
        message = await ctx.send(embed=embedSubscribeInProgress)
        fallen_assets = []
        account_info = algod_client.account_info(wallet)
        assets = account_info.get("assets", [])
        fo_count = 0
        for asset in assets:
            if asset["amount"] > 0 and (asset["asset-id"] in fo_rank1 or asset["asset-id"] in fo_rank2 or asset["asset-id"] in fo_rank3 or asset["asset-id"] in fo_rank4 or asset["asset-id"] in fo_rank5):
                fallen_assets.append(asset['asset-id'])  
                fo_count += 1      
        if fallen_assets == []:
            embedNoFO = discord.Embed(
                title=f"Awwww...{ctx.author.name} does not own any Fallen Order!",
                description=f"[Click Here To Shuffle!](https://algoxnft.com/shuffle/902)",
                color=0xFF0000
            )
            embedNoFO.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
            await message.edit(embed=embedNoFO)
            return
        total_units = int(units_available + amount)
        embedSubscribeConfirm = discord.Embed(
                title=f"🧙‍♂️ Kinship Subscription In Progress... 🧙‍♂️",
                description=f"{ctx.author.name} gathers their Fallen Order to auto-subscribe them to Kinship\n\nAvailable Kinship Units: {units_available}\nNew Total Units: {total_units}",
                color=0xFCE303
            )
        embedSubscribeConfirm.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        embedSubscribeConfirm.set_footer(text=f"\nBalance: {balance} $EXP\nTotal Cost: {cost} $EXP")
        action_row = create_actionrow(
                            create_button(style=ButtonStyle.green, label="Confirm", custom_id="confirm"),
                            create_button(style=ButtonStyle.red, label="Cancel", custom_id="cancel")
                        )
        await message.edit(embed=embedSubscribeConfirm, components=[action_row])
        try:
            while True:
                interaction: ComponentContext = await wait_for_component(client, components=action_row, timeout=20.0)
                interaction_author_id = interaction.author.id

                if interaction_author_id == ctx.author.id:
                    await interaction.defer(edit_origin=True)
                    action = interaction.custom_id
                    if action == "cancel":
                        await message.delete()
                        return
                    elif action == 'confirm':
                        embedSubscribeConfirm.set_footer(text=f"Please wait while I update your details...⏳")
                        await message.edit(embed=embedSubscribeConfirm, components=[])
                        await send_assets("Kinship Subscription. " + str(ctx.author.name), wallet, fallen_order_main, 811721471, "EXP", cost)
                        await update_kinsubs(wallet, total_units)
                        break

                else:
                    embedWrongUpgrade = discord.Embed(
                        title=f"This is not your Kinship subscription!",
                        color=0xFF0000
                    )
                    await interaction.send(embed=embedWrongUpgrade, hidden=True)
                    continue
        except asyncio.TimeoutError:
            embedTimeout = discord.Embed(
                    title=f"Woops! You took too long to respond...",
                    description=f"Ending {ctx.author.name}'s Kinship subscription..",
                    color=0xFF0000
                )
            await message.edit(embed=embedTimeout, components=[])
            await asyncio.sleep(10)
            await message.delete()
            return
        embedSubscribeKinshipDone = discord.Embed(
                title=f"🧙‍♂️ Kinship Subsciption Successful! 🧙‍♂️",
                description=f"Your {fo_count} Fallen Order characters are under our care!\n\nAvailable Kinship Units: {total_units}",
                color=0x28FF0A
            )
        embedSubscribeKinshipDone.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        embedSubscribeKinshipDone.set_footer(text=f"Thank you {name}, we will handle your Kinship on your behalf\n\nMetadata transactions are processed daily at 9:00AM EST\n\nYou will receive a DM with the ritual for confirmation!\n\nNew Balance: {balance-cost} $EXP")
        await message.edit(embed=embedSubscribeKinshipDone)


class AutoKinshipCog(commands.Cog):
    @cog_ext.cog_slash(name="auto-kinship", description="Subscribe To Auto-Kinship Delivered Daily On Time Without Worry!")
    async def auto_kinship(self, ctx):
        kinship_data = await get_kinship_subs(str(ctx.author.id))
        name = kinship_data[0]
        wallet = kinship_data[1]
        units_available = kinship_data[2]
        if wallet == '':
            embedNoReg = discord.Embed(
                title="Click Here To Register!",
                url="https://app.fallenorder.xyz",
                description=f"Please verify your wallet via our website to continue..\nEnsure you copy your user id below for the verification process:\nUser ID: {ctx.author.id}",
                color=0xFF1C0A,
            )
            await ctx.send(embed=embedNoReg)
            return
        fallen_assets = []
        account_info = algod_client.account_info(wallet)
        assets = account_info.get("assets", [])
        fo_count = 0
        for asset in assets:
            if asset["amount"] > 0 and (asset["asset-id"] in fo_rank1 or asset["asset-id"] in fo_rank2 or asset["asset-id"] in fo_rank3 or asset["asset-id"] in fo_rank4 or asset["asset-id"] in fo_rank5):
                fallen_assets.append(asset['asset-id'])  
                fo_count += 1      
        if fallen_assets == []:
            embedNoFO = discord.Embed(
                title=f"Awwww...{ctx.author.name} does not own any Fallen Order!",
                description=f"[Click Here To Shuffle!](https://algoxnft.com/shuffle/902)",
                color=0xFF0000
            )
            embedNoFO.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
            await ctx.send(embed=embedNoFO)
            return
        if fo_count > 10:
            days_remaining = int(units_available/10)
        else:
            days_remaining = int(units_available/fo_count)
        embedSubscribe = discord.Embed(
                title=f"🧙‍♂️ Auto-Kinship Subscription 🧙‍♂️",
                description=f"Available Kinship Units: {units_available}\n\nCharacters: {fo_count}\n\nDays Remaining: {days_remaining}",
                color=0xFCE303
            )
        embedSubscribe.add_field(name=f"*How It Works*", value=f"1 Kinship Unit = 5 $EXP\n\n1 Unit will be withdrawn from your total units available daily per character up to a max of 10 Units. Characters past the first 10 will be handled free of charge.\n\nExample:\n1 Character = 1 Unit/Day\n5 Characters = 5 Units/Day\n12 Characters = 10 Units/Day\n500 Characters = 10 Units/Day\n\nUse /subscribe-kinship to add Units!", inline=False)   
        embedSubscribe.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        embedSubscribe.set_footer(text=f"Metadata transactions are processed daily at 9:00AM EST")
        await ctx.send(embed=embedSubscribe)

def setup(client: client):
    client.add_cog(StatBoostCog(client))
    client.add_cog(KinshipCog(client))
    client.add_cog(SubKinshipCog(client))
    client.add_cog(AutoKinshipCog(client))
    client.add_cog(AddNameCog(client))
    client.add_cog(AddAbilityCog(client))
    client.add_cog(AddPointsCog(client))
    client.add_cog(LevelUpCog(client))