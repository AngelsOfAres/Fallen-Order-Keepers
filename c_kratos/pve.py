from discord_slash import cog_ext
from discord.ext import commands
import discord
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageOps
import random
from discord_slash.utils.manage_components import create_select, create_select_option, create_actionrow, create_button, wait_for_component
import json
from discord_slash.model import ButtonStyle
import base64
from discord_slash import ComponentContext
import asyncio
from client import client
from txns import algod_client, add_boss_battle, headersDG, graphql, get_bossbattles, send_assets, fallen_order_manager
from embeds import embedDiscordErr, embedAzazel, embedMordekai, embedWrongChannel
from whitelist import fo_rank1, fo_rank2, fo_rank3, fo_rank4, fo_rank5

class BossLeaderboardCog(commands.Cog):
    @cog_ext.cog_slash(name="boss-rankings", description="Check Boss Battle Rankings!", options=[
                {
                    "name": "count",
                    "description": "Rankings To Display",
                    "type": 4,
                    "required": True
                },
                {
                    "name": "sortby",
                    "description": "Sorting Method",
                    "type": 3,
                    "required": True,
                    "choices": [
                        {
                            "name": "Weekly",
                            "value": "weekly_battles"
                        },
                        {
                            "name": "All Time",
                            "value": "bossbattles"
                        }
                    ]
                }
            ])
    async def get_boss_leaderboard(self, ctx, count, sortby):
        getBossbattles = f"""
        query getBossbattles {{
            queryDiscordWallets(order: {{desc: {sortby}}}) {{
                address
                name
                bossbattles
                weekly_battles
            }}
        }}
        """
        request = requests.post(graphql, json={'query': getBossbattles}, headers=headersDG)
        result = request.json()

        counter = 0
        limit = count
        embedBossLeaderboard = discord.Embed(title='⚔️ Leaderboard - Boss Battles ⚔️', description='Those who have dared to take on the Fallen Order Bosses:\n\n*Weekly | All Time*', color=0xFFFB0A)
        embedBossLeaderboard.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")

        for field in result['data']['queryDiscordWallets']:
            if counter == limit:
                break
            if field['bossbattles'] == 0:
                continue
            else:
                if field['bossbattles'] == 1:
                    string = "Point"
                else:
                    string = "Points"
                embedBossLeaderboard.add_field(name=field['name'], value=f"{field['weekly_battles']} | {field['bossbattles']} {string}", inline=False)
            counter += 1

        await ctx.send(embed=embedBossLeaderboard)


class BossDetailsCog(commands.Cog):
    @cog_ext.cog_slash(name="bosses", description="View Boss Stats & Abilities Breakdown")
    async def boss_details(self, ctx):
        embedBossDetailsStep1 = discord.Embed(
                        title=f"The Fallen Order Bosses gather...",
                        color=0xFF0000
                    )
        select_options = [  create_select_option(label="Azazel", value="Azazel"),
                            create_select_option(label="Mordekai", value="Mordekai")
                        ]
        select = create_select(options=select_options, placeholder="Select the boss you want to view", min_values=1, max_values=1)
        action_row = create_actionrow(select)
        message = await ctx.send(embed=embedBossDetailsStep1, components=[action_row])
        try:
            while True:
                interaction: ComponentContext = await wait_for_component(client, components=action_row, timeout=20.0)
                interaction_author_id = interaction.author.id
                if interaction_author_id == ctx.author.id:
                    await interaction.defer(edit_origin=True)
                    chosen_boss = interaction.selected_options[0]
                    break
                else:
                    embedWrongUpgrade = discord.Embed(
                        title=f"This is not your boss selection!",
                        description=f"{ctx.author.name} is currently viewing bosses..",
                        color=0xFF0000
                    )
                    await interaction.send(embed=embedWrongUpgrade, hidden=True)
                    continue
        except asyncio.TimeoutError:
            embedTimeout = discord.Embed(
                    title=f"Woops! You took too long to respond...",
                    description=f"Ending {ctx.author.name}'s boss selection..",
                    color=0xFF0000
                )
            await message.edit(embed=embedTimeout, components=[])
            await asyncio.sleep(10)
            await message.delete()
            return
        
        if chosen_boss == "Azazel":
            await message.edit(embed=embedAzazel, components=[])
        elif chosen_boss == "Mordekai":
            await message.edit(embed=embedMordekai, components=[])
        return

async def player_ability(ability, player):
    rank = int(player[0])
    level = player[1]
    if level == 0:
        level_multiplier = 1
    else:
        level_multiplier = 1 + level*0.05
    kinship = player[2]
    if kinship == 0:
        kinship_multiplier = 1
    else:
        kinship_multiplier = 1 + kinship*0.0025
    attack = player[3]
    abilitypower = player[4]
    damage_multiplier = (1 + rank*0.1)*level_multiplier*kinship_multiplier

    if ability == "Slash":
        if attack != 0:
            damage = int(((attack)*random.uniform(0.8,1.5))*damage_multiplier)
        else:
            damage = 0
    elif ability == "Fury":
        if attack != 0:
            damage = int(((attack)*random.uniform(1,2))*damage_multiplier)
        else:
            damage = 0
    elif ability == "Fireball":
        if abilitypower != 0:
            damage = int(((abilitypower)*random.uniform(0.8,1.5))*damage_multiplier)
        else:
            damage = 0
    elif ability == "Arcane Nova":
        if abilitypower != 0:
            damage = int(((abilitypower)*random.uniform(1,2))*damage_multiplier)
        else:
            damage = 0
    elif ability == "Retribution":
        damage = 0
    elif ability == "Eclipse":
        if attack != 0 and abilitypower != 0:
            damage = int((((attack+abilitypower)/2)*random.uniform(1,2))*damage_multiplier)
        else:
            damage = 0
    elif ability == "Soul Surge":
        damage = int((((attack+abilitypower)/2)*random.uniform(2,3))*damage_multiplier)
    else:
        damage = 0
    if damage != 0:
        damage = int(damage)

    return damage

async def boss_ability(boss_name, defense):
    if defense == 0:
        damage_reduction = 1
    else:
        damage_reduction = (100 - defense/25)/100

    if boss_name == "Azazel":
        abilities = [
            {"name": "Smash", "damage": random.randint(800,1200), "effect": "none"},
            {"name": "Slap", "damage": random.randint(600,800), "effect": "none"},
            {"name": "Tail Whip", "damage": random.randint(500,1000), "effect": "none"},
            {"name": "Dark Barrier", "damage": 0, "effect": "block"},
            {"name": "Eruption", "damage": random.randint(500,1000), "effect": "fire"},
            {"name": "Hellfire", "damage": random.randint(800,2000), "effect": "none"},
            {"name": "Tranquility", "damage": random.randint(500,2000), "effect": "heal"}
        ]
        chosen_ability = random.choice(abilities)
    elif boss_name == "Mordekai":
        abilities = [
            {"name": "Ghastly Vengeance", "damage": random.randint(1000,1200), "effect": "none"},
            {"name": "Ghost Army", "damage": random.randint(700,900), "effect": "none"},
            {"name": "Spirit Bomb", "damage": random.randint(800,1200), "effect": "none"},
            {"name": "Shadow Barrier", "damage": 0, "effect": "block"},
            {"name": "Abyssal Curse", "damage": random.randint(600,1000), "effect": "fire"},
            {"name": "Tremble", "damage": random.randint(600,2000), "effect": "none"},
            {"name": "Call Of The Undead", "damage": random.randint(1000,2000), "effect": "heal"}
        ]
        chosen_ability = random.choice(abilities)

    boss_data = [chosen_ability["name"], int(chosen_ability["damage"]*damage_reduction), chosen_ability["effect"]]
    return boss_data


class BossBattleCog(commands.Cog):
    @cog_ext.cog_slash(name="boss-battle", description="Battle Against A Boss!", options=[
                {
                    "name": "boss",
                    "description": "Select Boss To Battle!",
                    "type": 3,
                    "required": True,
                    "choices": [
                        {
                            "name": "Azazel",
                            "value": "Azazel"
                        },
                        {
                            "name": "Mordekai",
                            "value": "Mordekai"
                        }
                    ]
                }
            ])
    @commands.cooldown(1, 60, commands.BucketType.guild)
    async def boss_battle(self, ctx, boss):
        if ctx.channel.id != 1090380447776780308:
            await ctx.send(embed=embedWrongChannel, hidden=True)
            return
        userid = str(ctx.author.id)
        user_data = await get_bossbattles(userid)
        wallet = user_data[0]
        username = user_data[1]
        user_battle_count = int(user_data[2])
        user_weekly_battle_count = int(user_data[3])
        if wallet == '':
            embedNoReg = discord.Embed(
                title="Click Here To Register!",
                url="https://app.fallenorder.xyz",
                description=f"Please verify your wallet via our website to continue..\nEnsure you copy your user id below for the verification process:\nUser ID: {ctx.author.id}",
                color=0xFF1C0A,
            )
            await message.edit(embed=embedNoReg)
            return
        embedBattleInProgress = discord.Embed(
                title=f"⚔️ Initiating Boss Battle ⚔️",
                description=f"{ctx.author.name} gathers their Fallen Order to prepare for a boss battle...",
                color=0xFCE303
            )
        embedBattleInProgress.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        message = await ctx.send(embed=embedBattleInProgress)
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
        select = create_select(options=select_options, placeholder="Select the character you want to battle", min_values=1, max_values=1)
        action_row = create_actionrow(select)
        await message.edit(embed=embedBattleInProgress, components=[action_row])
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
                        title=f"This is not your boss battle!",
                        description=f"{ctx.author.name} is currently battling..",
                        color=0xFF0000
                    )
                    await interaction.send(embed=embedWrongUpgrade, hidden=True)
                    continue
        except asyncio.TimeoutError:
            embedTimeout = discord.Embed(
                    title=f"Woops! You took too long to respond...",
                    description=f"Ending {ctx.author.name}'s boss battle..",
                    color=0xFF0000
                )
            await message.edit(embed=embedTimeout, components=[])
            await asyncio.sleep(10)
            await message.delete()
            return
            
        embedBattleInProgress = discord.Embed(
            title=f"⚔️ Initiating Boss Battle ⚔️",
            description=f"Prepare yourself {ctx.author.name}! Azazel awakens and steps out of his lair...",
            color=0xFCE303
        )
        await message.edit(embed=embedBattleInProgress, components=[])
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
        level = int(metadata_decoded["properties"]["Level"])
        rank = int(metadata_decoded["properties"]["Rank"])
        kinship = int(metadata_decoded["properties"]["Kinship"])
        hitpoints = int(metadata_decoded["properties"]["HP"])
        attack = int(metadata_decoded["properties"]["ATK"])
        defense = int(metadata_decoded["properties"]["DEF"])
        abilitypower = int(metadata_decoded["properties"]["AP"])
        basic_1 = metadata_decoded.get("properties", {}).get("Ability 1", "None")
        basic_2 = metadata_decoded.get("properties", {}).get("Ability 2", "None")
        basic_3 = metadata_decoded.get("properties", {}).get("Ability 3", "None")
        ultimate = metadata_decoded.get("properties", {}).get("Ultimate", "None")
        # basic_1 = "Slash"
        # basic_2 = "Retribution"
        # basic_3 = "Eclipse"
        # ultimate = "Molten Rage"
        if basic_1 == "None" or basic_2 == "None" or basic_3 == "None" or ultimate == "None":
            embedNoAbilities = discord.Embed(
                    title=f"<@{ctx.author.id}>'s character is missing abilities!",
                    description=f"Character: {fallen_name}\n\nPlease assign all 3 basic abilities and ultimate to battle...",
                    color=0xFF0000
                )
            embedNoAbilities.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
            embedNoAbilities.set_footer(text=f"To add abilities use /swap-ability")
            await message.edit(embed=embedNoAbilities, components=[])
            return
        response1 = requests.get(fallen_image)
        image1 = Image.open(BytesIO(response1.content))
        size = (image1.width, image1.height)
        if boss == "Azazel":
            boss_hp = 10000
            boss_max = 10000
            boss_name = "Azazel, the Prince Of Hell"
            boss_name_short = "Azazel"
            boss_name_end = "Prince Of Hell"
            points = 1
            block_name = "Dark Barrier"
            fire_name = "Eruption"
            fire_damage_name = "FIRE"
            fire_string_1 = "set on FIRE"
            boss_fire_damage_1 = 300
            boss_fire_damage_2 = 600
            boss_rounds = 20
            response2 = requests.get("https://i.ibb.co/5WCwkwN/Azazel.png")
            image2 = Image.open(BytesIO(response2.content))
            image2 = image2.resize(size)
        elif boss == "Mordekai":
            boss_hp = 12000
            boss_max = 12000
            boss_name = "Mordekai, Master Of Gheists"
            boss_name_short = "Mordekai"
            boss_name_end = "Master Of Gheists"
            points = 2
            fire_name = "Abyssal Curse"
            fire_damage_name = "CURSE"
            fire_string_1 = "CURSED"
            boss_fire_damage_1 = 500
            boss_fire_damage_2 = 800
            boss_rounds = 16
            block_name = "Shadow Barrier"
            response2 = requests.get("https://i.ibb.co/Ry4VqBW/mordekai.jpg")
            image2 = Image.open(BytesIO(response2.content))
            image2 = image2.resize(size)
        padding = 600
        text_color_list = [(255, 38, 150), (204, 38, 255), (38, 237, 255), (38, 255, 71), (255, 226, 38), (255, 99, 38)]
        text_color = random.choice(text_color_list)
        transparent_image = Image.new('RGBA', (image1.width + image2.width + padding, max(image1.height + 500, image2.height + 500)), color=(0, 0, 0, 0))
        transparent_image.paste(image1, (0, 0))
        transparent_image.paste(ImageOps.mirror(image2), (image1.width + padding, 0))
        font = ImageFont.truetype("fonts/myfont.ttf", 170)
        fontSmall = ImageFont.truetype("fonts/myfont.ttf", 150)
        # font = ImageFont.truetype("fonts/Orbitron-Regular.ttf", 170)
        # fontSmall = ImageFont.truetype("fonts/Orbitron-Regular.ttf", 150)
        draw = ImageDraw.Draw(transparent_image)
        text_width = font.getlength("VS")
        text_x = int(((image1.width + image2.width + padding) - text_width) / 2)
        text_y = int(((max(image1.height, image2.height)) - text_width) / 2)
        draw.text((text_x, text_y), "VS", font=font, fill=text_color)
        text_width1 = fontSmall.getlength(str(ctx.author.name))
        text_width2 = fontSmall.getlength(boss_name_short)
        text_width3 = fontSmall.getlength(fallen_name)
        text_width4 = fontSmall.getlength(boss_name_end)
        text_padding = 40
        text_x1 = int((image1.width - text_width1) / 2)
        text_x2 = int((image2.width - text_width2) / 2) + image1.width + padding
        text_y1 = int((max(image1.height, image2.height)) + text_padding)
        text_y2 = int((max(image1.height, image2.height)) + text_padding)
        text_x3 = int((image1.width - text_width3) / 2)
        text_x4 = int((image2.width - text_width4) / 2) + image1.width + padding
        text_y3 = int((max(image1.height, image2.height)) + text_padding + text_padding*6)
        text_y4 = int((max(image1.height, image2.height)) + text_padding + text_padding*6)
        draw = ImageDraw.Draw(transparent_image)
        draw.text((text_x1, text_y1), str(ctx.author.name), font=fontSmall, fill=text_color)
        draw.text((text_x2, text_y2), boss_name_short, font=fontSmall, fill=text_color)
        draw.text((text_x3, text_y3), fallen_name, font=fontSmall, fill=text_color)
        draw.text((text_x4, text_y4), boss_name_end, font=fontSmall, fill=text_color)
        with BytesIO() as image_binary:
            transparent_image.save(image_binary, 'PNG')
            image_binary.seek(0)
            try:
                await message.edit(file=discord.File(fp=image_binary, filename=f'{ctx.author.name}_boss_battle.png'), embed=embedBattleInProgress)
            except discord.errors.HTTPException as e:
                await message.edit(embed=embedDiscordErr, components=[])
                await asyncio.sleep(10)
                await message.delete()
                return
        player_data = [rank, level, kinship, attack, defense, abilitypower]
        embedBattleOn = discord.Embed(
                    title=f"⚔️ PREPARE FOR BATTLE ⚔️",
                    description=f"<@{ctx.author.id}> VS {boss_name}",
                    color=0xFF0000
                )
        embedBattleOn.set_footer(text=f"Battle will commence in 5 seconds...⏳")
        await message.edit(embed=embedBattleOn, components=[])
        await asyncio.sleep(5)
        ultimate_on = False
        basic1_button = create_button(style=ButtonStyle.blurple, label=basic_1, custom_id=basic_1)
        basic2_button = create_button(style=ButtonStyle.blurple, label=basic_2, custom_id=basic_2)
        basic3_button = create_button(style=ButtonStyle.blurple, label=basic_3, custom_id=basic_3)
        ultimate_button = create_button(style=ButtonStyle.red, label=ultimate, custom_id=ultimate)
        action_row = create_actionrow(basic1_button, basic2_button, basic3_button, ultimate_button)
        round = 1
        embedBattleCommenced = discord.Embed(
                title=f"⚔️ BATTLE IS ON! ⚔️",
                description=f"<@{ctx.author.id}> VS {boss_name}\n\nATK | DEF | AP: {attack} | {defense} | {abilitypower}",
                color=0xFF0000
            )
        embedBattleCommenced.add_field(name=f"{ctx.author.name}'s move!", value=f"Choosing ability...", inline=False)
        mirage_on = False
        mirage_count = 0
        pestilence_on = False
        pestilence_count = 0
        molten_rage_on = False
        molten_rage_count = 0
        boss_fire_on = False
        boss_fire_count = 0
        boss_block_on = False
        boss_block_count = 0
        ultimate_on = True
        ultimate_cd = 0
        while hitpoints > 0 and boss_hp > 0:
            if round == 1:
                if basic_1 == "Purify":
                    basic1_button["disabled"] = True
                elif basic_2 == "Purify":
                    basic2_button["disabled"] = True
                elif basic_3 == "Purify":
                    basic3_button["disabled"] = True
            if boss_block_on or boss_fire_on:
                if boss_block_on:
                    description_block = f"\n{block_name}: {2-boss_block_count}"
                    if boss_block_count >= 2:
                        boss_block_on = False
                        boss_block_count = 0
                        description_block = ""
                else:
                    description_block = ""
                if boss_fire_on:
                    description_fire = f"\n{fire_name}: {3-boss_fire_count}"
                    if boss_fire_count >= 3:
                        boss_fire_on = False
                        boss_fire_count = 0
                        description_fire = ""
                else:
                    description_fire = ""
                embedBattleCommenced.description=f"<@{ctx.author.id}> VS {boss_name}\n\nATK | DEF | AP: {attack} | {defense} | {abilitypower}\n\nRound {round}\n{description_block}{description_fire}"
            else:
                embedBattleCommenced.description = f"<@{ctx.author.id}> VS {boss_name}\n\nATK | DEF | AP: {attack} | {defense} | {abilitypower}\n\nRound {round}"
            embedBattleCommenced.set_footer(text=f"{ctx.author.name}: {hitpoints} HP | {boss_name_short} HP: {boss_hp}")
            if not ultimate_on:
                ultimate_cd += 1
                ultimate_button["disabled"] = True
            else:
                ultimate_button["disabled"] = False
            await message.edit(embed=embedBattleCommenced, components=[action_row])
            try:
                interaction: ComponentContext = await wait_for_component(client, components=action_row, timeout=30.0)
                interaction_author_id = interaction.author.id
                if interaction_author_id == ctx.author.id:
                    await interaction.defer(edit_origin=True)
                    action = interaction.custom_id
                    if action == basic_1:
                        basic1_button["disabled"] = True
                        basic2_button["disabled"] = False
                        basic3_button["disabled"] = False
                    if action == basic_2:
                        basic2_button["disabled"] = True
                        basic1_button["disabled"] = False
                        basic3_button["disabled"] = False
                    if action == basic_3:
                        basic3_button["disabled"] = True
                        basic1_button["disabled"] = False
                        basic2_button["disabled"] = False
                    await message.edit(components=[action_row])
                    if action == "Death Blow" or action == "Mirage" or action == "Pestilence" or action == "Divine Aura" or action == "Molten Rage":
                        ultimate_button["disabled"] = True
                        basic3_button["disabled"] = False
                        basic1_button["disabled"] = False
                        basic2_button["disabled"] = False
                        await message.edit(components=[action_row])
                    if action == "Death Blow":
                        ultimate_on = False
                        ultimate_cd = 0
                        if random.random() <= 0.333:
                            damage = 2500
                            boss_hp -= damage
                            if random.random() <= 0.5:
                                hitpoints -= 500
                                embedBattleCommenced.set_field_at(0, name=f"{ctx.author.name} uses {action}!", value=f"IT LANDS 2500 DAMAGE! 💀\n250 self-damage caused!", inline=False)
                            else:
                                embedBattleCommenced.set_field_at(0, name=f"{ctx.author.name} uses {action}!", value=f"IT LANDS 2500 DAMAGE! 💀\nNo self-damage caused!", inline=False)
                        else:
                            if random.random() <= 0.5:
                                hitpoints -= 500
                                embedBattleCommenced.set_field_at(0, name=f"{ctx.author.name} uses {action}!", value=f"Death Blow missed!\n250 self-damage caused!", inline=False)
                            else:
                                embedBattleCommenced.set_field_at(0, name=f"{ctx.author.name} uses {action}!", value=f"Death Blow missed!\nNo self-damage caused!", inline=False)
                    elif action == "Divine Aura":
                        ultimate_on = False
                        ultimate_cd = 0
                        heal_amount = random.randint(500,3000)
                        hitpoints += heal_amount
                        hitpoints = min(hitpoints, int(metadata_decoded["properties"]["HP"]))
                        embedBattleCommenced.set_field_at(0, name=f"{ctx.author.name} uses {action}!", value=f"{heal_amount} HP restored!", inline=False)
                    elif action == "Mirage":
                        ultimate_on = False
                        ultimate_cd = 0
                        mirage_on = True
                        mirage_count = 0
                        embedBattleCommenced.set_field_at(0, name=f"{ctx.author.name} uses {action}!", value=f"Next 2 rounds will be blocked!", inline=False)
                    elif action == "Pestilence":
                        ultimate_on = False
                        ultimate_cd = 0
                        pestilence_on = True
                        pestilence_count = 0
                        embedBattleCommenced.set_field_at(0, name=f"{ctx.author.name} uses {action}!", value=f"{boss_name_short} has been poisoned!", inline=False)
                    elif action == "Molten Rage":
                        ultimate_on = False
                        ultimate_cd = 0
                        molten_rage_on = True
                        molten_rage_count = 0
                        embedBattleCommenced.set_field_at(0, name=f"{ctx.author.name} uses {action}!", value=f"They are ENRAGED for the next 2 rounds!", inline=False)
                    else:
                        if not ultimate_on:
                            if ultimate_cd == 5:
                                ultimate_on = True
                                ultimate_button["disabled"] = False
                                ultimate_cd = 0
                        if action == "Purify":
                            if boss_block_on or boss_fire_on:
                                if boss_block_on:
                                    boss_block_count += 1
                                    description_block = f"\n{block_name}: {2-boss_block_count}"
                                    if boss_block_count >= 2:
                                        boss_block_on = False
                                        boss_block_count = 0
                                        description_block = ""
                                else:
                                    description_block = ""
                                if boss_fire_on:
                                    boss_fire_count += 1
                                    description_fire = f"\n{fire_name}: {3-boss_fire_count}"
                                    if boss_fire_count >= 3:
                                        boss_fire_on = False
                                        boss_fire_count = 0
                                        description_fire = ""
                                else:
                                    description_fire = ""
                                embedBattleCommenced.description=f"<@{ctx.author.id}> VS {boss_name}\n\nATK | DEF | AP: {attack} | {defense} | {abilitypower}\n\nRound {round}\n{description_block}{description_fire}"
                            else:
                                embedBattleCommenced.description = f"<@{ctx.author.id}> VS {boss_name}\n\nATK | DEF | AP: {attack} | {defense} | {abilitypower}\n\nRound {round}"                                
                            if boss_fire_on:
                                fire_damage = random.randint(boss_fire_damage_1, boss_fire_damage_2)
                                hitpoints -= fire_damage
                                fire_string = f"\n{fire_damage} {fire_damage_name} Damage Taken!"
                            else:
                                fire_string = ""
                            embedBattleCommenced.set_field_at(0, name=f"{ctx.author.name} uses {action}! {string}", value=f"All negative effects have been reduced by 1!{fire_string}", inline=False)
                        else:
                            if boss_fire_on:
                                fire_damage = random.randint(boss_fire_damage_1, boss_fire_damage_2)
                                hitpoints -= fire_damage
                                fire_string = f"\n{fire_damage} {fire_damage_name} Damage Taken!"
                            else:
                                fire_string = ""
                            if action == "Retribution":
                                if defense != 0:
                                    retribution_amount = int(defense*random.uniform(0.75,2))
                                else:
                                    retribution_amount = 0
                                hitpoints += retribution_amount
                                hitpoints = min(hitpoints, int(metadata_decoded["properties"]["HP"]))
                                embedBattleCommenced.set_field_at(0, name=f"{ctx.author.name} uses {action}!", value=f"{retribution_amount} HP restored by {ctx.author.name}!{fire_string}", inline=False)
                            else:
                                if boss_block_on:
                                    damage = 0
                                    embedBattleCommenced.set_field_at(0, name=f"{ctx.author.name} uses {action}!", value=f"It is ineffective against {block_name}!{fire_string}", inline=False)
                                else:
                                    if action == "Soul Surge":
                                        surge_damage = random.randint(100,300)
                                        hitpoints -= surge_damage
                                        hitpoints = max(hitpoints, 0)
                                        surge_string = f"\n{surge_damage} self-inflicted Surge damage!"
                                    else:
                                        surge_string = ""
                                    string = ""
                                    if molten_rage_on:
                                        if attack != 0:
                                            boosted_atk = int(attack*1.2)
                                        else:
                                            boosted_atk = 0
                                        if abilitypower != 0:
                                            boosted_ap = int(abilitypower*1.2)
                                        else:
                                            boosted_ap = 0
                                        player_data = [rank, level, kinship, boosted_atk, boosted_ap]
                                        string = "*ENRAGED*"
                                        if molten_rage_count >= 2:
                                            molten_rage_on = False
                                            molten_rage_count = 0
                                    else:
                                        player_data = [rank, level, kinship, int(attack), int(abilitypower)]
                                    damage = await player_ability(action, player_data)
                                    embedBattleCommenced.set_field_at(0, name=f"{ctx.author.name} uses {action}! {string}", value=f"{damage} damage dealt to {boss_name_short}!{surge_string}{fire_string}", inline=False)
                                    boss_hp -= damage
                    embedBattleCommenced.set_footer(text=f"{ctx.author.name}: {hitpoints} HP | {boss_name_short} HP: {boss_hp}")
                    if boss_block_on or boss_fire_on:
                        if boss_block_on:
                            boss_block_count += 1
                            description_block = f"\n{block_name}: {2-boss_block_count}"
                            if boss_block_count >= 2:
                                boss_block_on = False
                                boss_block_count = 0
                                description_block = ""
                        else:
                            description_block = ""
                        if boss_fire_on:
                            boss_fire_count += 1
                            description_fire = f"\n{fire_name}: {3-boss_fire_count}"
                            if boss_fire_count >= 3:
                                boss_fire_on = False
                                boss_fire_count = 0
                                description_fire = ""
                        else:
                            description_fire = ""
                        embedBattleCommenced.description=f"<@{ctx.author.id}> VS {boss_name}\n\nATK | DEF | AP: {attack} | {defense} | {abilitypower}\n\nRound {round}\n{description_block}{description_fire}"
                    else:
                        embedBattleCommenced.description = f"<@{ctx.author.id}> VS {boss_name}\n\nATK | DEF | AP: {attack} | {defense} | {abilitypower}\n\nRound {round}"
                    if molten_rage_on:
                        molten_rage_count += 1
                    if pestilence_on:
                        pestilence_count += 1
                    if mirage_on:
                        mirage_count += 1
                    await message.edit(embed=embedBattleCommenced)
                    if boss_hp <= 0:
                        boss_hp = 0
                        break
                    boss_data = await boss_ability(boss_name_short, defense)
                    await asyncio.sleep(2)
                    damage = boss_data[1]
                    effect = boss_data[2]
                    if pestilence_on:
                        pestilence_damage = random.randint(100,300)
                        if pestilence_count >= 3:
                            pestilence_on = False
                            pestilence_count = 0
                        string_pestilence = f"\n{pestilence_damage} poison damage taken by {boss_name_short}!"
                    else:
                        string_pestilence = ""
                    if effect == "fire":
                        boss_fire_on = True
                        boss_fire_count = 0
                        string_fire = f"\n{ctx.author.name} has been {fire_string_1} for 3 rounds!{string_pestilence}"
                    else:
                        string_fire = ""
                    if mirage_on:
                        damage = 0
                        string_fire = ""
                        string_mirage = f"\nIt is ineffective against {ctx.author.name}'s Mirage!"
                        if mirage_count >= 2:
                            mirage_on = False
                            mirage_count = 0
                    else:
                        string_mirage = ""
                    if effect == "heal":
                        boss_hp += boss_data[1]
                        boss_hp = min(boss_hp, boss_max)
                        embedBattleCommenced.set_field_at(0, name=f"{boss_name_short} uses {boss_data[0]}!", value=f"{boss_data[1]} HP restored by {boss_name_short}!{string_pestilence}", inline=False)
                    else:
                        if effect == "block":
                            boss_block_on = True
                            boss_block_count = 0
                            string_block = f"\n{ctx.author.name}'s next 2 attacks will be blocked!{string_pestilence}"
                            value_block = f"{string_block}{string_mirage}{string_fire}"
                        else:
                            string_block = ""
                            if string_mirage == "":
                                value_block = f"{damage} {boss_name_short} damage dealt to {ctx.author.name}!{string_block}{string_mirage}{string_fire}"
                            else:
                                value_block = f"{string_block}{string_mirage}{string_fire}"
                        hitpoints -= damage
                        embedBattleCommenced.set_field_at(0, name=f"{boss_name_short} uses {boss_data[0]}!", value=value_block, inline=False)
                    embedBattleCommenced.set_footer(text=f"{ctx.author.name}: {hitpoints} HP | {boss_name_short} HP: {boss_hp}")
                    if hitpoints <= 0:
                        hitpoints = 0
                        embedBossWin = discord.Embed(
                            title=f"⚔️ {boss_name_short} Wins The Battle ⚔️",
                            description=f"A glorious battle from {ctx.author.name} and their Fallen Order - {fallen_name}\n\nYou made it to round {round}!",
                            color=0xFF0000
                        )
                        embedBossWin.set_footer(text="Try leveling up, boosting your stats, upgrading your kinship, and most importantly match your character's abilities to its stats!")
                        embedBossWin.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
                        await message.edit(embed=embedBossWin, components=[])
                        return
                    await message.edit(embed=embedBattleCommenced)
                    await asyncio.sleep(1)
                    if round >= boss_rounds:
                        embedMaxRounds = discord.Embed(
                            title=f"⚔️ {boss_name_short} Activates His Ultimate ⚔️",
                            description=f"KAAAAAA MEEEEEEEE HAAAAAAAAA MEEEEEEEEE......",
                            color=0xFF0000
                        )
                        await message.edit(embed=embedMaxRounds, components=[])
                        await asyncio.sleep(5)
                        embedMaxRounds.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
                        embedMaxRounds.add_field(name=f"HAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAA\nAAAAAAAAAAAAAAAAAAAAAAAAAAA", value=f"💀 {ctx.author.name} was INSTA KILLED! 💀", inline=False)
                        await message.edit(embed=embedMaxRounds, components=[])
                        return
                    round += 1
                else:
                    embedWrongGame = discord.Embed(
                        title=f"This is not your boss battle!",
                        description=f"{ctx.author.name} is currently fighting...",
                        color=0xFF0000
                    )
                    await interaction.send(embed=embedWrongGame, hidden=True)
            except asyncio.TimeoutError:
                embedTimeout = discord.Embed(
                        title=f"Woops! You took too long to respond...",
                        description=f"Ending <@{ctx.author.id}>'s battle..",
                        color=0xFF0000
                    )
                await message.edit(embed=embedTimeout, components=[])
                await asyncio.sleep(10)
                await message.delete()
                return
        embedGameOver = discord.Embed(
                title=f"What a battle! <@{ctx.author.id}> WON!",
                description=f"\n\nATK | DEF | AP: {attack} | {defense} | {abilitypower}\n\n{boss_name_short} has been defeated...",
                color=0x28FF0A
            )
        embedGameOver.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        embedGameOver.set_footer(text=f"{ctx.author.name}: {hitpoints} HP | {boss_name_short}: {boss_hp}\n\nYou earned {points} Point!\n\n{ctx.author.name}'s Weekly Points: {user_weekly_battle_count+int(points)} | Total: {user_battle_count+int(points)}")
        await message.edit(embed=embedGameOver, components=[])
        await add_boss_battle(str(wallet), user_weekly_battle_count+int(points), user_battle_count+int(points))

    @boss_battle.error
    async def boss_battle_error(self, ctx, error):
        embedNotAllowed = discord.Embed(
                    title=f"There is a boss battle in progress!",
                    color=0xFF0000
                )
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(embed=embedNotAllowed, hidden=True)


def setup(client: client):
    client.add_cog(BossLeaderboardCog(client))
    client.add_cog(BossBattleCog(client))
    client.add_cog(BossDetailsCog(client))