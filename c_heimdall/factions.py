from discord_slash import cog_ext
from discord.ext import commands
from embeds import *
import discord
import json
import base64
import asyncio
from discord_slash.utils.manage_components import create_actionrow, create_button, wait_for_component
from discord_slash.model import ButtonStyle
from discord_slash import ComponentContext
from client import client
from txns import *

light_treasury = ""
dark_treasury = ""

class AddToTreasuryCog(commands.Cog):
    @cog_ext.cog_slash(name="treasury-donation", description="Donate EXP/ORDER/RAFFLE/Logs to your Faction Treasury!", options=[
                    {
                        "name": "token",
                        "description": "Token To Donate",
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
    async def treasury_donate(self, ctx, token, amount):
        if token == "ORDER":
            token_id = 811718424
        elif token == "EXP":
            token_id = 811721471
        elif token == "RAFFLE":
            token_id = 815766197
        elif token == "Oak Logs":
            token_id = 1064863037
        sender = str(ctx.author.id)
        sender_name = ctx.author.name
        wallet1, main_character, equipped_hatchet = await get_main_char(sender)
        if wallet1 == '':
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
            if sender_balance == -1:
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
                if main_character == 0:
                    embedNoMain = discord.Embed(
                        title=f"Main Character Not Selected",
                        description=f"Use /main-character to assign your main!",
                        color=0xFCE303
                    )
                    embedNoMain.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
                    await ctx.send(embed=embedNoMain)
                    return
                metadata_api = f"https://mainnet-idx.algonode.cloud/v2/transactions?tx-type=acfg&asset-id={main_character}&address={fallen_order_manager}"
                response = requests.get(metadata_api)
                if response.status_code == 200:
                    data = response.json()
                else:
                    print("Error fetching data from API")
                metadata_decoded = (json.loads((base64.b64decode((data["transactions"][0]["note"]).encode('utf-8'))).decode('utf-8')))
                faction = metadata_decoded["properties"]["Faction"]
                if faction == "Light":
                    treasury = light_treasury
                    heart = "🤍"
                elif faction == "Dark":
                    treasury = dark_treasury
                    heart = "🖤"
                if token == "Oak Logs":
                    await trade_logs(sender_name, wallet1, treasury, 1064863037, amount)
                else:
                    await send_assets(sender_name, wallet1, treasury, token_id, token, amount)
                new_sender_bal = sender_balance - amount
                embedSent = discord.Embed(
                        title=f"Donation of {amount} ${token} made to the {faction} Treasury!",
                        description=f"{heart} Donated By: <@{sender}> {heart}\n\n[View Treasury](https://algoexplorer.io/address/{treasury})",
                        color=0xFFFB0A
                    )
                embedSent.set_footer(text=f"{sender_name}'s New Balance: {new_sender_bal} ${token}\nThe {faction} side appreciates your efforts {sender} {heart}\n\nTogether We Rise!")
                await ctx.send(embed=embedSent)

class RemoveFromTreasuryCog(commands.Cog):
    @cog_ext.cog_slash(name="treasury-removal", description="Initiate Request To Remove EXP/ORDER/RAFFLE/Logs from your Faction Treasury!", options=[
                    {
                        "name": "receiver",
                        "description": "Receiving Address",
                        "type": 3,
                        "required": True
                    },
                    {
                        "name": "token",
                        "description": "Token To Remove",
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
    async def treasury_remove(self, ctx, receiver, token, amount):
        if token == "ORDER":
            token_id = 811718424
        elif token == "EXP":
            token_id = 811721471
        elif token == "RAFFLE":
            token_id = 815766197
        elif token == "Oak Logs":
            token_id = 1064863037
        sender = ctx.author.id
        sender_name = ctx.author.name
        wallet1, main_character, equipped_hatchet = await get_main_char(sender)
        sender_balance_order = await get_balance(wallet1, 811718424)
        if wallet1 == '':
            embedNoReg = discord.Embed(
                    title="Click Here To Register!",
                    url="https://app.fallenorder.xyz",
                    description=f"Please verify your wallet via our website to continue..\nEnsure you copy your user id below for the verification process:\nUser ID: {ctx.author.id}",
                    color=0xFF1C0A,
                )
            await ctx.send(embed=embedNoReg)
            return
        else:
            sender_balance = await get_balance(receiver, 811718424)           
            if sender_balance == -1:
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
            if main_character == 0:
                embedNoMain = discord.Embed(
                    title=f"Main Character Not Selected",
                    description=f"Use /main-character to assign your main!",
                    color=0xFCE303
                )
                embedNoMain.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
                await ctx.send(embed=embedNoMain)
                return
            metadata_api = f"https://mainnet-idx.algonode.cloud/v2/transactions?tx-type=acfg&asset-id={main_character}&address={fallen_order_manager}"
            response = requests.get(metadata_api)
            if response.status_code == 200:
                data = response.json()
            else:
                print("Error fetching data from API")
            metadata_decoded = (json.loads((base64.b64decode((data["transactions"][0]["note"]).encode('utf-8'))).decode('utf-8')))
            faction = metadata_decoded["properties"]["Faction"]
            if faction == "Light":
                treasury = light_treasury
                color = 0xFFFFFF
            elif faction == "Dark":
                treasury = dark_treasury
                color = 0x000000
            casters = []
            required_order = 10000
            total_order_delegated = sender_balance_order
            string = ""
            embedRemovalInProgress = discord.Embed(
                                    title=f"🧙 TREASURY REMOVAL IN PROGRESS 🧙‍♀️",
                                    description=f"**REQUEST**\n\n**Proposed By** - <@{sender}>\n\n**Amount:** {amount} ${token}\n\n**Receiving Address:**\n{receiver}",
                                    color=color
                                )
            embedRemovalInProgress.set_footer(text=f"\n$ORDER Required To Pass: 10000\nCurrent $ORDER Delegated: {total_order_delegated}\n\nIf you approve of this removal proposal, you may delegate your ORDER by clicking CAST")
            embedRemovalInProgress.add_field(name=f"Delegators:", value=f"{string}", inline=False)
            message = await ctx.send(embed=embedRemovalInProgress, components=[])
            i = 1
            while total_order_delegated < required_order:
                await asyncio.sleep(1)
                button = create_button(style=ButtonStyle.red, label="CAST!", custom_id="cast")
                action_row = create_actionrow(button)
                await message.edit(embed=embedRemovalInProgress, components=[action_row])
                try:
                    interaction: ComponentContext = await wait_for_component(client, components=action_row, timeout=120.0)
                    interaction_author_id = interaction.author.id
                    if interaction_author_id != sender and interaction_author_id not in casters:
                        button["disabled"] = True
                        button["style"] = ButtonStyle.green
                        button["label"] = "CASTED!"
                        wallet_caster, main_character2, equipped_hatchet = await get_main_char(str(interaction_author_id))
                        if wallet1 == '':
                            embedNoReg = discord.Embed(
                                    title="Click Here To Register!",
                                    url="https://app.fallenorder.xyz",
                                    description=f"Please verify your wallet via our website to continue..\nEnsure you copy your user id below for the verification process:\nUser ID: {ctx.author.id}",
                                    color=0xFF1C0A,
                                )
                            await interaction.send(embed=embedNoReg, hidden=True)
                            return
                        metadata_api = f"https://mainnet-idx.algonode.cloud/v2/transactions?tx-type=acfg&asset-id={main_character2}&address={fallen_order_manager}"
                        response = requests.get(metadata_api)
                        if response.status_code == 200:
                            data = response.json()
                        else:
                            print("Error fetching data from API")
                        metadata_decoded = (json.loads((base64.b64decode((data["transactions"][0]["note"]).encode('utf-8'))).decode('utf-8')))
                        faction2 = metadata_decoded["properties"]["Faction"]
                        if faction2 != faction:
                            embedNoReg = discord.Embed(
                                    title="This is not your faction treasury removal!",
                                    color=0xFF0000,
                                )
                            await interaction.send(embed=embedNoReg, hidden=True)
                            return
                        caster_balance_order = await get_balance(wallet_caster, 811718424)
                        if caster_balance_order == -1:
                            await interaction.send(embed=embedNoOptORDER, hidden=True)
                            break
                        else:
                            await interaction.defer(edit_origin=True)
                            casters.append(interaction_author_id)
                            total_order_delegated += caster_balance_order
                            i += 1
                            if total_order_delegated >= required_order:
                                if token == "Oak Logs":
                                    await trade_logs(sender_name, treasury, receiver, 1064863037, amount)
                                else:
                                    await send_assets(sender_name, treasury, receiver, token_id, token, amount)
                                embedRemovalSuccessful = discord.Embed(
                                    title=f"🧙 TREASURY REMOVAL SUCCESSFUL 🧙‍♀️",
                                    description=f"*Ritual In Progress...!\n\nThe Temple grounds shake as a blinding light shines from the shrine...*",
                                    color=color
                                )
                                await message.edit(embed=embedRemovalSuccessful, components=[])
                                return
                            string += f"<@{interaction_author_id}>" + "\n"
                            embedRemovalInProgress.set_footer(text=f"\n$ORDER Required To Pass: 10000\nCurrent $ORDER Delegated: {total_order_delegated}\n\nIf you approve of this removal proposal, you may delegate your ORDER by clicking CAST")
                            embedRemovalInProgress.set_field_at(0, name=f"Delegators:", value=f"{string}", inline=False)
                            await message.edit(embed=embedRemovalInProgress, components=[action_row])
                        continue
                    else:
                        embedWrongUpgrade = discord.Embed(
                            title=f"You Already Delegated Your $ORDER!",
                            description=f"*Awaiting delegated amount to reach {required_order} threshold...*",
                            color=0xFF0000
                        )
                        await interaction.send(embed=embedWrongUpgrade, hidden=True)
                        continue
                except asyncio.TimeoutError:
                    embedTimeout = discord.Embed(
                            title=f"Woops! You took too long to respond...",
                            description=f"Removal Request Denied! Gather voters faster next time, you have 5 minutes total to cast all votes.",
                            color=0xFF0000
                        )
                    await message.edit(embed=embedTimeout, components=[])
                    await asyncio.sleep(10)
                    return

def setup(client: client):
    client.add_cog(AddToTreasuryCog(client))
    client.add_cog(RemoveFromTreasuryCog(client))