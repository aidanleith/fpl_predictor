import pandas as pd
from ml.preprocessing.dataCleaning import cleanData
from ml.preprocessing.featureEngineering import featureEngineer
from ml.dataCollection.collector import dataCollector

class MLPipeline:

    def __init__(self, position, season):
        self.cleaner = cleanData()
        self.engineer = featureEngineer(position, season)
        self.collect = dataCollector()
        self.position = position

    def retrieveData(self, season):
        df = self.collect.gameweekMerged(season)
        return df

    def preprocessData(self, df):
        dfClean = self.cleaner.cleanAndSort(df)

        dfEngineered = self.engineer.fixGwRepeats(dfClean)
        dfEngineered = self.engineer.encode(dfEngineered)
        dfEngineered = self.engineer.createRollingAverages(dfEngineered)
        dfEngineered = self.engineer.addOpponentStrength(dfEngineered)
        dfEngineered = self.engineer.createFormIndicators(dfEngineered)
        finalDf = self.engineer.finalDf(dfEngineered)


p = MLPipeline("GK", "2024-25")
df = p.retrieveData("2024-25")
df = df[df["element"] == 4]
p.preprocessData(df)
    

    