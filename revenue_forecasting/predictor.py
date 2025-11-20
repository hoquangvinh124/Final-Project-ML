"""
Revenue Prediction Module
Direct model loading and prediction without API
"""
import pickle
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import os


class RevenuePredictor:
    """Revenue predictor for stores"""

    def __init__(self):
        """Initialize predictor"""
        base_dir = Path(__file__).parent
        self.models_dir = base_dir / 'ml-models' / 'store_models'
        self.metadata_file = self.models_dir / 'stores_metadata.csv'
        self.overall_model_path = base_dir / 'ml-models' / 'revenue_prediction.pkl'

        # Check if paths exist
        if not self.models_dir.exists():
            # Try models/ folder as fallback
            self.models_dir = base_dir / 'models' / 'store_models'
            self.overall_model_path = base_dir / 'models' / 'revenue_prediction.pkl'
            self.metadata_file = self.models_dir / 'stores_metadata.csv'

        # Load metadata if available
        self.metadata = None
        if self.metadata_file.exists():
            try:
                self.metadata = pd.read_csv(self.metadata_file)
            except Exception as e:
                print(f"Warning: Could not load metadata: {e}")
                self.metadata = None

        self.loaded_models = {}
        self.overall_model = None

        # Get available stores from model files
        self.available_stores = self._get_available_stores()

    def _get_available_stores(self):
        """Get list of available store numbers from model files"""
        stores = []
        if self.models_dir.exists():
            for model_file in self.models_dir.glob('store_*_model.pkl'):
                try:
                    # Extract store number from filename like "store_44_model.pkl"
                    store_nbr = int(model_file.stem.split('_')[1])
                    stores.append(store_nbr)
                except (ValueError, IndexError):
                    continue
        return sorted(stores) 

    def load_overall_model(self):
        """Load overall system model"""
        if self.overall_model is None:
            with open(self.overall_model_path, 'rb') as f:
                self.overall_model = pickle.load(f)
        return self.overall_model

    def load_store_model(self, store_nbr):
        """Load model for specific store"""
        if store_nbr in self.loaded_models:
            return self.loaded_models[store_nbr]

        # Check if store exists
        if store_nbr not in self.available_stores:
            raise ValueError(f"Store {store_nbr} not found")

        # Construct model path directly from store number
        model_file = self.models_dir / f'store_{store_nbr}_model.pkl'

        if not model_file.exists():
            raise FileNotFoundError(f"Model file not found: {model_file}")

        with open(model_file, 'rb') as f:
            model = pickle.load(f)

        self.loaded_models[store_nbr] = model
        return model

    def get_all_stores(self):
        """Get all stores info"""
        stores = []
        # Check if metadata is valid (has required columns)
        has_valid_metadata = (self.metadata is not None and
                             'store_nbr' in self.metadata.columns)

        if has_valid_metadata:
            for _, row in self.metadata.iterrows():
                stores.append({
                    'store_nbr': int(row['store_nbr']),
                    'city': row.get('city', 'Unknown'),
                    'type': row.get('type', 'A'),
                    'state': row.get('state', 'Unknown'),
                    'cluster': int(row.get('cluster', 0)),
                    'historical_avg_daily': float(row.get('historical_avg_daily', 0)),
                    'forecast_avg_daily': float(row.get('forecast_avg_daily', 0)),
                    'growth_percent': float(row.get('growth_percent', 0))
                })
        else:
            # Generate basic store info from available stores
            for store_nbr in self.available_stores:
                stores.append({
                    'store_nbr': store_nbr,
                    'city': f'Store {store_nbr}',
                    'type': 'A',
                    'state': 'Unknown',
                    'cluster': 0,
                    'historical_avg_daily': 0.0,
                    'forecast_avg_daily': 0.0,
                    'growth_percent': 0.0
                })
        return stores

    def get_store_info(self, store_nbr):
        """Get specific store info"""
        if store_nbr not in self.available_stores:
            raise ValueError(f"Store {store_nbr} not found")

        # Check if metadata is valid (has required columns)
        has_valid_metadata = (self.metadata is not None and
                             'store_nbr' in self.metadata.columns)

        if has_valid_metadata:
            store_data = self.metadata[self.metadata['store_nbr'] == store_nbr]
            if len(store_data) > 0:
                row = store_data.iloc[0]
                return {
                    'store_nbr': int(row['store_nbr']),
                    'city': row.get('city', 'Unknown'),
                    'type': row.get('type', 'A'),
                    'state': row.get('state', 'Unknown'),
                    'cluster': int(row.get('cluster', 0)),
                    'historical_avg_daily': float(row.get('historical_avg_daily', 0)),
                    'forecast_avg_daily': float(row.get('forecast_avg_daily', 0)),
                    'growth_percent': float(row.get('growth_percent', 0)),
                    'date_from': row.get('date_from', '2013-01-01'),
                    'date_to': row.get('date_to', '2017-08-15')
                }

        # Return basic info if metadata not available
        return {
            'store_nbr': store_nbr,
            'city': f'Store {store_nbr}',
            'type': 'A',
            'state': 'Unknown',
            'cluster': 0,
            'historical_avg_daily': 0.0,
            'forecast_avg_daily': 0.0,
            'growth_percent': 0.0,
            'date_from': '2013-01-01',
            'date_to': '2017-08-15'
        }

    def predict_overall(self, days):
        """Predict overall system revenue from today"""
        model = self.load_overall_model()

        start_date = datetime.now()
        future_dates = pd.date_range(start=start_date, periods=days, freq='D')
        future_df = pd.DataFrame({'ds': future_dates})

        forecast = model.predict(future_df)

        forecasts = []
        for _, row in forecast.iterrows():
            forecasts.append({
                'date': row['ds'].strftime("%Y-%m-%d"),
                'forecast': abs(float(row['yhat'])),
                'lower_bound': abs(float(row['yhat_lower'])),
                'upper_bound': abs(float(row['yhat_upper']))
            })

        summary = {
            'avg_daily_forecast': float(forecast['yhat'].abs().mean()),
            'total_forecast': float(forecast['yhat'].abs().sum()),
            'min_forecast': float(forecast['yhat'].abs().min()),
            'max_forecast': float(forecast['yhat'].abs().max()),
            'std_forecast': float(forecast['yhat'].abs().std())
        }

        return {
            'forecasts': forecasts,
            'summary': summary,
            'forecast_start': forecasts[0]['date'],
            'forecast_end': forecasts[-1]['date'],
            'total_days': len(forecasts)
        }

    def predict_store(self, store_nbr, days):
        """Predict store revenue from today"""
        model = self.load_store_model(store_nbr)
        store_info = self.get_store_info(store_nbr)

        # Create future dates starting from today
        start_date = datetime.now()
        future_dates = pd.date_range(start=start_date, periods=days, freq='D')
        future_df = pd.DataFrame({'ds': future_dates})

        forecast = model.predict(future_df)

        forecasts = []
        for _, row in forecast.iterrows():
            forecasts.append({
                'date': row['ds'].strftime("%Y-%m-%d"),
                'forecast': abs(float(row['yhat'])),
                'lower_bound': abs(float(row['yhat_lower'])),
                'upper_bound': abs(float(row['yhat_upper']))
            })

        avg_forecast = float(forecast['yhat'].abs().mean())
        total_forecast = float(forecast['yhat'].abs().sum())
        historical_avg = store_info['historical_avg_daily']
        growth = ((avg_forecast - historical_avg) / historical_avg * 100) if historical_avg > 0 else 0

        return {
            'store_nbr': store_nbr,
            'city': store_info['city'],
            'type': store_info['type'],
            'forecasts': forecasts,
            'forecast_avg_daily': avg_forecast,
            'total_forecast': total_forecast,
            'historical_avg_daily': historical_avg,
            'growth_percent': float(growth),
            'forecast_start': forecasts[0]['date'] if forecasts else None,
            'forecast_end': forecasts[-1]['date'] if forecasts else None
        }

    def get_top_stores(self, n=10):
        """Get top N stores by forecast revenue"""
        result = []
        # Check if metadata is valid (has required columns)
        has_valid_metadata = (self.metadata is not None and
                             'store_nbr' in self.metadata.columns and
                             'forecast_avg_daily' in self.metadata.columns)

        if has_valid_metadata:
            stores = self.metadata.sort_values('forecast_avg_daily', ascending=False).head(n)
            for _, row in stores.iterrows():
                result.append({
                    'store_nbr': int(row['store_nbr']),
                    'city': row.get('city', 'Unknown'),
                    'type': row.get('type', 'A'),
                    'forecast_avg_daily': float(row.get('forecast_avg_daily', 0)),
                    'historical_avg_daily': float(row.get('historical_avg_daily', 0)),
                    'growth_percent': float(row.get('growth_percent', 0))
                })
        else:
            # Return first N stores if no metadata
            for store_nbr in self.available_stores[:n]:
                result.append({
                    'store_nbr': store_nbr,
                    'city': f'Store {store_nbr}',
                    'type': 'A',
                    'forecast_avg_daily': 0.0,
                    'historical_avg_daily': 0.0,
                    'growth_percent': 0.0
                })
        return {'stores': result}

    def get_bottom_stores(self, n=10):
        """Get bottom N stores by forecast revenue"""
        result = []
        # Check if metadata is valid (has required columns)
        has_valid_metadata = (self.metadata is not None and
                             'store_nbr' in self.metadata.columns and
                             'forecast_avg_daily' in self.metadata.columns)

        if has_valid_metadata:
            stores = self.metadata.sort_values('forecast_avg_daily', ascending=True).head(n)
            for _, row in stores.iterrows():
                result.append({
                    'store_nbr': int(row['store_nbr']),
                    'city': row.get('city', 'Unknown'),
                    'type': row.get('type', 'A'),
                    'forecast_avg_daily': float(row.get('forecast_avg_daily', 0)),
                    'historical_avg_daily': float(row.get('historical_avg_daily', 0)),
                    'growth_percent': float(row.get('growth_percent', 0))
                })
        else:
            # Return last N stores if no metadata
            for store_nbr in self.available_stores[-n:]:
                result.append({
                    'store_nbr': store_nbr,
                    'city': f'Store {store_nbr}',
                    'type': 'A',
                    'forecast_avg_daily': 0.0,
                    'historical_avg_daily': 0.0,
                    'growth_percent': 0.0
                })
        return {'stores': result}


# Global instance
_predictor = None

def get_predictor():
    """Get or create predictor instance"""
    global _predictor
    if _predictor is None:
        _predictor = RevenuePredictor()
    return _predictor
