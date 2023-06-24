from discord_slash import cog_ext
from discord.ext import commands
from txns import get_wallet
import asyncio
from embeds import *
import discord
import pytz
from datetime import datetime
import random
from client import client
from txns import *
from whitelist import ghosts, ghostsIcons, fo_rank1, fo_rank2, fo_rank3, fo_rank4, fo_rank5

sign_ups = []
def get_guild():
    guild = client.get_guild(936698039941345370)
    return guild

guild = get_guild()

class DripCog(commands.Cog):
    @cog_ext.cog_slash(name="drip", description="Drips Out 1-5 $EXP Every 6 Hours!")
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def drip_claim(self, ctx):
        if ctx.channel.id == 937750181154279485 or ctx.channel.id == 936801867340582982:
            await ctx.send(embed=embedWrongChannelDrip, hidden=True)
            return
        else:
            userid = str(ctx.author.id)
            wallet, name, won, lost, expwon, explost, lastdrip, drip_exp = await get_wallet(userid)
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
                if balance == -1:
                    await ctx.send(embed=embedNoOptEXP)
                    return
                else:
                    utc = pytz.timezone('UTC')
                    lastdrip_datetime = datetime.strptime(lastdrip, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=utc)
                    now = datetime.now(utc)
                    time_diff = now - lastdrip_datetime
                    total_seconds = time_diff.total_seconds()
                    if total_seconds < 6 * 60 * 60:
                        next_claim = ((60*60*6) - total_seconds)
                        timer = ((datetime.utcfromtimestamp(next_claim)).strftime('%HH %MM %SS')).lstrip('0')
                        if timer.startswith("H "):
                            dt = timer[2:]
                        else:
                            dt = timer
                        embedNoDrip = discord.Embed(
                            title=f"You have already made a drip claim less than 6 hours ago!",
                            description=f"Please come back when your timer resets...",
                            color=0xFF1C0A,
                            )
                        embedNoDrip.set_footer(text=f"Next Claim In {dt} ⏱️")
                        await ctx.send(embed=embedNoDrip, hidden=True)
                        return
                    else:
                        exp = [1, 2, 3, 4, 5]
                        random_exp = random.choice(exp)
                        new_exp = int(drip_exp + random_exp)
                        current_time = (datetime.now(utc)).strftime('%Y-%m-%dT%H:%M:%SZ')
                        txnid = await send_assets("Angels Of Ares", fallen_order_main, wallet, 811721471, "EXP", random_exp)
                        embedDrip.add_field(name=f"Dripped out {random_exp} $EXP to <@{ctx.author.id}>!", value=f"[Txn Link](https://algoexplorer.io/tx/{txnid})", inline=True)
                        await ctx.send(embed=embedDrip)
                        embedDrip.clear_fields()
                        await add_drip(wallet, current_time, new_exp)
    @drip_claim.error
    async def drip_claim_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(embed=embedCD, hidden=True)

class WingRevenueCog(commands.Cog):
    @cog_ext.cog_slash(name="wing-revenue", description="Admin Use Only!")
    async def wing_count(self, ctx):
        await ctx.defer()
        if ctx.author.id != 805453439499894815:
            await ctx.send(embed=embedAdminOnly)
            return
        else:
            totalwings = 0
            send_data = []
            wallets = await get_all_wallets()

            for wallet in wallets:
                wingscount = 0
                if wallet["address"] != "AOAZMP5WTCCHOPKZZICV5KEZ7IH6BRFIDI47ONQU42QNOTTAW4ACZVXDHA":
                    account_info = algod_client.account_info(wallet['address'])
                    assets = account_info.get("assets", [])

                    for asset in assets:
                        if asset["amount"] > 0 and asset["asset-id"] in angel_wings:
                            wingscount = asset["amount"]
                
                if wingscount != 0:
                    send_data.append([wallet["address"], wingscount, wallet["userid"]])

                totalwings += wingscount
                current_time = (datetime.now()).strftime('%Y-%m-%dT%H:%M:%SZ')
                await update_wings(wallet["address"], current_time, wingscount)

        totalwings_with_angel = int(totalwings*1.33333)
        payment_per_wing = round(350/totalwings_with_angel, 3)
        embedAW.set_footer(text=f"All Algorand Drops Are Successful! 🧙‍♂️")
        await send_revenue(send_data, payment_per_wing)
        
        embedAW.add_field(name=f"View Revenue Wallet Below:", value=f"[AlgoExplorer Link](https://algoexplorer.io/address/{angel_wings_wallet})", inline=False)
        embedAW.add_field(name=f"-----------------------------------------------", value="", inline=False)
        embedAW.add_field(name=f"Total Staked Angel Wings", value=f"{totalwings_with_angel}", inline=False)
        embedAW.add_field(name=f"Payment Sent Per Angel Wing", value=f"{payment_per_wing}A", inline=False)
        await ctx.send(embed=embedAW)
        embedAW.clear_fields()
        send_data = []
        
    
class StakingCog(commands.Cog):
    @cog_ext.cog_slash(name="admin-staking-drop", description="Admin Use Only!")
    async def send_staking(self, ctx):
        if ctx.author.id != 805453439499894815:
            await ctx.send(embed=embedAdminOnly)
            return
        else:
            embedStaking = discord.Embed(
                    title="Staking Rewards Drop Commencing...",
                    color=0xFF1C0A,
                )
            embedStaking.set_footer(text=f"Please wait while I gather The Order and The Ghosts Of Algo 🧙‍♂️")
            message = await ctx.send(embed=embedStaking)
            send_data = []
            wallets = await get_all_wallets()
            total_staked = 0
            total_staked_ghosts = 0
            total_order_sent = 0
            total_exp_sent = 0
            for wallet in wallets:
                if wallet["address"] != "AOAZMP5WTCCHOPKZZICV5KEZ7IH6BRFIDI47ONQU42QNOTTAW4ACZVXDHA":
                    account_info = algod_client.account_info(wallet['address'])
                    assets = account_info.get("assets", [])

                    ghostcount = 0
                    ghosticoncount = 0
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

                count = fo_1count + fo_2count + fo_3count + fo_4count + fo_5count
                ghosts_final_count = ghostcount + ghosticoncount
                total_exp = ghostcount + (ghosticoncount*5) + (fo_1count*3) + (fo_2count*5) + (fo_3count*8) + (fo_4count*12) + (fo_5count*25)
                total_order = count
                send_data.append([wallet["address"], count, ghosts_final_count, total_order, total_exp])
                total_staked += count
                total_staked_ghosts += ghosts_final_count
                total_order_sent += total_order
                total_exp_sent += total_exp

        await staking_rewards(send_data)
        embedStaking = discord.Embed(
                    title="Staking Rewards Drop Complete!",
                    color=0xFF1C0A,
                )
        embedStaking.add_field(name=f"Staked Fallen Order", value=f"{total_staked}", inline=False)
        embedStaking.add_field(name=f"Staked Ghosts Of Algo", value=f"{total_staked_ghosts}", inline=False)
        embedStaking.add_field(name=f"Total Staking Rewards Sent", value=f"{total_order_sent} $ORDER | {total_exp_sent} $EXP", inline=False)
        embedStaking.set_footer(text=f"Play some games and upgrade your characters! 🧙‍♂️")
        embedStaking.set_image(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        await message.edit(embed=embedStaking)
        send_data = []

class BuyTicketsCog(commands.Cog):
    @cog_ext.cog_slash(name="tickets", description="Buy $RAFFLE Tickets With ORDER/EXP", options=[
                    {
                        "name": "payment",
                        "description": "Payment Currency",
                        "type": 3,
                        "required": True,
                        "choices": [
                            {
                                "name": "ORDER",
                                "value": "ORDER"
                            },
                            {
                                "name": "EXP",
                                "value": "EXP"
                            }
                        ]
                    },
                    {
                        "name": "amount",
                        "description": "Amount Of Tickets To Buy",
                        "type": 4,
                        "required": True
                    }
                ])
    async def buy_tickets(self, ctx, payment, amount):
        if payment == "ORDER":
            token_id = 811718424
            cost = amount * 5
        elif payment == "EXP":
            token_id = 811721471
            cost = amount * 50
        sender = ctx.author.id
        sender_name = ctx.author.name
        wallet, name, won, lost, expwon, explost, lastdrip, drip_exp = await get_wallet(sender)

        if wallet == '':
            embedNoReg = discord.Embed(
                    title="Click Here To Register!",
                    url="https://app.fallenorder.xyz",
                    description=f"Please verify your wallet via our website to continue..\nEnsure you copy your user id below for the verification process:\nUser ID: {ctx.author.id}",
                    color=0xFF1C0A,
                )
            await ctx.send(embed=embedNoReg)
        else:
            sender_balance = await get_balance(wallet, token_id)
            sender_balance_raffle = await get_balance(wallet, 815766197)
            
            if sender_balance == 0:
                await ctx.send(embed=embedErr, hidden=True)
            elif sender_balance < amount:
                await ctx.send(embed=embedErr, hidden=True)
            else:
                txnid = await send_assets(sender_name, wallet, fallen_order_main, token_id, payment, cost)
                txnid2 = await send_assets("Fallen Order Raffles", fallen_order_main, wallet, 815766197, "RAFFLE", amount)
                new_sender_bal = sender_balance - cost
                new_sender_bal_raffle = sender_balance_raffle + amount
                embedPurchased = discord.Embed(
                        title=f"I have transformed {cost} ${payment} into {amount} $RAFFLE Tickets for <@{sender}>",
                        description=f"[Payment Txn](https://algoexplorer.io/tx/{txnid}) | [Receipt Txn](https://algoexplorer.io/tx/{txnid2})",
                        color=0xFFFB0A
                    )
                embedPurchased.set_footer(text=f"New ${payment} Balance: {new_sender_bal}\nNew $RAFFLE Balance: {new_sender_bal_raffle}")
                embedPurchased.set_image(url="https://nft-media.algoexplorerapi.io/images/bafkreiabe7amkqwuz6kip7xnx6c5bx7v73bw2qofuaoqhu23nufrwfnn4e")
                await ctx.send(embed=embedPurchased)
                return
            
class BuyEXPCog(commands.Cog):
    @cog_ext.cog_slash(name="orderexp", description="Swap $ORDER for $EXP", options=[
                    {
                        "name": "amount",
                        "description": "Amount Of ORDER To Swap",
                        "type": 4,
                        "required": True
                    }
                ])
    async def buy_tickets(self, ctx, amount):
        exp_amount = amount * 10
        sender = str(ctx.author.id)
        sender_name = ctx.author.name
        wallet, name, won, lost, expwon, explost, lastdrip, drip_exp = await get_wallet(sender)

        if wallet == '':
            embedNoReg = discord.Embed(
                    title="Click Here To Register!",
                    url="https://app.fallenorder.xyz",
                    description=f"Please verify your wallet via our website to continue..\nEnsure you copy your user id below for the verification process:\nUser ID: {ctx.author.id}",
                    color=0xFF1C0A,
                )
            await ctx.send(embed=embedNoReg)
        else:
            sender_balance_exp = await get_balance(wallet, 811721471)
            sender_balance_order = await get_balance(wallet, 811718424)
            
            if sender_balance_order == 0:
                await ctx.send(embed=embedErr, hidden=True)
            elif sender_balance_order < amount:
                await ctx.send(embed=embedErr, hidden=True)
            else:
                txnid = await send_assets(sender_name, wallet, fallen_order_main, 811718424, "ORDER", amount)
                txnid2 = await send_assets("Token Swap. The Order", fallen_order_main, wallet, 811721471, "EXP", exp_amount)
                new_sender_bal_order = sender_balance_order - amount
                new_sender_bal_exp = sender_balance_exp + exp_amount
                embedSwapped = discord.Embed(
                        title=f"I have swapped {amount} $ORDER to {exp_amount} $EXP on <@{sender}>'s behalf",
                        description=f"[Payment Txn](https://algoexplorer.io/tx/{txnid}) | [Receipt Txn](https://algoexplorer.io/tx/{txnid2})",
                        color=0xFFFB0A
                    )
                embedSwapped.set_footer(text=f"New $ORDER Balance: {new_sender_bal_order}\nNew $EXP Balance: {new_sender_bal_exp}")
                embedSwapped.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
                await ctx.send(embed=embedSwapped)

class SendTokensCog(commands.Cog):
    @cog_ext.cog_slash(name="send", description="Send EXP/ORDER/RAFFLE/Logs to other users", options=[
                    {
                        "name": "user",
                        "description": "Receiving User",
                        "type": 6,
                        "required": True
                    },
                    {
                        "name": "token",
                        "description": "Token To Send",
                        "type": 3,
                        "required": True,
                        "choices": [
                            {
                                "name": "EXP",
                                "value": "EXP"
                            },
                            {
                                "name": "RAFFLE",
                                "value": "RAFFLE"
                            },
                            {
                                "name": "ORDER",
                                "value": "ORDER"
                            },
                            {
                                "name": "Oak Logs",
                                "value": "Oak Logs"
                            }
                        ]
                    },
                    {
                        "name": "amount",
                        "description": "Amount To Send",
                        "type": 4,
                        "required": True
                    }
                ])
    async def send(self, ctx, user, token, amount):
        if token == "ORDER":
            token_id = 811718424
        elif token == "EXP":
            token_id = 811721471
        elif token == "RAFFLE":
            token_id = 815766197
        elif token == "Oak Logs":
            token_id = 1064863037
        sender = str(ctx.author.id)
        receiver = str(user.id)
        receiver_name = user.name
        sender_name = ctx.author.name
        wallet1, name1, won1, lost1, expwon1, explost1, lastdrip1, drip_exp1 = await get_wallet(sender)
        wallet2, name2, won2, lost2, expwon2, explost2, lastdrip1, drip_exp1 = await get_wallet(receiver)
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
            sender_balance = await get_balance(wallet1, token_id) 
            receiver_balance = await get_balance(wallet2, token_id)            
            if sender_balance == -1 or receiver_balance == -1:
                if token == "ORDER":
                    await ctx.send(embed=embedNoOptORDER)
                if token == "EXP":
                    await ctx.send(embed=embedNoOptEXP)
                if token == "RAFFLE":
                    await ctx.send(embed=embedNoOptRAFFLE)
                if token == "Oak Logs":
                    embedNoOpt = discord.Embed(
                        title=f"You are not opted into Oak Logs!",
                        description=f"Please [click here](https://www.randgallery.com/algo-collection/?address=1064863037) to opt in and try again...",
                        color=0xFF0000
                    )
                    embedNoOpt.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
                    await ctx.send(embed=embedNoOpt)
            elif sender_balance == 0:
                await ctx.send(embed=embedErr, hidden=True)
            elif sender_balance < amount:
                await ctx.send(embed=embedErr, hidden=True)
            else:
                if token == "Oak Logs":
                    txnid = await trade_logs(sender_name, wallet1, wallet2, 1064863037, amount)
                else:
                    txnid = await send_assets(sender_name, wallet1, wallet2, token_id, token, amount)
                new_sender_bal = sender_balance - amount
                new_receiver_bal = receiver_balance + amount
                embedSent = discord.Embed(
                        title=f"I have bestowed {amount} ${token} upon <@{receiver}>",
                        description=f"Sent By: <@{sender}> 💛 [Txn Link](https://algoexplorer.io/tx/{txnid})",
                        color=0xFFFB0A
                    )
                embedSent.set_footer(text=f"{sender_name}'s New Balance: {new_sender_bal} ${token}\n{receiver_name}'s New Balance: {new_receiver_bal} ${token}")
                await ctx.send(embed=embedSent)

class AdminSendCog(commands.Cog):
    @cog_ext.cog_slash(name="admin-send", description="ADMIN ONLY! Send EXP/ORDER/RAFFLE to other users", options=[
                    {
                        "name": "sender",
                        "description": "Receiving Address",
                        "type": 3,
                        "required": True
                    },
                    {
                        "name": "receiver",
                        "description": "Receiving Address",
                        "type": 3,
                        "required": True
                    },
                    {
                        "name": "token",
                        "description": "Token To Send",
                        "type": 3,
                        "required": True,
                        "choices": [
                            {
                                "name": "EXP",
                                "value": "EXP"
                            },
                            {
                                "name": "RAFFLE",
                                "value": "RAFFLE"
                            },
                            {
                                "name": "ORDER",
                                "value": "ORDER"
                            }
                        ]
                    },
                    {
                        "name": "amount",
                        "description": "Amount To Send",
                        "type": 4,
                        "required": True
                    }
                ])
    async def admin_clawback(self, ctx, sender, receiver, token, amount):
        if ctx.author.id != 805453439499894815:
            await ctx.send(embed=embedAdminOnly)
            return
        else:
            if token == "ORDER":
                token_id = 811718424
            elif token == "EXP":
                token_id = 811721471
            elif token == "RAFFLE":
                token_id = 815766197
            
            sender_balance = await get_balance(sender, token_id) 
            receiver_balance = await get_balance(receiver, token_id)
            sender_short = sender[:5] + "..." + sender[-5:]
            receiver_short = receiver[:5] + "..." + receiver[-5:]
            
            if sender_balance == -1 or receiver_balance == -1:
                if token == "ORDER":
                    await ctx.send(embed=embedNoOptORDER)
                if token == "EXP":
                    await ctx.send(embed=embedNoOptEXP)
            elif sender_balance == 0:
                await ctx.send(embed=embedErr)
            elif sender_balance < amount:
                await ctx.send(embed=embedErr)
            else:
                new_sender_bal = sender_balance - amount
                new_receiver_bal = receiver_balance + amount
                txnid = await send_assets(sender_short, sender, receiver, token_id, token, amount)
                embedSent = discord.Embed(
                        title=f"I have bestowed {amount} ${token} upon {receiver_short}",
                        description=f"Sent By: {sender_short} 💛 [Txn Link](https://algoexplorer.io/tx/{txnid})",
                        color=0xFFFB0A
                    )
                embedSent.set_footer(text=f"{sender_short}'s New Balance: {new_sender_bal} ${token}\n{receiver_short}'s New Balance: {new_receiver_bal} ${token}")
                await ctx.send(embed=embedSent)

class ManualSendTokensCog(commands.Cog):
    @cog_ext.cog_slash(name="manual-send", description="Send EXP/ORDER/RAFFLE to a specific address!", options=[
                    {
                        "name": "address",
                        "description": "Receiving Wallet Address",
                        "type": 3,
                        "required": True
                    },
                    {
                        "name": "token",
                        "description": "Token To Send",
                        "type": 3,
                        "required": True,
                        "choices": [
                            {
                                "name": "EXP",
                                "value": "EXP"
                            },
                            {
                                "name": "RAFFLE",
                                "value": "RAFFLE"
                            },
                            {
                                "name": "ORDER",
                                "value": "ORDER"
                            }
                        ]
                    },
                    {
                        "name": "amount",
                        "description": "Amount To Send",
                        "type": 4,
                        "required": True
                    }
                ])
    async def manual_send(self, ctx, address, token, amount):
        if token == "ORDER":
            token_id = 811718424
        elif token == "EXP":
            token_id = 811721471
        elif token == "RAFFLE":
            token_id = 815766197
        sender = str(ctx.author.id)
        sender_name = ctx.author.name
        wallet, name, won, lost, expwon, explost, lastdrip, drip_exp = await get_wallet(sender)

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
            sender_balance = await get_balance(wallet, token_id)
            receiver_balance = await get_balance(address, token_id)
            if sender_balance == -1 or receiver_balance == -1:
                if token == "ORDER":
                    await ctx.send(embed=embedNoOptORDER)
                elif token == "EXP":
                    await ctx.send(embed=embedNoOptEXP)
                else:
                    await ctx.send(embed=embedNoOptRAFFLE)
            elif sender_balance == 0:
                await ctx.send(embed=embedErr, hidden=True)
            elif sender_balance < amount:
                await ctx.send(embed=embedErr, hidden=True)
            else:
                txnid = await send_assets(sender_name, wallet, address, token_id, token, amount)
                new_sender_bal = sender_balance - amount
                embedSent = discord.Embed(
                        title=f"I have bestowed {amount} ${token} upon {address}",
                        description=f"Sent By: <@{sender}> 💛 [Txn Link](https://algoexplorer.io/tx/{txnid})",
                        color=0xFFFB0A
                    )
                embedSent.set_footer(text=f"{sender_name}'s New Balance: {new_sender_bal} ${token}")
                await ctx.send(embed=embedSent)
                return

class BalanceCog(commands.Cog):
    @cog_ext.cog_slash(name="balance", description="Check Your On Chain Balances!")
    async def get_all_balances(self, ctx):
        await ctx.defer()
        wallet, name, won, lost, expwon, explost, lastdrip, drip_exp = await get_wallet(str(ctx.author.id))
        if wallet == '':
                embedNoReg = discord.Embed(
                    title="Click Here To Register!",
                    url="https://app.fallenorder.xyz",
                    description=f"Please verify your wallet via our website to continue..\nEnsure you copy your user id below for the verification process:\nUser ID: {ctx.author.id}",
                    color=0xFF1C0A,
                )
                await ctx.send(embed=embedNoReg)
                game_active -= 1
                return

        account_info = algod_client.account_info(wallet)
        assets = account_info.get("assets", [])

        ghostcount = 0
        ghosticoncount = 0
        wingcount = 0
        aoa = 0
        order = 0
        exp = 0
        raffle = 0
        ghost = 0
        fo_1count = 0
        fo_2count = 0
        fo_3count = 0
        fo_4count = 0
        fo_5count = 0

        for asset in assets:
            if asset["amount"] > 0 and asset["asset-id"] in angel_wings:
                wingcount = asset["amount"]
            if asset["asset-id"] == balance_list[0]:
                aoa = asset["amount"]
            if asset["asset-id"] == balance_list[1]:
                order = asset["amount"]
            if asset["asset-id"] == balance_list[2]:
                exp = asset["amount"]
            if asset["asset-id"] == balance_list[3]:
                raffle = asset["amount"]
            if asset["asset-id"] == balance_list[4]:
                ghost = asset["amount"]/10000
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
            if asset["amount"] > 0 and asset["asset-id"] in ghosts:
                ghostcount += 1
            if asset["amount"] > 0 and asset["asset-id"] in ghostsIcons:
                ghosticoncount += 1
        
        balances = [aoa, order, exp, raffle, ghost]
        balances_formatted = []

        for balance in balances:
            if balance >= 1000000000:
                formatted_bal = f"{balance / 1000000000:.3f}B"
            elif balance >= 1000000000:
                formatted_bal = f"{balance / 1000000:.3f}M"
            elif balance >= 1000000:
                formatted_bal = f"{balance / 1000000:.3f}M"
            elif balance >= 1000:
                formatted_bal = f"{balance / 1000:.3f}K"
            else:
                formatted_bal = str(balance)

            balances_formatted.append(formatted_bal)

        embedBalances = discord.Embed(
                    title=f"Current Holdings - {ctx.author.name}",
                    url=f"https://algoexplorer.io/address/{wallet}",
                    color=0xFCE303
                )
        embedBalances.add_field(name=f"AoA", value=f"{balances_formatted[0]}", inline=False)
        embedBalances.add_field(name=f"ORDER", value=f"{balances_formatted[1]}", inline=False)
        embedBalances.add_field(name=f"EXP", value=f"{balances_formatted[2]}", inline=False)
        embedBalances.add_field(name=f"RAFFLE", value=f"{balances_formatted[3]} Tickets", inline=False)
        embedBalances.add_field(name=f"GHOST", value=f"{balances_formatted[4]}", inline=False)
        embedBalances.add_field(name=f"Angel Wings", value=f"{wingcount}", inline=False)
        embedBalances.add_field(name=f"Fallen Order", value=f"{fo_1count} Angel | {fo_2count} Celestial | {fo_3count} Ethereal | {fo_4count} Empyreal | {fo_5count} Immortal ", inline=False)
        embedBalances.add_field(name=f"Ghosts Of Algo", value=f"{ghostcount} Ghosties | {ghosticoncount} Icon", inline=False)
        embedBalances.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        embedBalances.set_footer(text=f"*Holdings displayed are on chain and real time*", icon_url="https://s3.amazonaws.com/algorand-wallet-mainnet-thumbnails/prism-images/media/asset_verification_requests_logo_png/2022/06/22/d2c56a8e61244bd78017e38180d15c91.png--resize--w__200--q__70.webp")

        await ctx.send(embed=embedBalances)
    
def setup(client: client):
    client.add_cog(DripCog(client))
    client.add_cog(WingRevenueCog(client))
    client.add_cog(StakingCog(client))
    client.add_cog(BuyTicketsCog(client))
    client.add_cog(BuyEXPCog(client))
    client.add_cog(SendTokensCog(client))
    client.add_cog(AdminSendCog(client))
    client.add_cog(ManualSendTokensCog(client))
    client.add_cog(BalanceCog(client))

