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

    #creates 3 to 5 game rolling averages for features that all players regardless of position gain/lose points from
    def createRollingAverages(self, df):
        rollingCols = ["total_points", "goals_scored", "assists", "minutes",
                       "expected_goals", "expected_goal_involvements", "expected_assists",
                       "yellow_cards", "red_cards", "bonus"]
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
    
    #position specific features. note: FWD have no specific feature to gain or lose points from outside of general features
    def createPositionalStats(self, df):
        if self.position == "GK":
            newCols = ['saves', 'clean_sheets', 'goals_conceded', 'penalties_saved', 
                       'expected_goals_conceded']
            
            for col in newCols:
                df[f'{col}_last3'] = (
                        df[f'{col}']
                        .shift(1)
                        .rolling(3, min_periods=1)
                        .mean()
                )


        elif self.position == "DEF":
            newCols = ['goals_conceded', 'expected_goals_conceded', 'clean_sheets']
            
            for col in newCols:
                df[f'{col}_last3'] = (
                        df[f'{col}']
                        .shift(1)
                        .rolling(3, min_periods=1)
                        .mean()
                )

        #midfield specific stats, dont lose points for conceding but gain 1 for clean sheet
        elif self.position == "MID":
            newCols = ['clean_sheets']

            for col in newCols:
                df[f'{col}_last3'] = (
                        df[f'{col}']
                        .shift(1)
                        .rolling(3, min_periods=1)
                        .mean()
                )
        return df
    
    #encode categorical variables
    def encode(self, df):
        df['was_home'] = df['was_home'].astype(int)
        return df
    
    #add opponent team strength for each gameweek from team data csv
    def addOpponentStrength(self, df):
        collect = dataCollector()
        teamDf = collect.teamData(self.season)
        df = df.merge(teamDf[['strength', 'id']], left_on='opponent_team', right_on='id', how='left')
        df.drop(columns='id', inplace=True)

        return df
        
    
    #ensure no gw repeats as there are in csv file
    def fixGwRepeats(self, df):
        #create new column which splits df by each player id and counts number of rows
        df['corrected_gameweeks'] = df.groupby('element').cumcount()+1

        #replace gw column with corrected column, drop corrected column
        df['GW'] = df['corrected_gameweeks']
        df.drop(columns='corrected_gameweeks', inplace=True)

        return df

    #returns x,y with x being training features and y being total points in dataframes
    def finalDf(self,df):
        colsToKeep = ["was_home", "value", "selected", "transfers_in", "transfers_out",
                      "total_points_last3", "total_points_last5", "goals_scored_last3", 
                      "goals_scored_last5", "assists_last3", "assists_last5", "minutes_last3",
                      "minutes_last5", "expected_goals_last3", "expected_goals_last5",
                      "expected_goal_involvements_last3", "expected_goal_involvements_last5",
                      "expected_assists_last3", "expected_assists_last5", "yellow_cards_last3", 
                      "yellow_cards_last5", "red_cards_last3", "red_cards_last5", "bonus_last3",
                      "bonus_last5", "strength"]
        
        positionSpecific = []
        
        #use .extend to pass through multiple arguments, append accepts only 1
        if self.position == "GK":
            positionSpecific.extend(['saves_last3', 'clean_sheets_last3', 'goals_conceded_last3',
                                 'penalties_saved_last3', 'expected_goals_conceded_last3'])
        elif self.position == "DEF":
            positionSpecific.extend(['goals_conceded_last3', 'expected_goals_conceded_last3', 'clean_sheets_last3'])
        elif self.position == "MID":
            positionSpecific.extend(["clean_sheets_last3"])

        for col in positionSpecific:
            colsToKeep.append(col)

        x = df[colsToKeep]
        y = df["total_points"]
        return x, y