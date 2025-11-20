"""
Monitoring and Logging System for Logistics KPI Prediction Model
Author: Data Science Team
Date: November 18, 2025

Features:
- Prediction logging
- Performance tracking
- Data drift detection
- Model health monitoring
- Alert system
"""

import pandas as pd
import numpy as np
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import joblib
from scipy import stats
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring_logs.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PredictionLogger:
    """Log all predictions for audit and analysis"""
    
    def __init__(self, log_file: str = 'predictions_history.csv'):
        self.log_file = Path(log_file)
        self._initialize_log_file()
    
    def _initialize_log_file(self):
        """Create log file with headers if not exists"""
        if not self.log_file.exists():
            df = pd.DataFrame(columns=[
                'timestamp', 'item_id', 'category', 'stock_level',
                'predicted_kpi', 'confidence', 'response_time_ms',
                'model_version', 'features_used'
            ])
            df.to_csv(self.log_file, index=False)
            logger.info(f"✅ Created prediction log file: {self.log_file}")
    
    def log_prediction(self, 
                      item_data: Dict,
                      prediction: float,
                      confidence: str,
                      response_time: float,
                      model_version: str,
                      features_count: int):
        """Log a single prediction"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'item_id': item_data.get('item_id', 'N/A'),
                'category': item_data.get('category', 'N/A'),
                'stock_level': item_data.get('stock_level', 0),
                'predicted_kpi': round(prediction, 4),
                'confidence': confidence,
                'response_time_ms': round(response_time * 1000, 2),
                'model_version': model_version,
                'features_used': features_count
            }
            
            df = pd.DataFrame([log_entry])
            df.to_csv(self.log_file, mode='a', header=False, index=False)
            
            logger.info(f"📝 Logged prediction: KPI={prediction:.4f}, Time={response_time*1000:.2f}ms")
            
        except Exception as e:
            logger.error(f"❌ Failed to log prediction: {str(e)}")
    
    def get_recent_predictions(self, hours: int = 24) -> pd.DataFrame:
        """Get predictions from last N hours"""
        try:
            df = pd.read_csv(self.log_file)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_df = df[df['timestamp'] >= cutoff_time]
            
            logger.info(f"📊 Retrieved {len(recent_df)} predictions from last {hours} hours")
            return recent_df
            
        except Exception as e:
            logger.error(f"❌ Failed to retrieve predictions: {str(e)}")
            return pd.DataFrame()
    
    def get_statistics(self, hours: int = 24) -> Dict:
        """Get prediction statistics"""
        df = self.get_recent_predictions(hours)
        
        if df.empty:
            return {}
        
        stats = {
            'total_predictions': len(df),
            'avg_kpi': df['predicted_kpi'].mean(),
            'std_kpi': df['predicted_kpi'].std(),
            'min_kpi': df['predicted_kpi'].min(),
            'max_kpi': df['predicted_kpi'].max(),
            'avg_response_time_ms': df['response_time_ms'].mean(),
            'max_response_time_ms': df['response_time_ms'].max(),
            'predictions_per_category': df['category'].value_counts().to_dict(),
            'time_period': f"Last {hours} hours"
        }
        
        logger.info(f"📈 Statistics: {stats['total_predictions']} predictions, avg KPI={stats['avg_kpi']:.4f}")
        return stats


class PerformanceMonitor:
    """Monitor model performance metrics"""
    
    def __init__(self, metrics_file: str = 'performance_metrics.json'):
        self.metrics_file = Path(metrics_file)
        self.thresholds = {
            'r2_score': 0.95,  # Alert if below
            'rmse': 0.01,      # Alert if above
            'mae': 0.01,       # Alert if above
            'response_time': 1.0  # Alert if above (seconds)
        }
        self._initialize_metrics_file()
    
    def _initialize_metrics_file(self):
        """Create metrics file if not exists"""
        if not self.metrics_file.exists():
            initial_metrics = {
                'created_at': datetime.now().isoformat(),
                'evaluations': []
            }
            with open(self.metrics_file, 'w') as f:
                json.dump(initial_metrics, f, indent=2)
            logger.info(f"✅ Created metrics file: {self.metrics_file}")
    
    def evaluate_model(self, 
                      y_true: np.ndarray, 
                      y_pred: np.ndarray,
                      dataset_name: str = "validation") -> Dict:
        """Evaluate model performance"""
        try:
            r2 = r2_score(y_true, y_pred)
            rmse = np.sqrt(mean_squared_error(y_true, y_pred))
            mae = mean_absolute_error(y_true, y_pred)
            
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'dataset': dataset_name,
                'r2_score': round(r2, 6),
                'rmse': round(rmse, 6),
                'mae': round(mae, 6),
                'samples': len(y_true)
            }
            
            # Check thresholds and generate alerts
            alerts = []
            if r2 < self.thresholds['r2_score']:
                alerts.append(f"⚠️ R² dropped to {r2:.4f} (threshold: {self.thresholds['r2_score']})")
            if rmse > self.thresholds['rmse']:
                alerts.append(f"⚠️ RMSE increased to {rmse:.6f} (threshold: {self.thresholds['rmse']})")
            if mae > self.thresholds['mae']:
                alerts.append(f"⚠️ MAE increased to {mae:.6f} (threshold: {self.thresholds['mae']})")
            
            metrics['alerts'] = alerts
            
            # Save metrics
            self._save_evaluation(metrics)
            
            # Log results
            if alerts:
                logger.warning(f"⚠️ Performance alerts detected: {len(alerts)} issues")
                for alert in alerts:
                    logger.warning(alert)
            else:
                logger.info(f"✅ Model performance: R²={r2:.6f}, RMSE={rmse:.6f}, MAE={mae:.6f}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Failed to evaluate model: {str(e)}")
            return {}
    
    def _save_evaluation(self, metrics: Dict):
        """Save evaluation metrics"""
        try:
            with open(self.metrics_file, 'r') as f:
                data = json.load(f)
            
            data['evaluations'].append(metrics)
            
            # Keep only last 100 evaluations
            if len(data['evaluations']) > 100:
                data['evaluations'] = data['evaluations'][-100:]
            
            with open(self.metrics_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"❌ Failed to save evaluation: {str(e)}")
    
    def get_performance_history(self, last_n: int = 10) -> List[Dict]:
        """Get last N performance evaluations"""
        try:
            with open(self.metrics_file, 'r') as f:
                data = json.load(f)
            
            evaluations = data.get('evaluations', [])[-last_n:]
            logger.info(f"📊 Retrieved {len(evaluations)} performance evaluations")
            return evaluations
            
        except Exception as e:
            logger.error(f"❌ Failed to retrieve performance history: {str(e)}")
            return []


class DataDriftDetector:
    """Detect data drift in production data"""
    
    def __init__(self, reference_data: Optional[pd.DataFrame] = None):
        self.reference_data = reference_data
        self.drift_threshold = 0.05  # p-value threshold for KS test
    
    def set_reference_data(self, data: pd.DataFrame):
        """Set reference (training) data"""
        self.reference_data = data.copy()
        logger.info(f"✅ Reference data set: {len(data)} samples")
    
    def detect_drift(self, production_data: pd.DataFrame) -> Dict:
        """Detect drift between reference and production data"""
        if self.reference_data is None:
            logger.warning("⚠️ No reference data set. Load reference data first.")
            return {}
        
        try:
            drift_results = {
                'timestamp': datetime.now().isoformat(),
                'production_samples': len(production_data),
                'reference_samples': len(self.reference_data),
                'features_analyzed': 0,
                'drifted_features': [],
                'drift_scores': {}
            }
            
            # Get numeric columns present in both datasets
            numeric_cols = self.reference_data.select_dtypes(include=[np.number]).columns
            common_cols = [col for col in numeric_cols if col in production_data.columns]
            
            drift_results['features_analyzed'] = len(common_cols)
            
            # Perform Kolmogorov-Smirnov test for each feature
            for col in common_cols:
                ref_values = self.reference_data[col].dropna()
                prod_values = production_data[col].dropna()
                
                if len(ref_values) == 0 or len(prod_values) == 0:
                    continue
                
                # KS test
                ks_statistic, p_value = stats.ks_2samp(ref_values, prod_values)
                
                drift_results['drift_scores'][col] = {
                    'ks_statistic': round(ks_statistic, 4),
                    'p_value': round(p_value, 4),
                    'drifted': p_value < self.drift_threshold
                }
                
                if p_value < self.drift_threshold:
                    drift_results['drifted_features'].append(col)
                    logger.warning(f"⚠️ Drift detected in '{col}': p-value={p_value:.4f}")
            
            # Summary
            drift_percentage = (len(drift_results['drifted_features']) / 
                              drift_results['features_analyzed'] * 100 
                              if drift_results['features_analyzed'] > 0 else 0)
            
            drift_results['drift_percentage'] = round(drift_percentage, 2)
            
            if drift_percentage > 20:
                logger.warning(f"⚠️ ALERT: {drift_percentage:.1f}% of features show drift!")
                logger.warning("Consider retraining the model with recent data.")
            elif drift_percentage > 0:
                logger.info(f"ℹ️ Minor drift detected: {drift_percentage:.1f}% of features")
            else:
                logger.info("✅ No significant drift detected")
            
            return drift_results
            
        except Exception as e:
            logger.error(f"❌ Failed to detect drift: {str(e)}")
            return {}
    
    def get_feature_statistics(self, data: pd.DataFrame) -> pd.DataFrame:
        """Get statistical summary of features"""
        numeric_data = data.select_dtypes(include=[np.number])
        
        stats_df = pd.DataFrame({
            'mean': numeric_data.mean(),
            'std': numeric_data.std(),
            'min': numeric_data.min(),
            'max': numeric_data.max(),
            'q25': numeric_data.quantile(0.25),
            'median': numeric_data.median(),
            'q75': numeric_data.quantile(0.75)
        })
        
        return stats_df.round(4)


class ModelHealthChecker:
    """Check overall model health and system status"""
    
    def __init__(self, model_path: str = 'models'):
        self.model_path = Path(model_path)
        self.pred_logger = PredictionLogger()
        self.perf_monitor = PerformanceMonitor()
    
    def check_health(self) -> Dict:
        """Comprehensive health check"""
        health_status = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy',
            'checks': {}
        }
        
        # 1. Check model files exist
        model_exists = len(list(self.model_path.glob('*.pkl'))) > 0
        health_status['checks']['model_files'] = {
            'status': 'pass' if model_exists else 'fail',
            'message': 'Model files found' if model_exists else 'Model files missing'
        }
        
        # 2. Check recent predictions
        recent_preds = self.pred_logger.get_recent_predictions(hours=1)
        pred_count = len(recent_preds)
        health_status['checks']['recent_activity'] = {
            'status': 'pass',
            'predictions_last_hour': pred_count,
            'message': f'{pred_count} predictions in last hour'
        }
        
        # 3. Check response times
        if not recent_preds.empty and 'response_time_ms' in recent_preds.columns:
            avg_response = recent_preds['response_time_ms'].mean()
            max_response = recent_preds['response_time_ms'].max()
            
            response_status = 'pass' if avg_response < 1000 else 'warning' if avg_response < 2000 else 'fail'
            health_status['checks']['response_time'] = {
                'status': response_status,
                'avg_ms': round(avg_response, 2),
                'max_ms': round(max_response, 2),
                'message': f'Avg: {avg_response:.0f}ms, Max: {max_response:.0f}ms'
            }
        
        # 4. Check recent performance
        perf_history = self.perf_monitor.get_performance_history(last_n=1)
        if perf_history:
            latest_perf = perf_history[-1]
            r2 = latest_perf.get('r2_score', 0)
            perf_status = 'pass' if r2 >= 0.95 else 'warning' if r2 >= 0.85 else 'fail'
            
            health_status['checks']['model_performance'] = {
                'status': perf_status,
                'r2_score': r2,
                'rmse': latest_perf.get('rmse', 0),
                'message': f'R²={r2:.4f}'
            }
        
        # 5. Overall status
        statuses = [check['status'] for check in health_status['checks'].values()]
        if 'fail' in statuses:
            health_status['overall_status'] = 'unhealthy'
        elif 'warning' in statuses:
            health_status['overall_status'] = 'degraded'
        
        # Log health status
        if health_status['overall_status'] == 'healthy':
            logger.info("✅ System health check: HEALTHY")
        elif health_status['overall_status'] == 'degraded':
            logger.warning("⚠️ System health check: DEGRADED")
        else:
            logger.error("❌ System health check: UNHEALTHY")
        
        return health_status


# Utility functions
def run_monitoring_report(hours: int = 24):
    """Generate comprehensive monitoring report"""
    print("\n" + "="*80)
    print(f"📊 MONITORING REPORT - Last {hours} Hours")
    print("="*80 + "\n")
    
    # 1. Prediction statistics
    pred_logger = PredictionLogger()
    stats = pred_logger.get_statistics(hours=hours)
    
    if stats:
        print(f"📝 Prediction Statistics:")
        print(f"   Total predictions: {stats['total_predictions']}")
        print(f"   Average KPI: {stats['avg_kpi']:.4f}")
        print(f"   KPI range: [{stats['min_kpi']:.4f}, {stats['max_kpi']:.4f}]")
        print(f"   Avg response time: {stats['avg_response_time_ms']:.2f}ms")
        print(f"   Max response time: {stats['max_response_time_ms']:.2f}ms")
        print(f"\n   Predictions by category:")
        for cat, count in stats['predictions_per_category'].items():
            print(f"      {cat}: {count}")
    else:
        print("📝 No predictions in the specified time period")
    
    # 2. Performance history
    perf_monitor = PerformanceMonitor()
    perf_history = perf_monitor.get_performance_history(last_n=5)
    
    if perf_history:
        print(f"\n📈 Recent Performance Evaluations:")
        for i, perf in enumerate(perf_history[-5:], 1):
            print(f"   {i}. {perf['timestamp'][:19]}")
            print(f"      R²={perf['r2_score']:.6f}, RMSE={perf['rmse']:.6f}, MAE={perf['mae']:.6f}")
            if perf.get('alerts'):
                for alert in perf['alerts']:
                    print(f"      {alert}")
    
    # 3. System health
    health_checker = ModelHealthChecker()
    health = health_checker.check_health()
    
    print(f"\n🏥 System Health: {health['overall_status'].upper()}")
    for check_name, check_result in health['checks'].items():
        status_icon = "✅" if check_result['status'] == 'pass' else "⚠️" if check_result['status'] == 'warning' else "❌"
        print(f"   {status_icon} {check_name}: {check_result['message']}")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    # Example usage
    print("🔍 Monitoring System - Logistics KPI Prediction")
    print("=" * 60)
    
    # Run health check
    health_checker = ModelHealthChecker()
    health = health_checker.check_health()
    
    print(f"\n✅ Monitoring system initialized")
    print(f"Overall Status: {health['overall_status'].upper()}")
    
    # Generate report
    print("\nGenerating monitoring report...")
    run_monitoring_report(hours=24)
    
    print(f"\n📝 Logs available at:")
    print(f"   - monitoring_logs.log")
    print(f"   - predictions_history.csv")
    print(f"   - performance_metrics.json")
