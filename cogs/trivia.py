import json
import discord
import datetime
import requests

from discord.ext import commands


class Trivia(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Trivia is ready.')

    @commands.command()
    async def trivia(self, ctx):
        with open('trivia.json', 'r') as f:
            answers = json.load(f)

        data = requests.get("https://opentdb.com/api.php?amount=1").json()
        print(data)

        await ctx.send("Test")


def setup(bot):
    bot.add_cog(Trivia(bot))