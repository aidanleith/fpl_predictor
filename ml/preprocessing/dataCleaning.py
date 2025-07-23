import sys
sys.path.append('../..')

from ml.dataCollection.collector import dataCollector
from ml.dataCollection.config import dataSourceConfig
import pandas as pd
import numpy as np
import requests

class cleanData:

    def __init__(self):
        self.collector = dataCollector()
        self.configs = dataSourceConfig()
    
    #removes features not relevant to the model, handles missing values, 
    def clean(self):

        #list of positions
        positions = ["GK", "DEF", "MID", "FWD"]

        #combine dataframes and clean
        firstDf, secondDf = self.collector.gameweekMerged("2024-25")
        df = self.combine(firstDf, secondDf)
        self.drop(df)

        for pos in positions:
            posDf = firstDf[firstDf['position'] == pos]

            if pos == "GK":
                size = posDf.size
                print(posDf.iloc[0:82])
            elif pos == "DEF":
                continue
            elif pos == "MID":
                continue
            else:
                continue
        return True

    #combine two dataframes 
    def combine(self, df1, df2):
        #concat since the two dfs have same columns, ignore indices so they dont reset from 0 at second df
        #use join when u want to combine two dfs side by side
        #merge for finding all matches on a specified column/row name, then adding all found data for that match into one row
        res = pd.concat([df1,df2], ignore_index=True)

        return res
    
    def drop(self, df):
        
        return True
    
    def debug_problematic_lines(self, season):
        url = self.configs.getGameweekMergedUrl(season)
        response = requests.get(url)
        lines = response.text.split('\n')
        
        header_cols = len(lines[0].split(','))
        problematic_lines = []
        
        for i, line in enumerate(lines[1:], 1): 
            if line.strip(): 
                cols = len(line.split(','))
                if cols != header_cols:
                    problematic_lines.append((i, cols, line[:200])) 
                    if len(problematic_lines) < 5: 
                        print(f"Line {i}: {cols} fields")
                        print(f"Content: {line[:200]}...")
                        print("---")
        
        print(f"Found {len(problematic_lines)} problematic lines out of {len(lines)-1} total")
        return problematic_lines
    
        

d = cleanData()
d.clean()





        

