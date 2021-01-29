import json
import discord
import datetime
import asyncio
import requests
import html
import random

from discord.ext import commands
from discord import Embed


choice_emojis = ['🇦', '🇧', '🇨', '🇩']


async def trigger_delete(resolution, message):
    with open('trivia.json', 'r') as f:
        trivia = json.load(f)

    correct_answer = trivia[str(message.id)]['correct_answer']
    trivia.pop(str(message.id))

    with open('trivia.json', 'w') as f:
        json.dump(trivia, f, indent=4)

    await message.clear_reactions()
    embed = message.embeds[0]

    if resolution == 0:
        embed.add_field(name='\u200b', value=f"You ran out of time! **{correct_answer}** was the correct answer.",
                        inline=False)
        embed.colour = discord.Colour.red()
    elif resolution == 1:
        embed.add_field(name='\u200b', value=f"**{correct_answer}** is the correct answer!", inline=False)
        embed.colour = discord.Colour.green()
    elif resolution == 2:
        embed.add_field(name='\u200b', value=f"Sorry, that is incorrect! **{correct_answer}** "
                                             f"was the correct answer.", inline=False)
        embed.colour = discord.Colour.red()

    await message.edit(embed=embed)


class Trivia(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Trivia is ready.')

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if user != self.bot.user and reaction.message.author == self.bot.user:
            with open('trivia.json', 'r') as f:
                trivia = json.load(f)

            if str(reaction.message.id) in trivia:
                if reaction.count < 2 or trivia[str(reaction.message.id)]["user"] != user.id:
                    await reaction.message.remove_reaction(reaction, user)
                else:
                    index = choice_emojis.index(reaction.emoji)
                    if index == trivia[str(reaction.message.id)]["correct_index"]:
                        await trigger_delete(1, reaction.message)
                    else:
                        await trigger_delete(2, reaction.message)

    @commands.command()
    async def trivia(self, ctx):
        with open('trivia.json', 'r') as f:
            trivia = json.load(f)

        username = ctx.author.display_name

        data = requests.get("https://opentdb.com/api.php?amount=1").json()
        if data is not None and 'results' in data:
            embed = Embed()
            embed.set_author(name=f"{username}'s Trivia Question")

            data = data['results'][0]
            category = data['category']
            difficulty = data['difficulty'].capitalize()
            question = html.unescape(data['question'])
            answers = data['incorrect_answers']
            answers = [html.unescape(a) for a in answers]
            answers.append(data['correct_answer'])
            random.shuffle(answers)

            answer_text = '*You have 10 seconds to answer this question.*'
            for i in range(len(answers)):
                answer_text += f'\n\n{choice_emojis[i]} {answers[i]}'

            embed.add_field(name=f'**{question}**', value=answer_text, inline=False)
            embed.add_field(name="Difficulty", value=difficulty)
            embed.add_field(name="Category", value=category)

            message = await ctx.send(embed=embed)
            trivia[str(message.id)] = {}
            trivia[str(message.id)]['user'] = ctx.author.id
            trivia[str(message.id)]['correct_answer'] = html.unescape(data['correct_answer'])
            trivia[str(message.id)]['correct_index'] = answers.index(data['correct_answer'])

            with open('trivia.json', 'w') as f:
                json.dump(trivia, f, indent=4)

            for i in range(len(answers)):
                await message.add_reaction(choice_emojis[i])

            await asyncio.sleep(10)
            message = await ctx.fetch_message(message.id)
            if message.edited_at is None:
                await trigger_delete(0, message)
        else:
            await ctx.send("Error retrieving trivia questions. Please try again later.")


def setup(bot):
    bot.add_cog(Trivia(bot))
