import pandas as pd
from ml.dataCollection.collector import dataCollector

'''
Engineers df's that are comprised of an individuals stats for an entire season, not all players stats for whole season.
Functionality: Creates 3 and 5 game rolling averages, form indicator, position specific stats, opponent team strength, 
fixes repeating gameweek entries, and selects final df to train on.
'''

class featureEngineer:

    def __init__(self, position, season):
        self.position = position
        self.season = season

    #creates 3 to 5 game rolling averages of points, goals, assists, and mins
    def createRollingAverages(self, df):
        rollingCols = ["total_points", "goals_scored", "assists", "minutes"]

        #last 3 averages, requires at least 1 previous gameweek, first gameweek will always be None
        for col in rollingCols:
            df[f'{col}_last3'] = (
                    df[f'{col}']
                    .shift(1)
                    .rolling(3, min_periods=1)
                    .mean()
                    )
            
            #last 5 averages, requires at least 1 previous gameweek, first gameweek always None
            df[f'{col}_last5'] = (
                    df[f'{col}']
                    .shift(1)
                    .rolling(5, min_periods=1)
                    .mean()
                    )
        return df
    
    def createFormIndicators(self, df):

        return df
    
    def createPositionalStats(self, df):

        return df
    
    #encode categorical variables
    def encode(self, df):
        df['was_home'] = df['was_home'].astype(int)
        return df
    
    def addOpponentStrength(self, df):
        collect = dataCollector()
        teamDf = collect.teamData(self.season)
        
    
    #ensure no gw repeats as there are in csv file
    def fixGwRepeats(self, df):
        #create new column which splits df by each player id and counts number of rows
        df['corrected_gameweeks'] = df.groupby('element').cumcount()+1

        #replace gw column with corrected column, drop corrected column
        df['GW'] = df['corrected_gameweeks']
        df.drop(columns='corrected_gameweeks', inplace=True)

        return df

    def finalDf(self,df):
        colsToKeep = ["was_home", "value", "selected", "transfers_in", "transfers_out"]

        x = df[colsToKeep]
        y = df["total_points"]
        return x, y