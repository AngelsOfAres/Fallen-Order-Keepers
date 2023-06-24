from discord_slash import cog_ext
from discord.ext import commands
import discord
from client import client
from embeds import embedCommands1, embedCommands2, embedCommands3, embedAbilities, embedShuffle


class CommandsCog(commands.Cog):
    @cog_ext.cog_slash(name="commands", description="List Available Commands", options=[
                {
                    "name": "type",
                    "description": "List Of Commands To Display",
                    "type": 3,
                    "required": True,
                    "choices": [
                        {
                            "name": "General",
                            "value": "1"
                        },
                        {
                            "name": "Fallen Order",
                            "value": "2"
                        },
                        {
                            "name": "HouseOfHermes",
                            "value": "3"
                        }
                    ]
                }])
    async def command_list(self, ctx, type):
        if type == "1":
            await ctx.send(embed=embedCommands1)
        elif type == "2":
            await ctx.send(embed=embedCommands3)
        else:
            await ctx.send(embed=embedCommands2)
        return

class AbilitiesCog(commands.Cog):
    @cog_ext.cog_slash(name="abilities", description="List Character Abilities + Ultimates")
    async def command_list(self, ctx):
        await ctx.send(embed=embedAbilities)
        return

class ShuffleCog(commands.Cog):
    @cog_ext.cog_slash(name="shuffle", description="GIVE ME THE SHUFFLE!!!!!!")
    async def command_list(self, ctx):
        await ctx.send(embed=embedShuffle)
        return
            
def setup(client: client):
    client.add_cog(AbilitiesCog(client))
    client.add_cog(ShuffleCog(client))
    client.add_cog(CommandsCog(client))

