import pandas as pd
import numpy as np
import requests

'''
Class utilized by preprocessing pipeline to perform basic data cleaning such as dropping immediately irrelevant columns and sorting
df based on id first then gameweek. Will ensure that the final df is comprised of one players stats for the season in ascending order.
'''

class cleanData:

    def __init__(self):
        pass

    #removes features not relevant to the model, sorts
    def cleanAndSort(self, df):
        df = self.drop(df)
        df = self.sort(df)
        return df

    #drop unnecessary features from df
    def drop(self, df):
        try:
            toDrop = [
                "fixture", "ict_index", "kickoff_time", "team_a_score", "team_h_score", "modified"
            ]
            df.drop(columns=toDrop)
            return df
        
        except Exception as e:
            print(f"Exception occured dropping columns: {e}")
    
    #sort df by player id then gameweek in ascending order to have each player together in ascending gameweeks
    def sort(self, df):
        try:
            df.sort_values(by=["element", "GW"])
            return df
        except Exception as e:
            print(f"Exception occured sorting df by players: {e}")

    





        

