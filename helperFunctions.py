# helperFunctions for app.py
from flask import Flask, render_template, request, url_for
import requests
import json
import pandas as pd
import numpy as np
import time
from datetime import datetime
import io
import base64
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
#import plotly
#import plotly.express as px
#import sys

# # # # # # # # # # # # # # # # # # # # # # # # #
# Function: Convert date to readible variables  #
# # # # # # # # # # # # # # # # # # # # # # # # #
def convertDate(timestamp):
    date = datetime.fromtimestamp(timestamp).strftime("%A,%B,%d,%Y,%H,%M,%p")
    dayOfWeek, month, day, year, hour, minute, period = date.split(',')
    hour = int(hour)
    if hour > 12:
        hour -= 12
    if hour == 0:
        hour = 12
    return dayOfWeek, month, day, year, str(hour), minute, period



# # # # # # # # # # # # # # # # # # # # # # # # # # #
# Function: Handle gamertag to account for hashtag  #
# # # # # # # # # # # # # # # # # # # # # # # # # # #
def handleGamertag(gamertag):
    g=''
    if '#' in gamertag:
        g = gamertag.split('#')
        g = g[0] + '%23' + g[1]
    return g


# # # # # # # # # # # # # # # # # # # # # # # #
# Function: Convert gamertag back to readable #
# # # # # # # # # # # # # # # # # # # # # # # #
def convertGamertagBack(gamertag):
    g=''
    if '%' in gamertag:
        g = gamertag.split('%')
        g = g[0]
    return g



# # # # # # # # # # # # # # # # # # # # # # # # # #
# Function: Retrieve API data of 20 recent games  #
# # # # # # # # # # # # # # # # # # # # # # # # # #
def getData20Games(platform, gamertag):
    # Make API call
    url = "https://call-of-duty-modern-warfare.p.rapidapi.com/warzone-matches/"+gamertag+"/"+platform
    headers = {
        "X-RapidAPI-Key": "API-KEY",
        "X-RapidAPI-Host": "call-of-duty-modern-warfare.p.rapidapi.com"
    }
    # Sleep 1 second to prevent overload
    #time.sleep(1)
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = json.loads(response.text)
        try:
            if data['message']:
                return 'error'
        except:
            pass

        # # # # # # # #
        #     NEW     #
        # # # # # # # #
        # data --> data['data']
        data = data['data']

        # Retrieve data
        # Most recent game map and mode
        most_recent_map = data['matches'][0]['map']
        most_recent_mode = data['matches'][0]['mode']

        # SUMMARY OF 20 MOST RECENT GAMES DATA - static numbers
        summary_kills = str(int(data['summary']['all']['kills']))
        summary_kdRatio = str(round(data['summary']['all']['kdRatio'],2))
        summary_killsPerGame = str(int(data['summary']['all']['killsPerGame']))
        summary_headshotPercentage = str(int(data['summary']['all']['headshotPercentage'] * 100))
        summary_gulagWinPercentage = str(int(data['summary']['all']['gulagKills'] / 20 * 100))

        # Trend Data Across 20 games (for graphs)
        playerCount_list = []
        kills_list = []
        deaths_list = []
        kdRatio_list = []
        rank_list =[]
        percentTimeMoving_list = []
        longestStreak_list = []
        teamPlacement_list = []
        mode_list = []
        contractsComplete_list = []
        numContractsComplete_list = []
        date_list = []

        # time
        dayOfWeek_list = []
        month_list = []
        day_list = []
        year_list = []
        hour_list = []
        minute_list = []
        period_list = []

        for match in data['matches']:
            playerCount_list.append(match['playerCount']) # playerCount
            kills_list.append(match['playerStats']['kills']) # kills
            deaths_list.append(match['playerStats']['deaths']) # deaths
            rank_list.append(match['playerStats']['rank']) # rank
            kdRatio_list.append(match['playerStats']['kdRatio']) # kdRatio
            percentTimeMoving_list.append(match['playerStats']['percentTimeMoving']) # percentTimeMoving
            longestStreak_list.append(match['playerStats']['longestStreak']) # longestStreak
            teamPlacement_list.append(match['playerStats']['teamPlacement']) # teamPlacement
            mode_list.append(match['mode']) # mode

            # time
            dayOfWeek_list.append(convertDate(match['utcStartSeconds'])[0]) # day of week
            month_list.append(convertDate(match['utcStartSeconds'])[1]) # month
            day_list.append(convertDate(match['utcStartSeconds'])[2]) # day
            year_list.append(convertDate(match['utcStartSeconds'])[3]) # year
            hour_list.append(convertDate(match['utcStartSeconds'])[4]) # hour
            minute_list.append(convertDate(match['utcStartSeconds'])[5]) # minute
            period_list.append(convertDate(match['utcStartSeconds'])[6]) # AM or PM


            ### NEW ###
            #for contract in match['player']['brMissionStats']['missionStatsByType']:
                #contractsComplete_list.append(contract) # contracts completed
            #numContractsComplete_list.append(match['player']['brMissionStats']['missionsComplete']) # number of contracts completed


        # Store into dataframes
        # Contract now unsupported by API
        df_20games_summary = pd.DataFrame({"kills":[summary_kills],
                                            "kdRatio":[summary_kdRatio],
                                            "killsPerGame":[summary_killsPerGame],
                                            "headshotPercentage":[summary_headshotPercentage],
                                            "gulagWinPercentage":[summary_gulagWinPercentage]})

        df_20games_detailed = pd.DataFrame({"playerCount": playerCount_list,
                                            "kills": kills_list,
                                            "deaths": deaths_list,
                                            "kdRatio": kdRatio_list,
                                            "rank": rank_list,
                                            "percentTimeMoving": percentTimeMoving_list,
                                            "longestStreak": longestStreak_list,
                                            "teamPlacement": teamPlacement_list,
                                            "mode": mode_list,
                                            "dayOfWeek": dayOfWeek_list,
                                            "month": month_list,
                                            "day": day_list,
                                            "year": year_list,
                                            "hour": hour_list,
                                            "minute": minute_list,
                                            "period": period_list})
        return df_20games_summary, df_20games_detailed
    else:
        return 'error'



# # # # # # # # # # # # # # # # # # # # # # # # #
# Function: Retrieve API data of lifetime stats #
# # # # # # # # # # # # # # # # # # # # # # # # #
def getDataLifetime(platform, gamertag):
    # Make API call
    url = "https://call-of-duty-modern-warfare.p.rapidapi.com/warzone/"+gamertag+"/"+platform
    headers = {
        "X-RapidAPI-Key": "API-KEY",
        "X-RapidAPI-Host": "call-of-duty-modern-warfare.p.rapidapi.com"
    }
    # Sleep 1 second to prevent overload
    #time.sleep(1)
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = json.loads(response.text)
        try:
            if data['message']:
                return 'error'
        except:
            pass

        # # # # # # # #
        #     NEW     #
        # # # # # # # #
        # data --> data['data']['lifetime']['mode']['br']['properties']
        # Remove BR indices
        data = data['data']['lifetime']['mode']['br']['properties']
        #

        # Retrieve data
        lifetime_gamesPlayed = int(data['gamesPlayed'])
        lifetime_timePlayed = int(data['timePlayed'])

        # row 1
        lifetime_wins = int(data['wins'])
        lifetime_winPercentage = round(lifetime_wins / lifetime_gamesPlayed * 100,2)
        lifetime_daysPlayed = int(lifetime_timePlayed / 3600 / 24)
        lifetime_hoursPlayed = int(((lifetime_timePlayed / 3600 / 24) - lifetime_daysPlayed) * 24)
        lifetime_minutesPlayed = int(((((lifetime_timePlayed / 3600 / 24) - lifetime_daysPlayed) * 24) - lifetime_hoursPlayed) * 60)

        # row 2
        lifetime_kills = int(data['kills'])
        lifetime_deaths = data['deaths']
        lifetime_killsPerGame = int(lifetime_kills / lifetime_gamesPlayed)
        lifetime_kdRatio = round(data['kdRatio'],2)

        # extra info if needed
        lifetime_downs = data['downs']
        lifetime_topTwentyFive = data['topTwentyFive']
        lifetime_topTen = data['topTen']
        lifetime_topFive = data['topFive']
        lifetime_revives = data['revives']

        # Store into dataframe
        df_lifetime = pd.DataFrame({"wins":[lifetime_wins],
                                    "winPercentage":[lifetime_winPercentage],
                                    "daysPlayed":[lifetime_daysPlayed],
                                    "hoursPlayed":[lifetime_hoursPlayed],
                                    "minutesPlayed":[lifetime_minutesPlayed],
                                    "kills":[lifetime_kills],
                                    "deaths":[lifetime_deaths],
                                    "killsPerGame":[lifetime_killsPerGame],
                                    "kdRatio":[lifetime_kdRatio],
                                    "downs":[lifetime_downs],
                                    "gamesPlayed":[lifetime_gamesPlayed],
                                    "topTwentyFive":[lifetime_topTwentyFive],
                                    "topTen":[lifetime_topTen],
                                    "topFive":[lifetime_deaths],
                                    "revives":[lifetime_revives]})
        temp = ' '
        return df_lifetime, temp
    else:
        return 'error'



# # # # # # # # # # # # # # # # # # # # # # # #
# Function: Retrieve API data of weekly stats #
# # # # # # # # # # # # # # # # # # # # # # # #
# Using most recent 20 games! (Weekly stats is unsupported now)
def getDataWeekly(platform, gamertag):
    # Make API call
    url = "https://call-of-duty-modern-warfare.p.rapidapi.com/warzone-matches/"+gamertag+"/"+platform
    headers = {
        "X-RapidAPI-Key": "API-KEY",
        "X-RapidAPI-Host": "call-of-duty-modern-warfare.p.rapidapi.com"
    }
    # Sleep 1 second to prevent overload
    #time.sleep(1)
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = json.loads(response.text)
        try:
            if data['message']:
                return 'error'
        except:
            pass

        # # # # # # # #
        #     NEW     #
        # # # # # # # #
        # data --> data['data']
        data = data['data']

        # Retrieve data
        # SUMMARY OF 20 MOST RECENT GAMES DATA - static numbers
        weekly_kills = int(data['summary']['all']['kills'])
        weekly_deaths = int(data['summary']['all']['deaths'])
        weekly_kdRatio = round(data['summary']['all']['kdRatio'],2)
        weekly_killsPerGame = int(data['summary']['all']['killsPerGame'])
        weekly_damageDone = int(data['summary']['all']['damageDone'])
        weekly_damageTaken = int(data['summary']['all']['damageTaken'])
        weekly_matchesPlayed = int(data['summary']['all']['matchesPlayed'])
        weekly_hoursPlayed = (int(data['summary']['all']['timePlayed']) / 3600)

        # Store into dataframes
        df_weekly = pd.DataFrame({"kills":[weekly_kills],
                                  "deaths":[weekly_deaths],
                                  "kdRatio":[weekly_kdRatio],
                                  "killsPerGame":[weekly_killsPerGame],
                                  "damageDone":[weekly_damageDone],
                                  "damageTaken":[weekly_damageTaken],
                                  "matchesPlayed":[weekly_matchesPlayed],
                                  "hoursPlayed":[weekly_hoursPlayed]})
        # temp
        temp = ' '
        return df_weekly, temp
    else:
        return 'error'

