"""
Residuals Analysis for Ridge Regression Model
Phân tích chi tiết về sai số dự đoán của model

Ridge Regression Performance:
- Test R²: 0.999986
- Test RMSE: 0.000427
- Test MAE: 0.000342
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
import warnings
import os

warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

class ResidualsAnalyzer:
    """Comprehensive residuals analysis for Ridge Regression model"""
    
    def __init__(self, model_path='models/ridge_model.pkl', 
                 scaler_path='models/scaler.pkl',
                 data_path='data/logistics_dataset_with_date_features.csv'):
        """
        Initialize Residuals Analyzer
        
        Args:
            model_path: Path to saved Ridge Regression model
            scaler_path: Path to saved scaler
            data_path: Path to dataset
        """
        self.model_path = model_path
        self.scaler_path = scaler_path
        self.data_path = data_path
        self.output_dir = 'residuals_analysis_outputs'
        
        self.model = None
        self.scaler = None
        self.X_test = None
        self.y_test = None
        self.y_pred = None
        self.residuals = None
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
    def load_model_and_data(self):
        """Load model, scaler and prepare test data"""
        print("Loading model and data...")
        
        # Load model and scaler
        try:
            self.model = joblib.load(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
            print(f"✓ Model loaded from {self.model_path}")
            print(f"✓ Scaler loaded from {self.scaler_path}")
        except FileNotFoundError:
            print("⚠ Model files not found. Will train a new model...")
            self._train_new_model()
            return
        
        # Load and prepare data
        df = pd.read_csv(self.data_path)
        print(f"✓ Data loaded: {df.shape}")
        
        # Prepare features (same as training)
        df = self._prepare_features(df)
        
        # Split data
        X = df.drop(['KPI_score'], axis=1)
        y = df['KPI_score']
        
        _, self.X_test, _, self.y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Make predictions
        self.y_pred = self.model.predict(self.X_test)
        
        # Calculate residuals
        self.residuals = self.y_test - self.y_pred
        
        print(f"✓ Test set size: {len(self.X_test)}")
        print(f"✓ Residuals calculated: {len(self.residuals)}")
        print()
        
    def _prepare_features(self, df):
        """Prepare features for prediction"""
        df = df.copy()
        
        # Drop unnecessary columns
        columns_to_drop = ['item_id', 'last_restock_date', 'storage_location_id']
        df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])
        
        # Encode categorical variables
        categorical_columns = df.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            if col in df.columns:
                df[col] = pd.Categorical(df[col]).codes
        
        return df
    
    def _train_new_model(self):
        """Train a new Ridge Regression model if not found"""
        from sklearn.linear_model import Ridge
        
        print("\nTraining new Ridge Regression model...")
        
        # Load and prepare data
        df = pd.read_csv(self.data_path)
        df = self._prepare_features(df)
        
        # Split data
        X = df.drop(['KPI_score'], axis=1)
        y = df['KPI_score']
        
        X_train, self.X_test, y_train, self.y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(self.X_test)
        
        # Train model
        self.model = Ridge(alpha=1.0, random_state=42)
        self.model.fit(X_train_scaled, y_train)
        
        # Save model and scaler
        os.makedirs('models', exist_ok=True)
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)
        
        # Make predictions
        self.y_pred = self.model.predict(X_test_scaled)
        self.residuals = self.y_test - self.y_pred
        
        print("✓ Model trained and saved!")
        print()
        
    def plot_residuals_vs_fitted(self):
        """Plot residuals vs fitted values"""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Scatter plot
        scatter = ax.scatter(self.y_pred, self.residuals, alpha=0.6, 
                           c=self.residuals, cmap='RdYlGn_r', 
                           edgecolors='black', linewidth=0.5)
        
        # Add horizontal line at y=0
        ax.axhline(y=0, color='red', linestyle='--', linewidth=2, label='Zero Residual')
        
        # Add lowess smoothing line
        from scipy.signal import savgol_filter
        sorted_indices = np.argsort(self.y_pred)
        y_pred_sorted = self.y_pred[sorted_indices]
        residuals_sorted = self.residuals.values[sorted_indices]
        
        if len(residuals_sorted) > 50:
            window = min(51, len(residuals_sorted) // 2 * 2 + 1)  # Odd number
            smoothed = savgol_filter(residuals_sorted, window, 3)
            ax.plot(y_pred_sorted, smoothed, 'b-', linewidth=2, label='Trend Line')
        
        # Add standard deviation bands
        std_residuals = np.std(self.residuals)
        ax.axhline(y=2*std_residuals, color='orange', linestyle=':', 
                  linewidth=1.5, label='±2 SD')
        ax.axhline(y=-2*std_residuals, color='orange', linestyle=':', linewidth=1.5)
        
        ax.set_xlabel('Fitted Values (Predicted KPI Score)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Residuals', fontsize=12, fontweight='bold')
        ax.set_title('Residuals vs Fitted Values\n(Kiểm tra tính đồng nhất của phương sai)', 
                    fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Residual Value', fontsize=10, fontweight='bold')
        
        # Add statistics text box
        stats_text = f'Mean: {np.mean(self.residuals):.6f}\n'
        stats_text += f'Std Dev: {np.std(self.residuals):.6f}\n'
        stats_text += f'Min: {np.min(self.residuals):.6f}\n'
        stats_text += f'Max: {np.max(self.residuals):.6f}'
        
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
               fontsize=10, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/residuals_vs_fitted.png', dpi=300, bbox_inches='tight')
        print(f"Saved: {self.output_dir}/residuals_vs_fitted.png")
        plt.show()
        
    def plot_qq_plot(self):
        """Q-Q plot to check normality of residuals"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
        
        # Q-Q plot
        stats.probplot(self.residuals, dist="norm", plot=ax1)
        ax1.set_title('Q-Q Plot\n(Kiểm tra tính chuẩn của residuals)', 
                     fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # Histogram with normal distribution overlay
        ax2.hist(self.residuals, bins=50, density=True, alpha=0.7, 
                color='skyblue', edgecolor='black')
        
        # Fit normal distribution
        mu, sigma = stats.norm.fit(self.residuals)
        x = np.linspace(self.residuals.min(), self.residuals.max(), 100)
        ax2.plot(x, stats.norm.pdf(x, mu, sigma), 'r-', linewidth=2, 
                label=f'Normal(μ={mu:.6f}, σ={sigma:.6f})')
        
        ax2.set_xlabel('Residuals', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Density', fontsize=12, fontweight='bold')
        ax2.set_title('Histogram of Residuals with Normal Distribution', 
                     fontsize=14, fontweight='bold')
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3)
        
        # Add normality test results
        shapiro_stat, shapiro_p = stats.shapiro(self.residuals[:5000] if len(self.residuals) > 5000 else self.residuals)
        
        test_text = f'Shapiro-Wilk Test:\n'
        test_text += f'Statistic: {shapiro_stat:.6f}\n'
        test_text += f'P-value: {shapiro_p:.6f}\n'
        test_text += f'Result: {"Normal ✓" if shapiro_p > 0.05 else "Not Normal ✗"}'
        
        ax2.text(0.98, 0.98, test_text, transform=ax2.transAxes, 
                fontsize=10, verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/qq_plot.png', dpi=300, bbox_inches='tight')
        print(f"Saved: {self.output_dir}/qq_plot.png")
        plt.show()
        
    def plot_scale_location(self):
        """Scale-Location plot (Spread-Location plot)"""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Calculate standardized residuals
        standardized_residuals = np.sqrt(np.abs(self.residuals.values / np.std(self.residuals)))
        
        # Scatter plot
        scatter = ax.scatter(self.y_pred, standardized_residuals, alpha=0.6,
                           c=standardized_residuals, cmap='YlOrRd',
                           edgecolors='black', linewidth=0.5)
        
        # Add smoothing line
        from scipy.signal import savgol_filter
        sorted_indices = np.argsort(self.y_pred)
        y_pred_sorted = self.y_pred[sorted_indices]
        std_res_sorted = standardized_residuals[sorted_indices]
        
        if len(std_res_sorted) > 50:
            window = min(51, len(std_res_sorted) // 2 * 2 + 1)
            smoothed = savgol_filter(std_res_sorted, window, 3)
            ax.plot(y_pred_sorted, smoothed, 'b-', linewidth=2, label='Trend Line')
        
        ax.set_xlabel('Fitted Values', fontsize=12, fontweight='bold')
        ax.set_ylabel('√|Standardized Residuals|', fontsize=12, fontweight='bold')
        ax.set_title('Scale-Location Plot\n(Kiểm tra homoscedasticity - đồng nhất phương sai)', 
                    fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('√|Std. Residuals|', fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/scale_location.png', dpi=300, bbox_inches='tight')
        print(f"Saved: {self.output_dir}/scale_location.png")
        plt.show()
        
    def plot_residuals_histogram(self):
        """Detailed histogram analysis of residuals"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Standard histogram
        ax1 = axes[0, 0]
        n, bins, patches = ax1.hist(self.residuals, bins=50, alpha=0.7, 
                                    color='skyblue', edgecolor='black')
        
        # Color code bins
        cm = plt.cm.RdYlGn_r
        bin_centers = 0.5 * (bins[:-1] + bins[1:])
        col = cm(np.abs(bin_centers) / np.max(np.abs(bin_centers)))
        for c, p in zip(col, patches):
            p.set_facecolor(c)
        
        ax1.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Zero')
        ax1.axvline(x=np.mean(self.residuals), color='green', linestyle='--', 
                   linewidth=2, label=f'Mean: {np.mean(self.residuals):.6f}')
        ax1.set_xlabel('Residuals', fontsize=11, fontweight='bold')
        ax1.set_ylabel('Frequency', fontsize=11, fontweight='bold')
        ax1.set_title('Residuals Distribution', fontsize=12, fontweight='bold')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Box plot
        ax2 = axes[0, 1]
        bp = ax2.boxplot(self.residuals, vert=True, patch_artist=True,
                        widths=0.5, showmeans=True,
                        boxprops=dict(facecolor='lightblue', alpha=0.7),
                        medianprops=dict(color='red', linewidth=2),
                        meanprops=dict(marker='D', markerfacecolor='green', markersize=8))
        
        ax2.set_ylabel('Residuals', fontsize=11, fontweight='bold')
        ax2.set_title('Box Plot of Residuals', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # Add statistics
        q1, median, q3 = np.percentile(self.residuals, [25, 50, 75])
        iqr = q3 - q1
        stats_text = f'Q1: {q1:.6f}\nMedian: {median:.6f}\nQ3: {q3:.6f}\nIQR: {iqr:.6f}'
        ax2.text(1.15, 0.5, stats_text, transform=ax2.transAxes,
                fontsize=9, verticalalignment='center',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        # 3. Cumulative distribution
        ax3 = axes[1, 0]
        sorted_residuals = np.sort(self.residuals)
        cumulative = np.arange(1, len(sorted_residuals) + 1) / len(sorted_residuals)
        ax3.plot(sorted_residuals, cumulative, linewidth=2, color='blue')
        ax3.axhline(y=0.5, color='red', linestyle='--', linewidth=1, alpha=0.5)
        ax3.axvline(x=0, color='green', linestyle='--', linewidth=1, alpha=0.5)
        ax3.set_xlabel('Residuals', fontsize=11, fontweight='bold')
        ax3.set_ylabel('Cumulative Probability', fontsize=11, fontweight='bold')
        ax3.set_title('Cumulative Distribution Function', fontsize=12, fontweight='bold')
        ax3.grid(True, alpha=0.3)
        
        # 4. Statistics summary
        ax4 = axes[1, 1]
        ax4.axis('off')
        
        stats_data = [
            ['Metric', 'Value'],
            ['─'*20, '─'*20],
            ['Count', f'{len(self.residuals)}'],
            ['Mean', f'{np.mean(self.residuals):.8f}'],
            ['Std Dev', f'{np.std(self.residuals):.8f}'],
            ['Min', f'{np.min(self.residuals):.8f}'],
            ['Q1 (25%)', f'{np.percentile(self.residuals, 25):.8f}'],
            ['Median (50%)', f'{np.percentile(self.residuals, 50):.8f}'],
            ['Q3 (75%)', f'{np.percentile(self.residuals, 75):.8f}'],
            ['Max', f'{np.max(self.residuals):.8f}'],
            ['IQR', f'{np.percentile(self.residuals, 75) - np.percentile(self.residuals, 25):.8f}'],
            ['Skewness', f'{stats.skew(self.residuals):.8f}'],
            ['Kurtosis', f'{stats.kurtosis(self.residuals):.8f}'],
        ]
        
        table = ax4.table(cellText=stats_data, cellLoc='left', loc='center',
                         colWidths=[0.5, 0.5])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        
        # Style header
        for i in range(2):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # Highlight important rows
        table[(2, 0)].set_facecolor('#E7E6E6')
        table[(2, 1)].set_facecolor('#E7E6E6')
        
        ax4.set_title('Residuals Statistics Summary', fontsize=12, fontweight='bold', pad=20)
        
        plt.suptitle('Comprehensive Residuals Histogram Analysis', 
                    fontsize=16, fontweight='bold', y=0.995)
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/residuals_histogram.png', dpi=300, bbox_inches='tight')
        print(f"Saved: {self.output_dir}/residuals_histogram.png")
        plt.show()
        
    def plot_actual_vs_predicted(self):
        """Plot actual vs predicted values"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
        
        # Scatter plot
        ax1.scatter(self.y_test, self.y_pred, alpha=0.6, 
                   edgecolors='black', linewidth=0.5)
        
        # Perfect prediction line
        min_val = min(self.y_test.min(), self.y_pred.min())
        max_val = max(self.y_test.max(), self.y_pred.max())
        ax1.plot([min_val, max_val], [min_val, max_val], 'r--', 
                linewidth=2, label='Perfect Prediction')
        
        # Calculate metrics
        from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
        r2 = r2_score(self.y_test, self.y_pred)
        rmse = np.sqrt(mean_squared_error(self.y_test, self.y_pred))
        mae = mean_absolute_error(self.y_test, self.y_pred)
        
        ax1.set_xlabel('Actual KPI Score', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Predicted KPI Score', fontsize=12, fontweight='bold')
        ax1.set_title('Actual vs Predicted Values', fontsize=14, fontweight='bold')
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3)
        
        # Add metrics text box
        metrics_text = f'R² Score: {r2:.6f}\n'
        metrics_text += f'RMSE: {rmse:.6f}\n'
        metrics_text += f'MAE: {mae:.6f}'
        
        ax1.text(0.05, 0.95, metrics_text, transform=ax1.transAxes,
                fontsize=11, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
        
        # Residuals plot
        ax2.scatter(range(len(self.residuals)), self.residuals, 
                   alpha=0.6, edgecolors='black', linewidth=0.5)
        ax2.axhline(y=0, color='red', linestyle='--', linewidth=2)
        
        # Add bands
        std_res = np.std(self.residuals)
        ax2.axhline(y=2*std_res, color='orange', linestyle=':', linewidth=1.5, label='±2 SD')
        ax2.axhline(y=-2*std_res, color='orange', linestyle=':', linewidth=1.5)
        ax2.axhline(y=3*std_res, color='red', linestyle=':', linewidth=1.5, alpha=0.5, label='±3 SD')
        ax2.axhline(y=-3*std_res, color='red', linestyle=':', linewidth=1.5, alpha=0.5)
        
        ax2.set_xlabel('Observation Index', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Residuals', fontsize=12, fontweight='bold')
        ax2.set_title('Residuals Plot', fontsize=14, fontweight='bold')
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/actual_vs_predicted.png', dpi=300, bbox_inches='tight')
        print(f"Saved: {self.output_dir}/actual_vs_predicted.png")
        plt.show()
        
    def plot_residuals_by_percentile(self):
        """Analyze residuals by prediction percentiles"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # Create percentile bins
        percentiles = [0, 25, 50, 75, 100]
        bins = np.percentile(self.y_pred, percentiles)
        bin_labels = ['0-25%', '25-50%', '50-75%', '75-100%']
        
        # Assign each prediction to a percentile bin
        bin_indices = np.digitize(self.y_pred, bins[1:-1])
        
        # 1. Box plot by percentile
        ax1 = axes[0, 0]
        data_by_bin = [self.residuals[bin_indices == i] for i in range(len(bin_labels))]
        bp = ax1.boxplot(data_by_bin, labels=bin_labels, patch_artist=True,
                        showmeans=True)
        
        for patch, color in zip(bp['boxes'], ['lightblue', 'lightgreen', 'lightyellow', 'lightcoral']):
            patch.set_facecolor(color)
            
        ax1.axhline(y=0, color='red', linestyle='--', linewidth=1, alpha=0.5)
        ax1.set_xlabel('Prediction Percentile', fontsize=11, fontweight='bold')
        ax1.set_ylabel('Residuals', fontsize=11, fontweight='bold')
        ax1.set_title('Residuals by Prediction Percentile', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='y')
        
        # 2. Violin plot
        ax2 = axes[0, 1]
        positions = range(len(bin_labels))
        parts = ax2.violinplot(data_by_bin, positions=positions, 
                              showmeans=True, showmedians=True)
        
        ax2.set_xticks(positions)
        ax2.set_xticklabels(bin_labels)
        ax2.axhline(y=0, color='red', linestyle='--', linewidth=1, alpha=0.5)
        ax2.set_xlabel('Prediction Percentile', fontsize=11, fontweight='bold')
        ax2.set_ylabel('Residuals', fontsize=11, fontweight='bold')
        ax2.set_title('Residuals Distribution by Percentile', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 3. Mean and std by percentile
        ax3 = axes[1, 0]
        means = [np.mean(data) for data in data_by_bin]
        stds = [np.std(data) for data in data_by_bin]
        
        x = range(len(bin_labels))
        ax3.errorbar(x, means, yerr=stds, fmt='o-', capsize=5, 
                    capthick=2, linewidth=2, markersize=8)
        ax3.axhline(y=0, color='red', linestyle='--', linewidth=1, alpha=0.5)
        ax3.set_xticks(x)
        ax3.set_xticklabels(bin_labels)
        ax3.set_xlabel('Prediction Percentile', fontsize=11, fontweight='bold')
        ax3.set_ylabel('Mean Residual ± Std Dev', fontsize=11, fontweight='bold')
        ax3.set_title('Mean Residual by Percentile', fontsize=12, fontweight='bold')
        ax3.grid(True, alpha=0.3)
        
        # 4. Count and statistics table
        ax4 = axes[1, 1]
        ax4.axis('off')
        
        stats_data = [['Percentile', 'Count', 'Mean', 'Std Dev', 'RMSE']]
        for i, label in enumerate(bin_labels):
            data = data_by_bin[i]
            count = len(data)
            mean = np.mean(data)
            std = np.std(data)
            rmse = np.sqrt(np.mean(data**2))
            stats_data.append([label, f'{count}', f'{mean:.6f}', f'{std:.6f}', f'{rmse:.6f}'])
        
        table = ax4.table(cellText=stats_data, cellLoc='center', loc='center',
                         colWidths=[0.2, 0.15, 0.22, 0.22, 0.21])
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2.5)
        
        # Style header
        for i in range(5):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        ax4.set_title('Statistics by Percentile', fontsize=12, fontweight='bold', pad=20)
        
        plt.suptitle('Residuals Analysis by Prediction Percentiles', 
                    fontsize=16, fontweight='bold', y=0.995)
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/residuals_by_percentile.png', dpi=300, bbox_inches='tight')
        print(f"Saved: {self.output_dir}/residuals_by_percentile.png")
        plt.show()
        
    def plot_influence_diagnostics(self):
        """Plot influence diagnostics including Cook's distance"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
        
        # Calculate leverage (hat values) using pseudo-inverse
        X_scaled = self.scaler.transform(self.X_test)
        try:
            H = X_scaled @ np.linalg.pinv(X_scaled.T @ X_scaled) @ X_scaled.T
            leverage = np.diag(H)
        except:
            # Fallback: estimate leverage using SVD
            from scipy.linalg import svd
            U, s, Vt = svd(X_scaled, full_matrices=False)
            leverage = np.sum(U**2, axis=1)
        
        # Calculate standardized residuals
        std_residuals = self.residuals / np.std(self.residuals)
        
        # Calculate Cook's distance
        n = len(self.residuals)
        p = X_scaled.shape[1]
        cooks_d = (std_residuals**2 / p) * (leverage / (1 - leverage)**2)
        
        # 1. Cook's Distance plot
        ax1.stem(range(len(cooks_d)), cooks_d, linefmt='b-', 
                markerfmt='bo', basefmt='r-')
        
        # Add threshold line
        threshold = 4 / n
        ax1.axhline(y=threshold, color='red', linestyle='--', 
                   linewidth=2, label=f'Threshold: {threshold:.4f}')
        
        # Highlight influential points
        influential = np.where(cooks_d > threshold)[0]
        if len(influential) > 0:
            ax1.stem(influential, cooks_d[influential], 
                    linefmt='r-', markerfmt='ro', basefmt='r-')
        
        ax1.set_xlabel('Observation Index', fontsize=12, fontweight='bold')
        ax1.set_ylabel("Cook's Distance", fontsize=12, fontweight='bold')
        ax1.set_title(f"Cook's Distance Plot\n(Influential Points: {len(influential)})", 
                     fontsize=14, fontweight='bold')
        ax1.legend(fontsize=10)
        ax1.grid(True, alpha=0.3)
        
        # 2. Residuals vs Leverage
        ax2.scatter(leverage, std_residuals, alpha=0.6, 
                   edgecolors='black', linewidth=0.5)
        
        # Add reference lines
        ax2.axhline(y=0, color='red', linestyle='--', linewidth=1)
        ax2.axhline(y=2, color='orange', linestyle=':', linewidth=1, label='±2 SD')
        ax2.axhline(y=-2, color='orange', linestyle=':', linewidth=1)
        
        # Add leverage threshold
        lev_threshold = 2 * p / n
        ax2.axvline(x=lev_threshold, color='green', linestyle='--', 
                   linewidth=1, label=f'Leverage Threshold: {lev_threshold:.4f}')
        
        # Highlight high leverage points
        high_leverage = np.where(leverage > lev_threshold)[0]
        if len(high_leverage) > 0:
            ax2.scatter(leverage[high_leverage], std_residuals.values[high_leverage],
                       color='red', s=100, alpha=0.7, label='High Leverage')
        
        ax2.set_xlabel('Leverage', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Standardized Residuals', fontsize=12, fontweight='bold')
        ax2.set_title(f'Residuals vs Leverage\n(High Leverage Points: {len(high_leverage)})', 
                     fontsize=14, fontweight='bold')
        ax2.legend(fontsize=10)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/influence_diagnostics.png', dpi=300, bbox_inches='tight')
        print(f"Saved: {self.output_dir}/influence_diagnostics.png")
        plt.show()
        
        # Return influential points info
        return influential, high_leverage, cooks_d
        
    def generate_analysis_report(self):
        """Generate comprehensive residuals analysis report"""
        report_path = f'{self.output_dir}/residuals_analysis_report.txt'
        
        # Calculate statistics
        from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
        r2 = r2_score(self.y_test, self.y_pred)
        rmse = np.sqrt(mean_squared_error(self.y_test, self.y_pred))
        mae = mean_absolute_error(self.y_test, self.y_pred)
        
        # Normality tests
        shapiro_stat, shapiro_p = stats.shapiro(self.residuals[:5000] if len(self.residuals) > 5000 else self.residuals)
        skewness = stats.skew(self.residuals)
        kurtosis = stats.kurtosis(self.residuals)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("RESIDUALS ANALYSIS REPORT - RIDGE REGRESSION MODEL\n")
            f.write(f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")
            
            # Model Performance
            f.write("MODEL PERFORMANCE METRICS\n")
            f.write("-"*80 + "\n")
            f.write(f"R² Score:                {r2:.8f}\n")
            f.write(f"RMSE:                    {rmse:.8f}\n")
            f.write(f"MAE:                     {mae:.8f}\n")
            f.write(f"Test Set Size:           {len(self.y_test)}\n\n")
            
            # Residuals Statistics
            f.write("RESIDUALS STATISTICS\n")
            f.write("-"*80 + "\n")
            f.write(f"Mean:                    {np.mean(self.residuals):.8f}\n")
            f.write(f"Std Deviation:           {np.std(self.residuals):.8f}\n")
            f.write(f"Minimum:                 {np.min(self.residuals):.8f}\n")
            f.write(f"Q1 (25%):                {np.percentile(self.residuals, 25):.8f}\n")
            f.write(f"Median (50%):            {np.percentile(self.residuals, 50):.8f}\n")
            f.write(f"Q3 (75%):                {np.percentile(self.residuals, 75):.8f}\n")
            f.write(f"Maximum:                 {np.max(self.residuals):.8f}\n")
            f.write(f"IQR:                     {np.percentile(self.residuals, 75) - np.percentile(self.residuals, 25):.8f}\n\n")
            
            # Distribution Analysis
            f.write("DISTRIBUTION ANALYSIS\n")
            f.write("-"*80 + "\n")
            f.write(f"Skewness:                {skewness:.8f}\n")
            f.write(f"Kurtosis:                {kurtosis:.8f}\n")
            f.write(f"Shapiro-Wilk Statistic:  {shapiro_stat:.8f}\n")
            f.write(f"Shapiro-Wilk P-value:    {shapiro_p:.8f}\n")
            f.write(f"Normality:               {'YES ✓' if shapiro_p > 0.05 else 'NO ✗'}\n\n")
            
            # Outliers Analysis
            std_res = self.residuals / np.std(self.residuals)
            outliers_2sd = np.sum(np.abs(std_res) > 2)
            outliers_3sd = np.sum(np.abs(std_res) > 3)
            
            f.write("OUTLIERS ANALYSIS\n")
            f.write("-"*80 + "\n")
            f.write(f"Points beyond ±2 SD:     {outliers_2sd} ({outliers_2sd/len(self.residuals)*100:.2f}%)\n")
            f.write(f"Points beyond ±3 SD:     {outliers_3sd} ({outliers_3sd/len(self.residuals)*100:.2f}%)\n")
            f.write(f"Expected (±2 SD):        ~5%\n")
            f.write(f"Expected (±3 SD):        ~0.3%\n\n")
            
            # Interpretation
            f.write("INTERPRETATION & CONCLUSIONS\n")
            f.write("-"*80 + "\n")
            
            # Model Quality
            if r2 > 0.99:
                f.write("1. MODEL QUALITY: ⭐ EXCELLENT\n")
                f.write("   - R² > 0.99 indicates outstanding predictive performance\n")
            elif r2 > 0.95:
                f.write("1. MODEL QUALITY: ✓ VERY GOOD\n")
                f.write("   - R² > 0.95 indicates very good predictive performance\n")
            else:
                f.write("1. MODEL QUALITY: ○ GOOD\n")
                f.write("   - Model shows acceptable performance\n")
            
            # Residuals Distribution
            f.write("\n2. RESIDUALS DISTRIBUTION:\n")
            if shapiro_p > 0.05:
                f.write("   ✓ Residuals follow normal distribution (Shapiro-Wilk p > 0.05)\n")
            else:
                f.write("   ✗ Residuals deviate from normal distribution\n")
            
            if abs(skewness) < 0.5:
                f.write("   ✓ Low skewness - distribution is symmetric\n")
            else:
                f.write(f"   ⚠ Moderate skewness ({skewness:.3f})\n")
            
            if abs(kurtosis) < 3:
                f.write("   ✓ Kurtosis in acceptable range\n")
            else:
                f.write(f"   ⚠ High kurtosis ({kurtosis:.3f}) - heavy tails\n")
            
            # Homoscedasticity
            f.write("\n3. HOMOSCEDASTICITY (Equal Variance):\n")
            f.write("   - Check Scale-Location plot for constant variance\n")
            f.write("   - Residuals should be randomly scattered around zero\n")
            
            # Overall Assessment
            f.write("\n4. OVERALL ASSESSMENT:\n")
            if r2 > 0.999 and shapiro_p > 0.05 and abs(np.mean(self.residuals)) < 0.001:
                f.write("   ⭐ EXCELLENT - Model meets all diagnostic criteria\n")
                f.write("   - High R² score\n")
                f.write("   - Normal residuals distribution\n")
                f.write("   - Mean residual close to zero\n")
                f.write("   - Suitable for production use\n")
            elif r2 > 0.95:
                f.write("   ✓ GOOD - Model performs well with minor issues\n")
                f.write("   - Consider monitoring in production\n")
            else:
                f.write("   ○ ACCEPTABLE - Model may need improvements\n")
            
            f.write("\n" + "="*80 + "\n")
            f.write("END OF REPORT\n")
            f.write("="*80 + "\n")
        
        print(f"Saved: {report_path}")
        
        # Print to console
        print("\n" + "="*80)
        print("📊 RESIDUALS ANALYSIS REPORT")
        print("="*80)
        with open(report_path, 'r', encoding='utf-8') as f:
            print(f.read())
    
    def run_complete_analysis(self):
        """Run complete residuals analysis"""
        print("\n" + "="*80)
        print("STARTING COMPREHENSIVE RESIDUALS ANALYSIS")
        print("="*80 + "\n")
        
        # Load data
        self.load_model_and_data()
        
        print("\n[1/7] Generating Residuals vs Fitted plot...")
        self.plot_residuals_vs_fitted()
        
        print("\n[2/7] Generating Q-Q plot and normality tests...")
        self.plot_qq_plot()
        
        print("\n[3/7] Generating Scale-Location plot...")
        self.plot_scale_location()
        
        print("\n[4/7] Generating histogram analysis...")
        self.plot_residuals_histogram()
        
        print("\n[5/7] Generating Actual vs Predicted plot...")
        self.plot_actual_vs_predicted()
        
        print("\n[6/7] Generating residuals by percentile analysis...")
        self.plot_residuals_by_percentile()
        
        print("\n[7/7] Generating influence diagnostics...")
        influential, high_leverage, cooks_d = self.plot_influence_diagnostics()
        
        print("\n[BONUS] Generating analysis report...")
        self.generate_analysis_report()
        
        print("\n" + "="*80)
        print("✅ RESIDUALS ANALYSIS COMPLETED!")
        print(f"📁 All outputs saved to: {self.output_dir}/")
        print("="*80 + "\n")
        
        # Summary
        print("\n📊 QUICK SUMMARY:")
        print(f"   Influential points: {len(influential)}")
        print(f"   High leverage points: {len(high_leverage)}")
        print(f"   Max Cook's distance: {np.max(cooks_d):.6f}")
        print(f"   Mean residual: {np.mean(self.residuals):.8f}")
        print(f"   Std residual: {np.std(self.residuals):.8f}")
        print()


def main():
    """Main execution function"""
    analyzer = ResidualsAnalyzer()
    analyzer.run_complete_analysis()
    print("\n✅ Residuals analysis completed successfully!")


if __name__ == "__main__":
    main()
