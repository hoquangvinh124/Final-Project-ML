"""
Admin KPI Controller
Handle logistics KPI predictions using pretrained model
"""

import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
import threading
import logging

# Add log_model to path
project_root = Path(__file__).parent.parent
log_model_path = project_root / 'log_model'
sys.path.insert(0, str(log_model_path))

from log_model.src.ml.predict import load_model_artifacts, engineer_features, preprocess_new_data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Validation constants
MAX_STOCK_LEVEL = 10000
MAX_DAILY_DEMAND = 10000
KPI_EXCELLENT_THRESHOLD = 0.7
KPI_GOOD_THRESHOLD = 0.5


class AdminKPIController:
    """Controller for KPI prediction operations"""
    
    # Singleton pattern for model loading (thread-safe)
    _model = None
    _scaler = None
    _encoders = None
    _model_loaded = False
    _lock = threading.Lock()  # Thread safety for model loading
    
    def __init__(self):
        """Initialize controller"""
        self.model_dir = log_model_path / 'models'
        
    def load_model(self):
        """Load model artifacts (only once, thread-safe)"""
        with AdminKPIController._lock:
            if not AdminKPIController._model_loaded:
                try:
                    logger.info("Loading model artifacts...")
                    AdminKPIController._model, AdminKPIController._scaler, AdminKPIController._encoders = \
                        load_model_artifacts(str(self.model_dir))
                    AdminKPIController._model_loaded = True
                    logger.info("Model loaded successfully")
                    return True, "Model loaded successfully"
                except Exception as e:
                    logger.error(f"Error loading model: {e}")
                    return False, f"Error loading model: {str(e)}"
            return True, "Model already loaded"
    
    def validate_single_input(self, data):
       
        required_fields = [
            'item_id', 'category', 'stock_level', 'reorder_point',
            'reorder_frequency_days', 'lead_time_days', 'daily_demand',
            'demand_std_dev', 'item_popularity_score', 'zone',
            'picking_time_seconds', 'handling_cost_per_unit', 'unit_price',
            'holding_cost_per_unit_day', 'stockout_count_last_month',
            'order_fulfillment_rate', 'total_orders_last_month', 'turnover_ratio',
            'layout_efficiency_score', 'forecasted_demand_next_7d', 'last_restock_date'
        ]
        
        # Check required fields
        missing_fields = [field for field in required_fields if field not in data or data[field] == '']
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"
        
        # Validate numeric ranges using constants
        try:
            stock_level = float(data['stock_level'])
            if stock_level < 0:
                return False, "Stock level must be >= 0"
            if stock_level > MAX_STOCK_LEVEL:
                return False, f"Stock level exceeds maximum ({MAX_STOCK_LEVEL})"
            
            if float(data['reorder_point']) < 0:
                return False, "Reorder point must be >= 0"
            
            daily_demand = float(data['daily_demand'])
            if daily_demand < 0:
                return False, "Daily demand must be >= 0"
            if daily_demand > MAX_DAILY_DEMAND:
                return False, f"Daily demand exceeds maximum ({MAX_DAILY_DEMAND})"
            
            fulfillment_rate = float(data['order_fulfillment_rate'])
            if not 0 <= fulfillment_rate <= 1:
                return False, "Order fulfillment rate must be between 0 and 1"
            if not 0 <= float(data['item_popularity_score']) <= 1:
                return False, "Item popularity score must be between 0 and 1"
            if not 0 <= float(data['layout_efficiency_score']) <= 1:
                return False, "Layout efficiency score must be between 0 and 1"
        except ValueError as e:
            return False, f"Invalid numeric value: {str(e)}"
        
        # Validate category
        valid_categories = ['Electronics', 'Groceries', 'Apparel', 'Automotive', 'Pharma']
        if data['category'] not in valid_categories:
            return False, f"Category must be one of: {', '.join(valid_categories)}"
        
        # Validate zone
        valid_zones = ['A', 'B', 'C', 'D']
        if data['zone'] not in valid_zones:
            return False, f"Zone must be one of: {', '.join(valid_zones)}"
        
        # Validate date format
        try:
            datetime.strptime(data['last_restock_date'], '%Y-%m-%d')
        except ValueError:
            return False, "Last restock date must be in format YYYY-MM-DD"
        
        return True, ""
    
    def predict_single_item(self, item_data):
        # Load model if needed
        success, message = self.load_model()
        if not success:
            return {'success': False, 'error': message}
        
        # Validate input
        is_valid, error_msg = self.validate_single_input(item_data)
        if not is_valid:
            return {'success': False, 'error': error_msg}
        
        try:
            # Convert to DataFrame
            df = pd.DataFrame([item_data])
            # Add storage_location_id (required by model but not used in prediction)
            df['storage_location_id'] = 'L00'
            # Engineer features
            df = engineer_features(df)
            # Preprocess
            X = preprocess_new_data(df, AdminKPIController._scaler, AdminKPIController._encoders)
            # Predict
            kpi_score = AdminKPIController._model.predict(X)[0]
            # Interpret result
            interpretation = self.interpret_kpi_score(kpi_score)
            
            return {
                'success': True,
                'kpi_score': float(kpi_score),
                'interpretation': interpretation,
                'error': ''
            }
        
        except Exception as e:
            return {'success': False, 'error': f"Prediction error: {str(e)}"}
    
    def predict_batch(self, csv_file_path):
        """
        Predict KPI for multiple items from CSV
        
        Parameters:
        -----------
        csv_file_path : str
            Path to CSV file with item data
            
        Returns:
        --------
        dict : {'success': bool, 'results': pd.DataFrame, 'stats': dict, 'error': str}
        """
        # Load model if needed
        success, message = self.load_model()
        if not success:
            return {'success': False, 'error': message}
        
        try:
            # Load CSV with automatic encoding detection
            # Try multiple encodings to handle different CSV formats
            encodings_to_try = ['utf-8', 'utf-8-sig', 'latin1', 'iso-8859-1', 'cp1252', 'windows-1252', 'gbk', 'big5']
            df = None
            last_error = None
            successful_encoding = None
            
            for encoding in encodings_to_try:
                try:
                    df = pd.read_csv(csv_file_path, encoding=encoding, on_bad_lines='skip')
                    successful_encoding = encoding
                    logger.info(f"Successfully loaded CSV with encoding: {encoding}")
                    break
                except (UnicodeDecodeError, LookupError) as e:
                    last_error = e
                    logger.debug(f"Failed to load with {encoding}: {str(e)}")
                    continue
                except Exception as e:
                    # If it's not an encoding error, this might be the real issue
                    if "codec" not in str(e).lower() and "decode" not in str(e).lower():
                        return {'success': False, 'error': f"CSV error: {str(e)}"}
                    last_error = e
                    continue
            
            if df is None or df.empty:
                error_msg = f"Khong the doc file CSV. Da thu cac encoding: {', '.join(encodings_to_try)}."
                if last_error:
                    error_msg += f" Loi: {str(last_error)}"
                return {'success': False, 'error': error_msg}
            
            logger.info(f"CSV loaded successfully with {successful_encoding}, shape: {df.shape}")
            
            # Clean column names - strip whitespace and normalize
            df.columns = df.columns.str.strip()
            
            # Try to fix encoding issues in column names
            fixed_columns = []
            for col in df.columns:
                try:
                    # If column name contains non-ASCII characters that look wrong, try to fix
                    if any(ord(c) > 127 for c in str(col)):
                        # Try to encode back and decode with different encoding
                        for source_enc in ['latin1', 'cp1252', 'iso-8859-1']:
                            try:
                                fixed_col = col.encode(source_enc).decode('utf-8')
                                if fixed_col.isprintable() or fixed_col.isascii():
                                    logger.info(f"Fixed column name: '{col}' -> '{fixed_col}'")
                                    fixed_columns.append(fixed_col)
                                    break
                            except:
                                continue
                        else:
                            fixed_columns.append(col)
                    else:
                        fixed_columns.append(col)
                except:
                    fixed_columns.append(col)
            
            df.columns = fixed_columns
            logger.info(f"Column names after cleanup: {list(df.columns)}")
            
            # Validate required columns
            required_cols = [
                'item_id', 'category', 'stock_level', 'reorder_point',
                'reorder_frequency_days', 'lead_time_days', 'daily_demand',
                'demand_std_dev', 'item_popularity_score', 'zone',
                'picking_time_seconds', 'handling_cost_per_unit', 'unit_price',
                'holding_cost_per_unit_day', 'stockout_count_last_month',
                'order_fulfillment_rate', 'total_orders_last_month', 'turnover_ratio',
                'layout_efficiency_score', 'forecasted_demand_next_7d', 'last_restock_date'
            ]
            
            # Create case-insensitive column mapping
            df_cols_lower = {col.lower(): col for col in df.columns}
            missing_cols = []
            col_mapping = {}
            
            for req_col in required_cols:
                if req_col in df.columns:
                    col_mapping[req_col] = req_col
                elif req_col.lower() in df_cols_lower:
                    # Found with different case
                    col_mapping[req_col] = df_cols_lower[req_col.lower()]
                    logger.info(f"Column '{req_col}' found as '{df_cols_lower[req_col.lower()]}'")
                else:
                    missing_cols.append(req_col)
            
            if missing_cols:
                error_msg = f"Thieu cac cot: {', '.join(missing_cols)}\n\n"
                error_msg += f"Cac cot hien co trong file: {', '.join(list(df.columns)[:15])}"
                if len(df.columns) > 15:
                    error_msg += "..."
                return {'success': False, 'error': error_msg}
            
            # Rename columns to match required names (case-sensitive)
            if col_mapping:
                rename_dict = {v: k for k, v in col_mapping.items() if v != k}
                if rename_dict:
                    df = df.rename(columns=rename_dict)
                    logger.info(f"Renamed columns: {rename_dict}")
            
            logger.info(f"All required columns found. Processing {len(df)} rows...")
            
            # Validate data types and clean data
            try:
                # Convert numeric columns
                numeric_cols = ['stock_level', 'reorder_point', 'reorder_frequency_days', 
                               'lead_time_days', 'daily_demand', 'demand_std_dev', 
                               'item_popularity_score', 'picking_time_seconds', 
                               'handling_cost_per_unit', 'unit_price', 'holding_cost_per_unit_day',
                               'stockout_count_last_month', 'order_fulfillment_rate', 
                               'total_orders_last_month', 'turnover_ratio', 
                               'layout_efficiency_score', 'forecasted_demand_next_7d']
                
                for col in numeric_cols:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                
                # Remove rows with invalid data
                initial_rows = len(df)
                df = df.dropna(subset=numeric_cols)
                dropped_rows = initial_rows - len(df)
                
                if dropped_rows > 0:
                    logger.warning(f"Dropped {dropped_rows} rows with invalid data")
                
                if len(df) == 0:
                    return {'success': False, 'error': 'Khong co du lieu hop le sau khi lam sach. Vui long kiem tra dinh dang du lieu.'}
                    
            except Exception as e:
                logger.error(f"Data validation error: {e}")
                return {'success': False, 'error': f'Loi khi xu ly du lieu: {str(e)}'}
            
            # Add storage_location_id if not present
            if 'storage_location_id' not in df.columns:
                df['storage_location_id'] = 'L00'
            
            # Store item IDs
            item_ids = df['item_id'].values
            
            # Engineer features
            try:
                logger.info("Engineering features...")
                df = engineer_features(df)
                logger.info(f"Features engineered. New shape: {df.shape}")
            except Exception as e:
                logger.error(f"Feature engineering error: {e}")
                return {'success': False, 'error': f'Loi khi tao features: {str(e)}'}
            
            # Preprocess
            try:
                logger.info("Preprocessing data...")
                X = preprocess_new_data(df, AdminKPIController._scaler, AdminKPIController._encoders)
                logger.info(f"Data preprocessed. Shape: {X.shape}")
            except Exception as e:
                logger.error(f"Preprocessing error: {e}")
                return {'success': False, 'error': f'Loi khi tien xu ly du lieu: {str(e)}'}
            
            # Predict
            try:
                logger.info("Making predictions...")
                predictions = AdminKPIController._model.predict(X)
                logger.info(f"Predictions completed. {len(predictions)} items predicted")
            except Exception as e:
                logger.error(f"Prediction error: {e}")
                return {'success': False, 'error': f'Loi khi du doan: {str(e)}'}
            
            # Create results DataFrame
            results = pd.DataFrame({
                'item_id': item_ids,
                'predicted_kpi_score': predictions,
                'interpretation': [self.interpret_kpi_score(score) for score in predictions]
            })
            
            # Calculate statistics using constants
            stats = {
                'total_items': len(predictions),
                'mean_kpi': float(predictions.mean()),
                'min_kpi': float(predictions.min()),
                'max_kpi': float(predictions.max()),
                'std_kpi': float(predictions.std()),
                'excellent_count': int(sum(predictions >= KPI_EXCELLENT_THRESHOLD)),
                'good_count': int(sum((predictions >= KPI_GOOD_THRESHOLD) & (predictions < KPI_EXCELLENT_THRESHOLD))),
                'needs_improvement_count': int(sum(predictions < KPI_GOOD_THRESHOLD))
            }
            
            return {
                'success': True,
                'results': results,
                'stats': stats,
                'error': ''
            }
            
        except Exception as e:
            return {'success': False, 'error': f"Batch prediction error: {str(e)}"}
    
    def interpret_kpi_score(self, score):
        """
        Interpret KPI score using defined thresholds
        
        Parameters:
        -----------
        score : float
            KPI score (0-1)
            
        Returns:
        --------
        str : Interpretation text
        """
        if score >= KPI_EXCELLENT_THRESHOLD:
            return "✅ Excellent Performance"
        elif score >= KPI_GOOD_THRESHOLD:
            return "⚠️ Good Performance"
        else:
            return "❌ Needs Improvement"
    
    def get_recommendations(self, kpi_score):
        """
        Get actionable recommendations based on KPI score
        
        Parameters:
        -----------
        kpi_score : float
            KPI score (0-1)
            
        Returns:
        --------
        list : List of recommendation strings
        """
        if kpi_score >= KPI_EXCELLENT_THRESHOLD:
            return [
                "✅ Item is performing well",
                "✅ Maintain current inventory levels",
                "✅ Continue monitoring demand patterns",
                "✅ Consider as a model for other items"
            ]
        elif kpi_score >= KPI_GOOD_THRESHOLD:
            return [
                "⚠️ Room for improvement",
                "⚠️ Review demand forecasting accuracy",
                "⚠️ Optimize reorder points and frequency",
                "⚠️ Reduce picking time if possible",
                "⚠️ Analyze cost efficiency"
            ]
        else:  # Below KPI_GOOD_THRESHOLD
            return [
                "❌ Urgent attention required",
                "❌ High risk of stockouts or overstocking",
                "❌ Review and adjust inventory parameters",
                "❌ Investigate root causes (demand variability, lead times)",
                "❌ Check if item is cost-effective",
                "❌ Consider repositioning in warehouse for better efficiency"
            ]
    
    def get_feature_importance_info(self):
        """
        Get information about important features
        
        Returns:
        --------
        list : List of tuples (feature_name, importance_score, description)
        """
        return [
            ("order_fulfillment_rate", 0.856, "Percentage of orders fulfilled successfully"),
            ("efficiency_composite", 0.798, "Combined score of layout and fulfillment efficiency"),
            ("fulfillment_quality", 0.845, "Quality metric considering fulfillment rate and stockouts"),
            ("turnover_ratio", 0.742, "How quickly inventory is sold and replaced"),
            ("inventory_health", 0.723, "Overall inventory condition based on turnover and fulfillment"),
            ("item_popularity_score", 0.681, "How popular/in-demand the item is"),
            ("demand_supply_balance", 0.654, "Balance between stock coverage and fulfillment"),
            ("picking_efficiency", 0.612, "Efficiency of picking items from warehouse"),
            ("popularity_turnover", 0.598, "Combined metric of popularity and turnover"),
            ("forecast_accuracy", 0.534, "Accuracy of demand forecasting")
        ]
