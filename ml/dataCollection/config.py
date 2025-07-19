import os
from dotenv import load_dotenv

load_dotenv()

#Configs for database, FPL Client, and github repo data collection.

'''
#FPl Client (not currently in use)
class FPLClient:
    API_BASE_URL = "https://fantasy.premierleague.com/api"
'''

#Github Repo data source config
class dataSourceConfig:

    def __init__(self):
        self.base_url = "https://raw.githubusercontent.com/vaastav/Fantasy-Premier-League/master/data"
        self.season = ["2016-17", "2017-18", "2018-19", "2019-20", "2020-21", "2021-22", "2022-23", "2023-24",
                        "2024-25"
                        ]
    
    #retrieve specific url for a season
    def getSeasonUrl(self, season):
        if season not in self.season:
            raise ValueError (f"{season} is not supported. List of available season: {self.season}")
        else:
            return f"{self.base_url}/{season}"
    
    #retrieve list of all players stats for entire season
    def getCleanedPlayersUrl(self, season):
        return f"{self.getSeasonUrl(season)}/cleaned_players.csv"
    
    #retrieve list of a specific players performance for each gameweek for a specific season
    def getPlayerUrl(self, season, name):
        return f"{self.getSeasonUrl(season)}/players/{name}/gw.csv"
    
    #retrieve data on all players for a specific gameweek
    def getGameweekUrl(self, season, gw):
        return f"{self.getSeasonUrl(season)}/gws/gw{gw}.csv"

    #data on each player for each gameweek (large)
    def getGameweekMergedUrl(self, season):
        return f"{self.getSeasonUrl(season)}/gws/merged_gw.csv"
    
    #data on teams (strength, id, etc.)
    def getTeamsUrl(self, season):
        return f"{self.getSeasonUrl(season)}/teams.csv"
    
    def playerIdListUrl(self, season):
        return f"{self.getSeasonUrl(season)}/player_idlist.csv"
    
#Database using mySQL
class databaseConfig:

    def __init__(self):
        self.host = os.getenv('DB_HOST')
        self.port = int(os.getenv('DB_PORT'))
        self.database = os.getenv('DB_DATABASE')
        self.username = os.getenv('DB_USERNAME')
        self.password = os.getenv('DB_PASSWORD')

class FPLConfig:

    def __init__(self):
        self.database = databaseConfig()
        self.dataSource = dataSourceConfig()
