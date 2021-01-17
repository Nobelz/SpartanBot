# bot.py
import os
import json

from discord.ext import commands
from discord import Member
from dotenv import load_dotenv


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
BOT_OWNER = os.getenv('BOT_OWNER')


def _get_prefix(client, message):
    with open('config.json', 'r') as f:
        configs = json.load(f)

    return configs[str(message.guild.id)]["prefix"]


def prefix(guild):
    with open('config.json', 'r') as f:
        configs = json.load(f)

    return configs[str(guild.id)]["prefix"]


def is_admin(message):
    return message.author.guild_permissions.manage_guild or str(message.author.id) == BOT_OWNER


bot = commands.Bot(command_prefix=_get_prefix)


@bot.event
async def on_ready():
    print('Bot is ready.')


@bot.command()
async def ping(ctx):
    await ctx.message.add_reaction('🏓')
    await ctx.send(f"{ctx.author.mention} Pong! {int(round(bot.latency * 1000, 0))}ms")


@bot.command()
async def version(ctx):
    await ctx.send("Bot version: 1.6.2, made by Nobelium")


@bot.command(help='Server configuration of bot')
async def config(ctx, *, args):
    if is_admin(ctx.message):
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
                elif arguments[1] == 'coronarole' and len(arguments) == 3:
                    role_id = parse_role_to_id(arguments[2])
                    if role_id is not None and ctx.guild.get_role(role_id) is not None:
                        if "corona" not in server_dict:
                            server_dict["corona"] = {}
                        server_dict["corona"]["role"] = role_id
                        message = "Corona role set to " + arguments[2] + "."
                    else:
                        raise ValueError
                elif arguments[1] == 'coronachannel' and len(arguments) == 3:
                    channel_id = parse_channel_to_id(arguments[2])
                    if channel_id is not None and ctx.guild.get_channel(channel_id) is not None:
                        if "corona" not in server_dict:
                            server_dict["corona"] = {}
                        if "messages" in server_dict["corona"]:
                            channel = bot.get_channel(server_dict['corona']['channel'])
                            if channel is not None:
                                if 'messages' in server_dict['corona']:
                                    messages = server_dict['corona']['messages']
                                    for message_id in messages:
                                        message = await channel.fetch_message(message_id)
                                        if message is not None:
                                            await message.delete()
                            del server_dict['corona']["messages"]
                        server_dict["corona"]["channel"] = channel_id
                        message = "Corona channel set to " + arguments[2] + "."
                    else:
                        raise ValueError
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
                    await ctx.send(f"School name not set yet. Set the school name using "
                                   f"`{prefix(ctx.guild)}config set schoolname <school name>`")
            elif arguments[0] == 'prefix':
                await ctx.send("Server prefix: " + server_dict["prefix"])
            elif arguments[0] == 'coronarole':
                if 'corona' in server_dict and 'role' in server_dict['corona']:
                    await ctx.send(f"Corona role ID: {server_dict['corona']['role']}")
                else:
                    await ctx.send(f"Corona role not set yet. Set the corona role using "
                                   f"`{prefix(ctx.guild)}config set coronarole <role mention>`")
            elif arguments[0] == 'coronachannel':
                if 'corona' in server_dict and 'channel' in server_dict['corona']:
                    await ctx.send(f"Corona channel ID: {server_dict['corona']['channel']}")
                else:
                    await ctx.send(f"Corona channel not set yet. Set the corona channel using "
                                   f"`{prefix(ctx.guild)}config set coronachannel <channel mention>`")
            else:
                await ctx.send("Config value with that key not found. Please try again.")
        else:
            await ctx.send(f'Proper command usage: `{prefix(ctx.guild)}config set <key> <value(s)>` or '
                           f'`{prefix(ctx.guild)}config <key>`')
    else:
        await ctx.send('Access denied. You must have the \'Manage Server\' permissions to access this command.')


def parse_role_to_id(role_str):
    if role_str[1:3] != '@&':
        return None
    parse_role_id = role_str[3:len(role_str) - 1]
    try:
        parse_role_id = int(parse_role_id)
        return parse_role_id
    except ValueError:
        return None


def parse_channel_to_id(channel_str):
    if channel_str[1] != '#':
        return None
    parse_channel_id = channel_str[2:len(channel_str) - 1]
    try:
        parse_channel_id = int(parse_channel_id)
        return parse_channel_id
    except ValueError:
        return None


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
    is_reacted = False                               
    if isinstance(message.author, Member) and message.author.guild_permissions.mention_everyone is False \
            and ('@everyone' in message.content or '@here' in message.content):
        await message.add_reaction('<:banhammer:688897781380939881>')
        is_reacted = True
    if 'cameron' in message.content.lower() or check_id_in_members(member_id=481268659856343040,
                                                                   member_list=message.mentions):
        await message.add_reaction('🧂')
        is_reacted = True
    if 'zhanda' in message.content.lower() or check_id_in_members(member_id=173625956441915392,
                                                                  member_list=message.mentions):
        await message.add_reaction('<:Thiccnos:688897525545173258>')
        is_reacted = True
    if 'david' in message.content.lower() or check_id_in_members(member_id=757314714396131439,
                                                               member_list=message.mentions):
        await message.add_reaction('🧠')
        is_reacted = True
    if not is_reacted:
        await bot.process_commands(message)  
                                   

def check_id_in_members(member_id, member_list):
    for member in member_list:
        if member.id == member_id:
            return True

    return False


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

bot.run(TOKEN)
