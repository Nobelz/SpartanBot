import json
import ratemyprofessor
import matplotlib.pyplot as plt
import discord

from discord.ext import commands


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

        professor = ratemyprofessor.get_professor_by_school_and_name(ratemyprofessor.get_school_by_name(
            configs[str(ctx.guild.id)]), prof)

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

                dates = [r.date for r in ratings[4:]]

                i = 0
                running_averages = []
                while i < len(ratings) - 4:
                    average = [r.rating for r in ratings[i: i + 5]]
                    running_averages.append(sum(average) / 5)
                    i += 1

                plt.plot(dates, running_averages, color='blue')
                plt.title(f'Running Average for {professor.name}', fontsize=15)
                plt.ylabel('Rating', fontsize=12)
                plt.xlabel('Date', fontsize=12)
                plt.ylim(1.0, 5.0)
                plt.grid(True)
                plt.savefig('graph.png')
                plt.clf()
                await ctx.send(file=discord.File('graph.png'))

    # test command
    @commands.command()
    async def test(self, ctx, *, prof):
        with open('config.json', 'r') as f:
            configs = json.load(f)

        professor = ratemyprofessor.get_professor_by_school_and_name(ratemyprofessor.get_school_by_name(
            configs[str(ctx.guild.id)]), prof)

        if professor is None:
            await ctx.send("Professor not found. Please try again.")
        else:
            message = f"Professor name: {professor.name}\n"

            if professor.rating != 0:
                message += f"Professor rating: {professor.rating} / 5.0\n"
            else:
                message += f"Professor rating: N/A\n"

            if professor.difficulty != 0:
                message += f"Professor difficulty: {professor.difficulty} / 5.0"
            else:
                message += f"Professor difficulty: N/A"

            await ctx.send(message)

            if professor.num_ratings > 9:
                ratings = professor.get_ratings()
                ratings.sort(reverse=True)

                dates = [r.date for r in ratings[4:]]

                i = 0
                running_averages = []
                while i < len(ratings) - 4:
                    average = [r.rating for r in ratings[i: i + 5]]
                    running_averages.append(sum(average) / 5)
                    i += 1

                plt.plot(dates, running_averages, color='blue')
                plt.title('Running Average', fontsize=20)
                plt.ylabel('Rating', fontsize=12)
                plt.xlabel('Date', fontsize=12)
                plt.ylim(1.0, 5.0)
                plt.grid(True)
                plt.savefig('graph.png')
                plt.clf()
                await ctx.send(file=discord.File('graph.png'))


def setup(bot):
    bot.add_cog(RateMyProfessor(bot))
