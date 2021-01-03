# bot.py
import os
import json

from discord.ext import commands
from discord import Member
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


def _get_prefix(client, message):
    with open('config.json', 'r') as f:
        configs = json.load(f)

    return configs[str(message.guild.id)]["prefix"]


def prefix(guild):
    with open('config.json', 'r') as f:
        configs = json.load(f)

    return configs[str(guild.id)]["prefix"]


bot = commands.Bot(command_prefix=_get_prefix)


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

    with open('config.json', 'r') as f:
        configs = json.load(f)
        server_dict = configs[str(ctx.guild.id)]

    if arguments[0] == 'set' and len(arguments) >= 3:
        message = ""

        try:
            if arguments[1] == 'schoolname':
                server_dict["schoolName"] = " ".join(arguments[2:])
                message = "School name set to " + " ".join(arguments[2:]) + "."
            elif arguments[1] == 'prefix' and len(arguments) == 3:
                server_dict["prefix"] = arguments[2]
                message = "Bot prefix set to " + arguments[2] + "."
            else:
                raise ValueError

            with open('config.json', 'w') as f:
                json.dump(configs, f, indent=4)

            await ctx.send(message)
        except ValueError:
            await ctx.send("Config value with that key not found or invalid syntax. Please try again.")
    elif len(arguments) == 1:
        if arguments[0] == 'schoolname':
            if 'schoolName' in server_dict:
                await ctx.send("School name: " + server_dict['schoolName'])
            else:
                await ctx.send(f"School name not set yet. "
                               f"Set the school name using `{prefix(ctx.guild)}config set schoolname <school name>`")

        elif arguments[0] == 'prefix':
            await ctx.send("Server prefix: " + server_dict["prefix"])
        else:
            await ctx.send("Config value with that key not found. Please try again.")
    else:
        await ctx.send(f'Proper command usage: `{prefix(ctx.guild)}config set <key> <value(s)>` or '
                       f'`{prefix(ctx.guild)}config <key>`')


@bot.event
async def on_guild_join(guild):
    with open('config.json', 'r') as f:
        configs = json.load(f)

    configs[str(guild.id)] = {}
    configs[str(guild.id)]['prefix'] = '!!'

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
