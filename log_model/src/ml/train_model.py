"""
Logistics KPI Prediction Model Training Pipeline
Goal: Achieve R² > 85% for KPI score prediction
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import xgboost as xgb
import lightgbm as lgb
from catboost import CatBoostRegressor
import warnings
import joblib
from datetime import datetime
import os

warnings.filterwarnings('ignore')

class LogisticsKPIPredictor:
    """Complete ML pipeline for logistics KPI prediction"""
    
    def __init__(self, random_state=42):
        self.random_state = random_state
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.best_model = None
        self.feature_names = None
        self.results = {}
        
    def load_data(self, filepath):
        """Load and prepare dataset"""
        print("Loading dataset...")
        df = pd.read_csv(filepath)
        print(f"Dataset loaded: {df.shape}")
        return df
    
    def engineer_features(self, df):
        """Create advanced domain-specific features"""
        print("\nEngineering features...")
        df = df.copy()
        
        # Convert date to datetime
        df['last_restock_date'] = pd.to_datetime(df['last_restock_date'])
        reference_date = df['last_restock_date'].max()
        
        # Date features
        df['days_since_restock'] = (reference_date - df['last_restock_date']).dt.days
        df['restock_month'] = df['last_restock_date'].dt.month
        df['restock_day_of_week'] = df['last_restock_date'].dt.dayofweek
        df['restock_quarter'] = df['last_restock_date'].dt.quarter
        
        # Demand features
        df['demand_variability'] = df['demand_std_dev'] / (df['daily_demand'] + 1e-5)
        df['stock_coverage_days'] = df['stock_level'] / (df['daily_demand'] + 1e-5)
        df['forecast_accuracy'] = df['forecasted_demand_next_7d'] / (df['daily_demand'] * 7 + 1e-5)
        df['demand_stability'] = 1 / (df['demand_variability'] + 1e-5)
        
        # Inventory features
        df['reorder_urgency'] = (df['stock_level'] - df['reorder_point']) / (df['daily_demand'] + 1e-5)
        df['stock_buffer'] = df['stock_level'] - df['reorder_point']
        df['reorder_frequency_ratio'] = df['reorder_frequency_days'] / (df['lead_time_days'] + 1e-5)
        df['stock_to_reorder_ratio'] = df['stock_level'] / (df['reorder_point'] + 1e-5)
        
        # Operational efficiency features
        df['cost_efficiency'] = df['handling_cost_per_unit'] / (df['unit_price'] + 1e-5)
        df['profit_margin'] = (df['unit_price'] - df['handling_cost_per_unit']) / (df['unit_price'] + 1e-5)
        df['picking_efficiency'] = df['layout_efficiency_score'] / (df['picking_time_seconds'] + 1e-5)
        df['holding_cost_ratio'] = df['holding_cost_per_unit_day'] / (df['unit_price'] + 1e-5)
        
        # Order performance features
        df['fulfillment_quality'] = df['order_fulfillment_rate'] * (1 - df['stockout_count_last_month'] / 10)
        df['order_volume_per_demand'] = df['total_orders_last_month'] / (df['daily_demand'] * 30 + 1e-5)
        df['stockout_risk'] = df['stockout_count_last_month'] / (df['total_orders_last_month'] + 1e-5)
        
        # Popularity and turnover features
        df['popularity_turnover'] = df['item_popularity_score'] * df['turnover_ratio']
        df['demand_popularity_ratio'] = df['daily_demand'] / (df['item_popularity_score'] + 1e-5)
        
        # Complex interaction features
        df['efficiency_composite'] = (df['layout_efficiency_score'] + df['order_fulfillment_rate']) / 2
        df['inventory_health'] = (df['turnover_ratio'] / 15) * df['order_fulfillment_rate'] * (1 - df['stockout_risk'])
        df['demand_supply_balance'] = df['stock_coverage_days'] * df['order_fulfillment_rate']
        
        print(f"Features engineered. New shape: {df.shape}")
        return df
    
    def preprocess_data(self, df, fit=True):
        """Preprocess data with encoding and scaling"""
        print("\nPreprocessing data...")
        df = df.copy()
        
        # Drop unnecessary columns
        columns_to_drop = ['item_id', 'last_restock_date', 'storage_location_id']
        df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])
        
        # Separate features and target
        if 'KPI_score' in df.columns:
            X = df.drop('KPI_score', axis=1)
            y = df['KPI_score']
        else:
            X = df
            y = None
        
        # Encode categorical variables
        categorical_cols = ['category', 'zone']
        for col in categorical_cols:
            if col in X.columns:
                if fit:
                    self.label_encoders[col] = LabelEncoder()
                    X[col] = self.label_encoders[col].fit_transform(X[col])
                else:
                    X[col] = self.label_encoders[col].transform(X[col])
        
        # Store feature names
        if fit:
            self.feature_names = X.columns.tolist()
        
        # Scale numerical features
        if fit:
            X_scaled = self.scaler.fit_transform(X)
        else:
            X_scaled = self.scaler.transform(X)
        
        X_scaled = pd.DataFrame(X_scaled, columns=X.columns, index=X.index)
        
        print(f"Preprocessing complete. Features: {X_scaled.shape[1]}")
        return X_scaled, y
    
    def handle_outliers(self, X, y, method='iqr', threshold=3):
        """Remove or cap outliers"""
        print("\nHandling outliers...")
        initial_size = len(X)
        
        # IQR method for outlier detection
        Q1 = X.quantile(0.25)
        Q3 = X.quantile(0.75)
        IQR = Q3 - Q1
        
        # Define outlier boundaries
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        # Identify outliers
        outlier_mask = ((X < lower_bound) | (X > upper_bound)).any(axis=1)
        outlier_count = outlier_mask.sum()
        
        # Remove samples with outliers (conservative approach)
        X_clean = X[~outlier_mask]
        y_clean = y[~outlier_mask]
        
        print(f"Outliers detected: {outlier_count} ({outlier_count/initial_size*100:.2f}%)")
        print(f"Samples after cleaning: {len(X_clean)} (removed {initial_size - len(X_clean)})")
        
        return X_clean, y_clean
    
    def train_baseline_models(self, X_train, y_train, X_test, y_test):
        """Train multiple baseline models"""
        print("\n" + "="*80)
        print("TRAINING BASELINE MODELS")
        print("="*80)
        
        models = {
            'Ridge Regression': Ridge(alpha=1.0, random_state=self.random_state),
            'Lasso Regression': Lasso(alpha=0.1, random_state=self.random_state),
            'Random Forest': RandomForestRegressor(
                n_estimators=100, 
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=self.random_state,
                n_jobs=-1
            ),
            'Gradient Boosting': GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=self.random_state
            )
        }
        
        results = {}
        kfold = KFold(n_splits=5, shuffle=True, random_state=self.random_state)
        
        for name, model in models.items():
            print(f"\nTraining {name}...")
            
            # Train model
            model.fit(X_train, y_train)
            
            # Predictions
            y_train_pred = model.predict(X_train)
            y_test_pred = model.predict(X_test)
            
            # Metrics
            train_r2 = r2_score(y_train, y_train_pred)
            test_r2 = r2_score(y_test, y_test_pred)
            test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
            test_mae = mean_absolute_error(y_test, y_test_pred)
            
            # Cross-validation
            cv_scores = cross_val_score(model, X_train, y_train, cv=kfold, 
                                       scoring='r2', n_jobs=-1)
            
            results[name] = {
                'model': model,
                'train_r2': train_r2,
                'test_r2': test_r2,
                'cv_r2_mean': cv_scores.mean(),
                'cv_r2_std': cv_scores.std(),
                'test_rmse': test_rmse,
                'test_mae': test_mae,
                'predictions': y_test_pred
            }
            
            print(f"  Train R²: {train_r2:.4f}")
            print(f"  Test R²: {test_r2:.4f}")
            print(f"  CV R² (mean ± std): {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
            print(f"  Test RMSE: {test_rmse:.4f}")
            print(f"  Test MAE: {test_mae:.4f}")
        
        return results
    
    def train_advanced_models(self, X_train, y_train, X_test, y_test):
        """Train advanced gradient boosting models"""
        print("\n" + "="*80)
        print("TRAINING ADVANCED MODELS")
        print("="*80)
        
        models = {
            'XGBoost': xgb.XGBRegressor(
                n_estimators=500,
                learning_rate=0.05,
                max_depth=7,
                min_child_weight=3,
                subsample=0.8,
                colsample_bytree=0.8,
                gamma=0.1,
                reg_alpha=0.1,
                reg_lambda=1.0,
                random_state=self.random_state,
                n_jobs=-1
            ),
            'LightGBM': lgb.LGBMRegressor(
                n_estimators=500,
                learning_rate=0.05,
                max_depth=7,
                num_leaves=31,
                min_child_samples=20,
                subsample=0.8,
                colsample_bytree=0.8,
                reg_alpha=0.1,
                reg_lambda=1.0,
                random_state=self.random_state,
                n_jobs=-1,
                verbose=-1
            ),
            'CatBoost': CatBoostRegressor(
                iterations=500,
                learning_rate=0.05,
                depth=7,
                l2_leaf_reg=3,
                subsample=0.8,
                random_state=self.random_state,
                verbose=False
            )
        }
        
        results = {}
        kfold = KFold(n_splits=5, shuffle=True, random_state=self.random_state)
        
        for name, model in models.items():
            print(f"\nTraining {name}...")
            
            # Train model
            model.fit(X_train, y_train)
            
            # Predictions
            y_train_pred = model.predict(X_train)
            y_test_pred = model.predict(X_test)
            
            # Metrics
            train_r2 = r2_score(y_train, y_train_pred)
            test_r2 = r2_score(y_test, y_test_pred)
            test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))
            test_mae = mean_absolute_error(y_test, y_test_pred)
            
            # Cross-validation
            cv_scores = cross_val_score(model, X_train, y_train, cv=kfold, 
                                       scoring='r2', n_jobs=-1)
            
            results[name] = {
                'model': model,
                'train_r2': train_r2,
                'test_r2': test_r2,
                'cv_r2_mean': cv_scores.mean(),
                'cv_r2_std': cv_scores.std(),
                'test_rmse': test_rmse,
                'test_mae': test_mae,
                'predictions': y_test_pred
            }
            
            print(f"  Train R²: {train_r2:.4f}")
            print(f"  Test R²: {test_r2:.4f}")
            print(f"  CV R² (mean ± std): {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
            print(f"  Test RMSE: {test_rmse:.4f}")
            print(f"  Test MAE: {test_mae:.4f}")
            
            # Check if target achieved
            if test_r2 >= 0.85:
                print(f"  ✅ TARGET ACHIEVED! R² = {test_r2:.4f} >= 0.85")
        
        return results
    
    def create_ensemble(self, models_dict, X_test, y_test):
        """Create ensemble prediction from top models"""
        print("\n" + "="*80)
        print("CREATING ENSEMBLE MODEL")
        print("="*80)
        
        # Get predictions from all models
        predictions = []
        weights = []
        
        for name, info in models_dict.items():
            pred = info['predictions']
            weight = info['cv_r2_mean']  # Use CV score as weight
            predictions.append(pred)
            weights.append(weight)
            print(f"{name} - Weight: {weight:.4f}")
        
        # Normalize weights
        weights = np.array(weights)
        weights = weights / weights.sum()
        
        # Weighted ensemble prediction
        ensemble_pred = np.zeros_like(predictions[0])
        for pred, weight in zip(predictions, weights):
            ensemble_pred += pred * weight
        
        # Evaluate ensemble
        ensemble_r2 = r2_score(y_test, ensemble_pred)
        ensemble_rmse = np.sqrt(mean_squared_error(y_test, ensemble_pred))
        ensemble_mae = mean_absolute_error(y_test, ensemble_pred)
        
        print(f"\n📊 ENSEMBLE RESULTS:")
        print(f"  Test R²: {ensemble_r2:.4f}")
        print(f"  Test RMSE: {ensemble_rmse:.4f}")
        print(f"  Test MAE: {ensemble_mae:.4f}")
        
        if ensemble_r2 >= 0.85:
            print(f"  ✅ ENSEMBLE TARGET ACHIEVED! R² = {ensemble_r2:.4f} >= 0.85")
        
        return {
            'predictions': ensemble_pred,
            'test_r2': ensemble_r2,
            'test_rmse': ensemble_rmse,
            'test_mae': ensemble_mae,
            'weights': weights
        }
    
    def plot_results(self, y_test, predictions, model_name, r2_score_val):
        """Plot prediction results"""
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        
        # Actual vs Predicted
        axes[0].scatter(y_test, predictions, alpha=0.5, s=20)
        axes[0].plot([y_test.min(), y_test.max()], 
                    [y_test.min(), y_test.max()], 
                    'r--', lw=2, label='Perfect Prediction')
        axes[0].set_xlabel('Actual KPI Score')
        axes[0].set_ylabel('Predicted KPI Score')
        axes[0].set_title(f'{model_name}\nR² = {r2_score_val:.4f}')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Residuals
        residuals = y_test - predictions
        axes[1].scatter(predictions, residuals, alpha=0.5, s=20)
        axes[1].axhline(y=0, color='r', linestyle='--', lw=2)
        axes[1].set_xlabel('Predicted KPI Score')
        axes[1].set_ylabel('Residuals')
        axes[1].set_title('Residual Plot')
        axes[1].grid(True, alpha=0.3)
        
        # Residuals distribution
        axes[2].hist(residuals, bins=50, edgecolor='black', alpha=0.7)
        axes[2].axvline(x=0, color='r', linestyle='--', lw=2)
        axes[2].set_xlabel('Residuals')
        axes[2].set_ylabel('Frequency')
        axes[2].set_title(f'Residual Distribution\nMean: {residuals.mean():.4f}, Std: {residuals.std():.4f}')
        axes[2].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'results_{model_name.replace(" ", "_")}.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_feature_importance(self, model, model_name, top_n=20):
        """Plot feature importance"""
        if hasattr(model, 'feature_importances_'):
            importance = model.feature_importances_
            feature_importance_df = pd.DataFrame({
                'feature': self.feature_names,
                'importance': importance
            }).sort_values('importance', ascending=False).head(top_n)
            
            plt.figure(figsize=(10, 8))
            plt.barh(range(len(feature_importance_df)), feature_importance_df['importance'])
            plt.yticks(range(len(feature_importance_df)), feature_importance_df['feature'])
            plt.xlabel('Importance')
            plt.title(f'Top {top_n} Feature Importance - {model_name}')
            plt.gca().invert_yaxis()
            plt.tight_layout()
            plt.savefig(f'feature_importance_{model_name.replace(" ", "_")}.png', 
                       dpi=300, bbox_inches='tight')
            plt.show()
            
            return feature_importance_df
    
    def save_model(self, model, model_name):
        """Save trained model and preprocessing objects"""
        os.makedirs('models', exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        model_path = f'models/{model_name.replace(" ", "_")}_{timestamp}.pkl'
        scaler_path = f'models/scaler_{timestamp}.pkl'
        encoders_path = f'models/encoders_{timestamp}.pkl'
        
        joblib.dump(model, model_path)
        joblib.dump(self.scaler, scaler_path)
        joblib.dump(self.label_encoders, encoders_path)
        
        print(f"\n✅ Model saved: {model_path}")
        print(f"✅ Scaler saved: {scaler_path}")
        print(f"✅ Encoders saved: {encoders_path}")
        
        return model_path
    
    def run_pipeline(self, filepath):
        """Execute complete training pipeline"""
        print("="*80)
        print("LOGISTICS KPI PREDICTION - COMPLETE PIPELINE")
        print("TARGET: R² > 85%")
        print("="*80)
        
        # Load data
        df = self.load_data(filepath)
        
        # Feature engineering
        df = self.engineer_features(df)
        
        # Preprocessing
        X, y = self.preprocess_data(df, fit=True)
        
        # Handle outliers (optional - can be toggled)
        # X, y = self.handle_outliers(X, y)
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=self.random_state
        )
        print(f"\nTrain set: {X_train.shape}, Test set: {X_test.shape}")
        
        # Train baseline models
        baseline_results = self.train_baseline_models(X_train, y_train, X_test, y_test)
        
        # Train advanced models
        advanced_results = self.train_advanced_models(X_train, y_train, X_test, y_test)
        
        # Combine all results
        all_results = {**baseline_results, **advanced_results}
        
        # Create ensemble
        top_models = {k: v for k, v in advanced_results.items()}
        ensemble_results = self.create_ensemble(top_models, X_test, y_test)
        
        # Find best model
        best_model_name = max(all_results, key=lambda k: all_results[k]['test_r2'])
        best_model_info = all_results[best_model_name]
        self.best_model = best_model_info['model']
        
        print("\n" + "="*80)
        print("FINAL RESULTS SUMMARY")
        print("="*80)
        
        # Print all model results
        results_df = pd.DataFrame({
            name: {
                'Train R²': info['train_r2'],
                'Test R²': info['test_r2'],
                'CV R² Mean': info['cv_r2_mean'],
                'CV R² Std': info['cv_r2_std'],
                'Test RMSE': info['test_rmse'],
                'Test MAE': info['test_mae']
            }
            for name, info in all_results.items()
        }).T
        
        print("\n📊 All Models Performance:")
        print(results_df.to_string())
        
        print(f"\n🏆 BEST MODEL: {best_model_name}")
        print(f"   Test R²: {best_model_info['test_r2']:.4f}")
        print(f"   CV R²: {best_model_info['cv_r2_mean']:.4f} ± {best_model_info['cv_r2_std']:.4f}")
        
        print(f"\n🎯 ENSEMBLE MODEL:")
        print(f"   Test R²: {ensemble_results['test_r2']:.4f}")
        
        # Check if target achieved
        if best_model_info['test_r2'] >= 0.85:
            print(f"\n✅ SUCCESS! Target R² > 85% ACHIEVED with {best_model_name}")
        elif ensemble_results['test_r2'] >= 0.85:
            print(f"\n✅ SUCCESS! Target R² > 85% ACHIEVED with ENSEMBLE")
        else:
            print(f"\n⚠️ Target not achieved. Best R²: {max(best_model_info['test_r2'], ensemble_results['test_r2']):.4f}")
            print("   Consider: More feature engineering, hyperparameter tuning, or data collection")
        
        # Visualizations
        print("\nGenerating visualizations...")
        self.plot_results(y_test, best_model_info['predictions'], 
                         best_model_name, best_model_info['test_r2'])
        feature_imp = self.plot_feature_importance(self.best_model, best_model_name)
        
        # Save best model
        model_path = self.save_model(self.best_model, best_model_name)
        
        # Save results
        results_df.to_csv('model_comparison_results.csv')
        print("\n✅ Results saved: model_comparison_results.csv")
        
        if feature_imp is not None:
            feature_imp.to_csv('feature_importance.csv', index=False)
            print("✅ Feature importance saved: feature_importance.csv")
        
        print("\n" + "="*80)
        print("PIPELINE COMPLETED SUCCESSFULLY!")
        print("="*80)
        
        return {
            'best_model': self.best_model,
            'best_model_name': best_model_name,
            'results': all_results,
            'ensemble_results': ensemble_results,
            'model_path': model_path,
            'feature_importance': feature_imp
        }


if __name__ == "__main__":
    # Initialize predictor
    predictor = LogisticsKPIPredictor(random_state=42)
    
    # Run complete pipeline
    results = predictor.run_pipeline('data/logistics_dataset.csv')
    
    print("\n🎉 Training completed! Check the generated files for detailed results.")
