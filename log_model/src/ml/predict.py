"""
Quick Prediction Script for Logistics KPI Model
Load trained model and make predictions on new data
"""

import sys
import io

# Fix encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import joblib
import pandas as pd
import numpy as np
import os
from datetime import datetime


def load_model_artifacts(model_dir='models'):
    """Load the latest saved model artifacts"""
    print("Loading model artifacts...")
    
    # Check if model directory exists
    if not os.path.exists(model_dir):
        raise FileNotFoundError(
            f"Model directory '{model_dir}' not found. "
            "Please create the directory and train the model first."
        )
    
    # Find latest files
    model_files = [f for f in os.listdir(model_dir) if f.startswith('Ridge_Regression')]
    scaler_files = [f for f in os.listdir(model_dir) if f.startswith('scaler')]
    encoder_files = [f for f in os.listdir(model_dir) if f.startswith('encoders')]
    
    if not model_files:
        raise FileNotFoundError(
            "No trained model found in the models directory. "
            "Please run 'python src/ml/train_model.py' to train the model first."
        )
    
    # Get latest files (assuming timestamp in filename)
    latest_model = sorted(model_files)[-1]
    latest_scaler = sorted(scaler_files)[-1]
    latest_encoder = sorted(encoder_files)[-1]
    
    model = joblib.load(os.path.join(model_dir, latest_model))
    scaler = joblib.load(os.path.join(model_dir, latest_scaler))
    encoders = joblib.load(os.path.join(model_dir, latest_encoder))
    
    print(f"✅ Model loaded: {latest_model}")
    print(f"✅ Scaler loaded: {latest_scaler}")
    print(f"✅ Encoders loaded: {latest_encoder}")
    
    return model, scaler, encoders


def engineer_features(df):
    """Apply same feature engineering as training"""
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
    
    return df


def preprocess_new_data(df, scaler, encoders):
    """Preprocess new data for prediction"""
    df = df.copy()
    
    # Drop unnecessary columns
    columns_to_drop = ['item_id', 'last_restock_date', 'storage_location_id']
    df = df.drop(columns=[col for col in columns_to_drop if col in df.columns], errors='ignore')
    
    # Remove target if present
    if 'KPI_score' in df.columns:
        df = df.drop('KPI_score', axis=1)
    
    # Encode categorical variables
    categorical_cols = ['category', 'zone']
    for col in categorical_cols:
        if col in df.columns and col in encoders:
            df[col] = encoders[col].transform(df[col])
    
    # Scale features
    df_scaled = scaler.transform(df)
    df_scaled = pd.DataFrame(df_scaled, columns=df.columns, index=df.index)
    
    return df_scaled


def predict_kpi(input_data, model=None, scaler=None, encoders=None):
    """
    Make KPI predictions on new data
    
    Parameters:
    -----------
    input_data : str or pd.DataFrame
        Either path to CSV file or pandas DataFrame
    model : sklearn model, optional
        Pre-loaded model. If None, will load from disk
    scaler : sklearn scaler, optional
        Pre-loaded scaler. If None, will load from disk
    encoders : dict, optional
        Pre-loaded encoders. If None, will load from disk
    
    Returns:
    --------
    predictions : np.array
        Predicted KPI scores
    """
    
    # Load model artifacts if not provided
    if model is None or scaler is None or encoders is None:
        model, scaler, encoders = load_model_artifacts()
    
    # Load data
    if isinstance(input_data, str):
        print(f"\nLoading data from: {input_data}")
        df = pd.read_csv(input_data)
    else:
        df = input_data.copy()
    
    print(f"Input data shape: {df.shape}")
    
    # Store item_id for later reference if available
    item_ids = df['item_id'].values if 'item_id' in df.columns else None
    
    # Engineer features
    print("Engineering features...")
    df = engineer_features(df)
    
    # Preprocess
    print("Preprocessing data...")
    X = preprocess_new_data(df, scaler, encoders)
    
    # Make predictions
    print("Making predictions...")
    predictions = model.predict(X)
    
    # Create results dataframe
    results = pd.DataFrame({
        'Predicted_KPI_Score': predictions
    })
    
    if item_ids is not None:
        results.insert(0, 'item_id', item_ids)
    
    print(f"\n✅ Predictions completed!")
    print(f"   Total predictions: {len(predictions)}")
    print(f"   Mean KPI: {predictions.mean():.4f}")
    print(f"   Min KPI: {predictions.min():.4f}")
    print(f"   Max KPI: {predictions.max():.4f}")
    print(f"   Std KPI: {predictions.std():.4f}")
    
    return results


def predict_single_item(item_data_dict):
    """
    Make prediction for a single item
    
    Parameters:
    -----------
    item_data_dict : dict
        Dictionary with item features
    
    Returns:
    --------
    float : Predicted KPI score
    """
    df = pd.DataFrame([item_data_dict])
    result = predict_kpi(df)
    return result['Predicted_KPI_Score'].values[0]


def batch_predict_and_save(input_csv, output_csv=None):
    """
    Batch prediction with automatic output saving
    
    Parameters:
    -----------
    input_csv : str
        Path to input CSV file
    output_csv : str, optional
        Path to save predictions. If None, auto-generates filename
    """
    
    # Make predictions
    results = predict_kpi(input_csv)
    
    # Generate output filename if not provided
    if output_csv is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_csv = f'predictions_{timestamp}.csv'
    
    # Save results
    results.to_csv(output_csv, index=False)
    print(f"\n💾 Predictions saved to: {output_csv}")
    
    return results


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

if __name__ == "__main__":
    print("="*80)
    print("LOGISTICS KPI PREDICTION SYSTEM")
    print("="*80)
    
    # Example 1: Batch prediction from CSV
    print("\n📊 EXAMPLE 1: Batch Prediction from CSV")
    print("-" * 80)
    try:
        results = batch_predict_and_save(
            input_csv='data/logistics_dataset.csv',
            output_csv='predictions_output.csv'
        )
        print("\nFirst 10 predictions:")
        print(results.head(10))
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 2: Single item prediction
    print("\n\n📦 EXAMPLE 2: Single Item Prediction")
    print("-" * 80)
    
    sample_item = {
        'item_id': 'TEST_ITEM_001',
        'category': 'Electronics',
        'stock_level': 150,
        'reorder_point': 50,
        'reorder_frequency_days': 7,
        'lead_time_days': 3,
        'daily_demand': 15.5,
        'demand_std_dev': 3.2,
        'item_popularity_score': 0.75,
        'storage_location_id': 'L25',
        'zone': 'A',
        'picking_time_seconds': 45,
        'handling_cost_per_unit': 2.50,
        'unit_price': 99.99,
        'holding_cost_per_unit_day': 0.50,
        'stockout_count_last_month': 1,
        'order_fulfillment_rate': 0.95,
        'total_orders_last_month': 450,
        'turnover_ratio': 8.5,
        'layout_efficiency_score': 0.80,
        'last_restock_date': '2024-11-01',
        'forecasted_demand_next_7d': 110.0
    }
    
    try:
        predicted_kpi = predict_single_item(sample_item)
        print(f"\n📈 Predicted KPI Score: {predicted_kpi:.4f}")
        
        # Interpretation
        if predicted_kpi >= 0.7:
            print("   ✅ EXCELLENT - High performance item")
        elif predicted_kpi >= 0.5:
            print("   ⚠️ GOOD - Moderate performance")
        else:
            print("   ❌ NEEDS IMPROVEMENT - Low performance")
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 3: Load model once, predict multiple times
    print("\n\n⚡ EXAMPLE 3: Efficient Multiple Predictions")
    print("-" * 80)
    
    try:
        # Load model once
        model, scaler, encoders = load_model_artifacts()
        
        # Make multiple predictions efficiently
        df = pd.read_csv('data/logistics_dataset.csv')
        
        # Predict for first 5 items
        subset = df.head(5)
        predictions = predict_kpi(subset, model=model, scaler=scaler, encoders=encoders)
        
        print("\nPredictions for first 5 items:")
        print(predictions)
        
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*80)
    print("PREDICTION EXAMPLES COMPLETED")
    print("="*80)
