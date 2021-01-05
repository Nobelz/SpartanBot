import json
import os
import requests

from lxml import etree
from discord.ext import commands
from datetime import datetime
from dotenv import load_dotenv
from quickchart import QuickChart


load_dotenv()
BOT_OWNER = os.getenv('BOT_OWNER')

campus_url = "https://case.edu/return-to-campus/campus-information/covid-19-testing-and-case-data"

with open('covid.js', 'r') as f:
    script = f.read().replace('\n', '')


class Coronavirus(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Corona is ready.')

    # test command
    @commands.command()
    async def test(self, ctx):
        if str(ctx.message.author.id) == BOT_OWNER:
            await ctx.send("Bot owner recognized. This is a test of the coronavirus stats accessor system.")
            page = requests.get(campus_url)
            await ctx.send(f"HTML GET request returned code: {page.status_code}")
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

            cases_by_week_students = [float(e.text) for e in cases_by_week.find('div[4]')]
            cases_by_week_faculty = [float(e.text) for e in cases_by_week.find('div[6]')]
            date_strings = [d.text.replace('*', '') for d in date_strings]
            tests_administered = [int(float(e.text)) for e in html.xpath('//*[@role="main"]/div[3]/section/div/article/'
                                                                         'div/div/div/div/div[3]/div/canvas/div/'
                                                                         'div[4]')[0]]
            percent_positive_cumulative = [float(e.text) for e in percent_positive.find('div[4]')]
            percent_positive_weekly = [float(e.text) for e in percent_positive.find('div[6]')]

            if len(cases_by_week_students) == len(dates) == len(cases_by_week_faculty):
                await ctx.send("Attempting to retrieve graph image files from website...")

                chart_options = {
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
                    }
                }

                qc1 = QuickChart()
                qc1.width = 1000
                qc1.height = 500
                qc1.config = {
                    "type": "line",
                    "data": {
                        "labels": date_strings,
                        "datasets": [{
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
                            "text": "CWRU New Positive Cases By Week",
                            "fontSize": 22
                        }
                    }
                }

                await ctx.send(qc1.get_short_url())

                qc2 = QuickChart()
                qc2.width = 1000
                qc2.height = 500
                qc2.config = {
                    "type": "bar",
                    "data": {
                        "labels": date_strings,
                        "datasets": [{
                            "label": "Tests Administered",
                            "data": tests_administered,
                            "backgroundColor": "rgba(97, 97, 97, 0.05)",
                            "borderColor": "rgba(97, 97, 97, 1)",
                            "borderWidth": 3
                        }]
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
                            "text": "CWRU Testing: Tests Administered",
                            "fontSize": 22
                        }
                    }
                }

                await ctx.send(qc2.get_short_url())

                qc3 = QuickChart()
                qc3.width = 1000
                qc3.height = 500
                qc3.config = {
                    "type": "line",
                    "data": {
                        "labels": date_strings,
                        "datasets": [{
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
                            "text": "CWRU Testing: Percentage of Positive Results",
                            "fontSize": 22
                        }
                    }
                }

                await ctx.send(qc3.get_short_url())
            else:
                await ctx.send("Error retrieving data: data mismatch")
        else:
            await ctx.send(f"Access denied. Command reserved for bot owner <@{BOT_OWNER}> only")


def setup(bot):
    bot.add_cog(Coronavirus(bot))
