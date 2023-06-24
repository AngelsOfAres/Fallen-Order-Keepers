from discord_slash import cog_ext, ComponentContext
from discord.ext import commands
import discord
import random
import time
import asyncio
from client import client
import requests
from txns import headersDG, graphql, get_wallet, get_balance, clawback_exp, add_games
from embeds import embedLeaderboard, embedWrongChannel, embedCD, embedErr
from discord_slash.utils.manage_components import create_actionrow, create_button, wait_for_component
from discord_slash.model import ButtonStyle

user_last_played = {}

class LeaderboardCog(commands.Cog):
    @cog_ext.cog_slash(name="leaderboard", description="Check Rankings for House Of Hermes!", options=[
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
                            "name": "Won",
                            "value": "won"
                        },
                        {
                            "name": "Lost",
                            "value": "lost"
                        },
                        {
                            "name": "EXP Won",
                            "value": "expwon"
                        },
                        {
                            "name": "EXP Lost",
                            "value": "explost"
                        }
                    ]
                }
            ])
    async def get_games(self, ctx, count, sortby):
        getgames = f"""
        query getGames {{
            queryDiscordWallets(order: {{desc: {sortby}}}) {{
                address
                name
                explost
                expwon
                id
                userid
                lost
                won
            }}
        }}
        """
        request = requests.post(graphql, json={'query': getgames}, headers=headersDG)
        result = request.json()

        counter = 0
        limit = count

        for field in result['data']['queryDiscordWallets']:
            if counter == limit:
                break
            if field['won'] == 0 or field['lost'] == 0 or field['expwon'] == 0 or field['explost'] == 0:
                continue
            else:
                print(count, limit, counter)
                embedLeaderboard.add_field(name=field['name'], value=f"Total Games - {field['won'] + field['lost']}\nW | L - {field['won']} | {field['lost']}\nW | L $EXP - {field['expwon']} | {field['explost']}\n P | L - {round(field['expwon']/field['explost'],3)}", inline=False)
            counter += 1

        await ctx.send(embed=embedLeaderboard)
        embedLeaderboard.clear_fields()

class StatsCog(commands.Cog):
    @cog_ext.cog_slash(name="stats", description="Check Your Personal Stats!")
    async def stats(self, ctx):
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
        if won == 0 or lost == 0 or expwon == 0 or explost == 0:
            embedNoStats = discord.Embed(
                    title=f"You don't have enough games to produce stats..",
                    description=f"Play a couple games and try again!",
                    color=0xFF1C0A
                )
            await ctx.send(embed=embedNoStats)
            return
        else:
            balance = await get_balance(wallet, 811721471)
            embedStats = discord.Embed(
                    title=f"Personal Stats - {name}",
                    description=f"Balance: {balance} $EXP",
                    color=0xFFFB0A
                )
            embedStats.add_field(name=f"Total Games: {won + lost}", value=f"Won: {won} | Lost: {lost}", inline=True)
            embedStats.add_field(name=f"Won/Lost $EXP: {expwon} | {explost}", value=f"P/L: {round(expwon/explost,3)}", inline=True)
            embedStats.set_footer(text=f"W/L Ratio: {round(won/lost,3)}")
            await ctx.send(embed=embedStats)


# vvvvvvvvv BLACKJACK vvvvvvvvvv
suits = ['♠️', '♥️', '♣️', '♦️']
values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

def new_deck():
    deck = [(value, suit) for value in values for suit in suits]
    random.shuffle(deck)
    return deck

def calculate_hand(hand):
    total = 0
    aces = 0
    for value, suit in hand:
        if value == 'A':
            aces += 1
            total += 11
        elif value in ['K', 'Q', 'J']:
            total += 10
        else:
            total += int(value)
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    return total

class BlackjackCog(commands.Cog):
    @cog_ext.cog_slash(name="blackjack", description="Play BlackJack with Hermes!", options=[
                    {
                        "name": "bet",
                        "description": "Bet Amount 10-100",
                        "type": 4,
                        "required": True,
                    }
                ])
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def blackjack(self, ctx, bet):
        user_id = ctx.author.id
        embedMax = discord.Embed(
                title=f"Your bet of {bet} is not allowed!",
                description=f"Please enter a bet amount 10-100",
                color=0xFF0000
            )
        if user_id not in user_last_played:
            user_last_played[user_id] = time.monotonic()
        else:
            time_diff = time.monotonic() - user_last_played[user_id]
            if time_diff >= 10:
                user_last_played[user_id] = time.monotonic()
            else:
                await ctx.send(embed=embedCD, hidden=True)
                return        
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
            balance = await get_balance(wallet, 811721471)

            if (bet >= 10 and bet <= 100):
                if balance == 0:
                    await ctx.send(embed=embedErr, hidden=True)
                elif balance < bet:
                    await ctx.send(embed=embedErr, hidden=True)
                else:
                    deck = new_deck()
                    player_hand = [deck.pop(), deck.pop()]
                    dealer_hand = [deck.pop()]

                    embedBJ = discord.Embed(title=f"🃏 Blackjack - {name}", description=f"Bet: {bet} $EXP", color=0x00ff00)
                    embedBJ.add_field(name=f"{name}'s hand - {calculate_hand(player_hand)}", value=f"{player_hand[0][0]} {player_hand[0][1]} | {player_hand[1][0]} {player_hand[1][1]}", inline=False)
                    embedBJ.add_field(name=f"Hermes' hand - {calculate_hand(dealer_hand)}", value=f"{dealer_hand[0][0]} {dealer_hand[0][1]}", inline=False)

                    message = await ctx.send(embed=embedBJ)
                    player_total = calculate_hand(player_hand)
                    await message.edit(embed=embedBJ)

                    while player_total < 21:
                        if balance < bet*2:
                            action_row = create_actionrow(
                                create_button(style=ButtonStyle.green, label="Hit", custom_id="hit"),
                                create_button(style=ButtonStyle.red, label="Stand", custom_id="stand")
                            )
                        else:
                            action_row = create_actionrow(
                                create_button(style=ButtonStyle.green, label="Hit", custom_id="hit"),
                                create_button(style=ButtonStyle.red, label="Stand", custom_id="stand"),
                                create_button(style=ButtonStyle.blurple, label="Double Down", custom_id="double_down")
                            )

                        await message.edit(components=[action_row])
                        try:
                            interaction: ComponentContext = await wait_for_component(client, components=action_row, timeout=10.0)
                            interaction_author_id = interaction.author.id

                            if interaction_author_id == ctx.author.id:
                                await interaction.defer(edit_origin=True)
                                action = interaction.custom_id
                                if action == "hit":
                                    player_hand.append(deck.pop())
                                    player_total = calculate_hand(player_hand)
                                    embedBJ.set_field_at(0, name=f"{name}'s hand - {player_total}", value=' | '.join([f'{v}{s}' for v, s in player_hand]))
                                    embedBJ.set_field_at(1, name=f"Hermes' hand - {calculate_hand(dealer_hand)}", value=f"{dealer_hand[0][0]} {dealer_hand[0][1]}")
                                    await message.edit(embed=embedBJ)
                                    if player_total > 21:
                                        break
                                elif action == "double_down":
                                    if bet == 0:
                                        bet = bet
                                    else:
                                        balance = await get_balance(wallet, 811721471)
                                        if balance < bet*2:
                                            await ctx.send(embed=embedErr)
                                            break
                                        else:
                                            bet *= 2
                                    player_hand.append(deck.pop())
                                    player_total = calculate_hand(player_hand)
                                    if bet == 0:
                                        embedBJ.description = f"Bet: {int(bet)} + {int(bet)} $EXP"
                                    else:
                                        embedBJ.description = f"Bet: {int(bet/2)} + {int(bet/2)} $EXP"
                                    embedBJ.set_field_at(0, name=f"{name}'s hand - {player_total}", value=' | '.join([f'{v}{s}' for v, s in player_hand]))
                                    embedBJ.set_field_at(1, name=f"Hermes' hand - {calculate_hand(dealer_hand)}", value=f"{dealer_hand[0][0]} {dealer_hand[0][1]}")
                                    await message.edit(embed=embedBJ)
                                    break
                                else:
                                    break
                            else:
                                embedWrongGame = discord.Embed(
                                    title=f"This is not your game!",
                                    description=f"{ctx.author.name} is currently playing..",
                                    color=0xFF0000
                                )
                                await interaction.reply(embed=embedWrongGame, hidden=True)
                        except asyncio.TimeoutError:
                            embedTimeout = discord.Embed(
                                    title=f"Woops! You took too long to respond...",
                                    description=f"Ending {ctx.author.name}'s game..",
                                    color=0xFF0000
                                )
                            await message.edit(embed=embedTimeout, components=[])
                            await asyncio.sleep(6)
                            await message.delete()
                            game_activebj = False
                            return
                    
                    
                    # Dealer's turn
                    dealer_total = calculate_hand(dealer_hand)
                    if player_total == 21:
                            newwon = won + 1
                            newlost = lost
                            newexpwon = expwon + bet
                            newexplost = explost
                            newbalance = balance + bet
                            embedBJ.set_footer(text=f"BLACKJACK!! {name} WON! 🔥 | New Balance: {newbalance} $EXP")
                            embedBJ.color = 0x28FF0A
                            await message.edit(embed=embedBJ, components=[])
                            clawback = "win"

                    elif len(player_hand) == 5 and player_total < 21:
                            newwon = won + 1
                            newlost = lost
                            newexpwon = expwon + bet
                            newexplost = explost
                            newbalance = balance + bet
                            embedBJ.set_footer(text=f"FIVE CARD AUTO-WIN by {name}! 🔥 | New Balance: {newbalance} $EXP")
                            embedBJ.color = 0x28FF0A
                            await message.edit(embed=embedBJ, components=[])
                            clawback = "win"
                    else:
                        if player_total > 21:
                            newbalance = balance - bet
                            newwon = won
                            newlost = lost + 1
                            newexpwon = expwon
                            newexplost = explost + bet
                            embedBJ.set_footer(text=f"{name} busted! Hermes wins! 😔 | New Balance: {newbalance} $EXP")
                            embedBJ.color = 0xFF1C0A
                            await message.edit(embed=embedBJ, components=[])
                            clawback = "loss"
                        
                        else:
                            while dealer_total < 17:
                                dealer_hand.append(deck.pop())
                                dealer_total = calculate_hand(dealer_hand)

                            dealer_hand_str = ' | '.join([f'{v}{s}' for v, s in dealer_hand])
                            embedBJ.set_field_at(0, name=f"{name}'s hand - {calculate_hand(player_hand)}", value=' '.join([f'{v}{s}' for v, s in player_hand]))
                            embedBJ.set_field_at(1, name=f"Hermes' hand - {calculate_hand(dealer_hand)}", value=dealer_hand_str)
                            await message.edit(embed=embedBJ)

                            if dealer_total > 21:
                                newbalance = balance + bet
                                newwon = won + 1
                                newlost = lost
                                newexpwon = expwon + bet
                                newexplost = explost
                                embedBJ.set_footer(text=f"Hermes' busted! {name} wins! 😎 | New Balance: {newbalance} $EXP")
                                embedBJ.color = 0x28FF0A
                                await message.edit(embed=embedBJ)
                                clawback = "win"
                            elif player_total > dealer_total:
                                newwon = won + 1
                                newlost = lost
                                newexpwon = expwon + bet
                                newexplost = explost
                                newbalance = balance + bet
                                embedBJ.set_footer(text=f"{name} wins! 🔥 | New Balance: {newbalance} $EXP")
                                embedBJ.color = 0x28FF0A
                                await message.edit(embed=embedBJ)
                                clawback = "win"
                            elif dealer_total > player_total:
                                newbalance = balance - bet
                                newwon = won
                                newlost = lost + 1
                                newexpwon = expwon
                                newexplost = explost + bet
                                embedBJ.set_footer(text=f"Hermes wins! 😈 | New Balance: {newbalance} $EXP")
                                embedBJ.color = 0xFF1C0A
                                await message.edit(embed=embedBJ)
                                clawback = "loss"
                            else:
                                newbalance = balance
                                newwon = won
                                newlost = lost
                                newexpwon = expwon
                                newexplost = explost
                                embedBJ.set_footer(text=f"It's a push! 🎯 | New Balance: {newbalance} $EXP")
                                embedBJ.color = 0xFFFB0A
                                await message.edit(embed=embedBJ)
                                clawback = None
                        
                    await message.edit(components=[])
                    game_activebj = False
                    await add_games(wallet, newwon, newlost, newexpwon, newexplost)
                    if clawback is not None:
                        await clawback_exp(wallet, bet, clawback)

            else:
                await ctx.send(embed=embedMax, hidden=True)        
    @blackjack.error
    async def drip_claim_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(embed=embedCD, hidden=True)
                
    # ^^^^^^^^^ BLACKJACK ^^^^^^^^^^

class RPSLSCog(commands.Cog):
    @cog_ext.cog_slash(name="rps", description="Rock, Paper, Scissors, Lizard, SPOCK!", options=[
                {
                    "name": "rps",
                    "description": "Rock/Paper/Scissors",
                    "type": 3,
                    "required": True,
                    "choices": [
                        {
                            "name": "Rock",
                            "value": "Rock"
                        },
                        {
                            "name": "Paper",
                            "value": "Paper"
                        },
                        {
                            "name": "Scissors",
                            "value": "Scissors"
                        },
                        {
                            "name": "Lizard",
                            "value": "Lizard"
                        },
                        {
                            "name": "Spock",
                            "value": "Spock"
                        }
                    ]
                },
                {
                    "name": "bet",
                    "description": "Bet Amount",
                    "type": 4,
                    "required": True,
                }
            ])
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def rps(self, ctx, rps, bet):
        if ctx.channel.id != 1078081577701089411:
            await ctx.send(embed=embedWrongChannel, hidden=True)
        else:
            user_id = ctx.author.id
            embedMax = discord.Embed(
                    title=f"Your bet of {bet} is not allowed!",
                    description=f"Please enter a bet amount 1-1000",
                    color=0xFF0000
                )

            if user_id not in user_last_played:
                user_last_played[user_id] = time.monotonic()
            else:
                time_diff = time.monotonic() - user_last_played[user_id]
                if time_diff >= 10:
                    user_last_played[user_id] = time.monotonic()
                else:
                    await ctx.send(embed=embedCD, hidden=True)
                    return
            rpsBot = ["Rock", "Paper", "Scissors"]
            randomChoice = random.choice(rpsBot)
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
                balance = await get_balance(wallet, 811721471)
                if (bet <= 1000):
                    embedLoss = discord.Embed(
                        title=f"<@{ctx.author.id}>'s {rps} got wrecked...what a LOSS 😔",
                        description=f"Bet: {bet} $EXP",
                        color=0xFF1C0A
                    )
                    embedTie = discord.Embed(
                        title=f"<@{ctx.author.id}> & Hermes both play {rps}...it's a TIE! 🎯",
                        description=f"Bet: {bet} $EXP",
                        color=0xFFFB0A
                    )
                    embedWin = discord.Embed(
                        title=f"<@{ctx.author.id}>'s {rps} destroys Hermes' {randomChoice}...a WIN by fate! 🔥",
                        description=f"Bet: {bet} $EXP",
                        color=0x28FF0A
                    )

                    if balance == 0:
                        await ctx.send(embed=embedErr, hidden=True)
                    elif balance < bet:
                        await ctx.send(embed=embedErr, hidden=True)
                    else:
                        if rps == randomChoice:
                            clawback = None
                            newwon = won
                            newexpwon = expwon
                            newlost = lost
                            newexplost = explost
                            embedTie.add_field(name=f"{name} - {rps}", value=f'Hermes - {randomChoice}', inline=True)
                            embedTie.set_footer(text=f"New Balance: {balance} $EXP")
                            embedFinal=embedTie
                        elif (rps == "Rock" and (randomChoice == "Scissors" or randomChoice == "Lizard")) or (rps == "Paper" and (randomChoice == "Rock" or randomChoice == "Spock")) or (rps == "Scissors" and (randomChoice == "Paper" or randomChoice == "Lizard")) or (rps == "Lizard" and (randomChoice == "Paper")) or (rps == "Spock" and (randomChoice == "Rock")):
                            clawback = "win"
                            new_balance = balance + bet
                            newwon = won + 1
                            newexpwon = expwon + bet
                            newlost = lost
                            newexplost = explost
                            embedWin.add_field(name=f"{name} - {rps}", value=f'Hermes - {randomChoice}', inline=True)
                            embedWin.set_footer(text=f"New Balance: {new_balance} $EXP")
                            embedFinal=embedWin
                        else:
                            clawback = "loss"
                            new_balance = balance - bet
                            newwon = won
                            newexpwon = expwon
                            newlost = lost + 1
                            newexplost = explost + bet
                            embedLoss.add_field(name=f"Hermes - {randomChoice}", value=f'{name} - {rps}', inline=True)
                            embedLoss.set_footer(text=f"New Balance: {new_balance} $EXP")
                            embedFinal=embedLoss
                        
                        await ctx.send(embed=embedFinal)
                        if clawback is not None:
                            await clawback_exp(wallet, bet, clawback)
                        await add_games(wallet, newwon, newlost, newexpwon, newexplost)

                else:
                    await ctx.send(embed=embedMax, hidden=True)
    @rps.error
    async def drip_claim_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(embed=embedCD, hidden=True)


class DiceCog(commands.Cog):
    @cog_ext.cog_slash(name="dice", description="Play Dice With Hermes!", options=[
                    {
                        "name": "bet",
                        "description": "Bet Amount",
                        "type": 4,
                        "required": True
                    }
                ])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def roll(self, ctx, bet):
        if ctx.channel.id != 1042200246962364606:
            await ctx.send(embed=embedWrongChannel, hidden=True)
        else:
            user_id = ctx.author.id
            if user_id not in user_last_played:
                user_last_played[user_id] = time.monotonic()
            else:
                time_diff = time.monotonic() - user_last_played[user_id]
                if time_diff >= 10:
                    user_last_played[user_id] = time.monotonic()
                else:
                    await ctx.send(embed=embedCD, hidden=True)
                    return

            user_rand_num = random.randint(1, 100)
            rand_num = random.randint(1, 100)
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
                balance = await get_balance(wallet, 811721471)
                embedMax = discord.Embed(
                    title=f"Your bet of {bet} is not allowed!",
                    description=f"Please enter a bet amount 1-420",
                    color=0xFF0000,
                )

                if (bet <= 420):
                    embedLoss = discord.Embed(
                        title=f"<@{ctx.author.id}> rolls against Hermes...{name} lost 😔",
                        description=f"Bet: {bet} $EXP",
                        color=0xFF1C0A
                    )
                    embedTie = discord.Embed(
                        title=f"BULLSEYE!!! <@{ctx.author.id}> rolls against Hermes...{name} DOUBLED their bet! 🎯",
                        description=f"Bet: {bet} $EXP",
                        color=0xFFFB0A
                    )
                    embedWin = discord.Embed(
                        title=f"<@{ctx.author.id}> rolls against Hermes...{name} WON! 🔥",
                        description=f"Bet: {bet} $EXP",
                        color=0x28FF0A
                    )

                    if balance == 0:
                        await ctx.send(embed=embedErr, hidden=True)
                    elif balance < bet:
                        await ctx.send(embed=embedErr, hidden=True)
                    else:
                        if user_rand_num < rand_num:
                            clawback = "loss"
                            new_balance = balance - bet
                            newlost = lost+1
                            newexplost = explost + bet
                            newwon = won
                            newexpwon = expwon
                            embedLoss.add_field(name=f"Hermes - {rand_num}", value=f'{name} - {user_rand_num}', inline=True)
                            embedLoss.add_field(name="New Balance: ", value=f"{new_balance} $EXP", inline=True)
                            embedFinal=embedLoss
                        elif user_rand_num == rand_num:
                            clawback = "tie"
                            new_balance = balance + bet*2
                            newwon = won + 1
                            newexpwon = expwon + bet
                            newlost = lost
                            newexplost = explost
                            embedTie.add_field(name=f"{name} - {user_rand_num}", value=f'Hermes - {rand_num}', inline=True)
                            embedTie.add_field(name="New Balance: ", value=f"{new_balance} $EXP", inline=True)
                            embedFinal=embedTie
                        else:
                            clawback = "win"
                            new_balance = balance + bet
                            newwon = won + 1
                            newexpwon = expwon + bet
                            newlost = lost
                            newexplost = explost
                            embedWin.add_field(name=f"{name} - {user_rand_num}", value=f'Hermes - {rand_num}', inline=True)
                            embedWin.add_field(name="New Balance: ", value=f"{new_balance} $EXP", inline=True)
                            embedFinal=embedWin
                        
                        await ctx.send(embed=embedFinal)
                        await clawback_exp(wallet, bet, clawback)
                        await add_games(wallet, newwon, newlost, newexpwon, newexplost)
                else:
                    await ctx.send(embed=embedMax, hidden=True)
    @roll.error
    async def drip_claim_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(embed=embedCD, hidden=True)

def setup(client: client):
    client.add_cog(LeaderboardCog(client))
    client.add_cog(StatsCog(client))
    client.add_cog(BlackjackCog(client))
    client.add_cog(DiceCog(client))
    client.add_cog(RPSLSCog(client))

