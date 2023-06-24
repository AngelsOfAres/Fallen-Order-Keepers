from discord_slash import cog_ext
from discord.ext import commands
import discord
import requests
import imageio.v2 as imageio
from PIL import Image, ImageOps
import random
from io import BytesIO
from discord import File
import math
from discord_slash.utils.manage_components import create_select, create_select_option, create_actionrow, create_button, wait_for_component
import json
from discord_slash.model import ButtonStyle
import base64
from discord_slash import ComponentContext
import asyncio
import pytz
from client import client
from txns import fallen_order_main, algod_client, get_wallet, edit_metadata, get_balance, send_assets, fallen_order_manager, clawback_character, logs_payment
from whitelist import fo_rank1, fo_rank2, fo_rank3
from fusion_wl import *

required_exp_to_level_up = [83, 257, 533, 921, 1433, 2083, 2884, 3853, 5007, 6365, 7947, 9775, 11872, 14262, 16979, 20047]
new_hp = [10000, 10500, 11000, 11500, 12000, 12500, 13000, 13500, 14000]

class FusionCog(commands.Cog):
    @cog_ext.cog_slash(name="fusion", description="Add 1 Level Point To Your Fallen Order and get a Stat Booster!", options=[
                    {
                        "name": "rank",
                        "description": "Rank To Fuse Into",
                        "type": 4,
                        "required": True,
                        "choices": [
                            {
                                "name": "Rank 2",
                                "value": "2"
                            },
                            {
                                "name": "Rank 3",
                                "value": "3"
                            },
                            {
                                "name": "Rank 4",
                                "value": "4"
                            }
                        ]
                    }
                ])
    @commands.cooldown(1, 30, commands.BucketType.guild)
    async def fusion(self, ctx, rank):
        if rank == 2:
            fo_rank_wl = fo_rank1
            cost_order = 100
            cost_exp =  5000
            cost_logs =  50
            random_fallen = random.choice(available_fusion_2)
        elif rank == 3:
            fo_rank_wl = fo_rank2
            cost_order = 500
            cost_exp =  20000
            cost_logs = 125
            random_fallen = random.choice(available_fusion_3)
        elif rank == 4:
            fo_rank_wl = fo_rank3
            cost_order = 1000
            cost_exp =  50000
            cost_logs =  300
            random_fallen = random.choice(available_fusion_4)
        embedFusionInProgress = discord.Embed(
                title=f"🧙‍♂️ Initiating Rank {rank} Fusion! 🧙‍♂️",
                description=f"{ctx.author.name} gathers their Rank {int(rank)-1} Fallen Order to FUSE!",
                color=0xFCE303
            )
        embedFusionInProgress.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        message = await ctx.send(embed=embedFusionInProgress)
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
        balance_order = await get_balance(wallet, 811718424)
        if balance_order < cost_order:
            embedNoEXP = discord.Embed(title=f"Woops! You do not own enough $ORDER!", description=f"Fusing into a Rank {rank} costs:\n\n{cost_order} $ORDER | {cost_exp} $EXP | {cost_logs} Oak Logs", color=0xFF0000)
            embedNoEXP.set_thumbnail(url="https://s3.amazonaws.com/algorand-wallet-mainnet-thumbnails/prism-images/media/assets-logo-png/2022/10/11/a26da3af714a40e8bad2b29a6dfc4655.png--resize--w__200--q__70.webp")   
            await message.edit(embed=embedNoEXP)
            return
        balance_exp = await get_balance(wallet, 811721471)
        if balance_exp < cost_exp:
            embedNoEXP = discord.Embed(title=f"Woops! You do not own enough $EXP!", description=f"Fusing into a Rank {rank} costs:\n\n{cost_order} $ORDER | {cost_exp} $EXP | {cost_logs} Oak Logs", color=0xFF0000)
            embedNoEXP.set_thumbnail(url="https://s3.amazonaws.com/algorand-wallet-mainnet-thumbnails/prism-images/media/assets-logo-png/2022/10/11/a26da3af714a40e8bad2b29a6dfc4655.png--resize--w__200--q__70.webp")   
            await message.edit(embed=embedNoEXP)
            return
        balance_logs = await get_balance(wallet, 1064863037)
        if balance_logs < cost_logs:
            embedNoEXP = discord.Embed(title=f"Woops! You do not own enough Oak Logs!", description=f"Fusing into a Rank {rank} costs:\n\n{cost_order} $ORDER | {cost_exp} $EXP | {cost_logs} Oak Logs", color=0xFF0000)
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
            if asset["amount"] > 0 and asset["asset-id"] in fo_rank_wl:
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
                title=f"Awwww...{ctx.author.name} does not own any Rank {rank-1} Fallen Order!",
                description=f"Get yourself an army pleb!\n\n[Click Here To Shuffle!](https://algoxnft.com/shuffle/902)",
                color=0xFF0000
            )
            embedNoFO.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
            await message.edit(embed=embedNoFO)
            return        
        select_options = [create_select_option(label=fallen[0] + " - " + fallen[2], value=str(fallen[1])) for fallen in fallen_assets]
        select = create_select(options=select_options, placeholder="Select the first character", min_values=1, max_values=1)
        action_row = create_actionrow(select)
        await message.edit(embed=embedFusionInProgress, components=[action_row])
        try:
            while True:
                interaction: ComponentContext = await wait_for_component(client, components=action_row, timeout=30.0)
                interaction_author_id = interaction.author.id
                if interaction_author_id == ctx.author.id:
                    await interaction.defer(edit_origin=True)
                    chosen_fallen1 = interaction.selected_options[0]
                    break
                else:
                    embedWrongUpgrade = discord.Embed(
                        title=f"This is not your fusion!",
                        description=f"{ctx.author.name} is currently fusing..",
                        color=0xFF0000
                    )
                    await interaction.send(embed=embedWrongUpgrade, hidden=True)
                    continue
        except asyncio.TimeoutError:
            embedTimeout = discord.Embed(
                    title=f"Woops! You took too long to respond...",
                    description=f"Ending {ctx.author.name}'s fusion..",
                    color=0xFF0000
                )
            await message.edit(embed=embedTimeout, components=[])
            await asyncio.sleep(10)
            await message.delete()
            return
        select_options = [create_select_option(label=fallen[0] + " - " + fallen[2], value=str(fallen[1])) for fallen in fallen_assets]
        select = create_select(options=select_options, placeholder="Select the second character", min_values=1, max_values=1)
        action_row = create_actionrow(select)
        await message.edit(embed=embedFusionInProgress, components=[action_row])
        try:
            while True:
                interaction: ComponentContext = await wait_for_component(client, components=action_row, timeout=30.0)
                interaction_author_id = interaction.author.id
                if interaction_author_id == ctx.author.id:
                    await interaction.defer(edit_origin=True)
                    chosen_fallen2 = interaction.selected_options[0]
                    if chosen_fallen2 == chosen_fallen1:
                        embedTimeout = discord.Embed(
                                title=f"Woops! Can't Fuse The Same Character...",
                                description=f"Ending {ctx.author.name}'s fusion..",
                                color=0xFF0000
                            )
                        await message.edit(embed=embedTimeout, components=[])
                        return
                    break
                else:
                    embedWrongUpgrade = discord.Embed(
                        title=f"This is not your fusion!",
                        description=f"{ctx.author.name} is currently fusing..",
                        color=0xFF0000
                    )
                    await interaction.send(embed=embedWrongUpgrade, hidden=True)
                    continue
        except asyncio.TimeoutError:
            embedTimeout = discord.Embed(
                    title=f"Woops! You took too long to respond...",
                    description=f"Ending {ctx.author.name}'s fusion..",
                    color=0xFF0000
                )
            await message.edit(embed=embedTimeout, components=[])
            await asyncio.sleep(10)
            await message.delete()
            return
        metadata_api1 = f"https://mainnet-idx.algonode.cloud/v2/transactions?tx-type=acfg&asset-id={chosen_fallen1}&address={fallen_order_manager}"
        response1 = requests.get(metadata_api1)
        if response1.status_code == 200:
            data1 = response1.json()
        else:
            print("Error fetching data from API")
        metadata_decoded1 = (json.loads((base64.b64decode((data1["transactions"][0]["note"]).encode('utf-8'))).decode('utf-8')))
        metadata_api2 = f"https://mainnet-idx.algonode.cloud/v2/transactions?tx-type=acfg&asset-id={chosen_fallen2}&address={fallen_order_manager}"
        response2 = requests.get(metadata_api2)
        if response2.status_code == 200:
            data2 = response2.json()
        else:
            print("Error fetching data from API")
        metadata_decoded2 = (json.loads((base64.b64decode((data2["transactions"][0]["note"]).encode('utf-8'))).decode('utf-8')))
        level1 = int(metadata_decoded1["properties"]["Level"])
        asset_info1 = algod_client.asset_info(chosen_fallen1)
        fallen_image_url1 = asset_info1["params"]["url"]
        fallen_image1 = "https://ipfs.algonft.tools/ipfs/" + (fallen_image_url1).replace("ipfs://", "")
        fallen_name1 = metadata_decoded1.get("properties", {}).get("Name", "None")
        kinship1 = int(metadata_decoded1["properties"]["Kinship"])
        metadata_decoded1["properties"]["Kinship"] = 0
        attack1 = int(metadata_decoded1["properties"]["ATK"])
        metadata_decoded1["properties"]["ATK"] = 0
        defense1 = int(metadata_decoded1["properties"]["DEF"])
        metadata_decoded1["properties"]["DEF"] = 0
        abilitypower1 = int(metadata_decoded1["properties"]["AP"])
        metadata_decoded1["properties"]["AP"] = 0
        metadata_decoded1["properties"]["HP"] = 10000
        points1 = int(metadata_decoded2["properties"]["Points"])
        metadata_decoded1["properties"]["Points"] = 1000
        woodcutting_data1 = metadata_decoded1.get("properties", {}).get("Woodcutting", "None")
        if woodcutting_data1 == "None":
            woodcutting_exp1 = 0
        else:
            woodcutting_data_split1 = woodcutting_data1.split("/")
            woodcutting_exp1 = int(woodcutting_data_split1[1])
        wc_string = "0/0"
        metadata_decoded1["properties"]["Woodcutting"] = wc_string
        metadata_encoded1 = json.dumps(metadata_decoded1)
        print(metadata_encoded1)

        level2 = int(metadata_decoded2["properties"]["Level"])
        asset_info2 = algod_client.asset_info(chosen_fallen2)
        fallen_image_url2 = asset_info2["params"]["url"]
        fallen_image2 = "https://ipfs.algonft.tools/ipfs/" + (fallen_image_url2).replace("ipfs://", "")
        fallen_name2 = metadata_decoded2.get("properties", {}).get("Name", "None")
        kinship2 = int(metadata_decoded2["properties"]["Kinship"])
        metadata_decoded2["properties"]["Kinship"] = 0
        attack2 = int(metadata_decoded2["properties"]["ATK"])
        metadata_decoded2["properties"]["ATK"] = 0
        defense2 = int(metadata_decoded2["properties"]["DEF"])
        metadata_decoded2["properties"]["DEF"] = 0
        abilitypower2 = int(metadata_decoded2["properties"]["AP"])
        metadata_decoded2["properties"]["AP"] = 0
        metadata_decoded2["properties"]["HP"] = 10000
        points2 = int(metadata_decoded2["properties"]["Points"])
        metadata_decoded2["properties"]["Points"] = 1000
        woodcutting_data2 = metadata_decoded2.get("properties", {}).get("Woodcutting", "None")
        if woodcutting_data2 == "None":
            woodcutting_exp2 = 0
        else:
            woodcutting_data_split2 = woodcutting_data2.split("/")
            woodcutting_exp2 = int(woodcutting_data_split2[1])
        metadata_decoded2["properties"]["Woodcutting"] = wc_string
        metadata_encoded2 = json.dumps(metadata_decoded2)
        print(metadata_encoded2)

        response1 = requests.get(fallen_image1)
        image1 = Image.open(BytesIO(response1.content))
        response2 = requests.get(fallen_image2)
        image2 = Image.open(BytesIO(response2.content))
        transparent_image = Image.new('RGBA', (image1.width + image2.width, max(image1.height, image2.height)), color=(0, 0, 0, 0))
        transparent_image.paste(image1, (0, 0))
        transparent_image.paste(ImageOps.mirror(image2), (image1.width, 0))
        buffer = BytesIO()
        transparent_image.save(buffer, format='PNG')
        buffer.seek(0)
        image_file = File(buffer, filename=f'fusion_combo.png')

        total_points = math.ceil((points1+points2+attack1+attack2+defense1+defense2+abilitypower1+abilitypower2)/2)
        total_level = math.ceil((level1+level2)/2)
        total_kinship = kinship1+kinship2
        total_woodcutting_exp = math.ceil((woodcutting_exp1+woodcutting_exp2)/2)

        metadata_api3 = f"https://mainnet-idx.algonode.cloud/v2/transactions?tx-type=acfg&asset-id={random_fallen}&address={fallen_order_manager}"
        response3 = requests.get(metadata_api3)
        if response3.status_code == 200:
            data3 = response3.json()
        else:
            print("Error fetching data from API")
        metadata_decoded3 = (json.loads((base64.b64decode((data3["transactions"][0]["note"]).encode('utf-8'))).decode('utf-8')))
        asset_info3 = algod_client.asset_info(random_fallen)
        fallen_image_url3 = asset_info3["params"]["url"]
        fallen_image3 = "https://ipfs.algonft.tools/ipfs/" + (fallen_image_url3).replace("ipfs://", "")
        fallen_name3 = asset_info3['params']['unit-name']
        i = 0
        for exp in required_exp_to_level_up:
            if total_woodcutting_exp < exp:
                total_wc_level = i
                break
            i += 1
        wc_string = str(total_wc_level) + "/" + str(total_woodcutting_exp)
        metadata_decoded3["properties"]["Level"] = total_level
        metadata_decoded3["properties"]["Name"] = fallen_name1
        metadata_decoded3["properties"]["HP"] = new_hp[total_level]
        metadata_decoded3["properties"]["Kinship"] = total_kinship
        metadata_decoded3["properties"]["Points"] = total_points
        metadata_decoded3["properties"]["Woodcutting"] = wc_string
        metadata_encoded3 = json.dumps(metadata_decoded3)
        print(metadata_encoded3)

        embedConfirmUpgrade = discord.Embed(
                title=f"⚠️ Confirm Rank {rank} Fusion! ⚠️",
                description=f"{fallen_name1} + {fallen_name2} will be fused to combine into a Rank {rank}!\n\nNew Character Stats:",
                color=0xFCE303
            )
        embedConfirmUpgrade.add_field(name=f"Level | Kinship | Points", value=f"{total_level} | {total_kinship} | {total_points}", inline=False)   
        embedConfirmUpgrade.add_field(name=f"Woodcutting LVL | Experience", value=f"{total_wc_level} | {total_woodcutting_exp}", inline=False)
        embedConfirmUpgrade.set_footer(text=f"Confirm Level Up?\n\nCost: {cost_order} $ORDER | {cost_exp} $EXP | {cost_logs} Oak Logs")
        embedConfirmUpgrade.set_image(url="attachment://fusion_combo.png")
        embedConfirmUpgrade.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        action_row = create_actionrow(
                            create_button(style=ButtonStyle.green, label="FUSION!!!", custom_id="confirm"),
                            create_button(style=ButtonStyle.red, label="CANCEL", custom_id="cancel")
                        )
        await message.edit(file=image_file, embed=embedConfirmUpgrade, components=[action_row])
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
                    embedConfirmUpgrade.set_footer(text=f"{fallen_name1} + {fallen_name2} - Rank {rank} fusion in progress! ⏳")
                    await message.edit(embed=embedConfirmUpgrade, components=[])
                    await send_assets(str(ctx.author.name), wallet, fallen_order_main, 811718424, "ORDER", cost_order)
                    await send_assets(str(ctx.author.name), wallet, fallen_order_main, 811721471, "EXP", cost_exp)
                    await logs_payment(wallet, 1064863037, cost_logs)
                    if rank == "2":
                        available_fusion_2.remove(random_fallen)
                        with open('fusion_wl.py', 'w') as f:
                            f.write(f"available_fusion_2 = {available_fusion_2}")
                    elif rank == "3":
                        available_fusion_3.remove(random_fallen)
                        with open('fusion_wl.py', 'w') as f:
                            f.write(f"available_fusion_3 = {available_fusion_3}")
                    elif rank == "4":
                        available_fusion_4.remove(random_fallen)
                        with open('fusion_wl.py', 'w') as f:
                            f.write(f"available_fusion_4 = {available_fusion_4}")
                    await clawback_character(wallet, chosen_fallen1)
                    await clawback_character(wallet, chosen_fallen2)
                    await edit_metadata(chosen_fallen1, metadata_encoded1)
                    await edit_metadata(chosen_fallen2, metadata_encoded2)
                    await edit_metadata(random_fallen, metadata_encoded3)
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
        embedFusionComplete = discord.Embed(
                title=f"🧙 RANK {rank} FUSION COMPLETE! 🧙‍♀️",
                url=f"https://nftexplorer.app/asset/{random_fallen}",
                description=f"Fused Fallen: {fallen_name3}",
                color=0x28FF0A
            )
        embedFusionComplete.add_field(name=f"Level | Kinship | Points", value=f"{total_level} | {total_kinship} | {total_points}", inline=False)
        embedFusionComplete.add_field(name=f"Woodcutting LVL | Experience", value=f"{total_wc_level} | {total_woodcutting_exp}", inline=False)
        embedFusionComplete.add_field(name=f"Total Paid", value=f"{cost_order} $ORDER | {cost_exp} $EXP | {cost_logs} Oak Logs", inline=False)
        embedFusionComplete.set_image(url=fallen_image3)
        embedFusionComplete.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        embedFusionComplete.set_footer(text=f"🔥 CONGRATULATIONS! RANKED UP LIKE A BOSS! 🔥")
        await message.delete()
        await ctx.send(embed=embedFusionComplete, components=[])

    @fusion.error
    async def fusion_error(self, ctx, error):
        embedNotAllowed = discord.Embed(
                    title=f"Please wait 30sec before this command becomes available again!",
                    color=0xFF0000
                )
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(embed=embedNotAllowed, hidden=True)

def setup(client: client):
    client.add_cog(FusionCog(client))