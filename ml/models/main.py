from ml.preprocessing.pipeline import MLPipeline
from ml.dataCollection.collector import dataCollector
from ml.models.trainer import baseTrainer

'''
Current problems: need to figure out way to get multiple seasons of data for a player who has multiple seasons,
model performing decent but not great (maybe lack of data), need to figure out how to account for injuries, 
figure out how to deal with new players to the league who dont have past data in pl, how to store models,
should automatically predict points for all players before each gameweek and store predictions in database for easy access
'''

class modelHandler:

    def main(self):
        season = "2024-25"
        collector = dataCollector()
        models = {}

        #collect all player data 
        allDf = collector.gameweekMerged(season)

        #retrieve range of players needed to create predictions for
        numPlayers = allDf['element'].nunique()
        uniqueId = list(range(1,numPlayers+1))

        for id in range(4,5):
            #ensure this is a copy to not receive "view" warnings
            playerDf = allDf[allDf['element'] == id].copy()
            position = playerDf['position'].iloc[0]

            trainer = baseTrainer(position)

            preprocess = MLPipeline(position, season)

            x,y = preprocess.preprocessData(playerDf)
            xTrain, yTrain, xTest, yTest = preprocess.split(x, y)

            trainer.fit(xTrain, yTrain)
            featureImportance = trainer.featureImportance()
            results = trainer.evaluate(xTrain, yTrain, xTest, yTest)


p = modelHandler()

p.main()