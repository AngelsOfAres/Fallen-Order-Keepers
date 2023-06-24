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
from txns import algod_client, send_assets, fallen_order_main, fallen_order_manager, get_main_char, get_balance
from embeds import embedNoOptEXP

ac1_id = 1069374333
ac1_image = "https://ipfs.algonft.tools/ipfs/bafybeifoykjgqevltdwo44f3gjwuvmn2ougacfdnay2ji5mukjnwgqz5ie"

channel_list = [936808094414045204, 936801867340582982, 1012036883976564786, 1081221312011309127, 1082157256679882862, 1080360866467287140, 1080746370429898832, 1087215342297813072, 1083208605303574609, 1042200246962364606, 1078081795943305217]
ramsay_quote = ["My gran could do better! And she's dead!", "This stew is so undercooked, it's following Mary to school!", "This is a really tough decision…'cause you're both crap", "I wouldn't trust you running a bath let alone a restaurant", "You are a true IDIOT SANDWICH!!!"]

async def quest_ramsays_rampage(ctx):
    await ctx.defer()
    userid = str(ctx.author.id)
    wallet, main_character, equipped_hatchet = await get_main_char(userid)
    if wallet == '':
        embedNoReg = discord.Embed(
            title="Click Here To Register!",
            url="https://app.fallenorder.xyz",
            description=f"Please verify your wallet via our website to continue..\nEnsure you copy your user id below for the verification process:\nUser ID: {ctx.author.id}",
            color=0xFF1C0A,
        )
        await ctx.send(embed=embedNoReg)
        return
    balance_ac1 = await get_balance(wallet, ac1_id)
    balance_exp = await get_balance(wallet, 811721471)
    if balance_ac1 == -1:
        embedAchievement = discord.Embed(
            title=f"You must first opt in to the Achievement for this quest!",
            description=f"Try /quest again to complete the quest once you have opted in...\n\n[Click Here To Opt In!](https://www.randgallery.com/algo-collection/?address={ac1_id})",
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
    response1 = requests.get(fallen_image)
    image1 = Image.open(BytesIO(response1.content))
    response2 = requests.get("https://dramscotland.co.uk/wp-content/uploads/2021/08/Gordon-Ramsay-.jpg")
    image2 = Image.open(BytesIO(response2.content))
    size = (image1.width, image1.height)
    image2 = image2.resize(size)
    transparent_image = Image.new('RGBA', (image1.width + image2.width, max(image1.height, image2.height)), color=(0, 0, 0, 0))
    transparent_image.paste(image1, (0, 0))
    transparent_image.paste(image2, (image1.width, 0))
    buffer = BytesIO()
    transparent_image.save(buffer, format='PNG')
    buffer.seek(0)
    image_file = File(buffer, filename='transparent_image.png')
    embedTutorial1 = discord.Embed(
                title=f"🧙 Quest - Ramsay's Rampage 🧙‍♀️",
                description=f"*Welcome <@{ctx.author.id}>*\n\n*I see you brought {fallen_name} along with you...*\n\n*Are you both ready for Ramsay's Rampage?*",
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
                                title=f"🧙 Phase 1 - Ramsay's Rampage 🧙‍♀️",
                                description=f"*Chef Ramsay is having a rough day at Hell's Kitchen. Idiot sandwich here....idiot sandwich there...it's a bloody mess!\n\nThe chef asks you to help him with prep...\n\nYour objective is to cook a Goblin Stew*",
                                color=0xFCE303
                            )
                    embedTutorial2.set_footer(text=f"Are you prepared to help Chef Ramsay?")
                    button1 = create_button(style=ButtonStyle.blurple, label="Goblin Stew On Its Way Chef!", custom_id="continue")
                    button2 = create_button(style=ButtonStyle.red, label="Welp! No Thanks..", custom_id="cancel")
                    action_row = create_actionrow(button1, button2)
                    await message.edit(file=image_file, embed=embedTutorial2, components=[action_row])
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
            if interaction_author_id == ctx.author.id:
                await interaction.defer(edit_origin=True)
                action = interaction.custom_id
                if action == "cancel":
                    await message.delete()
                    await asyncio.sleep(1)
                    return
                elif action == 'continue':
                    embedTutorial3a = discord.Embed(
                                title=f"🧙 Phase 2 - Ramsay's Rampage 🧙‍♀️",
                                description=f"*Dobby The Elf pops up!\n\nIn order to cook a Goblin Stew you need to get your ingredients from me...\n\nbut I won't just hand them to you! Catch me if you can!\n\nDobby The Elf runs and hides in another channel. Find him to gather your ingredients!*",
                                color=0xFCE303
                            )
                    button1 = create_button(style=ButtonStyle.blurple, label="Let's Hunt Dobby Down!", custom_id="continue")
                    button2 = create_button(style=ButtonStyle.red, label="Screw You Dobby...", custom_id="cancel")
                    action_row = create_actionrow(button1, button2)
                    await message.edit(embed=embedTutorial3a, components=[action_row])
                    while True:
                        try:
                            interaction: ComponentContext = await wait_for_component(client, components=action_row, timeout=60.0)
                            interaction_author_id = interaction.author.id
                            if interaction_author_id == ctx.author.id:
                                await interaction.defer(edit_origin=True)
                                action = interaction.custom_id
                                if action == 'continue':                                        
                                    embedTutorial4 = discord.Embed(
                                                title=f"🧙 Phase 3 -  Ramsay's Rampage 🧙‍♀️",
                                                description=f"*THE HUNT IS ON!*\n\n**Return Here Once You Have All FOUR Ingredients From Dobby!**",
                                                color=0xFCE303
                                            )
                                    await message.edit(embed=embedTutorial4, components=[])
                                elif action == "cancel":
                                    await message.delete()
                                    await asyncio.sleep(2)
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
    guild = client.get_guild(936698039941345370)
    items = ["Bat Ears", "Troll Snot", "Crow Feather", "Goblin Head"]
    random_channels = [random.choice(channel_list), random.choice(channel_list), random.choice(channel_list), random.choice(channel_list)]
    button = create_button(style=ButtonStyle.green, label="STEAL!", custom_id="continue")
    i = 0
    for channel in random_channels:
        embedHideAndSeek1 = discord.Embed(
            title=f"🍲 Dobby is found hiding... 🍲",
            description=f"*Click below to steal {items[i]} from him!*",
            color=0xFCE303
        )
        embedHideAndSeek2 = discord.Embed(
            title=f"🍲 YOU GRABBED {items[i]}! 🍲",
            description=f"*Dobby runs and hides in another channel...\n\nFind him to grab your next ingredient!*",
            color=0x28FF0A
        )
        channel = guild.get_channel(channel)
        action_row = create_actionrow(button)
        hunt_message = await channel.send(embed=embedHideAndSeek1, components=[action_row])
        while True:
            try:
                interaction: ComponentContext = await wait_for_component(client, components=action_row, timeout=20.0)
                interaction_author_id = interaction.author.id
                if interaction_author_id == ctx.author.id:
                    await interaction.defer(edit_origin=True)
                    action = interaction.custom_id
                    await hunt_message.edit(embed=embedHideAndSeek2, components=[])
                    await asyncio.sleep(5)
                    await hunt_message.delete()
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
                        description=f"Dobby Got Away!",
                        color=0xFF0000
                    )
                await hunt_message.edit(embed=embedTimeout, components=[])
                await hunt_message.delete()
                await message.delete()
                return             
        i += 1
    button1 = create_button(style=ButtonStyle.blurple, label="I GOT THEM ALL!!", custom_id="continue")
    action_row_main = create_actionrow(button1)
    await message.edit(embed=embedTutorial4, components=[action_row_main])
    while True:
        try:
            interaction: ComponentContext = await wait_for_component(client, components=action_row_main, timeout=60.0)
            interaction_author_id = interaction.author.id
            if interaction_author_id == ctx.author.id:
                await interaction.defer(edit_origin=True)
                action = interaction.custom_id
                embedTutorial4 = discord.Embed(
                            title=f"🧙 Phase 4 - Ramsay's Rampage 🧙‍♀️",
                            description=f"*Dobby The Elf respects your hustle...\n\nYou managed to steal all 4 ingredients from him successfully!*\n\n**Ingredients Acquired**\nBat Ears | Troll Snot | Crow Feather | Goblin Head",
                            color=0xFCE303
                        )
                
                button1 = create_button(style=ButtonStyle.blurple, label="Let's Cook This Goblin Stew!", custom_id="continue")
                button2 = create_button(style=ButtonStyle.red, label="I'm Afraid I'll Overcook It...", custom_id="cancel")
                action_row = create_actionrow(button1, button2)
                await message.edit(embed=embedTutorial4, components=[action_row])
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
    while True:
        try:
            interaction: ComponentContext = await wait_for_component(client, components=action_row, timeout=60.0)
            interaction_author_id = interaction.author.id
            if interaction_author_id == ctx.author.id:
                await interaction.defer(edit_origin=True)
                action = interaction.custom_id
                if action == "cancel":
                    await asyncio.sleep(2)
                    await message.delete()
                    return
                elif action == 'continue':
                    embedTutorial5 = discord.Embed(
                                title=f"🧙 Phase 5 - Ramsay's Rampage 🧙‍♀️",
                                description=f"*Cooking: Goblin Stew...*\n\n**In order to cook a goblin stew, you must follow these instructions:**\n\n*First place your Troll Snot in the pot\nSecond, add the Crow Feather to add flavor\nThen grind up the Bat Wings and add them in\nFinally, add the Goblin Head to make it a hearty stew!*",
                                color=0xFCE303
                            )                        
                    buttonconfirm = create_button(style=ButtonStyle.green, label="Ready To Cook!", custom_id="continue")
                    action_row_ready = create_actionrow(buttonconfirm)
                    await message.edit(embed=embedTutorial5, components=[action_row_ready])
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
    embedTutorialWrongIngredient = discord.Embed(
                title=f"🧙 Quest Failed! 🧙‍♀️",
                description=f"*OOPS! You used the wrong combination of ingredients...\n\nTry the quest again!*",
                color=0xFCE303
            )
    button1 = create_button(style=ButtonStyle.blurple, label="Bat Wings", custom_id="bat wings")
    button2 = create_button(style=ButtonStyle.blurple, label="Troll Snot", custom_id="troll snot")
    button3 = create_button(style=ButtonStyle.blurple, label="Crow Feather", custom_id="crow feather")
    button4 = create_button(style=ButtonStyle.blurple, label="Goblin Head", custom_id="goblin head")
    action_row = create_actionrow(button1, button2, button3, button4)
    while True:
        try:
            interaction: ComponentContext = await wait_for_component(client, components=action_row_ready, timeout=60.0)
            interaction_author_id = interaction.author.id
            if interaction_author_id == ctx.author.id:
                await interaction.defer(edit_origin=True)
                action = interaction.custom_id
                embedTutorial5 = discord.Embed(
                            title=f"🧙 Phase 6 - Ramsay's Rampage 🧙‍♀️",
                            description=f"*Cooking Goblin Stew...*🍲",
                            color=0xFCE303
                        )                        
                action_row_ready = create_actionrow(buttonconfirm)
                await message.edit(embed=embedTutorial5, components=[action_row])
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
    while True:
        try:
            interaction: ComponentContext = await wait_for_component(client, components=action_row, timeout=20.0)
            interaction_author_id = interaction.author.id
            if interaction_author_id == ctx.author.id:
                await interaction.defer(edit_origin=True)
                action = interaction.custom_id
                if action != "troll snot":
                    await message.edit(embed=embedTutorialWrongIngredient, components=[])
                    await asyncio.sleep(6)
                    await message.delete()
                    return
                button2["disabled"] = True
                await message.edit(components=[action_row])
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
    while True:
        try:
            interaction: ComponentContext = await wait_for_component(client, components=action_row, timeout=20.0)
            interaction_author_id = interaction.author.id
            if interaction_author_id == ctx.author.id:
                await interaction.defer(edit_origin=True)
                action = interaction.custom_id
                if action != "crow feather":
                    await message.edit(embed=embedTutorialWrongIngredient, components=[])
                    await asyncio.sleep(6)
                    await message.delete()
                    return
                button3["disabled"] = True
                await message.edit(components=[action_row])
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
    while True:
        try:
            interaction: ComponentContext = await wait_for_component(client, components=action_row, timeout=20.0)
            interaction_author_id = interaction.author.id
            if interaction_author_id == ctx.author.id:
                await interaction.defer(edit_origin=True)
                action = interaction.custom_id
                if action != "bat wings":
                    await message.edit(embed=embedTutorialWrongIngredient, components=[])
                    await asyncio.sleep(6)
                    await message.delete()
                    return
                button1["disabled"] = True
                await message.edit(components=[action_row])
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
    while True:
        try:
            interaction: ComponentContext = await wait_for_component(client, components=action_row, timeout=20.0)
            interaction_author_id = interaction.author.id
            if interaction_author_id == ctx.author.id:
                await interaction.defer(edit_origin=True)
                action = interaction.custom_id
                if action != "goblin head":
                    await message.edit(embed=embedTutorialWrongIngredient)
                    await asyncio.sleep(6)
                    await message.delete()
                    return
                embedTutorialCookingSuccessful1 = discord.Embed(
                    title=f"🧙 Quest Approval In Progress 🧙‍♀️",
                    description=f"*You approach Chef Ramsay full of anxiety and present him with your freshly made Goblin Stew...will he like it though???*",
                    color=0xFCE303
                )        
                await message.edit(embed=embedTutorialCookingSuccessful1, components=[])
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
    await asyncio.sleep(5)
    if random.randint(0,100) > 20:
        response2 = requests.get("https://img.buzzfeed.com/buzzfeed-static/static/2015-05/22/8/campaign_images/webdr06/gordon-ramsay-called-someone-an-idiot-sandwich-an-2-2831-1432296359-9_dblbig.jpg?resize=1200:*")
        image2 = Image.open(BytesIO(response2.content))
        size = (image1.width, image1.height)
        image2 = image2.resize(size)
        transparent_image = Image.new('RGBA', (image1.width + image2.width, max(image1.height, image2.height)), color=(0, 0, 0, 0))
        transparent_image.paste(image1, (0, 0))
        transparent_image.paste(image2, (image1.width, 0))
        buffer = BytesIO()
        transparent_image.save(buffer, format='PNG')
        buffer.seek(0)
        image_file = File(buffer, filename='transparent_image.png')
        embedTutorialCookingUnsuccessful2 = discord.Embed(
                    title=f"🧙 Quest Failed! 🧙‍♀️",
                    description=f"Chef Ramsay has a message for you after trying your dish...\n\n*{random.choice(ramsay_quote)}*",
                    color=0xFF0000
                )
        embedTutorialCookingUnsuccessful2.set_footer(text="That Chef is a meanie...give it another shot and he might be more accepting next time!")
        await message.delete()
        await ctx.send(file=image_file, embed=embedTutorialCookingUnsuccessful2)
        return
    embedTutorialCookinguccessful2 = discord.Embed(
                title=f"🧙 Quest Successful!! 🧙‍♀️",
                description=f"*Chef Ramsay approves of your Goblin Stew!\nPhew! That was a rush...*",
                color=0x28FF0A
            )     
    balance_ac1 = await get_balance(wallet, ac1_id)
    if balance_ac1 > 0:
        embedTutorialCookinguccessful2.set_footer(text=f"You have already received this achievement! Great work!")
        await message.edit(embed=embedTutorialCookinguccessful2)
        return
    await message.edit(embed=embedTutorialCookinguccessful2)
    await asyncio.sleep(3)
    txid = await send_assets("Congratulations! You completed Ramsay's Rampage quest and earned an achievement! The Order", fallen_order_main, wallet, ac1_id, "AC1", 1)
    txid2 = await send_assets("Congratulations! You completed Ramsay's Rampage quest and earned 250 $EXP! The Order", fallen_order_main, wallet, 811721471, "EXP", 250)
    embedAchievementClaimed = discord.Embed(
                title=f"🏆 Achievement Claimed! 🏆",
                url=f"https://algoexplorer.io/tx/{txid}",
                description=f"Congratulations! You earned the following reward for completing the quest:\n\nAchievement - Ramsay's Rampage\n250 $EXP",
                color=0x28FF0A
            )  
    embedAchievementClaimed.set_image(url=ac1_image)
    embedAchievementClaimed.set_footer(text="Let's collect more achievements!")
    embedAchievementClaimed.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
    await ctx.send(embed=embedAchievementClaimed)