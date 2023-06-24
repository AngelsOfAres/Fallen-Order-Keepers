from discord_slash import cog_ext
from discord.ext import commands
import discord
from client import client
from c_adeona.general_quests.gq1_ramsays_rampage import quest_ramsays_rampage
from c_adeona.general_quests.gq2_the_summoning import quest_the_summoning
from c_adeona.wc_quests.wc1_im_a_lumberjack import quest_im_a_lumberjack

class MainQuestCog(commands.Cog):
    @cog_ext.cog_slash(name="quest", description="Start A Quest!", options=[
                {
                    "name": "quest",
                    "description": "Choose Quest!",
                    "type": 3,
                    "required": True,
                    "choices": [
                        {
                            "name": "Ramsay's Rampage",
                            "value": "1"
                        },
                        {
                            "name": "The Summoning",
                            "value": "2"
                        },
                        {
                            "name": "I'm A Lumberjack!",
                            "value": "3"
                        }
                    ]
                }
            ])
    @commands.cooldown(1, 60, commands.BucketType.guild)
    async def start_quest(self, ctx, quest):
        if quest == "1":
            await quest_ramsays_rampage(ctx)
            return
        elif quest == "2":
            await quest_the_summoning(ctx)
            return
        elif quest == "3":
            await quest_im_a_lumberjack(ctx)
            return
        else:
            return
    @start_quest.error
    async def start_quest_error(self, ctx, error):
        embedNotAllowed = discord.Embed(
                    title=f"There is a quest in progress!",
                    description=f"Please wait a few minutes while the other player concludes their journey...",
                    color=0xFF0000
                )
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(embed=embedNotAllowed, hidden=True)


def setup(client: client):
    client.add_cog(MainQuestCog(client))