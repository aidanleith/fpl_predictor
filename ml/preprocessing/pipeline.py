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
        print(x.iloc[0:38, 10:20])
        print(y)

    #splits the dataframe into training (80%) and testing (20%)
    def split(self, df):
        split = 0.2
        splitIndex = int(len(df) * (1-split))

        xTrain = df.iloc[:splitIndex]
        yTrain = df.iloc[:splitIndex]
        xTest = df.iloc[splitIndex:]
        yTest = df.iloc[splitIndex:]

        return xTrain, yTrain, xTest, yTest


p = MLPipeline("FWD", "2024-25")
df = p.retrieveData("2024-25")
df = df[df["element"] == 4]
p.preprocessData(df)

    

    