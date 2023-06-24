from discord_slash import cog_ext
from discord.ext import commands
import discord
import requests
import random
from discord_slash.utils.manage_components import create_select, create_select_option, create_actionrow, wait_for_component, create_button
from discord_slash.model import ButtonStyle
from discord.utils import get
import json
import base64
from discord_slash import ComponentContext
import asyncio
from client import client
from txns import algod_client, get_main_char, update_character, equip_main_hatchet, freeze_asset, get_balance, edit_hatchet, edit_metadata, send_logs, send_assets, fallen_order_main, fallen_order_accessories, get_all_lumberjacks, fallen_order_manager
from embeds import embedAdminOnly, embedNoOptEXP
from whitelist import fo_rank1, fo_rank2, fo_rank3, fo_rank4, fo_rank5
from skills_wl import hatchet_rank1, full_hatchet_rank1

oak_logs = 1064863037
oak_tree_image = "https://i.ibb.co/4RFK9Ts/oaktree.png"
oak_logs_image = "https://i.ibb.co/ggGBzjB/oaklogs.png"
oof = ["Better luck next time...", "That tree was a tough one...", "My arms hurt man...", "Can you maybe just like ok?", "Bruh..........."]
required_exp_to_level_up = [83, 257, 533, 921, 1433, 2083, 2884, 3853, 5007, 6365, 7947, 9775, 11872, 14262, 16979, 20047]

async def get_guild():
    guild = client.get_guild(936698039941345370)
    return guild

class AdminLumberjackRoles(commands.Cog):
    @cog_ext.cog_slash(name="admin-lumberjack", description="Admin Use Only!")
    async def admin_lumberjack(self, ctx):
        await ctx.defer()
        if ctx.author.id != 805453439499894815:
            await ctx.send(embed=embedAdminOnly)
            return
        else:
            equipped_hatchets = await get_all_lumberjacks()
            embedLumberjacks = discord.Embed(
                title="Lumberjack Roles Assigned!",
                description=f"I have given the Lumberjack role to the following users:",
                color=0x28FF0A,
            )
            for user in equipped_hatchets:
                guild = await get_guild()
                member = guild.get_member(int(user['userid']))
                role = get(guild.roles, id=1087398515682070638)
                if user['equipped_hatchet'] != 0:
                    if member is not None:
                        if role not in member.roles:
                            embedLumberjacks.add_field(name=f"{member.name} 🪓", value=f"-", inline=True)
                            await member.add_roles(role)
                else:
                    if member is not None:
                        if role in member.roles:
                            await member.remove_roles(role)      
        await ctx.send(embed=embedLumberjacks)

class InventoryCog(commands.Cog):
    @cog_ext.cog_slash(name="inventory", description="View Your Inventory!")
    async def get_inventory(self, ctx):
        wallet, main_character, equipped_hatchet = await get_main_char(str(ctx.author.id))
        if wallet == '':
            embedNoReg = discord.Embed(
                title="Click Here To Register!",
                url="https://app.fallenorder.xyz",
                description=f"Please verify your wallet via our website to continue..\nEnsure you copy your user id below for the verification process:\n\nUser ID: {ctx.author.id}",
                color=0xFF1C0A,
            )
            await ctx.send(embed=embedNoReg)
            return
        balance_order = await get_balance(wallet, 811718424)
        balance_exp = await get_balance(wallet, 811721471)
        balance_logs = await get_balance(wallet, oak_logs)
        balance_ac1 = await get_balance(wallet, 1069374333)
        balance_ac2 = await get_balance(wallet, 1070260390)
        balance_wac1 = await get_balance(wallet, 1069835750)
        if balance_logs == -1:
            balance_logs = "Not Opted!"
        if balance_order == -1:
            balance_order = "Not Opted!"
        if balance_exp == -1:
            balance_exp = "Not Opted!"
        if balance_ac1 <= 0:
            balance_ac1 = "-"
        else:
            balance_ac1 = "🏆"
        if balance_ac2 <= 0:
            balance_ac2 = "-"
        else:
            balance_ac2 = "🏆"
        if balance_wac1 <= 0:
            balance_wac1 = "-"
        else:
            balance_wac1 = "🏆"
        if main_character == 0:
            embedNoMain = discord.Embed(
                title="You do not have a Main character assigned!",
                description=f"You may select your main by using /main-character",
                color=0xFF1C0A,
            )
            await ctx.send(embed=embedNoMain)
            return
        if equipped_hatchet== 0:
            equipped_hatchet_name = "-"
        else:
            asset_info = algod_client.asset_info(equipped_hatchet)
            equipped_hatchet_name = asset_info['params']['name']
        metadata_api = f"https://mainnet-idx.algonode.cloud/v2/transactions?tx-type=acfg&asset-id={main_character}&address={fallen_order_manager}"
        response = requests.get(metadata_api)
        if response.status_code == 200:
            data = response.json()
        else:
            print("Error fetching data from API")
        metadata_decoded = json.loads((base64.b64decode((data["transactions"][0]["note"]).encode('utf-8'))).decode('utf-8'))
        asset_info = algod_client.asset_info(main_character)
        fallen_image_url = asset_info["params"]["url"]
        fallen_image = "https://ipfs.algonft.tools/ipfs/" + (fallen_image_url).replace("ipfs://", "")
        fallen_name = metadata_decoded.get("properties", {}).get("Name", asset_info['params']['unit-name'])
        woodcutting_data = metadata_decoded.get("properties", {}).get("Woodcutting", "None")
        if woodcutting_data == "None":
            woodcutting_level = 0
            woodcutting_exp = 0
        else:
            woodcutting_data_split = woodcutting_data.split("/")
            woodcutting_level = int(woodcutting_data_split[0])
            woodcutting_exp = int(woodcutting_data_split[1])
        level = metadata_decoded["properties"]["Level"]
        kinship = metadata_decoded["properties"]["Kinship"]
        attack = metadata_decoded["properties"]["ATK"]
        defense = metadata_decoded["properties"]["DEF"]
        abilitypower = metadata_decoded["properties"]["AP"]
        hitpoints = metadata_decoded["properties"]["HP"]
        embedInventory = discord.Embed(
            title=f"📦 <@{ctx.author.id}>'s Inventory 📦",
            url=f"https://nftexplorer.app/asset/{main_character}",
            description=f"**Main Character:** {fallen_name}\n**Woodcutting:** LVL {woodcutting_level} | Exp: {woodcutting_exp}\n**Exp To LVL {woodcutting_level+1}**: {required_exp_to_level_up[woodcutting_level]}\n**Equipped Hatchet:** {equipped_hatchet_name}\n\n**Achievements**\n*Ramsay's Rampage:* {balance_ac1}\n*The Summoning:* {balance_ac2}\n*I'm A Lumberjack!:* {balance_wac1}",
            color=0x28FF0A
        )
        embedInventory.add_field(name=f"$ORDER | $EXP | Oak Logs", value=f"{balance_order} | {balance_exp} | {balance_logs}", inline=False)
        embedInventory.add_field(name=f"Level | HP | Kinship", value=f"{level} | {hitpoints} | {kinship}", inline=False)
        embedInventory.add_field(name=f"ATK | DEF | AP", value=f"{attack} | {defense} | {abilitypower}", inline=False)
        embedInventory.set_image(url=fallen_image)
        embedInventory.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        embedInventory.set_footer(text=f"Master {ctx.author.name}, let's do some work!")
        await ctx.send(embed=embedInventory)

        
class MainCharCog(commands.Cog):
    @cog_ext.cog_slash(name="main-character", description="Select Your Main Character!")
    async def select_main_character(self, ctx):
        embedSelectionInProgress = discord.Embed(
                title=f"🧙‍♂️ Initiating Character Selection... 🧙‍♂️",
                description=f"{ctx.author.name} gathers their Fallen Order to assign their main leader...",
                color=0xFCE303
            )
        embedSelectionInProgress.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        message = await ctx.send(embed=embedSelectionInProgress)
        wallet, main_character, equipped_hatchet = await get_main_char(str(ctx.author.id))
        if main_character == 0:
            current_fallen = "None"
        else:
            metadata_api = f"https://mainnet-idx.algonode.cloud/v2/transactions?tx-type=acfg&asset-id={main_character}&address={fallen_order_manager}"
            response = requests.get(metadata_api)
            if response.status_code == 200:
                data = response.json()
            else:
                print("Error fetching data from API")
            metadata_decoded = json.loads((base64.b64decode((data["transactions"][0]["note"]).encode('utf-8'))).decode('utf-8'))
            asset_info = algod_client.asset_info(main_character)
            current_fallen_raw = asset_info["params"]["unit-name"]
            current_fallen = metadata_decoded.get("properties", {}).get("Name", current_fallen_raw)
        if wallet == '':
            embedNoReg = discord.Embed(
                title="Click Here To Register!",
                url="https://app.fallenorder.xyz",
                description=f"Please verify your wallet via our website to continue..\nEnsure you copy your user id below for the verification process:\n\nUser ID: {ctx.author.id}",
                color=0xFF1C0A,
            )
            await message.edit(embed=embedNoReg)
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
        if equipped_hatchet== 0:
            equipped_hatchet_name = "-"
        else:
            asset_info = algod_client.asset_info(equipped_hatchet)
            equipped_hatchet_name = asset_info['params']['name']
        select_options = [create_select_option(label=fallen[0] + " - " + fallen[2], value=str(fallen[1])) for fallen in fallen_assets]
        select = create_select(options=select_options, placeholder="Select your new main character", min_values=1, max_values=1)
        action_row = create_actionrow(select)
        embedSelectionInProgress.description = f"Current Main Character:\n{current_fallen}\n\nEquipped Hatchet:\n{equipped_hatchet_name}"
        await message.edit(embed=embedSelectionInProgress, components=[action_row])
        try:
            while True:
                interaction: ComponentContext = await wait_for_component(client, components=action_row, timeout=30.0)
                interaction_author_id = interaction.author.id

                if interaction_author_id == ctx.author.id:
                    await interaction.defer(edit_origin=True)
                    chosen_fallen = int(interaction.selected_options[0])
                    await message.edit(components=[])
                    break
                else:
                    embedWrongUpgrade = discord.Embed(
                        title=f"This is not your character selection!",
                        description=f"Another player is currently selecting their main character..",
                        color=0xFF0000
                    )
                    await interaction.send(embed=embedWrongUpgrade, hidden=True)
                    continue
        except asyncio.TimeoutError:
            embedTimeout = discord.Embed(
                    title=f"Woops! You took too long to respond...",
                    description=f"Ending {ctx.author.name}'s character selection..",
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
        fallen_name_raw = asset_info["params"]["unit-name"]
        fallen_name = metadata_decoded.get("properties", {}).get("Name", fallen_name_raw)
        level = metadata_decoded["properties"]["Level"]
        kinship = metadata_decoded["properties"]["Kinship"]
        attack = metadata_decoded["properties"]["ATK"]
        defense = metadata_decoded["properties"]["DEF"]
        abilitypower = metadata_decoded["properties"]["AP"]
        hitpoints = metadata_decoded["properties"]["HP"]
        if chosen_fallen == main_character:
            embedAlreadySelected = discord.Embed(
                title=f"🧙 Already Set As Main! 🧙‍♀️",
                url=f"https://nftexplorer.app/asset/{chosen_fallen}",
                description=f"Chosen Fallen: {fallen_name}\nEquipped Hatchet: {equipped_hatchet_name}",
                color=0x28FF0A
            )
            embedAlreadySelected.add_field(name=f"Level | HP | Kinship", value=f"{level} | {hitpoints} | {kinship}", inline=False)   
            embedAlreadySelected.add_field(name=f"ATK | DEF | AP", value=f"{attack} | {defense} | {abilitypower}", inline=False)
            embedAlreadySelected.set_image(url=fallen_image)
            embedAlreadySelected.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
            embedAlreadySelected.set_footer(text=f"Ready to put my Skills to use, Master {ctx.author.name}! 💪🏻")
            await message.edit(embed=embedAlreadySelected, component=[])
            return
        embedCharacterSelectionComplete = discord.Embed(
                title=f"🧙 Character Selection Complete 🧙‍♀️",
                url=f"https://nftexplorer.app/asset/{chosen_fallen}",
                description=f"Chosen Fallen: {fallen_name}\nEquipped Hatchet: {equipped_hatchet_name}",
                color=0x28FF0A
            )
        embedCharacterSelectionComplete.add_field(name=f"Level | HP | Kinship", value=f"{level} | {hitpoints} | {kinship}", inline=False)   
        embedCharacterSelectionComplete.add_field(name=f"ATK | DEF | AP", value=f"{attack} | {defense} | {abilitypower}", inline=False)
        embedCharacterSelectionComplete.set_image(url=fallen_image)
        embedCharacterSelectionComplete.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        embedCharacterSelectionComplete.set_footer(text=f"Ready to put my Skills to use, Master {ctx.author.name}! 💪🏻")
        await message.edit(embed=embedCharacterSelectionComplete)
        await update_character(wallet, int(chosen_fallen))

    @select_main_character.error
    async def select_main_character_error(self, ctx, error):
        embedNotAllowed = discord.Embed(
                    title=f"Please wait 30sec before this command becomes available again!",
                    color=0xFF0000
                )
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(embed=embedNotAllowed, hidden=True)


class EquipHatchetCog(commands.Cog):
    @cog_ext.cog_slash(name="equip-hatchet", description="Equip A Hatchet To Your Main Character!")
    async def equip_hatchet(self, ctx):
        hatchet_image = "https://ipfs.algonft.tools/ipfs/QmSXLhwWeXDBtA31FDUY9xTiVysMrGmH2nfTJDwHL5Qt25"
        embedHatchetSelectionInProgress = discord.Embed(
                title=f"🪓 Character Equip 🪓",
                description=f"{ctx.author.name} initiating equip...",
                color=0xFF0000
            )
        embedHatchetSelectionInProgress.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        message = await ctx.send(embed=embedHatchetSelectionInProgress)
        wallet, main_character, equipped_hatchet = await get_main_char(str(ctx.author.id))
        hatchets = []
        account_info = algod_client.account_info(wallet)
        assets = account_info.get("assets", [])
        for asset in assets:
            if asset["amount"] > 0 and asset["asset-id"] in full_hatchet_rank1:
                metadata_api = f"https://mainnet-idx.algonode.cloud/v2/transactions?tx-type=acfg&asset-id={asset['asset-id']}"
                response = requests.get(metadata_api)
                if response.status_code == 200:
                    data = response.json()
                else:
                    print("Error fetching data from API")
                asset_info = algod_client.asset_info(asset['asset-id'])
                hatchet_name = data["transactions"][0]["asset-config-transaction"]["params"]["name"]
                hatchets.append([asset_info['index'], hatchet_name])
        if hatchets == []:
            embedNoFO = discord.Embed(
                title=f"Awwww...{ctx.author.name} does not own any Hatchets!",
                description=f"Tag @angel.algo to grab yourself a Hatchet",
                color=0xFF0000
            )
            embedNoFO.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
            await message.edit(embed=embedNoFO)
            return
        if equipped_hatchet == 0:
            equipped_hatchet_name = "-"
        else:
            asset_info = algod_client.asset_info(equipped_hatchet)
            equipped_hatchet_name = asset_info['params']['name']
        embedHatchetSelectionInProgress.description = f"Equipped Hatchet\n\n{equipped_hatchet_name}"
        select_options = [create_select_option(label=hatchet[1], value=str(hatchet[0])) for hatchet in hatchets]
        select = create_select(options=select_options, placeholder="Select the hatchet you want to equip", min_values=1, max_values=1)
        action_row = create_actionrow(select)
        await message.edit(embed=embedHatchetSelectionInProgress, components=[action_row])
        try:
            while True:
                interaction: ComponentContext = await wait_for_component(client, components=action_row, timeout=30.0)
                interaction_author_id = interaction.author.id
                if interaction_author_id == ctx.author.id:
                    await interaction.defer(edit_origin=True)
                    chosen_hatchet = int(interaction.selected_options[0])
                    break
                else:
                    embedWrongUpgrade = discord.Embed(
                        title=f"This is not your hatchet equip!",
                        color=0xFF0000
                    )
                    await interaction.send(embed=embedWrongUpgrade, hidden=True)
                    continue
        except asyncio.TimeoutError:
            embedTimeout = discord.Embed(
                    title=f"Woops! You took too long to respond...",
                    description=f"Ending {ctx.author.name}'s hatchet equip..",
                    color=0xFF0000
                )
            await message.edit(embed=embedTimeout, components=[])
            await asyncio.sleep(10)
            await message.delete()
            return
        if chosen_hatchet == equipped_hatchet:
            embedAlreadyEquipped = discord.Embed(
                title=f"🪓 Hatchet Already Equipped! 🪓",
                description=f"Equipped Hatchet:\n\n{hatchet_name}",
                color=0xFCE303
            )
            embedAlreadyEquipped.set_image(url=hatchet_image)
            embedAlreadyEquipped.set_footer(text=f"Been waiting to chop some wood bubba! 🪓")
            embedAlreadyEquipped.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
            await message.edit(embed=embedAlreadyEquipped, components=[])
            return
        main_character_data = f"https://mainnet-idx.algonode.cloud/v2/transactions?tx-type=acfg&asset-id={main_character}&address={fallen_order_manager}"
        hatchet_data = f"https://mainnet-idx.algonode.cloud/v2/transactions?tx-type=acfg&asset-id={chosen_hatchet}"
        response = requests.get(main_character_data)
        if response.status_code == 200:
            data = response.json()
        else:
            print("Error fetching data from API")
        response2 = requests.get(hatchet_data)
        if response2.status_code == 200:
            data2 = response2.json()
        else:
            print("Error fetching data from API")
        metadata_decoded = json.loads((base64.b64decode((data["transactions"][0]["note"]).encode('utf-8'))).decode('utf-8'))
        fallen_name = metadata_decoded.get("properties", {}).get("Name", "None")
        hatchet_name = data2["transactions"][0]["asset-config-transaction"]["params"]["name"]
        await freeze_asset("freeze", wallet, chosen_hatchet)
        if equipped_hatchet != 0:
            await freeze_asset("unfreeze" , wallet, equipped_hatchet)
        await equip_main_hatchet(wallet, chosen_hatchet)

        embedHatchetSelectionComplete = discord.Embed(
                title=f"🪓 Hatchet Equip Successful! 🪓",
                url=f"https://www.randgallery.com/algo-collection/?address={chosen_hatchet}",
                description=f"{hatchet_name} equipped onto {fallen_name}!",
                color=0xFCE303
            )
        embedHatchetSelectionComplete.set_image(url=hatchet_image)
        embedHatchetSelectionComplete.set_footer(text=f"Ready to chop some wood bubba! 🪓")
        embedHatchetSelectionComplete.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        await message.edit(embed=embedHatchetSelectionComplete, components=[])


class DequipHatchetCog(commands.Cog):
    @cog_ext.cog_slash(name="dequip-hatchet", description="Dequip Current Hatchet From Your Main Character!")
    async def deequip_hatchet(self, ctx):
        hatchet_image = "https://ipfs.algonft.tools/ipfs/QmSXLhwWeXDBtA31FDUY9xTiVysMrGmH2nfTJDwHL5Qt25"
        embedHatchetSelectionInProgress = discord.Embed(
                title=f"🪓 Character Dequip 🪓",
                description=f"{ctx.author.name} initiating dequip...",
                color=0xFF0000
            )
        embedHatchetSelectionInProgress.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        message = await ctx.send(embed=embedHatchetSelectionInProgress)
        wallet, main_character, equipped_hatchet = await get_main_char(str(ctx.author.id))
        await asyncio.sleep(2)
        if equipped_hatchet == 0:
            equipped_hatchet_name = "-"
        else:
            asset_info = algod_client.asset_info(equipped_hatchet)
            equipped_hatchet_name = asset_info['params']['name']
        if equipped_hatchet == 0:
            embedAlreadyEquipped = discord.Embed(
                title=f"🪓 No Hatchet Equipped! 🪓",
                color=0xFCE303
            )
            embedAlreadyEquipped.set_footer(text=f"Use /equip-hatchet to add a Hatchet to your Main Character! 🪓")
            embedAlreadyEquipped.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
            await message.edit(embed=embedAlreadyEquipped, components=[])
            return
        await freeze_asset("unfreeze" , wallet, equipped_hatchet)
        await equip_main_hatchet(wallet, 0)

        embedHatchetSelectionComplete = discord.Embed(
                title=f"🪓 Hatchet Dequip Successful! 🪓",
                description=f"{equipped_hatchet_name} dequipped and unfrozen from {ctx.author.name}'s wallet",
                color=0xFCE303
            )
        embedHatchetSelectionComplete.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        await message.edit(embed=embedHatchetSelectionComplete, components=[])

class ReplenishHatchetCog(commands.Cog):
    @cog_ext.cog_slash(name="replenish-hatchet", description="Replenish Your Equipped Hatchet With 100 Uses for 100 $EXP!")
    @commands.cooldown(1, 20, commands.BucketType.user)
    async def replenish_hatchet(self, ctx):
        embedReplenish1 = discord.Embed(
                title=f"🪓 Replenishing Hatchet 🪓",
                description=f"{ctx.author.name} initiating replenish...",
                color=0xFF0000
            )
        embedReplenish1.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        message = await ctx.send(embed=embedReplenish1)
        wallet, main_character, equipped_hatchet = await get_main_char(str(ctx.author.id))
        if equipped_hatchet == 0:
            embedNoHatchet = discord.Embed(
                title=f"🪓 No Hatchet Equipped! 🪓",
                color=0xFCE303
            )
            embedNoHatchet.set_footer(text=f"Use /equip-hatchet to add a Hatchet to your Main Character! 🪓")
            embedNoHatchet.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
            await message.edit(embed=embedNoHatchet)
            return
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
        equipped_data = f"https://mainnet-idx.algonode.cloud/v2/transactions?tx-type=acfg&asset-id={equipped_hatchet}&address={fallen_order_accessories}"
        response_equipped = requests.get(equipped_data)
        if response_equipped.status_code == 200:
            data_equipped = response_equipped.json()
        else:
            print("Error fetching data from API")
        asset_info = algod_client.asset_info(equipped_hatchet)
        equipped_hatchet_name = asset_info['params']['name']
        metadata_decoded = json.loads((base64.b64decode((data_equipped["transactions"][0]["note"]).encode('utf-8'))).decode('utf-8'))
        available_uses = int(metadata_decoded["properties"]["Uses"])
        new_uses = available_uses + 100
        metadata_decoded["properties"]["Uses"] = new_uses
        metadata_encoded = json.dumps(metadata_decoded)
        embedConfirmReplenish = discord.Embed(
                title=f"⚠️ Confirm Replenish! ⚠️",
                description=f"{equipped_hatchet_name}\n\nAvailable Uses: {available_uses}\n\nNew Uses: {new_uses}\n\nCost: 100 $EXP",
                color=0xFFFB0A
            )
        embedConfirmReplenish.set_footer(text="Let's get back to the chop chop bubba! 🪓")
        embedConfirmReplenish.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        action_row = create_actionrow(
                            create_button(style=ButtonStyle.green, label="Confirm", custom_id="confirm"),
                            create_button(style=ButtonStyle.red, label="Cancel", custom_id="cancel")
                        )

        await message.edit(embed=embedConfirmReplenish, components=[action_row])
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
                    embedConfirmReplenish.set_footer(text=f"Please wait while I update your metadata...⏳")
                    await message.edit(embed=embedConfirmReplenish, components=[])
                    await send_assets("Hatchet Replenish. " + str(ctx.author.name), wallet, fallen_order_main, 811721471, "EXP", 100)
                    await edit_hatchet(equipped_hatchet, metadata_encoded)

            else:
                embedWrongUpgrade = discord.Embed(
                    title=f"This is not your hatchet replenish!",
                    color=0xFF0000
                )
                await interaction.send(embed=embedWrongUpgrade, hidden=True)
        except asyncio.TimeoutError:
            embedTimeout = discord.Embed(
                    title=f"Woops! You took too long to respond...",
                    description=f"Ending {ctx.author.name}'s hatchet replenish..",
                    color=0xFF0000
                )
            await message.edit(embed=embedTimeout, components=[])
            await asyncio.sleep(10)
            await message.delete()
            return
        embedReplenish2 = discord.Embed(
                title=f"Successfully Replenished {equipped_hatchet_name}",
                url=f"https://nftexplorer.app/asset/{equipped_hatchet}",
                description=f"New Uses: {new_uses}\n\nNew Balance: {balance_exp - 100} $EXP",
                color=0x28FF0A
            )
        embedReplenish2.set_footer(text="Let's get back to the chop chop bubba! 🪓")
        embedReplenish2.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        await message.edit(embed=embedReplenish2)
        
    @replenish_hatchet.error
    async def replenish_hatchet_error(self, ctx, error):
        embedNotAllowed = discord.Embed(
                    title=f"One replenish every 20 seconds!",
                    color=0xFF0000
                )
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(embed=embedNotAllowed, hidden=True)


class ChopTreeCog(commands.Cog):
    @cog_ext.cog_slash(name="chop", description="Dequip Current Hatchet From Your Main Character!", options=[
                {
                    "name": "tree",
                    "description": "Type Of Tree To Attempt To Chop",
                    "type": 3,
                    "required": True,
                    "choices": [
                        {
                            "name": "LVL 1 - Oak Tree",
                            "value": "1"
                        }
                    ]
                }])
    @commands.cooldown(1, 12, commands.BucketType.user)
    async def chop_tree(self, ctx, tree):
        if ctx.channel.id != 1087215342297813072:
            embedWrongChannel = discord.Embed(
                title=f"🪓 Woodcutting is restricted to The Wilderness 🪓",
                description=f"Head over to the Woodcutting channel to start chopping!",
                color=0xFF0000
            )
            await ctx.send(embed=embedWrongChannel, hidden=True)
            return
        if tree == "1":
            tree_type = "Oak Tree"
            log_name = "Oak Logs"
            logs_id = oak_logs
            log_image = oak_logs_image
            tree_image = oak_tree_image
            required_level = 0
            tree_exp = 25
        embedChop1 = discord.Embed(
                title=f"🪓 Woodcutting - {tree_type} 🪓",
                description=f"{ctx.author.name} initiating woodchop...",
                color=0xFF0000
            )
        embedChop1.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        message = await ctx.send(embed=embedChop1)
        wallet, main_character, equipped_hatchet = await get_main_char(str(ctx.author.id))
        if wallet == '':
            embedNoReg = discord.Embed(
                title="Click Here To Register!",
                url="https://app.fallenorder.xyz",
                description=f"Please verify your wallet via our website to continue..\nEnsure you copy your user id below for the verification process:\nUser ID: {ctx.author.id}",
                color=0xFF1C0A,
            )
            await message.edit(embed=embedNoReg, hidden=True)
            return
        if main_character == 0:
            embedNoMain = discord.Embed(
                title=f"Main Character Not Selected",
                description=f"Use /main-character to assign your main!",
                color=0xFCE303
            )
            embedNoMain.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
            await message.edit(embed=embedNoMain)
            return
        else:
            char_data = f"https://mainnet-idx.algonode.cloud/v2/transactions?tx-type=acfg&asset-id={main_character}&address={fallen_order_manager}"
            response_char = requests.get(char_data)
            if response_char.status_code == 200:
                data_char = response_char.json()
            else:
                print("Error fetching data from API")
            char_metadata_decoded = json.loads((base64.b64decode((data_char["transactions"][0]["note"]).encode('utf-8'))).decode('utf-8'))
        if equipped_hatchet == 0:
            embedNoHatchet = discord.Embed(
                title=f"🪓 No Hatchet Equipped! 🪓",
                color=0xFCE303
            )
            embedNoHatchet.set_footer(text=f"Use /equip-hatchet to add a Hatchet to your Main Character! 🪓")
            embedNoHatchet.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
            await message.edit(embed=embedNoHatchet)
            return
        if equipped_hatchet in full_hatchet_rank1:
            if tree == "1":
                base_chance = 10
            else:
                # handle other tree ranks in the future
                print("here 2")
                return
        else:
            print("here 1")
            return
            # handle other rank hatchets in the future
        equipped_data = f"https://mainnet-idx.algonode.cloud/v2/transactions?tx-type=acfg&asset-id={equipped_hatchet}&address={fallen_order_accessories}"
        response_equipped = requests.get(equipped_data)
        if response_equipped.status_code == 200:
            data_equipped = response_equipped.json()
        else:
            print("Error fetching data from API")
        asset_info = algod_client.asset_info(equipped_hatchet)
        equipped_hatchet_name = asset_info['params']['name']
        balance_logs = await get_balance(wallet, logs_id)
        if balance_logs == -1:
            embedNoOptLogs = discord.Embed(
                title=f"You Are Not Opted Into {log_name}!",
                description=f"[Click Here To Opt In...](https://www.randgallery.com/algo-collection/?address={logs_id})",
                color=0xFF1C0A,
            )
            embedNoOptLogs.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
            await message.edit(embed=embedNoOptLogs)
            return
        woodcutting_data = char_metadata_decoded.get("properties", {}).get("Woodcutting", "None")
        rank = int(char_metadata_decoded["properties"]["Rank"])
        level = int(char_metadata_decoded["properties"]["Level"])
        kinship = int(char_metadata_decoded["properties"]["Kinship"])
        if kinship == 0:
            kinship_multiplier = 1
        else:
            kinship_multiplier = 1 + kinship*0.0005
        if level == 0:
            level_multiplier = 1
        else:
            level_multiplier = 1+level*0.005
        chance_multipler = (1 + (rank)*0.02)*(level_multiplier)*(kinship_multiplier)
        if woodcutting_data == "None":
            woodcutting_level = 0
            woodcutting_exp = 0
            final_base_chance_multiplier = chance_multipler
        else:
            woodcutting_data_split = woodcutting_data.split("/")
            woodcutting_level = int(woodcutting_data_split[0])
            woodcutting_exp = int(woodcutting_data_split[1])
            level_multiplier_wc = 1 + woodcutting_level*0.005
            final_base_chance_multiplier = chance_multipler*level_multiplier_wc
        if woodcutting_level < required_level:
            # Insert logic to handle message to user saying your level is lower than requirement for selected tree
            return
        metadata_decoded = json.loads((base64.b64decode((data_equipped["transactions"][0]["note"]).encode('utf-8'))).decode('utf-8'))
        available_uses = int(metadata_decoded["properties"]["Uses"])
        if available_uses == 0:
            embedNoUses = discord.Embed(
                title=f"🪓 {equipped_hatchet_name} has 0 Uses available! 🪓",
                description=f"To replenish Uses, you may use /replenish-hatchet to add 100 Uses for 100 $EXP",
                color=0xFF0000
            )
            embedNoUses.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
            await message.edit(embed=embedNoUses)
            return
        new_uses = available_uses - 1
        metadata_decoded["properties"]["Uses"] = new_uses
        metadata_encoded = json.dumps(metadata_decoded)
        await edit_hatchet(equipped_hatchet, metadata_encoded)
        embedChop2 = discord.Embed(
                title=f"Attempting To Chop {tree_type}...🪓",
                description=f"1 Use removed from {equipped_hatchet_name}",
                color=0xFCE303
            )
        embedChop2.set_image(url=tree_image)
        embedChop2.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        await message.edit(embed=embedChop2)
        await asyncio.sleep(5)
        final_base_chance = base_chance*final_base_chance_multiplier
        random_number = random.uniform(0,100)
        if final_base_chance < random_number:
            embedChopFail = discord.Embed(
                title=f"FAILED To Chop {tree_type}...😔",
                description=f"Base Success Rate: 10%\n\nMultiplier: {round(final_base_chance_multiplier,3)}\n\nFinal Success Rate: {round(final_base_chance,3)}\n\nTree Resistance: {round(random_number,3)}",
                color=0xFF0000
            )
            embedChopFail.set_image(url=tree_image)
            embedChopFail.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
            embedChopFail.set_footer(text=random.choice(oof) + f"\n{new_uses} Uses Remaining on {equipped_hatchet_name}\n\nCurrent Experience: {woodcutting_exp}\n\nExperience To Level {woodcutting_level+1}: {required_exp_to_level_up[woodcutting_level]}")
            await message.edit(embed=embedChopFail)
            return
        new_woodcutting_exp = woodcutting_exp + tree_exp
        if new_woodcutting_exp > required_exp_to_level_up[woodcutting_level]:
            new_woodcutting_level = woodcutting_level + 1
            levelup_string = f"\n\nLEVEL UP!! CONGRATULATIONS!\n\nNew Level: {new_woodcutting_level}"
        else:
            new_woodcutting_level = woodcutting_level
            levelup_string = f""
        wc_string = str(new_woodcutting_level) + "/" + str(new_woodcutting_exp)
        char_metadata_decoded["properties"]["Woodcutting"] = wc_string
        char_metadata_encoded = json.dumps(char_metadata_decoded)
        await edit_metadata(main_character, char_metadata_encoded)
        await send_logs(wallet, logs_id)
        if random.randint(0,100) <= 20:
            exp_won = random.randint(1,20)
            exp_string = f"\n\nYou struck a vein of $EXP...\n{exp_won} $EXP Gained!{levelup_string}"
            await send_assets("Woodcutting. $EXP Vein Struck! The Order", fallen_order_main, wallet, 811721471, "EXP", exp_won)
        else:
            exp_string = f"{levelup_string}"
        embedChopSuccess = discord.Embed(
                title=f"🌳 SUCCESSFULLY CHOPPED {tree_type}! 🌳",
                description=f"Base Success Rate: 10%\n\nMultiplier: {round(final_base_chance_multiplier,3)}\n\nFinal Success Rate: {round(final_base_chance,3)}\n\nTree Resistance: {round(random_number,3)}{exp_string}",
                color=0x28FF0A
            )
        embedChopSuccess.set_image(url=log_image)
        embedChopSuccess.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        embedChopSuccess.set_footer(text=f"{log_name} sent to your inventory!\n\nCurrent Experience: {new_woodcutting_exp}\n\nExperience To Level {new_woodcutting_level+1}: {required_exp_to_level_up[new_woodcutting_level]}")
        await message.edit(embed=embedChopSuccess)
        
    @chop_tree.error
    async def chop_tree_error(self, ctx, error):
        embedNotAllowed = discord.Embed(
                    title=f"One chop every 12 seconds!",
                    color=0xFF0000
                )
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(embed=embedNotAllowed, hidden=True)


class RandomHatchetCog(commands.Cog):
    @cog_ext.cog_slash(name="randomize-hatchet", description="Shuffle A Random Wooden Hatchet!")
    async def randomize_hatchet(self, ctx):
        if ctx.author.id != 805453439499894815:
            await ctx.send(embed=embedAdminOnly)
            return
        hatchet_image = "https://ipfs.algonft.tools/ipfs/QmSXLhwWeXDBtA31FDUY9xTiVysMrGmH2nfTJDwHL5Qt25"
        embedSelectionInProgress = discord.Embed(
                title=f"🪓 Initiating Wooden Hatchet Selection 🪓",
                description=f"What number will it be...",
                color=0xFF0000
            )
        embedSelectionInProgress.set_image(url=hatchet_image)
        embedSelectionInProgress.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        message = await ctx.send(embed=embedSelectionInProgress)
        chosen_hatchet = random.choice(hatchet_rank1)
        metadata_api = f"https://mainnet-idx.algonode.cloud/v2/transactions?tx-type=acfg&asset-id={chosen_hatchet}"
        response = requests.get(metadata_api)
        if response.status_code == 200:
            data = response.json()
        else:
            print("Error fetching data from API")
        hatchet_name = data["transactions"][-1]["asset-config-transaction"]["params"]["name"]
        await asyncio.sleep(5)
        embedSelectionComplete = discord.Embed(
                title=f"🪓 CLICK HERE TO OPT IN TO YOUR NEW HATCHET! 🪓",
                url=f"https://www.randgallery.com/algo-collection/?address={chosen_hatchet}",
                description=f"{hatchet_name} was chosen...\n\nGrats on your new Hatchet!",
                color=0xFCE303
            )
        embedSelectionComplete.set_image(url=hatchet_image)
        embedSelectionComplete.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        await message.edit(embed=embedSelectionComplete)



def setup(client: client):
    client.add_cog(MainCharCog(client))
    client.add_cog(RandomHatchetCog(client))
    client.add_cog(AdminLumberjackRoles(client))
    client.add_cog(ReplenishHatchetCog(client))
    client.add_cog(ChopTreeCog(client))
    client.add_cog(EquipHatchetCog(client))
    client.add_cog(DequipHatchetCog(client))
    client.add_cog(InventoryCog(client))
    