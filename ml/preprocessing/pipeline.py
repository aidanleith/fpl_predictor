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
        #self.collect = dataCollector()

    #retrieve raw data on a player for a specific season
    '''def retrieveData(self, season):
        df = self.collect.gameweekMerged(season)
        return df'''

    #data cleaning and feature engineering. returns my training features (x) and target values (y)
    def preprocessData(self, df):
        dfClean = self.cleaner.cleanAndSort(df)

        dfEngineered = self.engineer.fixGwRepeats(dfClean)
        dfEngineered = self.engineer.encode(dfEngineered)
        dfEngineered = self.engineer.createRollingAverages(dfEngineered)
        dfEngineered = self.engineer.addOpponentStrength(dfEngineered)
        dfEngineered = self.engineer.createPositionalStats(dfEngineered)
        x, y = self.engineer.finalDf(dfEngineered)
        return x,y

    #splits the dataframe into training (80%) and testing (20%)
    def split(self, x, y):
        change = 4
        train_indices = []
        test_indices = []
        
        for i in range(len(x)):
            if (i + 1) % change == 0:  # Every 4th game (1-indexed)
                test_indices.append(i)
            else:
                train_indices.append(i)
        
        xTrain = x.iloc[train_indices]
        yTrain = y.iloc[train_indices]
        xTest = x.iloc[test_indices]
        yTest = y.iloc[test_indices]

        return xTrain, yTrain, xTest, yTest


    

    