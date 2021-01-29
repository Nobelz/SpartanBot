import json
import os
import requests

from discord import Embed
from lxml import etree
from discord.ext import commands
from datetime import datetime
from dotenv import load_dotenv
from quickchart import QuickChart
from operator import add


load_dotenv()
BOT_OWNER = os.getenv('BOT_OWNER')


class Coronavirus(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Corona is ready.')

    # corona command
    @commands.command()
    async def corona(self, ctx, *, args):
        arguments = args.split(' ')
        with open('config.json', 'r') as f:
            configs = json.load(f)
            server_dict = configs[str(ctx.guild.id)]

        if 'corona' in server_dict and 'role' in server_dict['corona'] and 'channel' in server_dict['corona']:
            role = ctx.guild.get_role(server_dict['corona']['role'])

            if role in ctx.author.roles:
                try:
                    if len(arguments) == 1:
                        if arguments[0] == 'push':
                            channel = self.bot.get_channel(server_dict['corona']['channel'])
                            if channel is not None:
                                if 'messages' in server_dict['corona']:
                                    messages = server_dict['corona']['messages']
                                    for message_id in messages:
                                        message = await channel.fetch_message(message_id)
                                        if message is not None:
                                            await message.delete()
                                ids = []

                                for embed in get_embeds():
                                    message = await channel.send(embed=embed)
                                    ids.append(message.id)
                                server_dict['corona']['messages'] = ids

                                with open('config.json', 'w') as f:
                                    json.dump(configs, f, indent=4)

                                end_message = f"Corona stats successfully pushed to {channel.mention}."
                            else:
                                raise ValueError
                        elif arguments[0] == 'update':
                            if 'messages' in server_dict['corona']:
                                channel = self.bot.get_channel(server_dict['corona']['channel'])
                                if channel is not None:
                                    message_ids = server_dict['corona']['messages']
                                    messages = []
                                    for message_id in message_ids:
                                        message = await channel.fetch_message(message_id)
                                        messages.append(message)
                                    ids = []
                                    embeds = get_embeds()
                                    for i in range(3):
                                        await messages[i].edit(embed=embeds[i])

                                    end_message = f"Corona stats successfully updated in {channel.mention}."
                                else:
                                    raise ValueError
                            else:
                                await ctx.send("Corona data has not been pushed at least once. "
                                               "Please push data before updating data first.")
                        else:
                            raise ValueError
                    else:
                        raise ValueError
                    await ctx.send(end_message)
                except ValueError:
                    await ctx.send("Improper usage of command. Please try again.")
            else:
                await ctx.send("Access denied. You must have the proper role to use this command.")
        else:
            await ctx.send("Corona config not set up. "
                           "Please use the config command to set up the corona channel and role.")


def get_embeds():
    data = get_cwru_data()

    if data is not None:
        embeds = []

        time_str = datetime.now().strftime("%b. %d, %Y at %I:%M %p EST").replace(' 0', ' ')
        for i in range(3):
            embed = Embed()
            embed.set_image(url=data["charts"][i])
            embed.set_footer(text=f"Last Updated: {time_str}")
            dates = data['data']['dates']['str']
            if i == 0:
                embed.title = f"CWRU Cases Report for Week of {dates[len(dates) - 1]}:"

                staff_cases = data['data']['cases']['staff']
                embed.add_field(name="Faculty/Staff Cases", value=get_diff_string(staff_cases))

                student_cases = data['data']['cases']['students']
                embed.add_field(name="Student Cases", value=get_diff_string(student_cases))

                total_cases = list(map(add, staff_cases, student_cases))
                embed.add_field(name="Total Cases", value=get_diff_string(total_cases))

                embed.add_field(name="Cumulative Faculty/Staff Cases", value=f"**{sum(staff_cases)}**")
                embed.add_field(name="Cumulative Student Cases", value=f"**{sum(student_cases)}**")
                embed.add_field(name="Cumulative Cases Total", value=f"**{sum(total_cases)}**")
            elif i == 1:
                embed.title = f"CWRU Tests Report for Week of {dates[len(dates) - 1]}:"

                tests = data['data']['tests']
                embed.add_field(name="Tests Administered", value=f"**{tests[len(tests) - 1]}**")
                embed.add_field(name="Cumulative Tests Administered", value=f"**{sum(tests)}**")
            else:
                embed.title = f"CWRU Percent Positive Report for Week of {dates[len(dates) - 1]}:"

                week_percent = data['data']['percentPositive']['weekly']
                embed.add_field(name="Percent Positive Rate", value=get_diff_string(week_percent,
                                                                                    is_percent=True))

                cum_percent = data['data']['percentPositive']['cumulative']
                embed.add_field(name="Cumulative Positive Rate", value=get_diff_string(cum_percent,
                                                                                       is_percent=True))
            embeds.append(embed)
            i += 1

        return embeds
    else:
        return None


def get_diff_string(number_array, is_percent=False):
    emojis = [
        '<:redarrowup:796451168335167519>',
        '<:greenarrowdown:796451267039723630>',
        '<:straightline:796453949129228328>'
    ]

    current = number_array[len(number_array) - 1]
    previous = number_array[len(number_array) - 2]
    if current > previous:
        emoji_str = f"{emojis[0]} (+{(current - previous) if not is_percent else round(current - previous, 2)}" \
                    f"{'%' if is_percent else ''})"
    elif previous > current:
        emoji_str = f"{emojis[1]} (-{(previous - current) if not is_percent else round(previous - current, 2)}" \
                    f"{'%' if is_percent else ''})"
    else:
        emoji_str = f"{emojis[2]} (+0{'%' if is_percent else ''})"

    return f"**{current}{'%' if is_percent else ''}** {emoji_str}"


def get_cwru_data():
    campus_url = "https://case.edu/covid19/health-safety/testing/covid-19-testing-and-case-data"
    page = requests.get(campus_url)
    html = etree.HTML(page.text)
    cases_by_week = html.xpath('//*[@role="main"]/div[3]/section/div/article/div/div/div/div/div[2]/div/'
                               'canvas/div')[0]
    percent_positive = html.xpath('//*[@role="main"]/div[3]/section/div/article/div/div/div/div/div[4]/div/'
                                  'canvas/div')[0]

    date_strings = cases_by_week.find('div[2]')
    dates = []
    for date_str in date_strings:
        date_str = date_str.text.split('-')[0]
        if len(date_str.split('.')[0]) == 4:
            date_str = date_str[:3] + date_str[4:]

        date = datetime.strptime(date_str, "%b. %d")
        if date.month < 8:
            date = date.replace(year=2021)
        else:
            date = date.replace(year=2020)
        dates.append(date)

    cases_by_week_students = [int(float(e.text)) for e in cases_by_week.find('div[4]')]
    cases_by_week_faculty = [int(float(e.text)) for e in cases_by_week.find('div[6]')]
    date_strings = [d.text.replace('*', '') for d in date_strings]
    tests_administered = [int(float(e.text)) for e in html.xpath('//*[@role="main"]/div[3]/section/div/article/'
                                                                 'div/div/div/div/div[3]/div/canvas/div/'
                                                                 'div[4]')[0]]
    percent_positive_cumulative = [float(e.text) for e in percent_positive.find('div[4]')]
    percent_positive_weekly = [float(e.text) for e in percent_positive.find('div[6]')]

    if len(cases_by_week_students) == len(dates) == len(cases_by_week_faculty):
        cases_chart = _generate_graph(date_strings)
        cases_chart.config["type"] = "line"
        cases_chart.config["data"]["datasets"] = [{
            "label": "Students",
            "data": cases_by_week_students,
            "lineTension": 0.4,
            "backgroundColor": "rgba(49, 104, 166, 0.05)",
            "borderColor": "rgba(49, 104, 166, 1)",
            "borderWidth": 3
        }, {
            "label": "Faculty/Staff",
            "data": cases_by_week_faculty,
            "lineTension": 0.4,
            "backgroundColor": "rgba(97, 97, 97, 0.05)",
            "borderColor": "rgba(97, 97, 97, 1)",
            "borderWidth": 3
        }]
        cases_chart.config["options"]["title"]["text"] = "CWRU New Positive Cases By Week"

        tests_chart = _generate_graph(date_strings)
        tests_chart.config["type"] = "bar"
        tests_chart.config["data"]["datasets"] = [{
            "label": "Tests Administered",
            "data": tests_administered,
            "backgroundColor": "rgba(97, 97, 97, 0.05)",
            "borderColor": "rgba(97, 97, 97, 1)",
            "borderWidth": 3
        }]
        tests_chart.config["options"]["title"]["text"] = "CWRU Testing: Tests Administered"

        positive_chart = _generate_graph(date_strings)
        positive_chart.config["type"] = "line"
        positive_chart.config["data"]["datasets"] = [{
            "label": "Cumulative Positivity Rate",
            "data": percent_positive_cumulative,
            "lineTension": 0.4,
            "backgroundColor": "rgba(49, 104, 166, 0.05)",
            "borderColor": "rgba(49, 104, 166, 1)",
            "borderWidth": 3
        }, {
            "label": "Weekly Positivity Rate",
            "data": percent_positive_weekly,
            "lineTension": 0.4,
            "backgroundColor": "rgba(97, 97, 97, 0.05)",
            "borderColor": "rgba(97, 97, 97, 1)",
            "borderWidth": 3
        }]
        positive_chart.config["options"]["title"]["text"] = "CWRU Testing: Percentage of Positive Results"

        return {
            "charts": [cases_chart.get_short_url(), tests_chart.get_short_url(), positive_chart.get_short_url()],
            "data": {
                "dates": {
                    "datetime": dates,
                    "str": date_strings
                },
                "cases": {
                    "students": cases_by_week_students,
                    "staff": cases_by_week_faculty
                },
                "tests": tests_administered,
                "percentPositive": {
                    "weekly": percent_positive_weekly,
                    "cumulative": percent_positive_cumulative
                }
            }
        }
    else:
        return None


def _generate_graph(date_strings):
    chart = QuickChart()
    chart.width = 800
    chart.height = 400
    chart.config = {
        "data": {
            "labels": date_strings
        },
        "options": {
            "scales": {
                "yAxes": [{
                    "ticks": {
                        "beginAtZero": True,
                        "suggestedMax": 1
                    }
                }]
            },
            "legend": {
                "position": "bottom"
            },
            "title": {
                "display": True,
                "fontSize": 22
            }
        }
    }

    return chart


def setup(bot):
    bot.add_cog(Coronavirus(bot))
