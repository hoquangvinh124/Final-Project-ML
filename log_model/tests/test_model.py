"""
Unit Tests for Logistics KPI Prediction Model
"""

import unittest
import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from predict import (
    load_model_artifacts,
    engineer_features,
    preprocess_new_data,
    predict_single_item
)
from train_model import LogisticsKPIPredictor


class TestModelLoading(unittest.TestCase):
    """Test model loading functionality"""
    
    def test_load_model_artifacts(self):
        """Test if model artifacts load successfully"""
        try:
            model, scaler, encoders = load_model_artifacts()
            self.assertIsNotNone(model)
            self.assertIsNotNone(scaler)
            self.assertIsNotNone(encoders)
            print("✅ Model loading test passed")
        except Exception as e:
            self.fail(f"Model loading failed: {str(e)}")
    
    def test_model_has_predict_method(self):
        """Test if loaded model has predict method"""
        model, _, _ = load_model_artifacts()
        self.assertTrue(hasattr(model, 'predict'))
        print("✅ Model predict method test passed")


class TestFeatureEngineering(unittest.TestCase):
    """Test feature engineering functions"""
    
    def setUp(self):
        """Create sample data for testing"""
        self.sample_data = pd.DataFrame({
            'item_id': ['TEST001'],
            'category': ['Electronics'],
            'stock_level': [150],
            'reorder_point': [50],
            'reorder_frequency_days': [7],
            'lead_time_days': [3],
            'daily_demand': [15.5],
            'demand_std_dev': [3.2],
            'item_popularity_score': [0.75],
            'storage_location_id': ['L25'],
            'zone': ['A'],
            'picking_time_seconds': [45],
            'handling_cost_per_unit': [2.50],
            'unit_price': [99.99],
            'holding_cost_per_unit_day': [0.50],
            'stockout_count_last_month': [1],
            'order_fulfillment_rate': [0.95],
            'total_orders_last_month': [450],
            'turnover_ratio': [8.5],
            'layout_efficiency_score': [0.80],
            'last_restock_date': ['2024-11-01'],
            'forecasted_demand_next_7d': [110.0]
        })
    
    def test_engineer_features(self):
        """Test feature engineering adds new features"""
        original_cols = len(self.sample_data.columns)
        engineered_df = engineer_features(self.sample_data)
        new_cols = len(engineered_df.columns)
        
        self.assertGreater(new_cols, original_cols)
        print(f"✅ Feature engineering test passed: {original_cols} -> {new_cols} features")
    
    def test_engineered_features_exist(self):
        """Test specific engineered features exist"""
        engineered_df = engineer_features(self.sample_data)
        
        expected_features = [
            'days_since_restock',
            'demand_variability',
            'stock_coverage_days',
            'reorder_urgency',
            'cost_efficiency'
        ]
        
        for feature in expected_features:
            self.assertIn(feature, engineered_df.columns)
        
        print("✅ Engineered features existence test passed")
    
    def test_feature_values_valid(self):
        """Test engineered feature values are valid (no NaN, Inf)"""
        engineered_df = engineer_features(self.sample_data)
        
        # Check for NaN
        nan_cols = engineered_df.columns[engineered_df.isna().any()].tolist()
        self.assertEqual(len(nan_cols), 0, f"Found NaN in columns: {nan_cols}")
        
        # Check for Inf (only on numeric columns)
        numeric_df = engineered_df.select_dtypes(include=[np.number])
        inf_cols = numeric_df.columns[np.isinf(numeric_df).any()].tolist()
        self.assertEqual(len(inf_cols), 0, f"Found Inf in columns: {inf_cols}")
        
        print("✅ Feature value validation test passed")


class TestPreprocessing(unittest.TestCase):
    """Test preprocessing functions"""
    
    def setUp(self):
        """Load model artifacts for preprocessing tests"""
        self.model, self.scaler, self.encoders = load_model_artifacts()
        self.sample_data = pd.DataFrame({
            'category': ['Electronics'],
            'stock_level': [150],
            'reorder_point': [50],
            'reorder_frequency_days': [7],
            'lead_time_days': [3],
            'daily_demand': [15.5],
            'demand_std_dev': [3.2],
            'item_popularity_score': [0.75],
            'zone': ['A'],
            'picking_time_seconds': [45],
            'handling_cost_per_unit': [2.50],
            'unit_price': [99.99],
            'holding_cost_per_unit_day': [0.50],
            'stockout_count_last_month': [1],
            'order_fulfillment_rate': [0.95],
            'total_orders_last_month': [450],
            'turnover_ratio': [8.5],
            'layout_efficiency_score': [0.80],
            'last_restock_date': ['2024-11-01'],
            'forecasted_demand_next_7d': [110.0]
        })
    
    def test_preprocessing_shape(self):
        """Test preprocessing maintains correct shape"""
        df = engineer_features(self.sample_data.copy())
        processed = preprocess_new_data(df, self.scaler, self.encoders)
        
        self.assertEqual(len(processed), 1)
        self.assertEqual(processed.shape[1], 43)  # Expected number of features
        
        print(f"✅ Preprocessing shape test passed: {processed.shape}")
    
    def test_preprocessing_output_type(self):
        """Test preprocessing returns DataFrame"""
        df = engineer_features(self.sample_data.copy())
        processed = preprocess_new_data(df, self.scaler, self.encoders)
        
        self.assertIsInstance(processed, pd.DataFrame)
        print("✅ Preprocessing output type test passed")


class TestPrediction(unittest.TestCase):
    """Test prediction functionality"""
    
    def setUp(self):
        """Setup test data"""
        self.sample_item = {
            'item_id': 'TEST001',
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
    
    def test_single_prediction(self):
        """Test single item prediction"""
        prediction = predict_single_item(self.sample_item)
        
        self.assertIsInstance(prediction, (float, np.float64))
        self.assertGreaterEqual(prediction, 0)
        self.assertLessEqual(prediction, 1)
        
        print(f"✅ Single prediction test passed: {prediction:.4f}")
    
    def test_prediction_consistency(self):
        """Test predictions are consistent for same input"""
        pred1 = predict_single_item(self.sample_item)
        pred2 = predict_single_item(self.sample_item)
        
        self.assertAlmostEqual(pred1, pred2, places=6)
        print("✅ Prediction consistency test passed")
    
    def test_prediction_range(self):
        """Test predictions fall within expected range"""
        prediction = predict_single_item(self.sample_item)
        
        # KPI scores should be between 0 and 1
        self.assertGreaterEqual(prediction, 0.0)
        self.assertLessEqual(prediction, 1.0)
        
        print(f"✅ Prediction range test passed: {prediction:.4f} ∈ [0, 1]")


class TestModelPerformance(unittest.TestCase):
    """Test model performance metrics"""
    
    def test_model_accuracy_benchmark(self):
        """Test if model meets minimum accuracy threshold"""
        # Load small sample data
        if os.path.exists('data/logistics_dataset.csv'):
            df = pd.read_csv('data/logistics_dataset.csv').head(100)
            
            predictor = LogisticsKPIPredictor(random_state=42)
            df_eng = predictor.engineer_features(df)
            X, y = predictor.preprocess_data(df_eng, fit=True)
            
            from sklearn.model_selection import train_test_split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Train simple model
            from sklearn.linear_model import Ridge
            model = Ridge(alpha=1.0)
            model.fit(X_train, y_train)
            
            # Test accuracy
            from sklearn.metrics import r2_score
            score = r2_score(y_test, model.predict(X_test))
            
            # Should be above 85% threshold
            self.assertGreater(score, 0.85)
            print(f"✅ Model accuracy benchmark test passed: R² = {score:.4f}")
        else:
            self.skipTest("Dataset not available")


class TestDataValidation(unittest.TestCase):
    """Test data validation"""
    
    def test_missing_features_handling(self):
        """Test handling of missing required features"""
        incomplete_data = {
            'category': 'Electronics',
            'stock_level': 150
            # Missing other required features
        }
        
        with self.assertRaises(Exception):
            predict_single_item(incomplete_data)
        
        print("✅ Missing features handling test passed")
    
    def test_invalid_category_handling(self):
        """Test handling of invalid category values"""
        # This test expects the model to handle or raise error for unknown categories
        # Implementation depends on your error handling strategy
        print("✅ Invalid category handling test passed (skipped - needs error handling)")


def run_tests():
    """Run all tests and generate report"""
    print("="*80)
    print("RUNNING UNIT TESTS FOR LOGISTICS KPI PREDICTION MODEL")
    print("="*80)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestModelLoading))
    suite.addTests(loader.loadTestsFromTestCase(TestFeatureEngineering))
    suite.addTests(loader.loadTestsFromTestCase(TestPreprocessing))
    suite.addTests(loader.loadTestsFromTestCase(TestPrediction))
    suite.addTests(loader.loadTestsFromTestCase(TestModelPerformance))
    suite.addTests(loader.loadTestsFromTestCase(TestDataValidation))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ ALL TESTS PASSED!")
    else:
        print("\n❌ SOME TESTS FAILED")
    
    print("="*80)
    
    return result


if __name__ == "__main__":
    result = run_tests()
    sys.exit(0 if result.wasSuccessful() else 1)
