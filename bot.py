# bot.py
import os
import json
import datetime

from discord.ext import commands
from discord.ext import tasks
from discord import Member
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
PREFIX = os.getenv('BOT_PREFIX')

bot = commands.Bot(command_prefix=PREFIX)


@bot.event
async def on_ready():
    print('Bot is ready.')


@bot.command()
async def ping(ctx):
    await ctx.message.add_reaction('🏓')
    await ctx.send(f"{ctx.author.mention} Pong! {int(round(bot.latency * 1000, 0))}ms")


@bot.command(help='Server configuration of bot')
async def config(ctx, *, args):
    arguments = args.split()

    if arguments[0] == 'set':
        if len(arguments) == 2:
            with open('config.json', 'r') as f:
                configs = json.load(f)

            configs[str(ctx.guild.id)] = str(arguments[1])

            with open('config.json', 'w') as f:
                json.dump(configs, f, indent=4)

            await ctx.send(f'School Name set to {arguments[1]}.')
        else:
            await ctx.send(f'Proper command usage: `{PREFIX}config set <school name>` or `{PREFIX}config schoolname`')
    elif arguments[0] == 'schoolname':
        with open('config.json', 'r') as f:
            configs = json.load(f)

        await ctx.send(f'School Name: {configs[str(ctx.guild.id)]}')
    else:
        await ctx.send(f'Proper command usage: `{PREFIX}config set <school name>` or `{PREFIX}config schoolname`')


@bot.event
async def on_guild_join(guild):
    with open('config.json', 'r') as f:
        configs = json.load(f)

    configs[str(guild.id)] = "Case Western Reserve University"

    with open('config.json', 'w') as f:
        json.dump(configs, f, indent=4)


@bot.event
async def on_guild_remove(guild):
    with open('config.json', 'r') as f:
        configs = json.load(f)

    configs.pop(str(guild.id))

    with open('config.json', 'w') as f:
        json.dump(configs, f, indent=4)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('Command not found')


@bot.event
async def on_message(message):
    if isinstance(message.author, Member) and message.author.guild_permissions.mention_everyone is False \
            and ('@everyone' in message.content or '@here' in message.content):
        await message.add_reaction('<:banhammer:688897781380939881>')
    else:
        await bot.process_commands(message)


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run(TOKEN)
