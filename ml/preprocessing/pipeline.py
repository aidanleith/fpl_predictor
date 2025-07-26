import pandas as pd
from ml.preprocessing.dataCleaning import cleanData
from ml.preprocessing.featureEngineering import featureEngineer
from ml.dataCollection.collector import dataCollector

'''
The following class retrieves the original data for an individual player for a specific season and 
prepares the dataframe for training. Data cleaning and feature engineering results 2 final dataframes,
x and y.
'''
class MLPipeline:

    def __init__(self, position, season):
        self.cleaner = cleanData()
        self.engineer = featureEngineer(position, season)
        self.collect = dataCollector()

    #retrieve raw data on a player for a specific season
    def retrieveData(self, season):
        df = self.collect.gameweekMerged(season)
        return df

    #data cleaning and feature engineering. returns my training features (x) and target values (y)
    def preprocessData(self, df):
        dfClean = self.cleaner.cleanAndSort(df)

        dfEngineered = self.engineer.fixGwRepeats(dfClean)
        dfEngineered = self.engineer.encode(dfEngineered)
        dfEngineered = self.engineer.createRollingAverages(dfEngineered)
        dfEngineered = self.engineer.addOpponentStrength(dfEngineered)
        dfEngineered = self.engineer.createPositionalStats(dfEngineered)
        x, y = self.engineer.finalDf(dfEngineered)

        print(x.columns)


p = MLPipeline("GK", "2024-25")
df = p.retrieveData("2024-25")
df = df[df["element"] == 344]
p.preprocessData(df)

    

    