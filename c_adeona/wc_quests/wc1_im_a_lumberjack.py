from discord_slash import cog_ext
from discord.ext import commands
import discord
import requests
from io import BytesIO
from PIL import Image
import random
from discord_slash.utils.manage_components import create_actionrow, create_button, wait_for_component
import json
from discord import File
from discord_slash.model import ButtonStyle
import base64
from discord_slash import ComponentContext
import asyncio
from client import client
from txns import algod_client, send_assets, fallen_order_main, fallen_order_manager, get_main_char, get_balance, edit_metadata, trade_logs, fallen_order_accessories
from embeds import embedNoOptEXP

wac1_id = 1069835750
wac1_image = "https://ipfs.algonode.xyz/ipfs/bafybeigb6gmhcrttofq5vjaye7hsfj3zsrfyleeqdcxxlm5hjo43ckpcqy#i"
quest_name = "I'm A Lumberjack!"

required_exp_to_level_up = [83, 257, 533, 921, 1433, 2083, 2884, 3853, 5007, 6365, 7947, 9775, 11872, 14262, 16979, 20047]
channel_list = [936808094414045204, 936801867340582982, 1012036883976564786, 1081221312011309127, 1082157256679882862, 1080360866467287140, 1080746370429898832, 1087215342297813072, 1083208605303574609, 1042200246962364606, 1078081795943305217]
ramsay_quote = ["My gran could do better! And she's dead!", "This stew is so undercooked, it's following Mary to school!", "This is a really tough decision…'cause you're both crap", "I wouldn't trust you running a bath let alone a restaurant", "You are a true IDIOT SANDWICH!!!"]

async def quest_im_a_lumberjack(ctx):
    await ctx.defer()
    userid = str(ctx.author.id)
    wallet, main_character, equipped_hatchet = await get_main_char(userid)
    embedMissingReq = discord.Embed(
            title=f"🪓 Quest Requirements 🪓",
            color=0xFCE303
        )
    embedMissingReq.set_footer(text=f"Main Character with LVL 1 Woodcutting\nEquipped Hatchet 🪓")
    embedMissingReq.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
    if wallet == '':
        embedNoReg = discord.Embed(
            title="Click Here To Register!",
            url="https://app.fallenorder.xyz",
            description=f"Please verify your wallet via our website to continue..\nEnsure you copy your user id below for the verification process:\nUser ID: {ctx.author.id}",
            color=0xFF1C0A,
        )
        await ctx.send(embed=embedNoReg)
        return
    if main_character == 0:
        await ctx.send(embed=embedMissingReq)
        return
    if equipped_hatchet == 0:
        await ctx.send(embed=embedMissingReq)
        return
    balance_wac1 = await get_balance(wallet, wac1_id)
    balance_exp = await get_balance(wallet, 811721471)
    if balance_wac1 == -1:
        embedAchievement = discord.Embed(
            title=f"You must first opt in to the Achievement for this quest!",
            description=f"Try /quest again to complete the quest once you have opted in...\n\n[Click Here To Opt In!](https://www.randgallery.com/algo-collection/?address={wac1_id})",
            color=0xFF0000
        )
        await ctx.send(embed=embedAchievement)
        return
    if balance_exp == -1:
        await ctx.send(embed=embedNoOptEXP)
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
    woodcutting_data = metadata_decoded.get("properties", {}).get("Woodcutting", "None")
    if woodcutting_data == "None":
        await ctx.send(embed=embedMissingReq)
        return
    else:
        woodcutting_data_split = woodcutting_data.split("/")
        woodcutting_level = int(woodcutting_data_split[0])
        woodcutting_exp = int(woodcutting_data_split[1])
    if woodcutting_level < 1:
        await ctx.send(embed=embedMissingReq)
        return
    embedTutorial1 = discord.Embed(
                title=f"🧙 Quest - {quest_name} 🧙‍♀️",
                description=f"*Welcome <@{ctx.author.id}>*\n\n*I see you brought {fallen_name} along with you...*\n\n*Are you both ready for {quest_name}*",
                color=0xFCE303
            )
    embedTutorial1.set_footer(text=f"Press Continue when ready..")
    embedTutorial1.set_thumbnail(url=fallen_image)
    button1 = create_button(style=ButtonStyle.blurple, label="Continue", custom_id="continue")
    button2 = create_button(style=ButtonStyle.red, label="Cancel", custom_id="cancel")
    action_row = create_actionrow(button1, button2)
    message = await ctx.send(embed=embedTutorial1, components=[action_row])
    while True:
        try:
            interaction: ComponentContext = await wait_for_component(client, components=action_row, timeout=60.0)
            interaction_author_id = interaction.author.id
            if interaction_author_id == ctx.author.id:
                await interaction.defer(edit_origin=True)
                action = interaction.custom_id
                if action == "cancel":
                    await message.delete()
                    await asyncio.sleep(1)
                    return
                elif action == 'continue':
                    await message.edit(components=[])
                    embedTutorial2 = discord.Embed(
                                title=f"🧙 Phase 2 - {quest_name} 🧙‍♀️",
                                description=f"*As the sun rises over the dense forest, a burly lumberjack named {ctx.author.name} and his companion {fallen_name} set out on his daily routine.\n\nYou walk along the familiar path that leads to your cabin on the outskirts of the woods\n\nAs you make your way through the forest, you notice something odd\nThe chirping of birds and rustling of leaves that normally fill the air is eerily quiet.\n\nInstead, you hear the sound of whimpering and groaning in the distance.\n\nFollowing the sound, {fallen_name} discovers a group of woodland creatures, including deer, rabbits, and squirrels, injured and in pain.\n\nTheir wounds appear to have been inflicted by some kind of sharp claws or teeth.\n\n{ctx.author.name} realizes that something is seriously wrong...*",
                                color=0xFCE303
                            )
                    embedTutorial2.set_thumbnail(url=fallen_image)
                    button1 = create_button(style=ButtonStyle.blurple, label="Let's Find Out What Happened Here...", custom_id="continue")
                    action_row = create_actionrow(button1)
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
                    description=f"Ending {ctx.author.name}'s quest..",
                    color=0xFF0000
                )
            await message.edit(embed=embedTimeout, components=[])
            await asyncio.sleep(10)
            await message.delete()
            return
    while True:
        try:
            interaction: ComponentContext = await wait_for_component(client, components=action_row, timeout=60.0)
            interaction_author_id = interaction.author.id
            await interaction.defer(edit_origin=True)
            if interaction_author_id == ctx.author.id:
                action = interaction.custom_id                                     
                embedTutorial3 = discord.Embed(
                            title=f"🧙 Phase 3 -  {quest_name} 🧙‍♀️",
                            description=f"*As you venture deeper into the forest, {fallen_name} comes face to face with a group of terrifying monsters.\n\nThey have razor-sharp teeth and claws, and their eyes glow with an ominous red light.\n\nYou realize that these monsters are responsible for the injuries caused to the forest creatures!*",
                            color=0xFCE303
                        )
                embedTutorial3.set_thumbnail(url=fallen_image)
                button1 = create_button(style=ButtonStyle.blurple, label="I Must Defend The Forest!", custom_id="continue")
                button2 = create_button(style=ButtonStyle.red, label="Run Away", custom_id="cancel")
                action_row = create_actionrow(button1, button2)
                await message.edit(embed=embedTutorial3, components=[action_row])
                while True:
                    try:
                        interaction: ComponentContext = await wait_for_component(client, components=action_row, timeout=60.0)
                        interaction_author_id = interaction.author.id
                        if interaction_author_id == ctx.author.id:
                            await interaction.defer(edit_origin=True)
                            action = interaction.custom_id
                            if action == "cancel":
                                await message.delete()
                                await asyncio.sleep(1)
                                return
                            elif action == 'continue':
                                embedHideAndSeek1 = discord.Embed(
                                    title=f"⚔️ HUNT IS ON! ⚔️",
                                    description=f"*You prepare your crossbow and aim carefully...\n\nOnce you are locked on target, a button will appear for you to shoot the monster down...*",
                                    color=0xFCE303
                                )
                                embedHideAndSeek1.set_thumbnail(url=fallen_image)
                                await message.edit(embed=embedHideAndSeek1, components=[])
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
                                description=f"Ending {ctx.author.name}'s quest..",
                                color=0xFF0000
                            )
                        await message.edit(embed=embedTimeout, components=[])
                        await asyncio.sleep(10)
                        await message.delete()
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
            embedTimeout = discord.Embed(
                    title=f"Woops! You took too long to respond...",
                    description=f"Ending {ctx.author.name}'s quest..",
                    color=0xFF0000
                )
            await message.edit(embed=embedTimeout, components=[])
            await asyncio.sleep(10)
            await message.delete()
            return
    animals = ["A Rabbit", "A Deer", "A Koala", "An Owl"]
    button = [create_button(style=ButtonStyle.green, label="SHOOT!", custom_id="shoot"), create_button(style=ButtonStyle.red, label=f"That's {random.choice(animals)}!", custom_id="animal")]
    i = 0
    while i <= 10:
        embedHideAndSeek1 = discord.Embed(
            title=f"⚔️ HUNT IS ON! ⚔️",
            description=f"*You prepare your crossbow and aim carefully...\n\nOnce you are locked on target, a button will appear for you to shoot the monster down...*",
            color=0xFCE303
        )
        embedHideAndSeek1.set_thumbnail(url=fallen_image)
        embedHideAndSeek1.set_footer(text=f"Round {i+1}")
        embedHideAndSeek2 = discord.Embed(
        title=f"⚔️ YOU SHOT A CRITTER! ⚔️",
        description=f"*You killed an innocent animal that wasn't a monster!\n\nThe forest animals are frown on you and step back in fear of you...\n\nYou failed to protect the forest and caused more damage, well done Sherlock...*",
        color=0xFF0000
        )
        embedHideAndSeek2.set_thumbnail(url=fallen_image)
        embedHideAndSeek3 = discord.Embed(
                title=f"⚔️ YOU SHOT ONE DOWN! ⚔️",
                description=f"*NICE SHOT! You shot one of the monsters down!\n\nIt's not over...get ready for the next one!*",
                color=0x28FF0A
            )
        embedHideAndSeek3.set_thumbnail(url=fallen_image)
        embedHideAndSeek3.set_footer(text=f"Round {i+1}")
        embedHideAndSeek4 = discord.Embed(
                title=f"⚔️ YOU MISSED!! ⚔️",
                description=f"*Awwwww! You missed your target and the monsters got away!\n\nYou'll have to hunt them down again!*",
                color=0xFF0000
            )
        embedHideAndSeek4.set_thumbnail(url=fallen_image)
        random_number = random.randint(1,100)
        if random_number < 30:
            action_row = create_actionrow(button[1])
        else:
            action_row = create_actionrow(button[0])
        await message.edit(embed=embedHideAndSeek1, components=[])
        await asyncio.sleep(random.randint(2,6))
        await message.edit(embed=embedHideAndSeek1, components=[action_row])
        while True:
            try:
                interaction: ComponentContext = await wait_for_component(client, components=action_row, timeout=2)
                interaction_author_id = interaction.author.id
                if interaction_author_id == ctx.author.id:
                    await interaction.defer(edit_origin=True)
                    action = interaction.custom_id
                    if action == "animal":
                        await message.edit(embed=embedHideAndSeek2, components=[])
                        return
                    elif action == "shoot":
                        if i <= 10:
                            await message.edit(embed=embedHideAndSeek3, components=[])
                            await asyncio.sleep(3)
                        else:
                            embedTutorial4 = discord.Embed(
                                title=f"🧙 Phase 4 -  {quest_name} 🧙‍♀️",
                                description=f"*Well Done!! You striked all the monsters down and protected the critters from more suffering.*",
                                color=0xFCE303
                            )
                            await message.edit(embed=embedTutorial4, components=[])
                            embedTutorial4.set_thumbnail(url=fallen_image)
                    break
                else:
                    embedWrongUpgrade = discord.Embed(
                        title=f"This is not your quest!",
                        color=0xFF0000
                    )
                    await interaction.send(embed=embedWrongUpgrade, hidden=True)
                    continue
            except asyncio.TimeoutError:
                if random_number >= 30:
                    await message.edit(embed=embedHideAndSeek4, components=[])
                    return
                await message.edit(embed=embedHideAndSeek1, components=[])
                break  
        i += 1
    embedTutorial5 = discord.Embed(
                title=f"🧙 Phase 4 -  {quest_name} 🧙‍♀️",
                description=f"*Well Done!! You striked all the monsters down and protected the critters from more suffering.\n\nUH OH!\n\nLOOK BEHIND YOU QUICK THERE'S A BIG MONSTER HERE FOR REVENGE!*",
                color=0xFCE303
            )
    embedTutorial5.set_thumbnail(url=fallen_image)
    button1 = create_button(style=ButtonStyle.green, label="STRIKE IT DOWN!", custom_id="continue")
    action_row = create_actionrow(button1)
    await asyncio.sleep(5)
    await message.edit(embed=embedTutorial5, components=[])
    await asyncio.sleep(1)
    await message.edit(embed=embedTutorial5, components=[action_row])
    while True:
        try:
            interaction: ComponentContext = await wait_for_component(client, components=action_row, timeout=2.0)
            interaction_author_id = interaction.author.id
            if interaction_author_id == ctx.author.id:
                await interaction.defer(edit_origin=True)
                action = interaction.custom_id
                if action == "cancel":
                    await message.delete()
                    await asyncio.sleep(1)
                    return
                elif action == 'continue':                    
                    embedTutorial6 = discord.Embed(
                                title=f"🧙 Phase 5 -  {quest_name} 🧙‍♀️",
                                description=f"*PHEW! That was close!\n\nYour reflexes served you well so far...*",
                                color=0xFCE303
                            )
                    embedTutorial6.set_thumbnail(url=fallen_image)
                    await message.edit(embed=embedTutorial6, components=[])
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
                    title=f"OUCH! You Were Slaughtered...",
                    description=f"That monster really wasn't here for games. Revenge was string with that one...\n\nPrepare better next time!",
                    color=0xFF0000
                )
            await message.edit(embed=embedTimeout, components=[])
            return
    i = 0
    random_number = random.randint(10,20)
    while i < random_number:
        embedChopping = discord.Embed(
                title=f"🪓 Phase 6 - {quest_name} 🪓",
                description=f"*There's a MASSIVE tree standing in your way to get back home...\n\nTime to prove your lumberjack skills\n\nChop away at it till you get through!*",
                color=0xFF0000
            )
        embedChopping.set_thumbnail(url=fallen_image)
        await asyncio.sleep(random.randint(3,6))
        buttons = [ create_button(style=ButtonStyle.blurple, label="Chop!", custom_id="1", disabled=True),
                    create_button(style=ButtonStyle.blurple, label="Chop!", custom_id="2", disabled=True),
                    create_button(style=ButtonStyle.blurple, label="Chop!", custom_id="3", disabled=True),
                    create_button(style=ButtonStyle.blurple, label="Chop!", custom_id="4", disabled=True),
                    create_button(style=ButtonStyle.blurple, label="Chop!", custom_id="5", disabled=True),
                    create_button(style=ButtonStyle.blurple, label="Chop!", custom_id="6", disabled=True),
                    create_button(style=ButtonStyle.blurple, label="Chop!", custom_id="7", disabled=True),
                    create_button(style=ButtonStyle.blurple, label="Chop!", custom_id="8", disabled=True)]
        random_button = random.randint(0,7)
        buttons[random_button]["disabled"] = False
        action_row = create_actionrow(buttons[0], buttons[1], buttons[2], buttons[3])
        action_row2 = create_actionrow(buttons[4], buttons[5], buttons[6], buttons[7])
        await message.edit(embed=embedChopping, components=[action_row, action_row2])
        while True:
            try:
                interaction: ComponentContext = await wait_for_component(client, components=[action_row, action_row2], timeout=120)
                interaction_author_id = interaction.author.id
                if interaction_author_id == ctx.author.id:
                    await interaction.defer(edit_origin=True)
                    action = interaction.custom_id
                    buttons[random_button]["disabled"] = True
                    await message.edit(embed=embedChopping, components=[action_row, action_row2])
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
                    title=f"You Took Too Long!",
                    description=f"That tree was thicker than a snickers bar! Damn...\n\nUse /quest to give it another shot!",
                    color=0xFF0000
                )
                await message.edit(embed=embedHideAndSeek1, components=[])
                break 
        i += 1
    embedTutorialCookinguccessful2 = discord.Embed(
                title=f"🧙 Quest Successful!! 🧙‍♀️",
                description=f"*GREAT WORK!\n\nYou not only protected the forest from evil monsters, but kept yourself safe from their big leader and proved your lumberjack skills with that huge tree!\n\nWELL DONE!*",
                color=0x28FF0A
            )     
    balance_wac1 = await get_balance(wallet, wac1_id)
    if balance_wac1 > 0:
        embedTutorialCookinguccessful2.set_footer(text=f"You have already received this achievement! Great work!")
        await message.edit(embed=embedTutorialCookinguccessful2, components=[])
        return
    await message.edit(embed=embedTutorialCookinguccessful2, components=[])
    await asyncio.sleep(3)
    new_woodcutting_exp = woodcutting_exp + 420
    levelup_string = f""
    while new_woodcutting_exp > required_exp_to_level_up[woodcutting_level]:
        woodcutting_level += 1
        levelup_string = f"\n\nLEVEL UP!! CONGRATULATIONS!\n\nNew Level: {woodcutting_level}"
    wc_string = str(woodcutting_level) + "/" + str(new_woodcutting_exp)
    metadata_decoded["properties"]["Woodcutting"] = wc_string
    metadata_encoded = json.dumps(metadata_decoded)
    await edit_metadata(main_character, metadata_encoded)
    txid = await send_assets("Congratulations! You completed I'm A Lumberjack quest and earned an achievement! The Order", fallen_order_main, wallet, wac1_id, "WAC1", 1)
    txid2 = await trade_logs("Congratulations! You completed I'm A Lumberjack quest and earned an achievement! The Order", fallen_order_accessories, wallet, 1064863037, 10)
    embedAchievementClaimed = discord.Embed(
                title=f"🏆 Woodcutting Achievement Claimed! 🏆",
                url=f"https://algoexplorer.io/tx/{txid}",
                description=f"Congratulations! You earned the following reward for completing the quest:\n\nAchievement - {quest_name}\n420 Woodcutting Experience\n10 Oak Logs\n\nNew WC EXP: {new_woodcutting_exp}{levelup_string}",
                color=0x28FF0A
            )  
    embedAchievementClaimed.set_image(url=wac1_image)
    embedAchievementClaimed.set_footer(text="Let's collect more achievements!")
    embedAchievementClaimed.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
    await ctx.send(embed=embedAchievementClaimed)