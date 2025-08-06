#Collector.py retrieves data from a specified url and returns a dataframe representing that data.
from ml.dataCollection.config import FPLConfig
import pandas as pd
import requests

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
        print(f"Trying to read CSV from: {url}")
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
    
        #find where line formatting changes
        formatChange = self._find_format_change_line(url)
        
        if formatChange is None:
            #return normally
            df = pd.read_csv(url)
            return df
        
        print(f"Format change at line {formatChange}")
        
        #read first part
        df1 = pd.read_csv(url, nrows=formatChange-1)
        print(f"First part: {len(df1)} rows, {len(df1.columns)} columns")

        desired_column_indices = list(range(21)) + list(range(28, 49))
        
        #read second part
        try:
            df2 = pd.read_csv(url, skiprows=formatChange, names=df1.columns, usecols=desired_column_indices)
            print(f"Second part: {len(df2)} rows, {len(df2.columns)} columns")
        except Exception as e:
            print(f"Error occurred: {e}")
        
        return pd.concat([df1,df2], ignore_index=True)
    
    #find the line number where CSV format changes
    def _find_format_change_line(self, url):
        response = requests.get(url)
        lines = response.text.split('\n')
        
        if not lines:
            return None
            
        header_cols = len(lines[0].split(','))
        
        for i, line in enumerate(lines[1:], 1):
            if line.strip():
                cols = len(line.split(','))
                if cols != header_cols:
                    return i
        
        return None

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