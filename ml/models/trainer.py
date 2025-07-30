import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np
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
        #self.isTrained = False
        self.features = None
        self.model = RandomForestRegressor(
            n_estimators=5,
            max_depth=3,
            min_samples_split=15,
            min_samples_leaf=8,
            max_features='sqrt',
            random_state=42
        )
        

    def fit(self, xTrain, yTrain):
        self.model.fit(xTrain, yTrain)
        #self.isTrained = True
        self.features = list(xTrain.columns)

    def predict(self, xTest):
        '''if not self.isTrained:
            print("Model not trained yet")
            return False'''
        
        return self.model.predict(xTest)
    
    def evaluate(self, xTrain, yTrain, xTest, yTest):
        """Evaluate model performance"""
        '''if not self.isTrained:
            print("Model not trained yet")
            return None'''
            
        predictions = self.predict(xTest)
        if predictions is None:
            return None
            
        mae = mean_absolute_error(yTest, predictions)
        mse = mean_squared_error(yTest, predictions)
        rmse = np.sqrt(mse)
        r2 = r2_score(yTest, predictions)
        
        print(f"Standard metrics: MAE={mae:.3f}, RMSE={rmse:.3f}, R²={r2:.3f}")
    
        # Run debug analysis
        debug_results = self.debug_model_performance(self.model, xTrain, yTrain, xTest, yTest)
        
        return {
            'mae': mae,
            'mse': mse,
            'rmse': rmse,
            'r2': r2,
            'debug_info': debug_results
        }
    
    def debug_model_performance(self, model, xTrain, yTrain, xTest, yTest):
        """Debug why R² is so negative"""
        
        print("=== MODEL DEBUGGING ===")
        
        # Basic data info
        print(f"Training samples: {len(xTrain)}")
        print(f"Test samples: {len(xTest)}")
        print(f"Features: {len(xTrain.columns)}")
        
        # Target variable analysis
        print(f"\nTarget Variable Analysis:")
        print(f"yTrain - Mean: {yTrain.mean():.2f}, Std: {yTrain.std():.2f}, Min: {yTrain.min():.2f}, Max: {yTrain.max():.2f}")
        print(f"yTest  - Mean: {yTest.mean():.2f}, Std: {yTest.std():.2f}, Min: {yTest.min():.2f}, Max: {yTest.max():.2f}")
        
        # Check for data issues
        print(f"\nData Quality Checks:")
        print(f"yTrain NaN values: {yTrain.isna().sum()}")
        print(f"yTest NaN values: {yTest.isna().sum()}")
        print(f"yTrain infinite values: {np.isinf(yTrain).sum()}")
        print(f"yTest infinite values: {np.isinf(yTest).sum()}")
        
        # Training vs Test predictions
        train_pred = model.predict(xTrain)
        test_pred = model.predict(xTest)
        
        print(f"\nPrediction Analysis:")
        print(f"Train Pred - Mean: {train_pred.mean():.2f}, Std: {train_pred.std():.2f}, Min: {train_pred.min():.2f}, Max: {train_pred.max():.2f}")
        print(f"Test Pred  - Mean: {test_pred.mean():.2f}, Std: {test_pred.std():.2f}, Min: {test_pred.min():.2f}, Max: {test_pred.max():.2f}")
        
        # Performance on train vs test
        train_mae = mean_absolute_error(yTrain, train_pred)
        train_r2 = r2_score(yTrain, train_pred)
        test_mae = mean_absolute_error(yTest, test_pred)
        test_r2 = r2_score(yTest, test_pred)
        
        print(f"\nTraining Performance:")
        print(f"Train MAE: {train_mae:.3f}, R²: {train_r2:.3f}")
        print(f"Test MAE:  {test_mae:.3f}, R²: {test_r2:.3f}")
        
        # Check if we're just predicting constants
        print(f"\nPrediction Variance:")
        print(f"Train pred variance: {np.var(train_pred):.3f}")
        print(f"Test pred variance: {np.var(test_pred):.3f}")
        
        # Manual R² calculation to verify
        ss_res = np.sum((yTest - test_pred) ** 2)
        ss_tot = np.sum((yTest - yTest.mean()) ** 2)
        manual_r2 = 1 - (ss_res / ss_tot)
        
        print(f"\nManual R² calculation: {manual_r2:.3f}")
        print(f"SS_res (residual sum of squares): {ss_res:.2f}")
        print(f"SS_tot (total sum of squares): {ss_tot:.2f}")
        
        # Show some actual vs predicted examples
        print(f"\nSample Predictions (first 10):")
        comparison_df = pd.DataFrame({
            'Actual': yTest.iloc[:10].values,
            'Predicted': test_pred[:10],
            'Difference': yTest.iloc[:10].values - test_pred[:10]
        })
        print(comparison_df)
        
        return {
            'train_mae': train_mae,
            'train_r2': train_r2,
            'test_mae': test_mae,
            'test_r2': test_r2,
            'prediction_variance': np.var(test_pred)
        }
    
    def featureImportance(self):
        """Get feature importance from trained model"""
        '''if not self.isTrained:
            print("Model not trained yet")
            return None'''
            
        importance_df = pd.DataFrame({
            'feature': self.features,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        return importance_df