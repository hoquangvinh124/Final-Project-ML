"""
Advanced Hyperparameter Tuning for Logistics KPI Prediction
Using Optuna for Bayesian Optimization to achieve R² > 85%
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
import xgboost as xgb
import lightgbm as lgb
from catboost import CatBoostRegressor
import optuna
from optuna.samplers import TPESampler
import joblib
import warnings
warnings.filterwarnings('ignore')

class HyperparameterTuner:
    """Advanced hyperparameter tuning using Optuna"""
    
    def __init__(self, X_train, y_train, X_test, y_test, random_state=42):
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test
        self.random_state = random_state
        self.best_params = {}
        self.best_models = {}
        
    def objective_xgboost(self, trial):
        """Objective function for XGBoost optimization"""
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 300, 1000),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
            'max_depth': trial.suggest_int('max_depth', 3, 12),
            'min_child_weight': trial.suggest_int('min_child_weight', 1, 10),
            'subsample': trial.suggest_float('subsample', 0.6, 1.0),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
            'gamma': trial.suggest_float('gamma', 0, 0.5),
            'reg_alpha': trial.suggest_float('reg_alpha', 0, 1.0),
            'reg_lambda': trial.suggest_float('reg_lambda', 0, 2.0),
            'random_state': self.random_state,
            'n_jobs': -1
        }
        
        model = xgb.XGBRegressor(**params)
        kfold = KFold(n_splits=5, shuffle=True, random_state=self.random_state)
        scores = cross_val_score(model, self.X_train, self.y_train, 
                                cv=kfold, scoring='r2', n_jobs=-1)
        return scores.mean()
    
    def objective_lightgbm(self, trial):
        """Objective function for LightGBM optimization"""
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 300, 1000),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
            'max_depth': trial.suggest_int('max_depth', 3, 12),
            'num_leaves': trial.suggest_int('num_leaves', 20, 150),
            'min_child_samples': trial.suggest_int('min_child_samples', 10, 100),
            'subsample': trial.suggest_float('subsample', 0.6, 1.0),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
            'reg_alpha': trial.suggest_float('reg_alpha', 0, 1.0),
            'reg_lambda': trial.suggest_float('reg_lambda', 0, 2.0),
            'random_state': self.random_state,
            'n_jobs': -1,
            'verbose': -1
        }
        
        model = lgb.LGBMRegressor(**params)
        kfold = KFold(n_splits=5, shuffle=True, random_state=self.random_state)
        scores = cross_val_score(model, self.X_train, self.y_train, 
                                cv=kfold, scoring='r2', n_jobs=-1)
        return scores.mean()
    
    def objective_catboost(self, trial):
        """Objective function for CatBoost optimization"""
        params = {
            'iterations': trial.suggest_int('iterations', 300, 1000),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
            'depth': trial.suggest_int('depth', 3, 10),
            'l2_leaf_reg': trial.suggest_float('l2_leaf_reg', 1, 10),
            'subsample': trial.suggest_float('subsample', 0.6, 1.0),
            'random_state': self.random_state,
            'verbose': False
        }
        
        model = CatBoostRegressor(**params)
        kfold = KFold(n_splits=5, shuffle=True, random_state=self.random_state)
        scores = cross_val_score(model, self.X_train, self.y_train, 
                                cv=kfold, scoring='r2', n_jobs=-1)
        return scores.mean()
    
    def tune_xgboost(self, n_trials=50):
        """Tune XGBoost hyperparameters"""
        print("\n" + "="*80)
        print("TUNING XGBOOST")
        print("="*80)
        
        study = optuna.create_study(
            direction='maximize',
            sampler=TPESampler(seed=self.random_state)
        )
        study.optimize(self.objective_xgboost, n_trials=n_trials, show_progress_bar=True)
        
        self.best_params['XGBoost'] = study.best_params
        print(f"\nBest CV R²: {study.best_value:.4f}")
        print(f"Best parameters: {study.best_params}")
        
        # Train final model with best parameters
        best_model = xgb.XGBRegressor(**study.best_params, random_state=self.random_state, n_jobs=-1)
        best_model.fit(self.X_train, self.y_train)
        self.best_models['XGBoost'] = best_model
        
        return study
    
    def tune_lightgbm(self, n_trials=50):
        """Tune LightGBM hyperparameters"""
        print("\n" + "="*80)
        print("TUNING LIGHTGBM")
        print("="*80)
        
        study = optuna.create_study(
            direction='maximize',
            sampler=TPESampler(seed=self.random_state)
        )
        study.optimize(self.objective_lightgbm, n_trials=n_trials, show_progress_bar=True)
        
        self.best_params['LightGBM'] = study.best_params
        print(f"\nBest CV R²: {study.best_value:.4f}")
        print(f"Best parameters: {study.best_params}")
        
        # Train final model with best parameters
        best_model = lgb.LGBMRegressor(**study.best_params, random_state=self.random_state, 
                                       n_jobs=-1, verbose=-1)
        best_model.fit(self.X_train, self.y_train)
        self.best_models['LightGBM'] = best_model
        
        return study
    
    def tune_catboost(self, n_trials=50):
        """Tune CatBoost hyperparameters"""
        print("\n" + "="*80)
        print("TUNING CATBOOST")
        print("="*80)
        
        study = optuna.create_study(
            direction='maximize',
            sampler=TPESampler(seed=self.random_state)
        )
        study.optimize(self.objective_catboost, n_trials=n_trials, show_progress_bar=True)
        
        self.best_params['CatBoost'] = study.best_params
        print(f"\nBest CV R²: {study.best_value:.4f}")
        print(f"Best parameters: {study.best_params}")
        
        # Train final model with best parameters
        best_model = CatBoostRegressor(**study.best_params, random_state=self.random_state, verbose=False)
        best_model.fit(self.X_train, self.y_train)
        self.best_models['CatBoost'] = best_model
        
        return study
    
    def evaluate_tuned_models(self):
        """Evaluate all tuned models"""
        from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
        
        print("\n" + "="*80)
        print("TUNED MODELS EVALUATION")
        print("="*80)
        
        results = {}
        for name, model in self.best_models.items():
            y_train_pred = model.predict(self.X_train)
            y_test_pred = model.predict(self.X_test)
            
            train_r2 = r2_score(self.y_train, y_train_pred)
            test_r2 = r2_score(self.y_test, y_test_pred)
            test_rmse = np.sqrt(mean_squared_error(self.y_test, y_test_pred))
            test_mae = mean_absolute_error(self.y_test, y_test_pred)
            
            results[name] = {
                'train_r2': train_r2,
                'test_r2': test_r2,
                'test_rmse': test_rmse,
                'test_mae': test_mae
            }
            
            print(f"\n{name}:")
            print(f"  Train R²: {train_r2:.4f}")
            print(f"  Test R²: {test_r2:.4f}")
            print(f"  Test RMSE: {test_rmse:.4f}")
            print(f"  Test MAE: {test_mae:.4f}")
            
            if test_r2 >= 0.85:
                print(f"  ✅ TARGET ACHIEVED! R² = {test_r2:.4f} >= 0.85")
        
        return results
    
    def run_complete_tuning(self, n_trials=50):
        """Run complete hyperparameter tuning pipeline"""
        print("="*80)
        print("ADVANCED HYPERPARAMETER TUNING")
        print(f"Optimization Trials per Model: {n_trials}")
        print("="*80)
        
        # Tune all models
        self.tune_xgboost(n_trials)
        self.tune_lightgbm(n_trials)
        self.tune_catboost(n_trials)
        
        # Evaluate all tuned models
        results = self.evaluate_tuned_models()
        
        # Find best model
        best_model_name = max(results, key=lambda k: results[k]['test_r2'])
        best_r2 = results[best_model_name]['test_r2']
        
        print("\n" + "="*80)
        print("TUNING RESULTS SUMMARY")
        print("="*80)
        print(f"🏆 BEST MODEL: {best_model_name}")
        print(f"   Test R²: {best_r2:.4f}")
        
        if best_r2 >= 0.85:
            print(f"\n✅ SUCCESS! Target R² > 85% ACHIEVED!")
        else:
            print(f"\n⚠️ Target not achieved. Best R²: {best_r2:.4f}")
        
        # Save best parameters
        pd.DataFrame(self.best_params).T.to_csv('best_hyperparameters.csv')
        print("\n✅ Best hyperparameters saved: best_hyperparameters.csv")
        
        # Save best model
        best_model = self.best_models[best_model_name]
        joblib.dump(best_model, f'models/best_tuned_model_{best_model_name}.pkl')
        print(f"✅ Best model saved: models/best_tuned_model_{best_model_name}.pkl")
        
        return {
            'best_model': best_model,
            'best_model_name': best_model_name,
            'results': results,
            'best_params': self.best_params
        }


def load_and_prepare_data(filepath):
    """Load and prepare data with feature engineering"""
    from train_model import LogisticsKPIPredictor
    
    predictor = LogisticsKPIPredictor(random_state=42)
    df = predictor.load_data(filepath)
    df = predictor.engineer_features(df)
    X, y = predictor.preprocess_data(df, fit=True)
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    return X_train, X_test, y_train, y_test, predictor


if __name__ == "__main__":
    import os
    os.makedirs('models', exist_ok=True)
    
    print("Loading and preparing data...")
    X_train, X_test, y_train, y_test, predictor = load_and_prepare_data('data/logistics_dataset.csv')
    
    print(f"Train set: {X_train.shape}, Test set: {X_test.shape}")
    
    # Initialize tuner
    tuner = HyperparameterTuner(X_train, y_train, X_test, y_test, random_state=42)
    
    # Run complete tuning (increase n_trials for better results, e.g., 100)
    results = tuner.run_complete_tuning(n_trials=50)
    
    print("\n🎉 Hyperparameter tuning completed!")
