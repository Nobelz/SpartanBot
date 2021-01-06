import json
import ratemyprofessor as rmp
import discord
import matplotlib.pyplot as plt

from discord.ext import commands
from matplotlib.patches import Patch


class RateMyProfessor(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('RMP is ready.')

    # rmp command
    @commands.command(aliases=['rate'], help='Looks up professor on RMP')
    async def rmp(self, ctx, *, prof):
        with open('config.json', 'r') as f:
            configs = json.load(f)

        if 'schoolName' not in configs[str(ctx.guild.id)]:
            await ctx.send("School name not set yet. Use the config command to set it before using this command.")
        else:
            professor = rmp.get_professor_by_school_and_name(rmp.get_school_by_name(
                configs[str(ctx.guild.id)]['schoolName']), prof)

            if professor is None:
                await ctx.send("Professor not found. Please try again.")
            else:
                message = f"Professor name: **{professor.name}**\n"

                if professor.rating != 0:
                    message += f"Professor rating: **{round(professor.rating, 1)}** / 5.0\n"
                else:
                    message += "Professor rating: **N/A**\n"

                if professor.difficulty != 0:
                    message += f"Professor difficulty: **{round(professor.difficulty, 1)}** / 5.0"
                else:
                    message += "Professor difficulty: **N/A**"

                await ctx.send(message)

                if professor.num_ratings > 9:
                    ratings = professor.get_ratings()
                    ratings.sort(reverse=True)

                    dates = [r.date for r in ratings]
                    running_dates = [r.date for r in ratings[4:]]
                    helpful_ratings = []

                    i = 0
                    while i < len(ratings):
                        average = [r.rating for r in ratings[0: i + 1]]
                        helpful_ratings.append(sum(average) / (i + 1))
                        i += 1

                    i = 0
                    running_averages = []
                    while i < len(ratings) - 4:
                        average = [r.rating for r in ratings[i: i + 5]]
                        running_averages.append(sum(average) / 5)
                        i += 1

                    plt.plot(running_dates, running_averages, color='blue')
                    plt.plot(dates, helpful_ratings, color='red')

                    plt.title(f'Ratings for {professor.name}', fontsize=15)
                    plt.ylabel('Rating', fontsize=12)
                    plt.xlabel('Date', fontsize=12)
                    plt.ylim(1.0, 5.0)
                    plt.legend(handles=[Patch(color='red', label='Average Rating'),
                                            Patch(color='blue', label='Running Average Rating')])
                    plt.grid(True)

                    plt.savefig('graph.png')
                    plt.clf()
                    await ctx.send(file=discord.File('graph.png'))

    # version command
    @commands.command()
    async def version(self, ctx):
        await ctx.send("Bot version: 1.6.0, made by Nobelium")


def setup(bot):
    bot.add_cog(RateMyProfessor(bot))
