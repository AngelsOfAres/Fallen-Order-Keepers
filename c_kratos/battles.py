from discord_slash import cog_ext
from discord.ext import commands
from txns import get_wallet
import asyncio
from embeds import *
import discord
import random
from client import client
from txns import *
from whitelist import ghosts, ghostsIcons, fo_rank1, fo_rank2, fo_rank3, fo_rank4, fo_rank5
import requests
import discord
from discord_slash.utils.manage_components import create_actionrow, create_actionrow, create_button, wait_for_component
import time
import asyncio
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageOps
from discord_slash import ComponentContext
from discord_slash.model import ButtonStyle
import random
from embeds import *
from txns import *
from client import client
from whitelist import fo_rank1, fo_rank2, fo_rank3, fo_rank4, fo_rank5

sign_ups = []
drip_on = False

class PvPBattleCog(commands.Cog):
    @cog_ext.cog_slash(name="battle", description="PvP Battle With Fallen Order!", options=[
                    {
                        "name": "bet",
                        "description": "Bet Amount",
                        "type": 4,
                        "required": True
                    }])
    async def pvp_battle(self, ctx, bet):
        if ctx.channel.id != 1080360866467287140:
            await ctx.send(embed=embedNotBattleChannel)
            return
        if bet > 1000:
            embedMax = discord.Embed(
                    title=f"Your bet of {bet} is not allowed!",
                    description=f"Please enter a bet amount 1-1000",
                    color=0xFF1C0A,
                )
            await ctx.send(embed=embedMax, hidden=True)
            return
        embedBattle = discord.Embed(
                    title=f"{ctx.author.name} is looking for a battle!",
                    description=f"Bet: {bet} $EXP",
                    color=discord.Color(random.randint(0, 0xFFFFFF))
                )
        
        embedBattle.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        message = await ctx.send(embed=embedBattle)
        player1 = str(ctx.author.id)
        player1_name = ctx.author.name
        action_row = create_actionrow(
                        create_button(style=ButtonStyle.blurple, label="Battle!", custom_id="battle")
                    )

        await message.edit(components=[action_row])
        try:
            while True:
                interaction: ComponentContext = await wait_for_component(client, components=action_row, timeout=60)
                await interaction.defer(edit_origin=True)
                if interaction.author.id != ctx.author.id:
                    player2_name = interaction.author.name
                    embedBattle2 = discord.Embed(
                                title=f"⌛ Battle Commencing...GOOD LUCK!",
                                description=f"Bet: {bet} $EXP",
                                color=discord.Color(random.randint(0, 0xFFFFFF))
                            )
                    embedBattle2.add_field(name=f"Round #1 starting....GOOD LUCK!", value=f"{player1_name} VS {player2_name}", inline=False)
                    embedBattle2.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
                    await message.edit(embed=embedBattle2, components=[])
                    player2 = str(interaction.author.id)

                    wallet1, name1, won1, lost1, expwon1, explost1, lastdrip1, drip_exp1 = await get_wallet(player1)
                    wallet2, name2, won2, lost2, expwon2, explost2, lastdrip2, drip_exp12= await get_wallet(player2)
                    if wallet1 == '' or wallet2 == '':
                        embedNoReg = discord.Embed(
                            title="Click Here To Register!",
                            url="https://app.fallenorder.xyz",
                            description=f"Please verify your wallet via our website to continue..\nEnsure you copy your user id below for the verification process:\nUser ID: {ctx.author.id}",
                            color=0xFF1C0A,
                        )
                        await ctx.send(embed=embedNoReg)
                        return
                    else:
                        player1_balance = await get_balance(wallet1, 811721471) 
                        player2_balance = await get_balance(wallet2, 811721471)
                        both_chosen_fallen = []
                        if player1_balance == -1 or player2_balance == -1:
                            await message.delete()
                            await ctx.send(embed=embedNoOptEXP)
                            return
                        
                        if player1_balance == 0 or player2_balance == 0:
                            await message.delete()
                            await ctx.send(embed=embedErr)
                            return
                        elif player1_balance < bet  or player2_balance < bet:
                            await message.delete()
                            await ctx.send(embed=embedErr)
                            return
                        else:
                            i = 0
                            for wallet in [wallet1, wallet2]:
                                fallen_assets = []
                                account_info = algod_client.account_info(wallet)
                                assets = account_info.get("assets", [])
                                for asset in assets:
                                    if asset["asset-id"] in fo_rank1 or asset["asset-id"] in fo_rank2 or asset["asset-id"] in fo_rank3 or asset["asset-id"] in fo_rank4 or asset["asset-id"] in fo_rank5:
                                        fallen_assets.append(asset['asset-id'])
                                
                                if fallen_assets == []:
                                    await message.delete()
                                    if i == 0:
                                        player = player1_name
                                    elif i == 1:
                                        player = player2_name
                                    embedNoFO = discord.Embed(
                                        title=f"Awwwwww..{player} does not own any Fallen Order!",
                                        description=f"[Click Here To Shuffle!](https://algoxnft.com/shuffle/902)",
                                        color=0xFF0000
                                    )
                                    await ctx.send(embed=embedNoFO)
                                    return

                                i += 1
                                
                                chosen_fallen = random.choice(fallen_assets)
                                asset_info = algod_client.asset_info(chosen_fallen)
                                
                                both_chosen_fallen.append(asset_info)

                            fallen_image_1_ipfs = both_chosen_fallen[0]["params"]["url"]
                            fallen_name_1_raw = both_chosen_fallen[0]["params"]["unit-name"]
                            fallen_image_2_ipfs = both_chosen_fallen[1]["params"]["url"]
                            fallen_name_2_raw = both_chosen_fallen[1]["params"]["unit-name"]
                            string_to_remove = "FO"
                            fallen_name_1 = fallen_name_1_raw.replace(string_to_remove, "#")
                            fallen_name_2 = fallen_name_2_raw.replace(string_to_remove, "#")

                            fallen_image_1_url = "https://ipfs.algonft.tools/ipfs/" + (fallen_image_1_ipfs).replace("ipfs://", "")
                            fallen_image_2_url = "https://ipfs.algonft.tools/ipfs/" + (fallen_image_2_ipfs).replace("ipfs://", "")
                            
                            response1 = requests.get(fallen_image_1_url)
                            image1 = Image.open(BytesIO(response1.content))
                            response2 = requests.get(fallen_image_2_url)
                            image2 = Image.open(BytesIO(response2.content))
                            padding = 600
                            text_color_list = [(255, 38, 150), (204, 38, 255), (38, 237, 255), (38, 255, 71), (255, 226, 38), (255, 99, 38)]
                            text_color = random.choice(text_color_list)
                            transparent_image = Image.new('RGBA', (image1.width + image2.width + padding, max(image1.height + 500, image2.height + 500)), color=(0, 0, 0, 0))
                            transparent_image.paste(image1, (0, 0))
                            transparent_image.paste(ImageOps.mirror(image2), (image1.width + padding, 0))
                            font = ImageFont.truetype("fonts/myfont.ttf", 240)
                            fontSmall = ImageFont.truetype("fonts/myfont.ttf", 200)
                            draw = ImageDraw.Draw(transparent_image)
                            text_width = font.getlength("VS")
                            text_x = int(((image1.width + image2.width + padding) - text_width) / 2)
                            text_y = int(((max(image1.height, image2.height)) - text_width) / 2)
                            draw.text((text_x, text_y), "VS", font=font, fill=text_color)
                            text_width3 = fontSmall.getlength(fallen_name_1)
                            text_width4 = fontSmall.getlength(fallen_name_2)
                            text_width1 = fontSmall.getlength(player1_name)
                            text_width2 = fontSmall.getlength(player2_name)
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
                            draw.text((text_x1, text_y1), player1_name, font=fontSmall, fill=text_color)
                            draw.text((text_x2, text_y2), player2_name, font=fontSmall, fill=text_color)
                            draw.text((text_x3, text_y3), fallen_name_1, font=fontSmall, fill=text_color)
                            draw.text((text_x4, text_y4), fallen_name_2, font=fontSmall, fill=text_color)
                            with BytesIO() as image_binary:
                                transparent_image.save(image_binary, 'PNG')
                                image_binary.seek(0)
                                embedBattle2.title = "🔥 BATTLE IS ON! 🔥"
                                try:
                                    await message.edit(file=discord.File(fp=image_binary, filename='transparent_image.png'), embed=embedBattle2)
                                except discord.errors.HTTPException as e:
                                    await message.edit(embed=embedDiscordErr)
                                    await asyncio.sleep(10)
                                    await message.delete()
                                    return
                            
                            round = 1
                            player1_hp = 500
                            player2_hp = 500

                            while player1_hp > 0 and player2_hp > 0:
                                player1_attack = random.randint(50,130)
                                player2_defense = random.randint(30, 100)
                                if player2_defense >= player1_attack:
                                    embedBattle2.set_field_at(0, name=f"Round #{round}", value=f"{player2_name} defended {player1_name}'s attack!", inline=False)
                                    embedBattle2.set_footer(text=f"{player1_name}'s HP: {player1_hp}  |  {player2_name}'s HP: {player2_hp}")
                                    round += 1
                                    await message.edit(embed=embedBattle2)
                                elif player2_defense < player1_attack:
                                    total_damage = player1_attack - player2_defense
                                    player2_hp -= total_damage
                                    embedBattle2.set_field_at(0, name=f"Round #{round}", value=f"{player1_name} attacked {player2_name} for {total_damage} damage!", inline=False)
                                    embedBattle2.set_footer(text=f"{player1_name}'s HP: {player1_hp}  |  {player2_name}'s HP: {player2_hp}")
                                    round += 1
                                    await message.edit(embed=embedBattle2)
                                
                                if player1_hp <= 0:
                                    txid = await send_assets(player1_name, wallet1, wallet2, 811721471, "EXP", bet)
                                    embedBattle2.set_field_at(0, name=f"Congrats! That was awesome!", value=f"[{bet} $EXP sent from {player1_name} to {player2_name}](https://algoexplorer.io/tx/{txid})", inline=False)
                                    embedBattle2.title = "🔥 " + player2_name + " WON! 🔥"
                                    embedBattle2.set_footer(text=f"💀 {player1_name}'s HP: {player1_hp}  |  {player2_name}'s HP: {player2_hp} 💪")
                                    await message.edit(embed=embedBattle2)
                                    return

                                elif player2_hp <= 0:
                                    txid = await send_assets(player2_name, wallet2, wallet1, 811721471, "EXP", bet)
                                    embedBattle2.set_field_at(0, name=f"Congrats! That was awesome!", value=f"[{bet} $EXP sent from {player2_name} to {player1_name}](https://algoexplorer.io/tx/{txid})", inline=False)
                                    embedBattle2.title = "🔥 " + player1_name + " WON! 🔥"
                                    embedBattle2.set_footer(text=f"💪 {player1_name}'s HP: {player1_hp} |  {player2_name}'s HP: {player2_hp} 💀")
                                    await message.edit(embed=embedBattle2)
                                    return
                                
                                time.sleep(2)
                                
                                player2_attack = random.randint(50, 130)
                                player1_defense = random.randint(30, 100)
                                if player1_defense >= player2_attack:
                                    embedBattle2.set_field_at(0, name=f"Round #{round}", value=f"{player1_name} defended {player2_name}'s attack!", inline=False)
                                    embedBattle2.set_footer(text=f"{player1_name}'s HP: {player1_hp}  |  {player2_name}'s HP: {player2_hp}")
                                    round += 1
                                    await message.edit(embed=embedBattle2)
                                elif player1_defense < player2_attack:
                                    total_damage = player2_attack - player1_defense
                                    player1_hp -= total_damage
                                    embedBattle2.set_field_at(0, name=f"Round #{round}", value=f"{player2_name} attacked {player1_name} for {total_damage} damage!", inline=False)
                                    embedBattle2.set_footer(text=f"{player1_name}'s HP: {player1_hp}  |  {player2_name}'s HP: {player2_hp}")
                                    round += 1
                                    await message.edit(embed=embedBattle2)
                                
                                time.sleep(2)
                            
                                if player1_hp <= 0:
                                    txid = await send_assets(player1_name, wallet1, wallet2, 811721471, "EXP", bet)
                                    embedBattle2.set_field_at(0, name=f"Congrats! That was awesome!", value=f"[{bet} $EXP sent from {player1_name} to {player2_name}](https://algoexplorer.io/tx/{txid})", inline=False)
                                    embedBattle2.title = "🔥 " + player2_name + " WON! 🔥"
                                    embedBattle2.set_footer(text=f"💀 {player1_name}'s HP: {player1_hp}  |  {player2_name}'s HP: {player2_hp} 💪")
                                    await message.edit(embed=embedBattle2)
                                    return

                                elif player2_hp <= 0:
                                    txid = await send_assets(player2_name, wallet2, wallet1, 811721471, "EXP", bet)
                                    embedBattle2.set_field_at(0, name=f"Congrats! That was awesome!", value=f"[{bet} $EXP sent from {player2_name} to {player1_name}](https://algoexplorer.io/tx/{txid})", inline=False)
                                    embedBattle2.title = "🔥 " + player1_name + " WON! 🔥"
                                    embedBattle2.set_footer(text=f"💪 {player1_name}'s HP: {player1_hp} |  {player2_name}'s HP: {player2_hp} 💀")
                                    await message.edit(embed=embedBattle2)
                                    return
                else:
                    await message.edit(embed=embedNoSelfBattle, components=[])
                    return
        except asyncio.TimeoutError:
            embedTimeout = discord.Embed(
                    title=f"Woops! You took too long to respond...",
                    description=f"Ending {ctx.author.name}'s battle..",
                    color=0xFF0000
                )
            await message.edit(embed=embedTimeout, components=[])
            await asyncio.sleep(10)
            await message.delete()



class DeathmatchCog(commands.Cog):
    @cog_ext.cog_slash(name="deathmatch", description="Enter The Daily Great War!")
    async def death_match(self, ctx):
        if ctx.channel.id != 1080746370429898832:
            await ctx.send(embed=embedNotDeathmatchChannel)
            return
        global sign_ups
        userid = str(ctx.author.id)
        wallet, name, won, lost, expwon, explost, lastdrip, drip_exp = await get_wallet(userid)
        
        fallen_assets = []
        account_info = algod_client.account_info(wallet)
        assets = account_info.get("assets", [])
        for asset in assets:
            if asset["amount"] > 0 and (asset["asset-id"] in fo_rank1 or asset["asset-id"] in fo_rank2 or asset["asset-id"] in fo_rank3 or asset["asset-id"] in fo_rank4 or asset["asset-id"] in fo_rank5):
                fallen_assets.append(asset['asset-id'])
        
        if fallen_assets == []:
            await ctx.send(embed=embedNoFallen)
            return
        else:
            if any(userid == info[1] for info in sign_ups):
                embedAlreadySigned = discord.Embed(
                    title=f"{ctx.author.name} is already signed up for the Death Match! ⚔️",
                    color=discord.Color(random.randint(0, 0xFFFFFF))
                )
                embedAlreadySigned.set_footer(text=f"Battle will commence once 5 players have signed up! Current Sign Ups: {len(sign_ups)}")
                await ctx.send(embed=embedAlreadySigned)
                return
            else:
                balance = await get_balance(wallet, 811721471)
                if balance == -1:
                    await ctx.send(embed=embedNoOptEXP)
                    return
                if balance == 0 or balance < 50:
                    await ctx.send(embed=embedErr)
                    return
                txid = await deathmatch_clawback(wallet)
                sign_ups.append([ctx.author.name, str(ctx.author.id), 200, 0])
                random_fallen = random.choice(fallen_assets)
                fallen_info = algod_client.asset_info(random_fallen)
                fallen_asset_id = fallen_info["index"]
                metadata_api = f"https://mainnet-idx.algonode.cloud/v2/transactions?tx-type=acfg&asset-id={fallen_asset_id}"
                response = requests.get(metadata_api)
                if response.status_code == 200:
                    data = response.json()
                else:
                    print("Error fetching data from API")
                asset_info = algod_client.asset_info(fallen_asset_id)
                fallen_image_url = asset_info["params"]["url"]
                fallen_image = "https://ipfs.algonft.tools/ipfs/" + (fallen_image_url).replace("ipfs://", "")
                embedSignedUp = discord.Embed(
                    title=f"⚔️ {ctx.author.name} entered Death Match! ⚔️",
                    description=f"[View Details](https://nftexplorer.app/asset/{random_fallen}) | [Entry Txn](https://algoexplorer.io/tx/{txid})",
                    color=discord.Color(random.randint(0, 0xFFFFFF))
                )
                embedSignedUp.set_footer(text=f"Death Match will commence once 5 players have signed up | Current Sign Ups: {len(sign_ups)}")
                embedSignedUp.set_image(url=f"{fallen_image}")
                await ctx.send(embed=embedSignedUp)
                
                if len(sign_ups) == 5:
                    await asyncio.sleep(5)
                    embedCommencing = discord.Embed(
                        title=f"⌛ DEATH MATCH COMMENCING IN 30 SECS!",
                        description=f"Ares slowly awakens from his slumber...the Fallen Order prepare for battle..",
                        color=0xFF0000
                    )
                    string = ""
                    for user in sign_ups:
                        string += "\n" + "<@" + user[1] + ">"
                    
                    embedCommencing.add_field(name=f"⚔️ Fallen Order Battlers ⚔️", value=f"{string}", inline=False)
                    message = await ctx.send(embed=embedCommencing)
                    await asyncio.sleep(30)

                    embedCommencing.title = "⚔️ DEATH MATCH IS ON! ⚔️"
                    embedCommencing.description = "250 $EXP goes to higher damage dealer"
                    embedCommencing.remove_field(0)
                    
                    game_on = True

                    while game_on:
                        field_id = 0
                        for user in sign_ups:
                            total_damage_caused = 0
                            round = 1
                            embedCommencing.add_field(name=f"Ares defended {user[0]}'s attack!", value=f"{user[0]}'s total damage: {total_damage_caused}", inline=False)

                            while user[2] > 0:
                                player_attack = random.randint(50, 130)
                                player_defense = random.randint(30, 100)
                                ares_attack = random.randint(50, 130)
                                ares_defense = random.randint(30, 100)
                                if ares_defense >= player_attack:
                                    embedCommencing.set_field_at(field_id, name=f"Ares defended {user[0]}'s attack!", value=f"{user[0]}'s total damage: {total_damage_caused}", inline=False)
                                    await message.edit(embed=embedCommencing)
                                elif ares_defense < player_attack:
                                    total_damage = player_attack - ares_defense
                                    total_damage_caused += total_damage
                                    embedCommencing.set_field_at(field_id, name=f"{user[0]} attacked Ares for {total_damage} damage!", value=f"{user[0]}'s total damage: {total_damage_caused}", inline=False)
                                    await message.edit(embed=embedCommencing)
                                
                                await asyncio.sleep(2)

                                if player_defense >= ares_attack:
                                    embedCommencing.set_field_at(field_id, name=f"{user[0]} defended Ares' attack!", value=f"{user[0]}'s total damage: {total_damage_caused}", inline=False)
                                    await message.edit(embed=embedCommencing)
                                elif player_defense < ares_attack:
                                    total_damage = ares_attack - player_defense
                                    user[2] -= total_damage
                                    embedCommencing.set_field_at(field_id, name=f"Ares attacked {user[0]} for {total_damage} damage!", value=f"{user[0]}'s total damage: {total_damage_caused}", inline=False)
                                    await message.edit(embed=embedCommencing)
                                round += 1

                                await asyncio.sleep(2)
                            
                            embedCommencing.set_field_at(field_id, name=f"{user[0]} fought for {round} rounds!", value=f"{user[0]}'s total damage: {total_damage_caused}", inline=False)
                            await message.edit(embed=embedCommencing)
                            field_id += 1
                            user[3] = total_damage_caused

                        sign_ups.sort(key=lambda x: x[3], reverse=True)
                        wallet, name, won, lost, expwon, explost, lastdrip, drip_exp = await get_wallet(sign_ups[0][1])
                        txid = await send_assets("Deathmatch battlers", fallen_order_main, wallet, 811721471, "EXP", 250)
                        i = 1
                        while i <= field_id:
                            if i == 1:
                                embedCommencing.set_field_at(i-1, name=f"🔥 {sign_ups[i-1][0]} dealt the most damage! 💪", value=f"Total Damage: {sign_ups[i-1][3]}", inline=False)
                            elif i == 2:
                                embedCommencing.set_field_at(i-1, name=f"{sign_ups[i-1][0]} put up a great fight...close call! 😰", value=f"Total Damage: {sign_ups[i-1][3]}", inline=False)
                            else:
                                embedCommencing.set_field_at(i-1, name=f"{sign_ups[i-1][0]} got rekt! 💀", value=f"Total Damage: {sign_ups[i-1][3]}", inline=False)
                            i += 1
                        embedCommencing.title = f"🏆 WHAT A BATTLE! CONGRATS TO {sign_ups[0][0]} 🏆"
                        embedCommencing.description = f"[250 $EXP sent to {sign_ups[0][0]}!](https://algoexplorer.io/tx/{txid})"
                        await message.edit(embed=embedCommencing)
                        sign_ups = []


class AdminDeathmatchSignupCog(commands.Cog):
    @cog_ext.cog_slash(name="add-sign-ups", description="Manually Sign Up Users For Death Match", options=[
                    {
                        "name": "user",
                        "description": "User To Sign Up",
                        "type": 6,
                        "required": True
                    }
                ])
    async def manual_sign_up(self, ctx, user):
        global sign_ups
        if ctx.author.id != 805453439499894815 and ctx.author.id != 666410598178750516:
            await ctx.send(embed=embedAdminOnly)
            return

        sign_ups.append([user.name, str(user.id), 50, 0])
        embedManualSignUp = discord.Embed(
                    title=f"Master, I have signed <@{user.id}> up for Death Match 🧙‍♂️",
                    description=f"They are ready for battle..",
                    color=0x28FF0A
                )
        embedManualSignUp.set_footer(text=f"Current Sign Ups: {sign_ups}")
        await ctx.send(embed=embedManualSignUp)


class SignUpsCog(commands.Cog):
    @cog_ext.cog_slash(name="sign-ups", description="List Current Sign Ups")
    async def sign_ups_display(self, ctx):
        global sign_ups
        i = 1
        for sign_up in sign_ups:
            embedCurrentSignUps.add_field(name=f"Warrior #{i}", value=f'<@{sign_up[1]}>', inline=False)
            i += 1
        if len(sign_ups) == 0:
            await ctx.send(embed=embedNoSignUps)
            return
        await ctx.send(embed=embedCurrentSignUps)
        embedCurrentSignUps.clear_fields()

def setup(client: client):
    client.add_cog(PvPBattleCog(client))
    client.add_cog(DeathmatchCog(client))
    client.add_cog(AdminDeathmatchSignupCog(client))
    client.add_cog(SignUpsCog(client))

