from discord_slash import cog_ext
from discord.ext import commands
from embeds import *
import discord
import json
import base64
import asyncio
from discord.utils import get
from discord_slash.utils.manage_components import create_actionrow, create_button, wait_for_component
from discord_slash.model import ButtonStyle
from discord_slash import ComponentContext
from client import client
from txns import *
from embeds import embedAdminOnly

channel_list = [936808094414045204, 936801867340582982, 1012036883976564786, 1081221312011309127, 1082157256679882862, 1080360866467287140, 1080746370429898832, 1087215342297813072, 1083208605303574609, 1042200246962364606, 1078081795943305217]
main_channel = 936801867340582982
light_treasury = ""
dark_treasury = ""

class TreasuryRaidCog(commands.Cog):
    @cog_ext.cog_slash(name="start-treasury-raid", description="ADMIN ONLY! Starts a random faction VS faction treasury raid")
    async def faction_raid(self, ctx):
        if ctx.author.id != 666410598178750516 or ctx.author.id != 805453439499894815:
            await ctx.send(embed=embedAdminOnly, hidden=True)
            return
        guild = client.get_guild(936698039941345370)
        channel = guild.get_channel(main_channel)
        light_role = get(guild.roles, id=1088528028243591288)
        dark_role = get(guild.roles, id=1088527880729919578)
        light_color = 0xFFFFFF
        dark_color = 0x000000
        faction = random.choice(["Light", "Dark"])
        stolen = ""
        raiders = []
        protectors = []
        if faction == "Light":
            raided = "Dark"
            treasury = light_treasury
            raided_treasury = dark_treasury
            color = light_color
            circle_def = "⚫"
            circle_atk = "⚪"
        elif faction == "Dark":
            raided = "Light"
            treasury = dark_treasury
            raided_treasury = light_treasury
            color = dark_color
            circle_def = "⚪"
            circle_atk = "⚫"
        steal_list = ["EXP", "ORDER", "RAFFLE", "Oak Logs"]
        stolen_order = 0
        stolen_exp = 0
        stolen_raffle = 0
        stolen_logs = 0
        total_steals = 0
        total_protects = 0
        round = 1
        string = ""
        embedRaidInProgress = discord.Embed(
                title=f"⚪ The {faction} Side Are RAIDING! ⚫",
                description=f"***STEAL/PROTECT the {raided} treasury!***",
                color=color
            )
        embedRaidInProgress.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        embedRaidGlobal = discord.Embed(
                title=f"⚪ The {faction} Side Are RAIDING! ⚫",
                description=f"**STEAL/PROTECT the {raided} treasury!**\n\n***RAID STATS***\n\nRound: {round}/100",
                color=color
            )
        embedRaidGlobal.add_field(name=f"***Raiders***", value=f"{len(raiders)}\n\n{string}", inline=False)
        embedRaidGlobal.add_field(name=f"***Protectors***", value=f"{len(protectors)}\n\n{string2}", inline=False)
        embedRaidGlobal.add_field(name=f"***Steals***", value=f"{total_steals}", inline=False)
        embedRaidGlobal.add_field(name=f"***Protects***", value=f"{total_protects}", inline=False)
        embedRaidGlobal.add_field(name=f"***Total Stolen\nORDER | EXP | RAFFLE | Oak Logs***", value=f"{stolen_order} | {stolen_exp} | {stolen_raffle} | {stolen_logs}", inline=False)
        embedRaidGlobal.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")    
        starting_message = f"🚨🚨🚨 {light_role.mention} VS {dark_role.mention} 🚨🚨🚨\n\n⚪⚫⚪⚫⚪ ***RAID IN PROGRESS*** ⚪⚫⚪⚫⚪\n\nThe {faction} Side Are RAIDING the {raided} treasury!\n\n60 Seconds until the portal opens to the treasury and the raiders will begin their attack...\n\nPrepare to hunt them down in the various channels to stop them from stealing from your treasury!\n\nPREPARE YOURSELVES!!!"
        await channel.send(starting_message)
        await asyncio.sleep(60)
        global_message = await channel.send(embed=embedRaidGlobal)
        embedDefended = discord.Embed(
                title=f"{circle_def} PROTECTED!! {circle_def}",
                description=f"***Well done! You protected the {raided} treasury!***",
                color=0x28FF0A
            )
        embedDefended.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        embedStolen = discord.Embed(
                title=f"{circle_atk} STOLEN!! {circle_atk}",
                description=f"***NICE! You stole {stolen} from the {raided} treasury!***",
                color=0xFF0000
            )
        embedStolen.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        embedCannotSteal = discord.Embed(
                title=f"You can not steal from your own treasury!",
                color=0xFF0000
            )
        embedCannotSteal.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        embedCannotDefend = discord.Embed(
                title=f"You can not steal from your own treasury!",
                color=0xFF0000
            )
        embedCannotDefend.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
        while round < 50:
            string = ""
            for raider in raiders:
                string += f"<@{raider}>\n"
            string2 = ""
            for protector in protectors:
                string2 += f"<@{protector}>\n"
            embedRaidGlobal.description = f"**STEAL/PROTECT the {raided} treasury!**\n\n***RAID STATS***\n\nRound: {round}/50"
            embedRaidGlobal.set_field_at(0, name=f"***Raiders***", value=f"{len(raiders)}\n\n{string}", inline=False)
            embedRaidGlobal.set_field_at(1, name=f"***Protectors***", value=f"{len(protectors)}\n\n{string2}", inline=False)
            embedRaidGlobal.set_field_at(2, name=f"***Steals***", value=f"{total_steals}", inline=False)
            embedRaidGlobal.set_field_at(3, name=f"***Protects***", value=f"{total_protects}", inline=False)
            embedRaidGlobal.set_field_at(4, name=f"***Total Stolen\nORDER | EXP | RAFFLE | Oak Logs***", value=f"{stolen_order} | {stolen_exp} | {stolen_raffle} | {stolen_logs}", inline=False)
            await global_message.edit(embed=embedRaidGlobal)
            round += 1
            random_channel_id = random.choice(channel_list)
            random_channel = guild.get_channel(random_channel_id)
            await asyncio.sleep(1)
            buttons = [create_button(style=ButtonStyle.red, label="STEAL!", custom_id="steal"), create_button(style=ButtonStyle.green, label="PROTECT!", custom_id="protect") ]
            action_row = create_actionrow(buttons[0], buttons[1])
            message = await random_channel.send(embed=embedRaidInProgress, components=[action_row])
            try:
                interaction: ComponentContext = await wait_for_component(client, components=action_row, timeout=6.0)
                interaction_author_id = interaction.author.id
                action = interaction.custom_id
                wallet, main_character, equipped_hatchet = await get_main_char(str(interaction_author_id))
                if main_character == 0:
                    embedNoMain = discord.Embed(
                        title=f"Main Character Not Selected",
                        description=f"Use /main-character to assign your main!",
                        color=0xFCE303
                    )
                    embedNoMain.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240")
                    await interaction.send(embed=embedNoMain, hidden=True)
                else:
                    metadata_api = f"https://mainnet-idx.algonode.cloud/v2/transactions?tx-type=acfg&asset-id={main_character}&address={fallen_order_manager}"
                    response = requests.get(metadata_api)
                    if response.status_code == 200:
                        data = response.json()
                    else:
                        print("Error fetching data from API")
                    metadata_decoded = (json.loads((base64.b64decode((data["transactions"][0]["note"]).encode('utf-8'))).decode('utf-8')))
                    faction2 = metadata_decoded["properties"]["Faction"]
                    if faction2 == faction:
                        if action == "steal":
                            await interaction.defer(edit_origin=True)
                            total_steals += 1
                            if interaction_author_id not in raiders:
                                raiders.append(interaction_author_id)
                            stolen = random.choice(steal_list)
                            random_number = random.randint(1,10)
                            if stolen == "Oak Logs":
                                stolen_logs += random_number
                            elif stolen == "ORDER":
                                stolen_order += random_number
                            elif stolen == "RAFFLE":
                                stolen_raffle += random_number
                            elif stolen == "EXP":
                                stolen_exp += random_number
                            embedStolen.description = f"***NICE! You stole {random_number} ${stolen} from the {raided} treasury!***"
                            await message.edit(embed=embedStolen, components=[])
                            await asyncio.sleep(3)
                            await message.delete()
                            continue
                        elif action == "protect":
                            await interaction.send(embed=embedCannotDefend, hidden=True)
                            continue
                    else:
                        if action == "protect":
                            await interaction.defer(edit_origin=True)
                            if interaction_author_id not in protectors:
                                protectors.append(interaction_author_id)
                            total_protects += 1
                            embedDefended.description = f"***Well done! You protected the {raided} treasury!***"
                            await message.edit(embed=embedDefended, components=[])
                            await asyncio.sleep(3)
                            await message.delete()
                            continue
                        elif action == "steal":
                            await interaction.send(embed=embedCannotSteal, hidden=True)
                            continue
                continue
            except asyncio.TimeoutError:
                embedTimeout = discord.Embed(
                        title=f"Woops! Too Late!",
                        description=f"Portal to {raided} treasury closing!",
                        color=0xFF0000
                    )
                await message.edit(embed=embedTimeout, components=[])
                await asyncio.sleep(3)
                await message.delete()
                continue    
        text_note = f"Treasury Raid Complete! The {faction} side stole {stolen_order} {stolen_exp} {stolen_raffle} {stolen_logs} ${stolen} from the {raided} treasury!"
        if stolen_logs > 0:
            txid_logs = await trade_logs(text_note, raided_treasury, treasury, 1064863037, stolen_logs)
        elif stolen_exp > 0:
            txid_exp = await send_assets(text_note, raided_treasury, treasury, 811718424, "EXP", stolen_exp)
        elif stolen_raffle > 0:
            txid_raffle = await send_assets(text_note, raided_treasury, treasury, 815766197, "RAFFLE", stolen_raffle)
        elif stolen_order > 0:
            txid_order = await send_assets(text_note, raided_treasury, treasury, 811721471, "ORDER", stolen_order)
        embedRaidGlobal = discord.Embed(
            title=f"⚪ ***TREASURY RAID IS OVER!*** ⚫",
            description=f"**The {faction} side has ended their raid on {raided}...the defense put up a strong fight but took some losses nonetheless**\n\n***RAID STATS***\n\nRound: {round}/100",
            color=color
        )
        embedRaidGlobal.add_field(name=f"***Raiders***", value=f"{len(raiders)}\n\n{string}", inline=False)
        embedRaidGlobal.add_field(name=f"***Protectors***", value=f"{len(protectors)}\n\n{string2}", inline=False)
        embedRaidGlobal.add_field(name=f"***Steals***", value=f"{total_steals}", inline=False)
        embedRaidGlobal.add_field(name=f"***Protects***", value=f"{total_protects}", inline=False)
        embedRaidGlobal.add_field(name=f"***Total Stolen\nORDER | EXP | RAFFLE | Oak Logs***", value=f"{stolen_order} | {stolen_exp} | {stolen_raffle} | {stolen_logs}", inline=False)
        embedRaidGlobal.add_field(name=f"***Treasury Theft Transactions***", value=f"[ORDER](https://algoexplorer.io/tx/{txid_order}) | [EXP](https://algoexplorer.io/tx/{txid_exp}) | [RAFFLER](https://algoexplorer.io/tx/{txid_raffle}) | [Oak Logs](https://algoexplorer.io/tx/{txid_logs})", inline=False)
        embedRaidGlobal.set_thumbnail(url="https://bunny-cdn.algoxnft.com/production/collections/fallen-order---main-assets-thumb.png?width=240") 
        starting_message = f"⚪⚫⚪⚫⚪⚫⚪ {light_role.mention} VS {dark_role.mention} ⚪⚫⚪⚫⚪⚫⚪"
        await global_message.delete()
        await channel.send(starting_message, embed=embedRaidGlobal)

def setup(client: client):
    client.add_cog(TreasuryRaidCog(client))
