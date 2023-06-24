from discord_slash import cog_ext
from discord.ext import commands
from discord.utils import get
import discord
import random
import requests
from discord_slash.utils.manage_components import create_select, create_select_option, create_actionrow
import asyncio
import json
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from discord_slash import ComponentContext
from discord_slash.utils.manage_components import create_select, create_select_option, create_actionrow, wait_for_component
from discord.utils import get
from client import client
from txns import algod_client, get_all_wallets, get_wallet, fallen_order_manager
from embeds import embedAdminOnly, embedAdminRoles, embedDiscordErr, embedNoFlex, embedNoCount
from whitelist import ghosts, ghostsIcons, fo_rank1, fo_rank2, fo_rank3, fo_rank4, fo_rank5

angel_wings = [789639573]
async def get_guild():
    guild = client.get_guild(936698039941345370)
    return guild

class AdminRolesCog(commands.Cog):
    @cog_ext.cog_slash(name="admin-roles", description="Admin Use Only!")
    async def admin_roles(self, ctx):
        await ctx.defer()
        if ctx.author.id != 805453439499894815:
            await ctx.send(embed=embedAdminOnly)
            return
        else:
            wallets = await get_all_wallets()

            for wallet in wallets:
                account_info = algod_client.account_info(wallet['address'])
                assets = account_info.get("assets", [])

                ghostcount = 0
                ghosticoncount = 0
                wingcount = 0
                fo_1count = 0
                fo_2count = 0
                fo_3count = 0
                fo_4count = 0
                fo_5count = 0
                lilangel_count = 0
                angel_count = 0
                celestial_count = 0
                ethereal_count = 0
                empyreal_count = 0
                immortal_count = 0

                for asset in assets:
                    if asset["amount"] > 0 and asset["asset-id"] in ghosts:
                        ghostcount += 1
                    if asset["amount"] > 0 and asset["asset-id"] in ghostsIcons:
                        ghosticoncount += 1
                    if asset["amount"] > 0 and asset["asset-id"] in fo_rank1:
                        fo_1count += 1
                    if asset["amount"] > 0 and asset["asset-id"] in fo_rank2:
                        fo_2count += 1
                    if asset["amount"] > 0 and asset["asset-id"] in fo_rank3:
                        fo_3count += 1
                    if asset["amount"] > 0 and asset["asset-id"] in fo_rank4:
                        fo_4count += 1
                    if asset["amount"] > 0 and asset["asset-id"] in fo_rank5:
                        fo_5count += 1
                    if asset["amount"] > 0 and asset["asset-id"] in angel_wings:
                        wingcount = asset["amount"]

                guild = await get_guild()
                count = ghostcount*1 + ghosticoncount*5 + fo_1count*2 + fo_2count*3 + fo_3count*5 + fo_4count*8 + fo_5count*15 + wingcount*5
                member = guild.get_member(int(wallet['userid']))
                if member is not None:
                    if count == 0:
                        break
                    elif count < 10:
                        #Lil Angel
                        lilangel_count += 1
                        role = get(guild.roles, id=1053388861998379008)
                        role1 = get(guild.roles, id=937694464351297566)
                        role2 = get(guild.roles, id=1077675549205463161)
                        role3 = get(guild.roles, id=1077675671070974063)
                        role4 = get(guild.roles, id=1077675803829080114)
                        role5 = get(guild.roles, id=1077675855737794650)
                    elif count < 25:
                        #Angel
                        angel_count += 1
                        role = get(guild.roles, id=937694464351297566)
                        role1 = get(guild.roles, id=1053388861998379008)
                        role2 = get(guild.roles, id=1077675549205463161)
                        role3 = get(guild.roles, id=1077675671070974063)
                        role4 = get(guild.roles, id=1077675803829080114)
                        role5 = get(guild.roles, id=1077675855737794650)
                    elif count < 42:
                        #Celestial
                        celestial_count += 1
                        role = get(guild.roles, id=1077675549205463161)
                        role1 = get(guild.roles, id=1053388861998379008)
                        role2 = get(guild.roles, id=937694464351297566)
                        role3 = get(guild.roles, id=1077675671070974063)
                        role4 = get(guild.roles, id=1077675803829080114)
                        role5 = get(guild.roles, id=1077675855737794650)
                    elif count < 69:
                        #Ethereal
                        ethereal_count += 1
                        role = get(guild.roles, id=1077675671070974063)
                        role1 = get(guild.roles, id=1053388861998379008)
                        role2 = get(guild.roles, id=937694464351297566)
                        role3 = get(guild.roles, id=1077675549205463161)
                        role4 = get(guild.roles, id=1077675803829080114)
                        role5 = get(guild.roles, id=1077675855737794650)
                    elif count < 99:
                        #Empyreal
                        empyreal_count += 1
                        role = get(guild.roles, id=1077675803829080114)
                        role1 = get(guild.roles, id=1053388861998379008)
                        role2 = get(guild.roles, id=937694464351297566)
                        role3 = get(guild.roles, id=1077675549205463161)
                        role4 = get(guild.roles, id=1077675671070974063)
                        role5 = get(guild.roles, id=1077675855737794650)
                    else:
                        #Immortal
                        immortal_count += 1
                        role = get(guild.roles, id=1077675855737794650)
                        role1 = get(guild.roles, id=1053388861998379008)
                        role2 = get(guild.roles, id=937694464351297566)
                        role3 = get(guild.roles, id=1077675549205463161)
                        role4 = get(guild.roles, id=1077675671070974063)
                        role5 = get(guild.roles, id=1077675803829080114)


                    if role not in member.roles:
                        if role.id == 1053388861998379008:
                            embedAdminRoles.add_field(name=f"{member.name}", value=f"Added LIL ANGEL role. Score: {count} 👼🏼", inline=True)
                        if role.id == 937694464351297566:
                            embedAdminRoles.add_field(name=f"{member.name}", value=f"Added ANGEL role. Score: {count} 😇", inline=True)
                        if role.id == 1077675549205463161:
                            embedAdminRoles.add_field(name=f"{member.name}", value=f"Added CELESTIAL role. Score: {count} 🧚", inline=True)
                        if role.id == 1077675671070974063:
                            embedAdminRoles.add_field(name=f"{member.name}", value=f"Added ETHEREAL role. Score: {count} 🧙", inline=True)
                        if role.id == 1077675803829080114:
                            embedAdminRoles.add_field(name=f"{member.name}", value=f"Added EMPYREAL role. Score: {count} 💪", inline=True)
                        if role.id == 1077675855737794650:
                            embedAdminRoles.add_field(name=f"{member.name}", value=f"Added IMMORTAL role. Score: {count} 🔥🔥🔥", inline=True)
                        await member.add_roles(role)
                    
                    await member.remove_roles(role1, role2, role3, role4, role5)
                                
        await ctx.send(embed=embedAdminRoles)
        embedAdminRoles.clear_fields()
        return

class RolesCog(commands.Cog):
    @cog_ext.cog_slash(name="roles", description="Update User Roles!")
    async def check_wallet_for_assets(self, ctx):
        wallet, name, won, lost, expwon, explost, lastdrip, drip_exp = await get_wallet(str(ctx.author.id))
        if wallet == '':
            embedNoReg = discord.Embed(
                    title="Click Here To Register!",
                    url="https://app.fallenorder.xyz",
                    description=f"Please verify your wallet via our website to continue..\nEnsure you copy your user id below for the verification process:\nUser ID: {ctx.author.id}",
                    color=0xFF1C0A,
                )
            await ctx.send(embed=embedNoReg)
            return
        else:
            account_info = algod_client.account_info(wallet)
            assets = account_info.get("assets", [])
            ghostcount = 0
            ghosticoncount = 0
            wingcount = 0
            fo_1count = 0
            fo_2count = 0
            fo_3count = 0
            fo_4count = 0
            fo_5count = 0
            for asset in assets:
                if asset["amount"] > 0 and asset["asset-id"] in ghosts:
                    ghostcount += 1
                if asset["amount"] > 0 and asset["asset-id"] in ghostsIcons:
                    ghosticoncount += 1
                if asset["amount"] > 0 and asset["asset-id"] in fo_rank1:
                    fo_1count += 1
                if asset["amount"] > 0 and asset["asset-id"] in fo_rank2:
                    fo_2count += 1
                if asset["amount"] > 0 and asset["asset-id"] in fo_rank3:
                    fo_3count += 1
                if asset["amount"] > 0 and asset["asset-id"] in fo_rank4:
                    fo_4count += 1
                if asset["amount"] > 0 and asset["asset-id"] in fo_rank5:
                    fo_5count += 1
                if asset["amount"] > 0 and asset["asset-id"] in angel_wings:
                    wingcount = asset["amount"]

            count = ghostcount*1 + ghosticoncount*5 + fo_1count*2 + fo_2count*3 + fo_3count*5 + fo_4count*8 + fo_5count*15 + wingcount*5
            if count == 0:
                await ctx.send(embed=embedNoCount)
                return
            
        guild = await get_guild()
        member = guild.get_member(int(ctx.author.id))
        if member is not None:
            if count < 10 and count > 0:
                #Lil Angel
                role = get(guild.roles, id=1053388861998379008)
                role1 = get(guild.roles, id=937694464351297566)
                role2 = get(guild.roles, id=1077675549205463161)
                role3 = get(guild.roles, id=1077675671070974063)
                role4 = get(guild.roles, id=1077675803829080114)
                role5 = get(guild.roles, id=1077675855737794650)
            elif count < 25:
                #Angel
                role = get(guild.roles, id=937694464351297566)
                role1 = get(guild.roles, id=1053388861998379008)
                role2 = get(guild.roles, id=1077675549205463161)
                role3 = get(guild.roles, id=1077675671070974063)
                role4 = get(guild.roles, id=1077675803829080114)
                role5 = get(guild.roles, id=1077675855737794650)
            elif count < 42:
                #Celestial
                role = get(guild.roles, id=1077675549205463161)
                role1 = get(guild.roles, id=1053388861998379008)
                role2 = get(guild.roles, id=937694464351297566)
                role3 = get(guild.roles, id=1077675671070974063)
                role4 = get(guild.roles, id=1077675803829080114)
                role5 = get(guild.roles, id=1077675855737794650)
            elif count < 69:
                #Ethereal
                role = get(guild.roles, id=1077675671070974063)
                role1 = get(guild.roles, id=1053388861998379008)
                role2 = get(guild.roles, id=937694464351297566)
                role3 = get(guild.roles, id=1077675549205463161)
                role4 = get(guild.roles, id=1077675803829080114)
                role5 = get(guild.roles, id=1077675855737794650)
            elif count < 99:
                #Empyreal
                role = get(guild.roles, id=1077675803829080114)
                role1 = get(guild.roles, id=1053388861998379008)
                role2 = get(guild.roles, id=937694464351297566)
                role3 = get(guild.roles, id=1077675549205463161)
                role4 = get(guild.roles, id=1077675671070974063)
                role5 = get(guild.roles, id=1077675855737794650)
            else:
                #Immortal
                role = get(guild.roles, id=1077675855737794650)
                role1 = get(guild.roles, id=1053388861998379008)
                role2 = get(guild.roles, id=937694464351297566)
                role3 = get(guild.roles, id=1077675549205463161)
                role4 = get(guild.roles, id=1077675671070974063)
                role5 = get(guild.roles, id=1077675803829080114)
            
            embedRoles = discord.Embed(
                    title=f"Welcome Home {role}!",
                    description=f"I've given you the {role} role based on your AoA holdings below:",
                    color=0x00E1FF
                )
            embedRoles.add_field(name=f"Angel Wings: ", value=f"{wingcount}", inline=True)
            embedRoles.add_field(name=f"Fallen Order: ", value=f"{fo_1count} Angel | {fo_2count} Celestial | {fo_3count} Ethereal | {fo_4count} Empyreal | {fo_5count} Immortal", inline=True)
            embedRoles.add_field(name=f"Ghosts: ", value=f"{ghostcount} Ghosties | {ghosticoncount} Icon", inline=True)
            embedRoles.add_field(name=f"Total Score: ", value=f"{count}", inline=True)
            embedRoles.set_footer(
                    text='If you have any questions or concerns please tag @angel.algo 💙',
                    icon_url="https://www.vesea.io/_next/image?url=https%3A%2F%2Fs3.us-east-2.amazonaws.com%2Fvesea.io-profiles%2Fprofile_pics%2F0xe3e0bb8fe0a2a65858eaa8c04758f14939ff2a95.WEBP%3Fr%3D352&w=960&q=75"
                )

            embedHasRole = discord.Embed(
                    title=f"Looks like you are good to go {role}!",
                    description=f"You already have your role assigned based on your current holdings",
                    color=0x28FF0A
                )
            embedHasRole.add_field(name=f"Angel Wings: ", value=f"{wingcount}", inline=True)
            embedHasRole.add_field(name=f"Fallen Order: ", value=f"{fo_1count} Angel | {fo_2count} Celestial | {fo_3count} Ethereal | {fo_4count} Empyreal | {fo_5count} Immortal", inline=True)
            embedHasRole.add_field(name=f"Ghosts: ", value=f"{ghostcount} Ghosties | {ghosticoncount} Icon", inline=True)
            embedHasRole.add_field(name=f"Total Score: ", value=f"{count}", inline=True)
            embedHasRole.set_footer(
                    text='If you have any questions or concerns please tag @angel.algo 💙',
                    icon_url="https://www.vesea.io/_next/image?url=https%3A%2F%2Fs3.us-east-2.amazonaws.com%2Fvesea.io-profiles%2Fprofile_pics%2F0xe3e0bb8fe0a2a65858eaa8c04758f14939ff2a95.WEBP%3Fr%3D352&w=960&q=75"
                )

            if role not in member.roles:
                await member.add_roles(role)
                await member.remove_roles(role1, role2, role3, role4, role5)
                await ctx.send(embed=embedRoles)
                return True
            
            await ctx.send(embed=embedHasRole)

class HoldersCog(commands.Cog):
    @cog_ext.cog_slash(name="holders", description="Display Top Holders!", options=[
                {
                    "name": "collection",
                    "description": "Collection Rankings To Display",
                    "type": 3,
                    "required": True,
                    "choices": [
                        {
                            "name": "Angel Wings",
                            "value": "wings"
                        },
                        {
                            "name": "Fallen Order",
                            "value": "fallen"
                        },
                        {
                            "name": "Ghosts Of Algo",
                            "value": "ghosts"
                        }
                    ]
                },
                {
                    "name": "count",
                    "description": "Count Of Holders To Display",
                    "type": 4,
                    "required": True
                }])
    async def holder_rankings(self, ctx, collection, count):
        await ctx.defer()
        wallets = await get_all_wallets()
        embedHoldersWings = discord.Embed(
                    title="🏆 Angel Wings - Holder Rankings 🏆",
                    color=0xFFFB0A
                )
        embedHoldersFallen = discord.Embed(
                    title="🏆 Fallen Order - Holder Rankings 🏆",
                    color=0xFFFB0A
                )
        embedHoldersGhosts = discord.Embed(
                    title="🏆 Ghosts Of Algo - Holder Rankings 🏆",
                    color=0xFFFB0A
                )

        user_data = []
        for wallet in wallets:
            account_info = algod_client.account_info(wallet['address'])
            assets = account_info.get("assets", [])

            ghostcount = 0
            ghosticoncount = 0
            wingcount = 0
            fo_1count = 0
            fo_2count = 0
            fo_3count = 0
            fo_4count = 0
            fo_5count = 0

            for asset in assets:
                if asset["amount"] > 0 and asset["asset-id"] in ghosts:
                    ghostcount += 1
                if asset["amount"] > 0 and asset["asset-id"] in ghostsIcons:
                    ghosticoncount += 1
                if asset["amount"] > 0 and asset["asset-id"] in fo_rank1:
                    fo_1count += 1
                if asset["amount"] > 0 and asset["asset-id"] in fo_rank2:
                    fo_2count += 1
                if asset["amount"] > 0 and asset["asset-id"] in fo_rank3:
                    fo_3count += 1
                if asset["amount"] > 0 and asset["asset-id"] in fo_rank4:
                    fo_4count += 1
                if asset["amount"] > 0 and asset["asset-id"] in fo_rank5:
                    fo_5count += 1
                if asset["amount"] > 0 and asset["asset-id"] in angel_wings:
                    wingcount = asset["amount"]
                    
            guild = await get_guild()
            member = guild.get_member(int(wallet['userid']))
            user_data.append([member, wingcount, fo_1count + fo_2count + fo_3count + fo_4count + fo_5count, ghostcount + ghosticoncount, fo_1count, fo_2count, fo_3count, fo_4count, fo_5count, ghostcount, ghosticoncount])

        i = 0
        if collection == "wings":
            sorted_list = sorted(user_data, key=lambda x: x[1], reverse = True)
            for user in sorted_list:
                if i == count:
                    break
                if user[0] is not None and user[0].name != "angel.algo":
                    embedHoldersWings.add_field(name=f"<@{user[0].id}> - {user[1]}", value=f".", inline=False)
                    i += 1
            await ctx.send(embed=embedHoldersWings)
        elif collection == "fallen":
            sorted_list = sorted(user_data, key=lambda x: x[2], reverse = True)
            for user in sorted_list:
                if i == count:
                    break
                if user[0] is not None and user[0].name != "angel.algo":
                    embedHoldersFallen.add_field(name=f"<@{user[0].id}> - {user[2]}", value=f"{user[4]} Angel | {user[5]} Celestial | {user[6]} Ethereal | {user[7]} Empyreal | {user[8]} Immortal", inline=False)
                    i += 1
            await ctx.send(embed=embedHoldersFallen)
        elif collection == "ghosts":
            sorted_list = sorted(user_data, key=lambda x: x[3], reverse = True)
            for user in sorted_list:
                if i == count:
                    break
                if user[0] is not None and user[0].name != "angel.algo":
                    embedHoldersGhosts.add_field(name=f"<@{user[0].id}> - {user[3]}", value=f"{user[9]} Ghosties | {user[10]} Icon", inline=False)
                    i += 1
            await ctx.send(embed=embedHoldersGhosts)
        return

class FlexCog(commands.Cog):
    @cog_ext.cog_slash(name="flex", description="Flex Your NFTs!", options=[
                    {
                        "name": "collection",
                        "description": "Fallen Order / Ghosts Of Algo",
                        "type": 3,
                        "required": True,
                        "choices": [
                            {
                                "name": "Fallen Order",
                                "value": "fallen"
                            },
                            {
                                "name": "Ghosts Of Algo",
                                "value": "ghost"
                            }
                        ]
                    }
                ])
    async def flex(self, ctx, collection):
        await ctx.defer()
        userid = str(ctx.author.id)
        wallet, name, won, lost, expwon, explost, lastdrip, drip_exp = await get_wallet(userid)
        
        fallen_assets = []
        ghost_assets = []
        account_info = algod_client.account_info(wallet)
        assets = account_info.get("assets", [])
        counter = 0
        for asset in assets:
            if counter >= 25:
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
                counter += 1
        for asset in assets:
            if asset["amount"] > 0 and (asset["asset-id"] in ghosts or asset["asset-id"] in ghostsIcons):
                ghost_assets.append(asset['asset-id'])
        
        if fallen_assets == []:
            await ctx.send(embed=embedNoFlex)
            return
        else:
            if collection == "fallen":
                embedChooseFlex = discord.Embed(
                                title=f"Master {ctx.author.name}, we have been summoned...",
                                color=0xFF1C0A
                            )
                counter = 0
                select_options = []
                for fallen in fallen_assets:
                    if counter >= 25:
                        break
                    select_options.append(create_select_option(label=fallen[0] + " - " + fallen[2], value=str(fallen[1])))
                    counter += 1
                select = create_select(options=select_options, placeholder="Pick one of us to flex!", min_values=1, max_values=1)
                action_row = create_actionrow(select)
                message = await ctx.send(embed=embedChooseFlex, components=[action_row])
                try:
                    while True:
                        interaction: ComponentContext = await wait_for_component(client, components=action_row, timeout=20.0)
                        interaction_author_id = interaction.author.id

                        if interaction_author_id == ctx.author.id:
                            await interaction.defer(edit_origin=True)
                            chosen_fallen = interaction.selected_options[0]
                            await asyncio.sleep(1)
                            await message.delete()
                            break
                        else:
                            embedWrongUpgrade = discord.Embed(
                                title=f"This is not your flex!",
                                description=f"{ctx.author.name} is currently flexing..",
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
                asset_info = algod_client.asset_info(chosen_fallen)
                fallen_image_url = asset_info["params"]["url"]
                fallen_image = "https://ipfs.algonft.tools/ipfs/" + (fallen_image_url).replace("ipfs://", "")
                metadata_decoded = json.loads((base64.b64decode((data["transactions"][0]["note"]).encode('utf-8'))).decode('utf-8'))
                name = str(metadata_decoded.get("properties", {}).get("Name", "-"))
                ability_1 = str(metadata_decoded.get("properties", {}).get("Ability 1", "-"))
                ability_2 = str(metadata_decoded.get("properties", {}).get("Ability 2", "-"))
                ability_3 = str(metadata_decoded.get("properties", {}).get("Ability 3", "-"))
                ultimate = str(metadata_decoded.get("properties", {}).get("Ultimate", "-"))
                level_flex = str(metadata_decoded["properties"]["Level"])
                points_flex = str(metadata_decoded["properties"]["Points"])
                rank_flex = str(metadata_decoded["properties"]["Rank"])
                kinship_flex = str(metadata_decoded["properties"]["Kinship"])
                hitpoints_flex = str(metadata_decoded["properties"]["HP"])
                atk_flex = str(metadata_decoded["properties"]["ATK"])
                def_flex = str(metadata_decoded["properties"]["DEF"])
                ap_flex = str(metadata_decoded["properties"]["AP"])
                response1 = requests.get(fallen_image)
                image1 = Image.open(BytesIO(response1.content))
                text_color_list = [(250, 2, 130), (193, 0, 252), (5, 230, 250), (12, 245, 48), (247, 216, 10), (255, 83, 15), (255, 3, 3)]
                text_color = random.choice(text_color_list)
                transparent_image = Image.new('RGBA', (int(image1.width*2.5), image1.height), color=(0, 0, 0, 0))
                font = ImageFont.truetype("fonts/myfont.ttf", 170)
                fontSmall = ImageFont.truetype("fonts/myfont.ttf", 150)
                fontTiny = ImageFont.truetype("fonts/myfont.ttf", 140)
                # font = ImageFont.truetype("fonts/Orbitron-Regular.ttf", 170)
                # fontSmall = ImageFont.truetype("fonts/Orbitron-Regular.ttf", 150)
                # fontTiny = ImageFont.truetype("fonts/Orbitron-Regular.ttf", 130)
                transparent_image.paste(image1)
                response2 = requests.get("https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
                logo_image = Image.open(BytesIO(response2.content))
                logo_size = (600, 600)
                logo_image = logo_image.resize(logo_size)
                position = (transparent_image.width - logo_size[0] - 160, 80)
                transparent_image.paste(logo_image, position)
                draw = ImageDraw.Draw(transparent_image)
                text_height2 = 230
                text_x1 = text_x2 = text_x3 = text_x4 = text_x5 = text_x6 = text_x7 = text_x8 = 2200
                text_y1 = 240
                text_y2 = text_y1 + text_height2
                text_y3 = text_y2 + text_height2
                text_y4 = text_y3 + text_height2
                text_y5 = text_y4 + text_height2
                text_y6 = text_y5 + text_height2
                text_y7 = text_y6 + text_height2
                text_y8 = text_y7 + text_height2
                draw.text((text_x1, text_y1 - 140), name, font=font, fill=text_color, align='center')
                draw.text((text_x2, text_y2), "Level " + level_flex, font=fontTiny, fill=text_color, align='center')
                draw.text((text_x3, text_y3), kinship_flex + " Kinship", font=fontTiny, fill=text_color, align='center')
                draw.text((text_x4, text_y4), hitpoints_flex + " HP", font=fontTiny, fill=text_color, align='center')
                draw.text((text_x5, text_y5), atk_flex + " ATK | " + def_flex + " DEF | " + ap_flex + " AP", font=fontTiny, fill=text_color, align='center')
                draw.text((text_x6, text_y6), ability_1 + " | " + ability_2 + " | " + ability_3, font=fontTiny, fill=text_color, align='center')
                draw.text((text_x7, text_y7), ultimate, font=fontTiny, fill=text_color, align='center')
                draw.text((text_x8, text_y8), "Owner: " + ctx.author.name, font=fontTiny, fill=text_color, align='center')

                with BytesIO() as image_binary:
                    transparent_image.save(image_binary, 'PNG')
                    image_binary.seek(0)
                    try:
                        await ctx.send(file=discord.File(fp=image_binary, filename=f'{ctx.author.name}_flex.png'))
                    except discord.errors.HTTPException as e:
                        await ctx.send(embed=embedDiscordErr)
                        await asyncio.sleep(10)
                        await ctx.delete()
                        return
                return
            elif collection == "ghost":
                random_ghost = random.choice(ghost_assets)
                ghost_info = algod_client.asset_info(random_ghost)
                ghost_name = ghost_info["params"]["name"]
                ghost_image = "https://ipfs.algonft.tools/ipfs/" + (ghost_info["params"]["url"]).replace("ipfs://", "")
                embedFlex = discord.Embed(
                    title=f"{ghost_name} appears out of thin air! BOO! 👻",
                    description=f"[View Details](https://nftexplorer.app/asset/{random_ghost})",
                    color=discord.Color(random.randint(0, 0xFFFFFF))
                )
                embedFlex.set_footer(text=f"Owned By: {ctx.author.name} 🧙‍♂️")
                embedFlex.set_image(url=f"{ghost_image}")
                await ctx.send(embed=embedFlex)
                return
            
class KinshipFlexCog(commands.Cog):
    @cog_ext.cog_slash(name="kinship-flex", description="Flex Your Kinship!")
    async def kinship_flex(self, ctx):
        await ctx.defer()
        userid = str(ctx.author.id)
        wallet, name, won, lost, expwon, explost, lastdrip, drip_exp = await get_wallet(userid)
        account_info = algod_client.account_info(wallet)
        assets = account_info.get("assets", [])
        count = 0
        fallen_done = []
        total_kinship = 0
        for asset in assets:
            if asset["amount"] > 0 and asset['asset-id'] not in fallen_done and (asset["asset-id"] in fo_rank1 or asset["asset-id"] in fo_rank2 or asset["asset-id"] in fo_rank3 or asset["asset-id"] in fo_rank4 or asset["asset-id"] in fo_rank5):
                fallen_done.append(asset['asset-id'])        
        embedKinship = discord.Embed(
            title=f"Character Kinship - <@{ctx.author.id}>",
            color=0xFCE303,
        )
        for fallen in fallen_done:
            count += 1
            metadata_api = f"https://mainnet-idx.algonode.cloud/v2/transactions?tx-type=acfg&asset-id={fallen}&address={fallen_order_manager}"
            response = requests.get(metadata_api)
            if response.status_code == 200:
                data = response.json()
            else:
                print("Error fetching data from API")
            metadata_decoded = json.loads((base64.b64decode((data["transactions"][0]["note"]).encode('utf-8'))).decode('utf-8'))
            asset_info = algod_client.asset_info(fallen)
            fallen_name = metadata_decoded.get("properties", {}).get("Name", asset_info['params']['unit-name'])
            kinship = int(metadata_decoded["properties"]["Kinship"])
            total_kinship += kinship
            embedKinship.add_field(name=f"{fallen_name} - {kinship}", value=f"-", inline=False)
            if count % 10 == 0 and count != len(fallen_done):
                embedKinship.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
                await ctx.send(embed=embedKinship)
                embedKinship.clear_fields()
        embedKinship.set_footer(text=f"Total Characters: {len(fallen_done)}\nTotal Kinship: {total_kinship}")
        embedKinship.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        await ctx.send(embed=embedKinship)
            
def setup(client: client):
    client.add_cog(AdminRolesCog(client))
    client.add_cog(RolesCog(client))
    client.add_cog(HoldersCog(client))
    client.add_cog(FlexCog(client))
    client.add_cog(KinshipFlexCog(client))
