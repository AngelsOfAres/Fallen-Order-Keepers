import discord
import requests
from io import BytesIO
from PIL import Image
import random
from discord_slash.utils.manage_components import create_actionrow, create_button, wait_for_component
import json
from discord_slash.model import ButtonStyle
from io import BytesIO
from PIL import Image
import base64
from discord_slash import ComponentContext
import asyncio
from client import client
from txns import algod_client, send_assets, fallen_order_main, fallen_order_manager, get_main_char, get_balance
from embeds import embedNoOptEXP, embedDiscordErr
from c_kratos.pve import boss_ability, player_ability

ac2_id = 1070260390
ac2_image = "https://ipfs.algonft.tools/ipfs/bafybeieboghre54lmneqaizttmprz2vxb2uvzbwsnqfmjzajqolx7niamy#i"
quest_name = "The Summoning"
button_colors = [ButtonStyle.blurple, ButtonStyle.blue, ButtonStyle.danger, ButtonStyle.green, ButtonStyle.red, ButtonStyle.grey, ButtonStyle.success, ButtonStyle.primary, ButtonStyle.secondary]
random_string_ghiest_battle = ["We can't stop! Keep fighting!", "Be careful they're surrounding us from every corner!", "I'm so not in shape for this shit...", "I just wanted to get some Kinship holy shit...", "COME AT ME GHIESTS LFG!", "Let's whoop their asses!!"]

async def quest_the_summoning(ctx):
    await ctx.defer()
    userid = ctx.author.id
    username = ctx.author.name
    embedMissingReq = discord.Embed(
            title=f"🏺 Quest Requirements 🏺",
            description=f"Main Character with the following stats:\n\nCharacter Name Set\nLevel 1+\n10+ Kinship\nAbilities + Ultimate Set\nBattle Stats Allocated",
            color=0xFCE303
        )
    embedMissingReq.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
    embedMissingReq.set_footer(text=f"To name your character use /rename\nTo level up your character use /levelup\nTo gain kinship use /kinship or /use-kinship-potion\nTo allocate your battle stats use /boost\nTo add abilities use /swap-ability")
    wallet, main_character, equipped_hatchet = await get_main_char(str(userid))
    if wallet == '':
        embedNoReg = discord.Embed(
            title="Click Here To Register!",
            url="https://app.fallenorder.xyz",
            description=f"Please verify your wallet via our website to continue..\nEnsure you copy your user id below for the verification process:\nUser ID: {userid}",
            color=0xFF1C0A,
        )
        await ctx.send(embed=embedNoReg)
        return
    balance_ac2 = await get_balance(wallet, ac2_id)
    balance_exp = await get_balance(wallet, 811721471)
    balance_boost = await get_balance(wallet, 815771120)
    if balance_ac2 == -1:
        embedAchievement = discord.Embed(
            title=f"You must first opt in to the Achievement for this quest!",
            description=f"Try /quest again to complete the quest once you have opted in...\n\n[Click Here To Opt In!](https://www.randgallery.com/algo-collection/?address={ac2_id})",
            color=0xFF0000
        )
        await ctx.send(embed=embedAchievement)
        return
    if balance_exp == -1:
        await ctx.send(embed=embedNoOptEXP)
        return
    if balance_boost == -1:
        embedNoOptBoost = discord.Embed(title=f"Woops! You must first opt into Stat Booster to receive it after your quest!", description=f"[Click Here To Opt In...](https://www.randgallery.com/algo-collection/?address=815771120)", color=0xFF0000)
        embedNoOptBoost.set_image(url="https://nft-media.algoexplorerapi.io/images/bafybeibdnf2qn7a3w5ckxecv4svykpntufjkqh2zank6kx6mn2idik2nz4")
        await ctx.send(embed=embedNoOptBoost)
        return
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
    fallen_name = metadata_decoded.get("properties", {}).get("Name", "No Name")
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
    if level < 1 or kinship < 10 or  basic_1 == "None" or basic_2 == "None" or basic_3 == "None" or ultimate == "None":
        await ctx.send(embed=embedMissingReq)
        return
    response1 = requests.get(fallen_image)
    image1 = Image.open(BytesIO(response1.content))
    size = (image1.width, image1.height)
    response2 = requests.get("https://i.ibb.co/SXgHkqZ/IMG-20230326-182252.jpg")
    image2 = Image.open(BytesIO(response2.content))
    image2 = image2.resize(size)
    response3 = requests.get("https://i.ibb.co/Ry4VqBW/mordekai.jpg")
    image3 = Image.open(BytesIO(response3.content))
    image3 = image3.resize(size)
    transparent_image = Image.new('RGBA', (image1.width + image2.width, max(image1.height, image2.height)), color=(0, 0, 0, 0))
    transparent_image.paste(image1, (0, 0))
    transparent_image.paste(image2, (image1.width, 0))
    transparent_image2 = Image.new('RGBA', (image1.width + image2.width, max(image1.height, image2.height)), color=(0, 0, 0, 0))
    transparent_image2.paste(image1, (0, 0))
    transparent_image2.paste(image3, (image1.width, 0))
    embedTutorial1 = discord.Embed(
                title=f"🧙 Quest - {quest_name} 🧙‍♀️",
                description=f"*Welcome <@{userid}>*\n\n*I see you brought {fallen_name} along with you...*\n\n*Are you both ready for {quest_name}?*",
                color=0xFCE303
            )
    embedTutorial1.set_footer(text=f"Press Continue when ready!")
    button1 = create_button(style=ButtonStyle.blurple, label="Continue", custom_id="continue")
    button2 = create_button(style=ButtonStyle.red, label="Cancel", custom_id="cancel")
    action_row = create_actionrow(button1, button2)
    message = await ctx.send(embed=embedTutorial1, components=[action_row])
    while True:
        try:
            interaction: ComponentContext = await wait_for_component(client, components=action_row, timeout=60.0)
            interaction_author_id = interaction.author.id
            if interaction_author_id == userid:
                await interaction.defer(edit_origin=True)
                action = interaction.custom_id
                if action == "cancel":
                    await message.delete()
                    await asyncio.sleep(1)
                    return
                elif action == 'continue':
                    embedTutorial2 = discord.Embed(
                                title=f"🧙 Phase 1 - {quest_name} 🧙‍♀️",
                                description=f"*As you and {fallen_name} enter the Temple, you feel the familiar sense of peace and tranquility wash over you. You walk towards the Altar to do your daily Kinship ritual...*",
                                color=0xFCE303
                            )
                    embedTutorial2.set_thumbnail(url=fallen_image)
                    await message.edit(embed=embedTutorial2, components=[])
                    await asyncio.sleep(5)
                    embedTutorial2.description = f"*As you and {fallen_name} enter the Temple, you feel the familiar sense of peace and tranquility wash over you. You walk towards the Altar to do your daily Kinship ritual...\n\n{fallen_name} says: Master {username}, something's wrong. I feel a sudden chill in the air we might be in trouble.*"
                    await message.edit(embed=embedTutorial2, components=[])
                    await asyncio.sleep(5)
                    embedTutorial2.description = f"*{username} and {fallen_name} walk into the Temple to do their daily Kinship ritual...\n\n{fallen_name} says: Master {username}, something's wrong. I feel a sudden chill in the air we might be in trouble.\n\nSuddenly, a group of Ghiests materialize out of thin air and surround you and your character. {fallen_name} draws their weapon and prepares for battle!*"
                    await message.edit(embed=embedTutorial2)
                    button1 = create_button(style=ButtonStyle.blurple, label="DEFEND THE TEMPLE!", custom_id="continue")
                    button2 = create_button(style=ButtonStyle.red, label="RUN AWAY!", custom_id="cancel")
                    action_row = create_actionrow(button1, button2)
                    await message.edit(embed=embedTutorial2, components=[])
                    await asyncio.sleep(5)
                    await message.edit(embed=embedTutorial2, components=[action_row])
                break
            else:
                embedWrongUpgrade = discord.Embed(
                    title=f"This is not your tutorial!",
                    color=0xFF0000
                )
                await interaction.send(embed=embedWrongUpgrade, hidden=True)
                continue
        except asyncio.TimeoutError:
            embedTimeout = discord.Embed(
                    title=f"Woops! You took too long to respond...",
                    description=f"Ending {username}'s quest..",
                    color=0xFF0000
                )
            await message.edit(embed=embedTimeout, components=[])
            await asyncio.sleep(10)
            await message.delete()
            return
    while True:
        try:
            interaction: ComponentContext = await wait_for_component(client, components=action_row, timeout=120.0)
            interaction_author_id = interaction.author.id
            if interaction_author_id == userid:
                await interaction.defer(edit_origin=True)
                action = interaction.custom_id
                if action =="cancel":
                    await message.delete()
                    return
                elif action == "continue":
                    embedGhiestPreBattle = discord.Embed(
                            title=f"👻 GHIEST BATTLE STARTING! 👻",
                            description=f"*A group of Spirits assemble to assist you in battle!\n(or are really just in the way..?)\n\nYou must strike down all of the Ghosts but not harm a single Spirit!\n\nThe Ghiests charge at you, they will reach you in 5 seconds!*",
                            color=0xFFFFFF
                        )
                    embedGhiestPreBattle.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
                    await message.edit(embed=embedGhiestPreBattle, components=[])
                    with BytesIO() as image_binary:
                        transparent_image.save(image_binary, 'PNG')
                        image_binary.seek(0)
                        try:
                            await message.edit(file=discord.File(fp=image_binary, filename=f'{username}_ghiests.png'), embed=embedGhiestPreBattle, components=[])
                        except discord.errors.HTTPException as e:
                            await message.edit(embed=embedDiscordErr, components=[])
                            await asyncio.sleep(10)
                            await message.delete()
                            return
                    await asyncio.sleep(6)
                    round = 1
                    ghiest_count = 30
                    while round <= 50:
                        embedGhiestBattle = discord.Embed(
                                title=f"👻 Phase 2 - GHIEST BATTLE ON! 👻",
                                description=f"*Round: {round}\n\nGhiests: {ghiest_count}\n\n{random.choice(random_string_ghiest_battle)}*",
                                color=0xFF0000
                            )
                        embedGhiestBattle.set_thumbnail(url=fallen_image)
                        buttons = [ create_button(style=ButtonStyle.blurple, label="😇", custom_id="spirit1"),
                                    create_button(style=ButtonStyle.blurple, label="😇", custom_id="spirit2"),
                                    create_button(style=ButtonStyle.blurple, label="😇", custom_id="spirit3"),
                                    create_button(style=ButtonStyle.blurple, label="😇", custom_id="spirit4"),
                                    create_button(style=ButtonStyle.blurple, label="😇", custom_id="spirit5"),
                                    create_button(style=ButtonStyle.blurple, label="😇", custom_id="spirit6"),
                                    create_button(style=ButtonStyle.blurple, label="😇", custom_id="spirit7"),
                                    create_button(style=ButtonStyle.blurple, label="😇", custom_id="spirit8"),
                                    create_button(style=ButtonStyle.blurple, label="😇", custom_id="spirit9"),
                                    create_button(style=ButtonStyle.blurple, label="😇", custom_id="spirit10")]
                        random_button = random.randint(0,9)
                        buttons[random_button]["label"] = "👻"
                        buttons[random_button]["custom_id"] = f"ghiest{random_button}"
                        for button in buttons:
                            button["style"] = random.choice(button_colors)
                        action_row = create_actionrow(buttons[0], buttons[1], buttons[2], buttons[3], buttons[4])
                        action_row2 = create_actionrow(buttons[5], buttons[6], buttons[7], buttons[8], buttons[9])
                        await message.edit(embed=embedGhiestBattle, components=[action_row, action_row2])
                        while True:
                            try:
                                interaction: ComponentContext = await wait_for_component(client, components=[action_row, action_row2], timeout=1.75)
                                interaction_author_id = interaction.author.id
                                if interaction_author_id == userid:
                                    await interaction.defer(edit_origin=True)
                                    action = interaction.custom_id
                                    if "ghiest" in action:
                                        ghiest_count -= 1
                                        if ghiest_count <= 0:
                                            round = 51
                                            break
                                        await message.edit(embed=embedGhiestBattle, components=[action_row, action_row2])
                                    elif "spirit" in action:
                                        embedHideAndSeek2 = discord.Embed(
                                        title=f"⚔️ YOU STRIKED A SPIRIT! ⚔️",
                                        description=f"*You spilled the sacred blood of an innocent spirit that was just trying to help!\n\nThe Temple starts to shake and crumble...\n\nQUEST FAILED! Try Again!*",
                                        color=0xFF0000
                                        )
                                        embedHideAndSeek2.set_thumbnail(url=fallen_image)
                                        await message.edit(embed=embedHideAndSeek2, components=[])
                                        return
                                    break
                                else:
                                    embedWrongUpgrade = discord.Embed(
                                        title=f"This is not your quest!",
                                        color=0xFF0000
                                    )
                                    await interaction.send(embed=embedWrongUpgrade, hidden=True)
                                    continue
                            except asyncio.TimeoutError:
                                break
                        round += 1
                        continue
                    break
            else:
                embedWrongUpgrade = discord.Embed(
                    title=f"This is not your quest!",
                    color=0xFF0000
                )
                await interaction.send(embed=embedWrongUpgrade, hidden=True)
                continue
        except asyncio.TimeoutError:
            embedTimeout = discord.Embed(
                    title=f"Woops! You took too long to respond...",
                    description=f"Ending {username}'s quest..",
                    color=0xFF0000
                )
            await message.edit(embed=embedTimeout, components=[])
            await asyncio.sleep(10)
            await message.delete()
            return
    if round > 50 and ghiest_count > 0:
        embedTutorial3 = discord.Embed(
            title=f"🧙 {quest_name} 🧙‍♀️",
            description=f"*The ghiests were too powerful and overtook you...\n\nQUEST FAILED! Try Again!*",
            color=0xFF0000
        )
        embedTutorial3.set_thumbnail(url=fallen_image)
        await message.edit(embed=embedTutorial3, components=[])
        return
    embedTutorial3 = discord.Embed(
                                title=f"🧙 Phase 3 - {quest_name} 🧙‍♀️",
                                description=f"*The ghiests slowly back off...\n\nThis doesn't look good...they seem to be combining together!*",
                                color=0xFCE303
                            )
    embedTutorial3.set_thumbnail(url=fallen_image)
    await message.edit(embed=embedTutorial3, components=[])
    await asyncio.sleep(5)
    embedTutorial3.description = f"*The ghiests slowly back off...\n\nThis doesn't look good...they seem to be combining together!\n\nA thick mist begins to form...*"
    await message.edit(embed=embedTutorial3)
    await asyncio.sleep(5)
    embedTutorial3.description = f"*The ghiests slowly back off...\n\nThis doesn't look good...they seem to be combining together!\n\nA thick mist begins to form...\n\nTHEY HAVE SUMMONED MORDEKAI!!!*"
    await message.edit(embed=embedTutorial3)
    await asyncio.sleep(5)
    embedTutorial3.description = f"*The ghiests slowly back off...\n\nThis doesn't look good...they seem to be combining together!\n\nA thick mist begins to form...\n\nTHEY HAVE SUMMONED MORDEKAI!!!\n\nThis will take your all, are you ready {fallen_name}?*"
    await message.edit(embed=embedTutorial3)
    button1 = create_button(style=ButtonStyle.blurple, label="TO BATTLE!", custom_id="continue")
    button2 = create_button(style=ButtonStyle.red, label="That's...umm...NO THANKS!", custom_id="cancel")
    action_row = create_actionrow(button1, button2)
    await asyncio.sleep(2)
    await message.edit(embed=embedTutorial3, components=[action_row])
    player_data = [rank, level, kinship, attack, defense, abilitypower]
    while True:
        try:
            interaction: ComponentContext = await wait_for_component(client, components=action_row, timeout=60.0)
            interaction_author_id = interaction.author.id
            if interaction_author_id == userid:
                await interaction.defer(edit_origin=True)
                action = interaction.custom_id
                break
            else:
                embedWrongUpgrade = discord.Embed(
                    title=f"This is not your quest!",
                    color=0xFF0000
                )
                await interaction.send(embed=embedWrongUpgrade, hidden=True)
                continue
        except asyncio.TimeoutError:
            embedTimeout = discord.Embed(
                    title=f"Woops! You took too long to respond...",
                    description=f"Ending {username}'s quest..",
                    color=0xFF0000
                )
            await message.edit(embed=embedTimeout, components=[])
            await asyncio.sleep(10)
            await message.delete()
            return
    embedMordekai = discord.Embed(
                                title=f"🏺 BATTLE OF MORDEKAI 🏺",
                                description=f"<@{userid}> VS Mordekai\n\nATK | DEF | AP: {attack} | {defense} | {abilitypower}",
                                color=0xFFFFFF
                            )
    embedMordekai.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
    embedBossWin = discord.Embed(
        title=f"⚔️ Mordekai Wins The Battle ⚔️",
        description=f"*Mordekai and his army of ghiests have taken over the Temple!\n\nQUEST FAILED! Try again!*",
        color=0xFF0000
    )
    embedBossWin.set_footer(text="Try leveling up, boosting your stats, upgrading your kinship, and most importantly match your character's abilities to its stats!")
    embedBossWin.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
    with BytesIO() as image_binary:
        transparent_image2.save(image_binary, 'PNG')
        image_binary.seek(0)
        try:
            await message.delete()
            message = await ctx.send(file=discord.File(fp=image_binary, filename=f'{username}_mordekai.png'), embed=embedMordekai, components=[])
        except discord.errors.HTTPException as e:
            await message.edit(embed=embedDiscordErr, components=[])
            await asyncio.sleep(10)
            await message.delete()
            return
    ultimate_on = False
    basic1_button = create_button(style=ButtonStyle.blurple, label=basic_1, custom_id=basic_1)
    basic2_button = create_button(style=ButtonStyle.blurple, label=basic_2, custom_id=basic_2)
    basic3_button = create_button(style=ButtonStyle.blurple, label=basic_3, custom_id=basic_3)
    ultimate_button = create_button(style=ButtonStyle.red, label=ultimate, custom_id=ultimate)
    action_row = create_actionrow(basic1_button, basic2_button, basic3_button, ultimate_button)
    round = 1
    embedMordekai.add_field(name=f"{username}'s move!", value=f"Choosing ability...", inline=False)
    boss_hp = 12000
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
                description_block = f"\nShadow Barrier: {2-boss_block_count}"
                if boss_block_count >= 2:
                    boss_block_on = False
                    boss_block_count = 0
                    description_block = ""
            else:
                description_block = ""
            if boss_fire_on:
                description_fire = f"\nAbyssal Curse: {3-boss_fire_count}"
                if boss_fire_count >= 3:
                    boss_fire_on = False
                    boss_fire_count = 0
                    description_fire = ""
            else:
                description_fire = ""
            embedMordekai.description=f"<@{userid}> VS Mordekai\n\nATK | DEF | AP: {attack} | {defense} | {abilitypower}\n\nRound {round}\n{description_block}{description_fire}"
        else:
            embedMordekai.description = f"<@{userid}> VS Mordekai\n\nATK | DEF | AP: {attack} | {defense} | {abilitypower}\n\nRound {round}"
        embedMordekai.set_footer(text=f"{username}: {hitpoints} HP | Mordekai HP: {boss_hp}")
        if not ultimate_on:
            ultimate_cd += 1
            ultimate_button["disabled"] = True
        else:
            ultimate_button["disabled"] = False
        await message.edit(embed=embedMordekai, components=[action_row])
        try:
            interaction: ComponentContext = await wait_for_component(client, components=action_row, timeout=30.0)
            interaction_author_id = interaction.author.id
            if interaction_author_id == userid:
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
                            embedMordekai.set_field_at(0, name=f"{username} uses {action}!", value=f"IT LANDS 2500 DAMAGE! 💀\n250 self-damage caused!", inline=False)
                        else:
                            embedMordekai.set_field_at(0, name=f"{username} uses {action}!", value=f"IT LANDS 2500 DAMAGE! 💀\nNo self-damage caused!", inline=False)
                    else:
                        if random.random() <= 0.5:
                            hitpoints -= 500
                            embedMordekai.set_field_at(0, name=f"{username} uses {action}!", value=f"Death Blow missed!\n250 self-damage caused!", inline=False)
                        else:
                            embedMordekai.set_field_at(0, name=f"{username} uses {action}!", value=f"Death Blow missed!\nNo self-damage caused!", inline=False)
                elif action == "Divine Aura":
                    ultimate_on = False
                    ultimate_cd = 0
                    heal_amount = random.randint(500,3000)
                    hitpoints += heal_amount
                    hitpoints = min(hitpoints, int(metadata_decoded["properties"]["HP"]))
                    embedMordekai.set_field_at(0, name=f"{username} uses {action}!", value=f"{heal_amount} HP restored!", inline=False)
                elif action == "Mirage":
                    ultimate_on = False
                    ultimate_cd = 0
                    mirage_on = True
                    mirage_count = 0
                    damage = int(((abilitypower+defense)*random.uniform(0.8,1.2))*0.1)
                    boss_hp -= damage
                    embedMordekai.set_field_at(0, name=f"{username} uses {action}!", value=f"Next 2 rounds will be blocked!", inline=False)
                elif action == "Pestilence":
                    ultimate_on = False
                    ultimate_cd = 0
                    pestilence_on = True
                    pestilence_count = 0
                    embedMordekai.set_field_at(0, name=f"{username} uses {action}!", value=f"Mordekai has been poisoned!", inline=False)
                elif action == "Molten Rage":
                    ultimate_on = False
                    ultimate_cd = 0
                    molten_rage_on = True
                    molten_rage_count = 0
                    embedMordekai.set_field_at(0, name=f"{username} uses {action}!", value=f"They are ENRAGED for the next 2 rounds!", inline=False)
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
                                description_block = f"\nShadow Barrier: {2-boss_block_count}"
                                if boss_block_count >= 2:
                                    boss_block_on = False
                                    boss_block_count = 0
                                    description_block = ""
                            else:
                                description_block = ""
                            if boss_fire_on:
                                boss_fire_count += 1
                                description_fire = f"\nAbyssal Curse: {3-boss_fire_count}"
                                if boss_fire_count >= 3:
                                    boss_fire_on = False
                                    boss_fire_count = 0
                                    description_fire = ""
                            else:
                                description_fire = ""
                            embedMordekai.description=f"<@{userid}> VS Mordekai\n\nATK | DEF | AP: {attack} | {defense} | {abilitypower}\n\nRound {round}\n{description_block}{description_fire}"
                        else:
                            embedMordekai.description = f"<@{userid}> VS Mordekai\n\nATK | DEF | AP: {attack} | {defense} | {abilitypower}\n\nRound {round}"                                
                        if boss_fire_on:
                            fire_damage = random.randint(300,600)
                            hitpoints -= fire_damage
                            fire_string = f"\n{fire_damage} Curse Damage Taken!"
                        else:
                            fire_string = ""
                        embedMordekai.set_field_at(0, name=f"{username} uses {action}! {string}", value=f"All negative effects have been reduced by 1!{fire_string}", inline=False)
                    else:
                        if boss_fire_on:
                            fire_damage = random.randint(500,750)
                            hitpoints -= fire_damage
                            fire_string = f"\n{fire_damage} Curse Damage Taken!"
                        else:
                            fire_string = ""
                        if action == "Retribution":
                            if defense != 0:
                                retribution_amount = int(defense*random.uniform(0.75,2))
                            else:
                                retribution_amount = 0
                            hitpoints += retribution_amount
                            hitpoints = min(hitpoints, int(metadata_decoded["properties"]["HP"]))
                            embedMordekai.set_field_at(0, name=f"{username} uses {action}!", value=f"{retribution_amount} HP restored by {username}!{fire_string}", inline=False)
                        else:
                            if boss_block_on:
                                damage = 0
                                embedMordekai.set_field_at(0, name=f"{username} uses {action}!", value=f"It is ineffective against Shadow Barrier!{fire_string}", inline=False)
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
                                embedMordekai.set_field_at(0, name=f"{username} uses {action}! {string}", value=f"{damage} damage dealt to Mordekai!{surge_string}{fire_string}", inline=False)
                                boss_hp -= damage
                embedMordekai.set_footer(text=f"{username}: {hitpoints} HP | Mordekai HP: {boss_hp}")
                if boss_block_on or boss_fire_on:
                    if boss_block_on:
                        boss_block_count += 1
                        description_block = f"\nShadow Barrier: {2-boss_block_count}"
                        if boss_block_count >= 2:
                            boss_block_on = False
                            boss_block_count = 0
                            description_block = ""
                    else:
                        description_block = ""
                    if boss_fire_on:
                        boss_fire_count += 1
                        description_fire = f"\nAbyssal Curse: {3-boss_fire_count}"
                        if boss_fire_count >= 3:
                            boss_fire_on = False
                            boss_fire_count = 0
                            description_fire = ""
                    else:
                        description_fire = ""
                    embedMordekai.description=f"<@{userid}> VS Mordekai\n\nATK | DEF | AP: {attack} | {defense} | {abilitypower}\n\nRound {round}\n{description_block}{description_fire}"
                else:
                    embedMordekai.description = f"<@{userid}> VS Mordekai\n\nATK | DEF | AP: {attack} | {defense} | {abilitypower}\n\nRound {round}"
                if molten_rage_on:
                    molten_rage_count += 1
                if pestilence_on:
                    pestilence_count += 1
                if mirage_on:
                    mirage_count += 1
                await message.edit(embed=embedMordekai)
                if boss_hp <= 0:
                    boss_hp = 0
                    break
                boss_data = await boss_ability("Mordekai", defense)
                await asyncio.sleep(2)
                damage = boss_data[1]
                effect = boss_data[2]
                if pestilence_on:
                    pestilence_damage = random.randint(100,300)
                    if pestilence_count >= 3:
                        pestilence_on = False
                        pestilence_count = 0
                    string_pestilence = f"\n{pestilence_damage} poison damage taken by Mordekai!"
                else:
                    string_pestilence = ""
                if effect == "fire":
                    boss_fire_on = True
                    boss_fire_count = 0
                    string_fire = f"\n{username} has been CURSED for 3 rounds!{string_pestilence}"
                else:
                    string_fire = ""
                if mirage_on:
                    damage = 0
                    string_fire = ""
                    string_mirage = f"\nIt is ineffective against {username}'s Mirage!"
                    if mirage_count >= 2:
                        mirage_on = False
                        mirage_count = 0
                else:
                    string_mirage = ""
                if effect == "heal":
                    boss_hp += boss_data[1]
                    boss_hp = min(boss_hp, 10000)
                    embedMordekai.set_field_at(0, name=f"Mordekai uses {boss_data[0]}!", value=f"{boss_data[1]} HP restored by Mordekai!{string_pestilence}", inline=False)
                else:
                    if effect == "block":
                        boss_block_on = True
                        boss_block_count = 0
                        string_block = f"\n{username}'s next 2 attacks will be blocked!{string_pestilence}"
                        value_block = f"{string_block}{string_mirage}{string_fire}"
                    else:
                        string_block = ""
                        if string_mirage == "":
                            value_block = f"{damage} Mordekai damage dealt to {username}!{string_block}{string_mirage}{string_fire}"
                        else:
                            value_block = f"{string_block}{string_mirage}{string_fire}"
                    hitpoints -= damage
                    embedMordekai.set_field_at(0, name=f"Mordekai uses {boss_data[0]}!", value=value_block, inline=False)
                embedMordekai.set_footer(text=f"{username}: {hitpoints} HP | Mordekai HP: {boss_hp}")
                if hitpoints <= 0:
                    hitpoints = 0
                    await message.edit(embed=embedBossWin, components=[])
                    return
                await message.edit(embed=embedMordekai)
                await asyncio.sleep(1)
                if round >= 15:
                    await message.edit(embed=embedBossWin, components=[])
                    return
                round += 1
            else:
                embedWrongGame = discord.Embed(
                    title=f"This is not your boss battle!",
                    description=f"{username} is currently fighting...",
                    color=0xFF0000
                )
                await interaction.send(embed=embedWrongGame, hidden=True)
        except asyncio.TimeoutError:
            embedTimeout = discord.Embed(
                    title=f"Woops! You took too long to respond...",
                    description=f"Ending <@{userid}>'s battle..",
                    color=0xFF0000
                )
            await message.edit(embed=embedTimeout, components=[])
            await asyncio.sleep(10)
            await message.delete()
            return
    embedSummoning = discord.Embed(
        title=f"🧙 THE SUMMONING OF HEIMDALL 🧙‍♀️",
        description=f"*You prepare to summon Heimdall to seal Mordekai and bind him into a time capsule!*",
        color=0xFCE303
    )  
    await message.edit(embed=embedSummoning)
    await asyncio.sleep(5)
    embedSummoning.description = f"*You prepare to summon Heimdall to seal Mordekai and bind him into a time capsule!\n\nThis ritual requires a total of 5 casters to be successful...\n\nYou gather with your fellow Fallen and begin casting the ritual...*"
    await message.edit(embed=embedSummoning)
    await asyncio.sleep(5)
    buttons = [create_button(style=ButtonStyle.red, label="CAST!", custom_id="0"),
               create_button(style=ButtonStyle.red, label="CAST!", custom_id="1"),
               create_button(style=ButtonStyle.red, label="CAST!", custom_id="2"),
               create_button(style=ButtonStyle.red, label="CAST!", custom_id="3")]
    action_row = create_actionrow(buttons[0], buttons[1], buttons[2], buttons[3])
    await message.edit(embed=embedSummoning, components=[action_row])
    casters = []
    i = 0
    while i <= 4:
        try:
            interaction: ComponentContext = await wait_for_component(client, components=action_row, timeout=30.0)
            interaction_author_id = interaction.author.id
            if interaction_author_id != userid and interaction_author_id not in casters:
                await interaction.defer(edit_origin=True)
                button_id = int(interaction.custom_id)
                casters.append(interaction_author_id)
                buttons[button_id]["disabled"] = True
                buttons[button_id]["style"] = ButtonStyle.green
                buttons[button_id]["label"] = "CASTED!"
                i += 1
                if i >= 4:
                    embedSummonSuccessful = discord.Embed(
                        title=f"🧙 THE SUMMONING OF HEIMDALL 🧙‍♀️",
                        description=f"*Ritual In Progress...!\n\nThe Temple grounds shake as a blinding light shines from the shrine...*",
                        color=0x28FF0A
                    )
                    await message.edit(embed=embedSummonSuccessful, components=[])
                    break
                await message.edit(embed=embedSummoning, components=[action_row])
                continue
            else:
                embedWrongUpgrade = discord.Embed(
                    title=f"You Are Already Casting!",
                    color=0xFF0000
                )
                await interaction.send(embed=embedWrongUpgrade, hidden=True)
                continue
        except asyncio.TimeoutError:
            embedTimeout = discord.Embed(
                    title=f"Woops! You took too long to respond...",
                    description=f"Mordekai and his army of ghiests took over the Temple!\n\nQUEST FAILED! Try Again!",
                    color=0xFF0000
                )
            await message.edit(embed=embedTimeout, components=[])
            await asyncio.sleep(10)
            return
    await asyncio.sleep(5)
    embedSummonSuccessful.description = f"*Ritual In Progress...!\n\nThe Temple grounds shake as a blinding light shines from the shrine...*\n\nHeimdall appears out of the divine glow, shimmering with wings spanning the Temple side to side!"
    await message.edit(embed=embedSummonSuccessful)
    await asyncio.sleep(5)
    embedSummonSuccessful.description = f"*Ritual In Progress...!\n\nThe Temple grounds shake as a blinding light shines from the shrine...*\n\nHeimdall appears out of the divine glow, shimmering with wings spanning the Temple side to side!\n\nMordekai trembles in fear as Heimdall calmly takes a few steps towards him..."
    await message.edit(embed=embedSummonSuccessful)
    await asyncio.sleep(5)
    embedSummonSuccessful.description = f"*Ritual In Progress...!\n\nThe Temple grounds shake as a blinding light shines from the shrine...*\n\nHeimdall appears out of the divine glow, shimmering with wings spanning the Temple side to side!\n\nMordekai trembles in fear as Heimdall calmly takes a few steps towards him...\n\nHeimdall casts a binding spell and channels Mordekai's spiritual aura and binds it inside a time capsule! 🏺"
    await message.edit(embed=embedSummonSuccessful)
    await asyncio.sleep(5)
    embedSummonSuccessful.title = f"🏺 QUEST SUCCESSFULL! 🏺"
    embedSummonSuccessful.description = f"*Ritual In Progress...!\n\nThe Temple grounds shake as a blinding light shines from the shrine...*\n\nHeimdall appears out of the divine glow, shimmering with wings spanning the Temple side to side!\n\nMordekai trembles in fear as Heimdall calmly takes a few steps towards him...\n\nHeimdall casts a binding spell and channels Mordekai's spiritual aura and binds it inside a time capsule! 🏺\n\nMordekai's reign of terror has come to an end at last...that battle was fierce and both you and {fallen_name} were glorious in your efforts to defend the temple!\n\nLet's give credit to your fearless Fallen casters for their help in completing the quest:\n<@{casters[0]}>\n<@{casters[1]}>\n<@{casters[2]}>\n<@{casters[3]}>\n\nEach of your fellow Fallen casters was sent 66 $EXP for their efforts!"
    balance_ac2 = await get_balance(wallet, ac2_id)
    if balance_ac2 > 0:
        embedSummonSuccessful.set_footer(text=f"You have already received this achievement! Great work!")
        await message.edit(embed=embedSummonSuccessful)
        return
    await message.edit(embed=embedSummonSuccessful)
    await asyncio.sleep(3)
    wallet1, main_character1, equipped_hatchet1 = await get_main_char(str(casters[0]))
    wallet2, main_character2, equipped_hatchet2 = await get_main_char(str(casters[1]))
    wallet3, main_character3, equipped_hatchet3 = await get_main_char(str(casters[2]))
    wallet4, main_character4, equipped_hatchet4 = await get_main_char(str(casters[3]))
    balance_exp1 = await get_balance(wallet, 811721471)
    balance_exp2 = await get_balance(wallet, 811721471)
    balance_exp3 = await get_balance(wallet, 811721471)
    balance_exp4 = await get_balance(wallet, 811721471)
    balances = [balance_exp1, balance_exp2, balance_exp3, balance_exp4]
    wallets = [wallet1, wallet2, wallet3, wallet4]
    txid = await send_assets("Congratulations! You completed The Summoning quest and earned an achievement! The Order", fallen_order_main, wallet, ac2_id, "ac2", 1)
    await send_assets("Congratulations! You completed The Summoning quest and earned 330 $EXP! The Order", fallen_order_main, wallet, 811721471, "EXP", 330)
    await send_assets("Congratulations! You completed The Summoning quest and earned 1 Stat Booster $BOOST! The Order", fallen_order_main, wallet, 815771120, "BOOST", 1)
    i = 0
    for balance in balances:
        if balance != -1:
            await send_assets("Congratulations! You helped a fellow Fallen complete The Summoning quest and earned 66 $EXP! The Order", fallen_order_main, wallets[i], 811721471, "EXP", 66)
        i += 1
    embedAchievementClaimed = discord.Embed(
                title=f"🏆 Achievement Claimed! 🏆",
                url=f"https://algoexplorer.io/tx/{txid}",
                description=f"Congratulations! You earned the following reward for completing the quest:\n\nAchievement - Summoner\n1 Stat Booster NFT\n330 $EXP\n\n66 $EXP to Cast Assists",
                color=0x28FF0A
            )  
    embedAchievementClaimed.set_image(url=ac2_image)
    embedAchievementClaimed.set_footer(text="Let's collect more achievements!")
    embedAchievementClaimed.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
    await ctx.send(embed=embedAchievementClaimed)