import pandas as pd
from sklearn.ensemble import RandomForestRegressor

'''

'''

class baseTrainer:

    #samples split generally 2 times leaf to ensure logical consistency, in other words,
    #when a split happens, two nodes are created. a split would never be possible if the number of split categories
    #was less than 2 times the min samples leaf 
    #42 used simply to always be able to reproduce same results, can use any number but will get different results with different nums
    def __init__(self, position):
        self.position = position
        self.isTrained = False
        self.features = None
        self.model = RandomForestRegressor(
            n_estimators=50,
            max_depth=10,
            min_samples_split=4,
            min_samples_leaf=2,
            max_features='sqrt',
            random_state=42
        )
        

    def fit(self, xTrain, yTrain):
        self.model.fit(xTrain, yTrain)
        self.isTrained = True
        self.features = xTrain.columns

    def predict(self, xTrain):
        if not self.isTrained:
            print("Model not trained yet")
            return False
        
        return self.model.predict(xTrain)
    
    def featureImportance(self):
        return False
