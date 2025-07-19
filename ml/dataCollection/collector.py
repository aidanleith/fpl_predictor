#Collector.py retrieves data from a specified url and returns a dataframe representing that data.
from ml.dataCollection.config import FPLConfig
import pandas as pd

class dataCollector:

    def __init__(self):
        self.configs = FPLConfig()

    #list of all players stats for entire season
    def playersStatsSeason(self, season):
        url = self.configs.dataSource.getCleanedPlayersUrl(season)
        df = pd.read_csv(url)
        return df
        
    #list of a specific players performance for each gameweek in a season
    def playerPerformanceGameweek(self, season, name):
        url = self.configs.dataSource.getPlayerUrl(season, name)
        df = pd.read_csv(url)
        return df
    
    #data for all players in a specific gameweek
    def gameweekStats(self, season):
        url = self.configs.dataSource.getGameweekUrl(season)
        df = pd.read_csv(url)
        return df
    
    #data on each player for each gameweek
    def gameweekMerged(self, season):
        url = self.configs.dataSource.getGameweekMergedUrl(season)
        df = pd.read_csv(url, on_bad_lines = 'warn')
        return df

    #seasonal team data
    def teamData(self, season):
        url = self.configs.dataSource.getTeamsUrl(season)
        df = pd.read_csv(url)
        return df
    
    #players names and associated id's as stored by FPL
    def playerIdList(self, season):
        url = self.configs.dataSource.playerIdListUrl(season)
        df = pd.read_csv(url)
        return df