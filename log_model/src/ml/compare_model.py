"""
Model Comparison and Visualization Tool
Visualize and compare performance of multiple ML models

📊 MÔ TẢ CÁC CHỈ SỐ ĐÁNH GIÁ MODEL
================================================================================

1. R² SCORE (Coefficient of Determination)
   ─────────────────────────────────────────
   • Ý nghĩa: Đo lường khả năng model giải thích biến thiên của dữ liệu
   • Khoảng giá trị: -∞ đến 1 (lý tưởng = 1)
   • Train R²: Hiệu suất trên tập huấn luyện
   • Test R²: Hiệu suất trên tập kiểm tra (quan trọng nhất)
   • CV R² Mean: Trung bình R² qua cross-validation
   • Đánh giá:
     - R² > 0.99: ⭐ EXCELLENT (Xuất sắc)
     - R² > 0.95: ✓ VERY GOOD (Rất tốt)
     - R² > 0.90: ○ GOOD (Tốt)
     - R² < 0.90: △ NEEDS IMPROVEMENT (Cần cải thiện)

2. RMSE (Root Mean Squared Error)
   ──────────────────────────────────
   • Ý nghĩa: Sai số trung bình bình phương giữa giá trị dự đoán và thực tế
   • Đơn vị: Cùng đơn vị với biến mục tiêu
   • Đặc điểm: Phạt nặng các sai số lớn hơn MAE
   • Mục tiêu: Càng nhỏ càng tốt (gần 0)
   • Ứng dụng: Đánh giá độ chính xác tổng thể, nhạy cảm với outliers

3. MAE (Mean Absolute Error)
   ─────────────────────────────
   • Ý nghĩa: Sai số tuyệt đối trung bình
   • Đơn vị: Cùng đơn vị với biến mục tiêu
   • Đặc điểm: Ít nhạy cảm với outliers hơn RMSE
   • Mục tiêu: Càng nhỏ càng tốt (gần 0)
   • Ứng dụng: Đo lường sai số trung bình thực tế

4. CV R² Std (Cross-Validation Standard Deviation)
   ────────────────────────────────────────────────
   • Ý nghĩa: Độ ổn định của model qua các fold cross-validation
   • Mục tiêu: Càng nhỏ càng tốt
   • Đánh giá:
     - Std < 0.001: Rất ổn định
     - Std < 0.005: Ổn định
     - Std > 0.005: Không ổn định
   • Ứng dụng: Đánh giá khả năng tổng quát hóa

5. OVERFITTING GAP (Train R² - Test R²)
   ──────────────────────────────────────
   • Ý nghĩa: Mức độ overfitting của model
   • Đánh giá:
     - Gap < 0.01: ✓ Không overfitting
     - Gap 0.01-0.05: ⚠ Overfitting nhẹ
     - Gap > 0.05: ❌ Overfitting nghiêm trọng
   • Lưu ý: Gap âm (Test > Train) có thể do regularization mạnh

6. COMPOSITE SCORE (Điểm Tổng Hợp)
   ────────────────────────────────────
   • Công thức: 40% Test R² + 30% RMSE⁻¹ + 20% MAE⁻¹ + 10% CV Stability
   • Khoảng giá trị: 0 đến 1
   • Mục đích: Xếp hạng tổng thể các model dựa trên nhiều tiêu chí
   • Ứng dụng: Chọn model tốt nhất cân bằng giữa accuracy và stability

📈 PHÂN TÍCH KẾT QUẢ SO SÁNH
================================================================================

Dựa trên kết quả thực nghiệm với 7 models:

TOP PERFORMERS:
• Ridge Regression: Test R² = 0.999986 (gần như hoàn hảo)
  - Sai số cực thấp (RMSE=0.000427, MAE=0.000342)
  - Rất ổn định (CV Std=0.000003)
  - Không có overfitting (Gap=-0.000001)
  → Best choice cho production

• CatBoost: Test R² = 0.997946
  - Hiệu suất xuất sắc với ensemble boosting
  - Sai số thấp (RMSE=0.005185)
  - Rất ổn định (CV Std=0.000552)
  → Alternative tốt cho dữ liệu phức tạp

• LightGBM: Test R² = 0.991299
  - Tốc độ training nhanh
  - Hiệu suất cao (RMSE=0.010672)
  - Ổn định (CV Std=0.001410)
  → Tốt cho datasets lớn

MEDIUM PERFORMERS:
• Gradient Boosting: Test R² = 0.988513
• Random Forest: Test R² = 0.964002
• XGBoost: Test R² = 0.951353
  → Phù hợp cho các bài toán chuẩn

POOR PERFORMERS:
• Lasso Regression: Test R² = -0.001632
  - Regularization quá mạnh
  - Không phù hợp với dữ liệu này
  → Không nên sử dụng

🎯 KHUYẾN NGHỊ
================================================================================

1. SỬ DỤNG CHO PRODUCTION:
   → Ridge Regression (R²=0.9999, RMSE=0.0004)
   Lý do: Accuracy cao nhất, ổn định, không overfitting

2. BACKUP MODEL:
   → CatBoost (R²=0.9979, RMSE=0.0052)
   Lý do: Hiệu suất tuyệt vời, xử lý tốt categorical features

3. KHI CẦN TỐC ĐỘ:
   → LightGBM (R²=0.9913, RMSE=0.0107)
   Lý do: Training nhanh, hiệu suất cao

4. TRÁNH SỬ DỤNG:
   → Lasso Regression
   Lý do: Hiệu suất kém với dataset này

================================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

class ModelComparator:
    """Compare and visualize multiple trained models"""
    
    def __init__(self, results_path='model_comparison_results.csv'):
        """
        Initialize ModelComparator
        
        Args:
            results_path: Path to model comparison results CSV
        """
        self.results_path = results_path
        self.results_df = None
        self.output_dir = 'visualization_outputs'
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
    def load_results(self):
        """Load model comparison results"""
        print(f"Loading results from {self.results_path}...")
        self.results_df = pd.read_csv(self.results_path, index_col=0)
        print(f"Loaded {len(self.results_df)} models")
        print(self.results_df)
        return self.results_df
    
    def plot_r2_comparison(self):
        """Plot R² scores comparison across all models"""
        fig, ax = plt.subplots(figsize=(14, 8))
        
        models = self.results_df.index
        train_r2 = self.results_df['Train R²']
        test_r2 = self.results_df['Test R²']
        cv_r2 = self.results_df['CV R² Mean']
        
        x = np.arange(len(models))
        width = 0.25
        
        bars1 = ax.bar(x - width, train_r2, width, label='Train R²', alpha=0.8)
        bars2 = ax.bar(x, test_r2, width, label='Test R²', alpha=0.8)
        bars3 = ax.bar(x + width, cv_r2, width, label='CV R² Mean', alpha=0.8)
        
        ax.set_xlabel('Models', fontsize=12, fontweight='bold')
        ax.set_ylabel('R² Score', fontsize=12, fontweight='bold')
        ax.set_title('R² Score Comparison Across Models', fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(models, rotation=45, ha='right')
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bars in [bars1, bars2, bars3]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.4f}',
                       ha='center', va='bottom', fontsize=8, rotation=0)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/r2_comparison.png', dpi=300, bbox_inches='tight')
        print(f"Saved: {self.output_dir}/r2_comparison.png")
        plt.show()
        
    def plot_error_metrics(self):
        """Plot error metrics (RMSE and MAE)"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        models = self.results_df.index
        rmse = self.results_df['Test RMSE']
        mae = self.results_df['Test MAE']
        
        # RMSE plot
        bars1 = ax1.barh(models, rmse, color='coral', alpha=0.8)
        ax1.set_xlabel('RMSE', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Models', fontsize=12, fontweight='bold')
        ax1.set_title('Root Mean Squared Error (RMSE)', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3, axis='x')
        
        # Add value labels
        for i, bar in enumerate(bars1):
            width = bar.get_width()
            ax1.text(width, bar.get_y() + bar.get_height()/2.,
                    f'{width:.6f}',
                    ha='left', va='center', fontsize=9)
        
        # MAE plot
        bars2 = ax2.barh(models, mae, color='skyblue', alpha=0.8)
        ax2.set_xlabel('MAE', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Models', fontsize=12, fontweight='bold')
        ax2.set_title('Mean Absolute Error (MAE)', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='x')
        
        # Add value labels
        for i, bar in enumerate(bars2):
            width = bar.get_width()
            ax2.text(width, bar.get_y() + bar.get_height()/2.,
                    f'{width:.6f}',
                    ha='left', va='center', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/error_metrics.png', dpi=300, bbox_inches='tight')
        print(f"Saved: {self.output_dir}/error_metrics.png")
        plt.show()
        
    def plot_overfitting_analysis(self):
        """Analyze overfitting by comparing train vs test R²"""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        models = self.results_df.index
        train_r2 = self.results_df['Train R²']
        test_r2 = self.results_df['Test R²']
        
        # Calculate overfitting gap
        overfit_gap = train_r2 - test_r2
        
        colors = ['red' if gap > 0.01 else 'green' for gap in overfit_gap]
        
        bars = ax.barh(models, overfit_gap, color=colors, alpha=0.7)
        ax.set_xlabel('Overfitting Gap (Train R² - Test R²)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Models', fontsize=12, fontweight='bold')
        ax.set_title('Overfitting Analysis', fontsize=14, fontweight='bold')
        ax.axvline(x=0, color='black', linestyle='--', linewidth=1)
        ax.grid(True, alpha=0.3, axis='x')
        
        # Add value labels
        for i, bar in enumerate(bars):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2.,
                   f'{width:.6f}',
                   ha='left' if width > 0 else 'right', 
                   va='center', fontsize=9)
        
        # Add legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='red', alpha=0.7, label='High Overfitting (>0.01)'),
            Patch(facecolor='green', alpha=0.7, label='Low Overfitting (≤0.01)')
        ]
        ax.legend(handles=legend_elements, loc='best')
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/overfitting_analysis.png', dpi=300, bbox_inches='tight')
        print(f"Saved: {self.output_dir}/overfitting_analysis.png")
        plt.show()
        
    def plot_cv_stability(self):
        """Plot cross-validation stability (mean ± std)"""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        models = self.results_df.index
        cv_mean = self.results_df['CV R² Mean']
        cv_std = self.results_df['CV R² Std']
        
        y_pos = np.arange(len(models))
        
        # Plot with error bars
        ax.barh(y_pos, cv_mean, xerr=cv_std, color='mediumpurple', 
                alpha=0.7, capsize=5, error_kw={'linewidth': 2})
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(models)
        ax.set_xlabel('CV R² Score', fontsize=12, fontweight='bold')
        ax.set_ylabel('Models', fontsize=12, fontweight='bold')
        ax.set_title('Cross-Validation Stability (Mean ± Std)', fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        
        # Add value labels
        for i, (mean, std) in enumerate(zip(cv_mean, cv_std)):
            ax.text(mean, i, f'{mean:.4f}±{std:.6f}',
                   ha='left', va='center', fontsize=8)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/cv_stability.png', dpi=300, bbox_inches='tight')
        print(f"Saved: {self.output_dir}/cv_stability.png")
        plt.show()
        
    def plot_radar_chart(self):
        """Create radar chart for top 4 models"""
        # Select top 4 models based on Test R²
        top_models = self.results_df.nlargest(4, 'Test R²')
        
        # Normalize metrics to 0-1 scale
        metrics = ['Test R²', 'CV R² Mean', 'Train R²']
        
        # For RMSE and MAE, use inverse (lower is better)
        normalized_data = top_models[metrics].copy()
        
        # Add inverse error metrics
        max_rmse = self.results_df['Test RMSE'].max()
        max_mae = self.results_df['Test MAE'].max()
        normalized_data['Low RMSE'] = 1 - (top_models['Test RMSE'] / max_rmse)
        normalized_data['Low MAE'] = 1 - (top_models['Test MAE'] / max_mae)
        
        categories = ['Test R²', 'CV R² Mean', 'Train R²', 'Low RMSE', 'Low MAE']
        N = len(categories)
        
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A']
        
        for idx, (model_name, row) in enumerate(top_models.iterrows()):
            values = normalized_data.loc[model_name].values.flatten().tolist()
            values += values[:1]
            
            ax.plot(angles, values, 'o-', linewidth=2, label=model_name, color=colors[idx])
            ax.fill(angles, values, alpha=0.15, color=colors[idx])
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, size=10)
        ax.set_ylim(0, 1)
        ax.set_title('Top 4 Models Performance Comparison (Radar Chart)', 
                    size=14, fontweight='bold', pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        ax.grid(True)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/radar_chart.png', dpi=300, bbox_inches='tight')
        print(f"Saved: {self.output_dir}/radar_chart.png")
        plt.show()
        
    def plot_heatmap(self):
        """Create heatmap of all metrics"""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Normalize all metrics to 0-1 scale for better visualization
        normalized_df = self.results_df.copy()
        
        # Normalize positive metrics (higher is better)
        for col in ['Train R²', 'Test R²', 'CV R² Mean']:
            normalized_df[col] = normalized_df[col]
        
        # Normalize negative metrics (lower is better) - invert
        max_rmse = normalized_df['Test RMSE'].max()
        max_mae = normalized_df['Test MAE'].max()
        max_cv_std = normalized_df['CV R² Std'].max()
        
        normalized_df['Test RMSE (inv)'] = 1 - (normalized_df['Test RMSE'] / max_rmse)
        normalized_df['Test MAE (inv)'] = 1 - (normalized_df['Test MAE'] / max_mae)
        normalized_df['CV Std (inv)'] = 1 - (normalized_df['CV R² Std'] / max_cv_std)
        
        # Select columns for heatmap
        heatmap_cols = ['Train R²', 'Test R²', 'CV R² Mean', 
                       'Test RMSE (inv)', 'Test MAE (inv)', 'CV Std (inv)']
        heatmap_data = normalized_df[heatmap_cols]
        
        sns.heatmap(heatmap_data, annot=True, fmt='.4f', cmap='RdYlGn', 
                   center=0.5, linewidths=1, linecolor='white',
                   cbar_kws={'label': 'Normalized Score'}, ax=ax)
        
        ax.set_title('Model Performance Heatmap (Normalized Metrics)', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Metrics', fontsize=12, fontweight='bold')
        ax.set_ylabel('Models', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/performance_heatmap.png', dpi=300, bbox_inches='tight')
        print(f"Saved: {self.output_dir}/performance_heatmap.png")
        plt.show()
        
    def plot_ranking(self):
        """Create ranking visualization based on multiple criteria"""
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Calculate composite score
        # Higher Test R² is better, lower RMSE is better, lower CV Std is better
        scores = self.results_df.copy()
        
        # Normalize and combine metrics
        test_r2_norm = scores['Test R²']
        rmse_norm = 1 - (scores['Test RMSE'] / scores['Test RMSE'].max())
        cv_std_norm = 1 - (scores['CV R² Std'] / scores['CV R² Std'].max())
        mae_norm = 1 - (scores['Test MAE'] / scores['Test MAE'].max())
        
        # Weighted composite score
        scores['Composite Score'] = (
            test_r2_norm * 0.4 +  # 40% weight on test R²
            rmse_norm * 0.3 +      # 30% weight on RMSE
            mae_norm * 0.2 +       # 20% weight on MAE
            cv_std_norm * 0.1      # 10% weight on CV stability
        )
        
        # Sort by composite score
        scores_sorted = scores.sort_values('Composite Score', ascending=True)
        
        colors = plt.cm.viridis(np.linspace(0, 1, len(scores_sorted)))
        
        bars = ax.barh(scores_sorted.index, scores_sorted['Composite Score'], 
                      color=colors, alpha=0.8)
        
        ax.set_xlabel('Composite Score', fontsize=12, fontweight='bold')
        ax.set_ylabel('Models', fontsize=12, fontweight='bold')
        ax.set_title('Model Ranking (Weighted Composite Score)', 
                    fontsize=14, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='x')
        
        # Add value labels and ranking
        for i, (bar, score) in enumerate(zip(bars, scores_sorted['Composite Score'])):
            width = bar.get_width()
            rank = len(scores_sorted) - i
            ax.text(width, bar.get_y() + bar.get_height()/2.,
                   f'  #{rank}: {score:.4f}',
                   ha='left', va='center', fontsize=10, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/model_ranking.png', dpi=300, bbox_inches='tight')
        print(f"Saved: {self.output_dir}/model_ranking.png")
        plt.show()
        
        return scores_sorted[['Test R²', 'Test RMSE', 'Test MAE', 'CV R² Std', 'Composite Score']]
        
    def plot_performance_summary(self):
        """Create comprehensive performance summary"""
        fig = plt.figure(figsize=(18, 12))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # 1. Test R² comparison
        ax1 = fig.add_subplot(gs[0, :2])
        test_r2_sorted = self.results_df.sort_values('Test R²', ascending=True)
        colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(test_r2_sorted)))
        bars = ax1.barh(test_r2_sorted.index, test_r2_sorted['Test R²'], color=colors)
        ax1.set_xlabel('Test R² Score', fontweight='bold')
        ax1.set_title('Test R² Performance', fontweight='bold', fontsize=12)
        ax1.grid(True, alpha=0.3, axis='x')
        for bar in bars:
            width = bar.get_width()
            ax1.text(width, bar.get_y() + bar.get_height()/2.,
                    f'{width:.4f}', ha='left', va='center', fontsize=8)
        
        # 2. Error comparison
        ax2 = fig.add_subplot(gs[0, 2])
        error_data = self.results_df[['Test RMSE', 'Test MAE']]
        error_data.plot(kind='bar', ax=ax2, alpha=0.7)
        ax2.set_title('Error Metrics', fontweight='bold', fontsize=12)
        ax2.set_ylabel('Error Value', fontweight='bold')
        ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45, ha='right')
        ax2.legend(fontsize=8)
        ax2.grid(True, alpha=0.3)
        
        # 3. Train vs Test R²
        ax3 = fig.add_subplot(gs[1, :])
        x = np.arange(len(self.results_df))
        width = 0.35
        ax3.bar(x - width/2, self.results_df['Train R²'], width, 
               label='Train R²', alpha=0.8)
        ax3.bar(x + width/2, self.results_df['Test R²'], width, 
               label='Test R²', alpha=0.8)
        ax3.set_xlabel('Models', fontweight='bold')
        ax3.set_ylabel('R² Score', fontweight='bold')
        ax3.set_title('Train vs Test R² Comparison', fontweight='bold', fontsize=12)
        ax3.set_xticks(x)
        ax3.set_xticklabels(self.results_df.index, rotation=45, ha='right')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Statistics table
        ax4 = fig.add_subplot(gs[2, :])
        ax4.axis('tight')
        ax4.axis('off')
        
        stats_data = []
        for model in self.results_df.index:
            row = self.results_df.loc[model]
            stats_data.append([
                model,
                f"{row['Test R²']:.4f}",
                f"{row['Test RMSE']:.6f}",
                f"{row['Test MAE']:.6f}",
                f"{row['CV R² Mean']:.4f}±{row['CV R² Std']:.6f}"
            ])
        
        table = ax4.table(cellText=stats_data,
                         colLabels=['Model', 'Test R²', 'RMSE', 'MAE', 'CV R² (Mean±Std)'],
                         cellLoc='center',
                         loc='center',
                         colWidths=[0.25, 0.15, 0.15, 0.15, 0.3])
        
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2)
        
        # Color code the best values
        for i, model in enumerate(self.results_df.index, start=1):
            if model == self.results_df['Test R²'].idxmax():
                table[(i, 1)].set_facecolor('#90EE90')
            if model == self.results_df['Test RMSE'].idxmin():
                table[(i, 2)].set_facecolor('#90EE90')
            if model == self.results_df['Test MAE'].idxmin():
                table[(i, 3)].set_facecolor('#90EE90')
        
        # Header styling
        for i in range(5):
            table[(0, i)].set_facecolor('#4472C4')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        plt.suptitle('Comprehensive Model Performance Summary', 
                    fontsize=16, fontweight='bold', y=0.995)
        
        plt.savefig(f'{self.output_dir}/performance_summary.png', dpi=300, bbox_inches='tight')
        print(f"Saved: {self.output_dir}/performance_summary.png")
        plt.show()
        
    def plot_scatter_predictions(self):
        """Create scatter plot comparing actual vs predicted for top models"""
        # This requires loading predictions - we'll create a demo visualization
        fig, ax = plt.subplots(figsize=(10, 10))
        
        # Get top 3 models
        top_3 = self.results_df.nlargest(3, 'Test R²')
        
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1']
        
        # Create diagonal line (perfect prediction)
        ax.plot([0, 1], [0, 1], 'k--', linewidth=2, label='Perfect Prediction', alpha=0.5)
        
        # Add model performance zones
        y_range = np.linspace(0, 1, 100)
        for model_name, color in zip(top_3.index, colors):
            r2 = top_3.loc[model_name, 'Test R²']
            # Simulate prediction scatter based on R²
            noise = np.random.normal(0, np.sqrt(1-r2) * 0.1, 100)
            x = np.linspace(0, 1, 100)
            y = x + noise
            ax.scatter(x, y, alpha=0.5, s=30, label=f'{model_name} (R²={r2:.4f})', color=color)
        
        ax.set_xlabel('Actual Values', fontsize=12, fontweight='bold')
        ax.set_ylabel('Predicted Values', fontsize=12, fontweight='bold')
        ax.set_title('Prediction Accuracy Comparison (Simulated)', fontsize=14, fontweight='bold')
        ax.legend(loc='upper left', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/scatter_predictions.png', dpi=300, bbox_inches='tight')
        print(f"Saved: {self.output_dir}/scatter_predictions.png")
        plt.show()
    
    def plot_training_efficiency(self):
        """Analyze model complexity and training efficiency"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        models = self.results_df.index
        test_r2 = self.results_df['Test R²']
        cv_std = self.results_df['CV R² Std']
        
        # Model complexity proxy (based on overfitting)
        complexity = self.results_df['Train R²'] - self.results_df['Test R²']
        
        # Plot 1: Performance vs Complexity
        colors = plt.cm.viridis(np.linspace(0, 1, len(models)))
        scatter1 = ax1.scatter(complexity, test_r2, c=range(len(models)), 
                              cmap='viridis', s=200, alpha=0.7, edgecolors='black', linewidth=2)
        
        for i, model in enumerate(models):
            ax1.annotate(model, (complexity[i], test_r2[i]), 
                        fontsize=9, ha='center', va='bottom')
        
        ax1.set_xlabel('Model Complexity (Overfit Gap)', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Test R² Score', fontsize=12, fontweight='bold')
        ax1.set_title('Performance vs Complexity Trade-off', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Stability vs Performance
        scatter2 = ax2.scatter(cv_std, test_r2, c=range(len(models)), 
                              cmap='plasma', s=200, alpha=0.7, edgecolors='black', linewidth=2)
        
        for i, model in enumerate(models):
            ax2.annotate(model, (cv_std[i], test_r2[i]), 
                        fontsize=9, ha='center', va='bottom')
        
        ax2.set_xlabel('CV Standard Deviation (Instability)', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Test R² Score', fontsize=12, fontweight='bold')
        ax2.set_title('Performance vs Stability Trade-off', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/training_efficiency.png', dpi=300, bbox_inches='tight')
        print(f"Saved: {self.output_dir}/training_efficiency.png")
        plt.show()
    
    def plot_metrics_distribution(self):
        """Create box plot of metric distributions"""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        metrics = ['Train R²', 'Test R²', 'Test RMSE', 'Test MAE']
        
        for ax, metric in zip(axes.flat, metrics):
            data = self.results_df[metric]
            
            # Create violin plot with box plot overlay
            parts = ax.violinplot([data], positions=[0], widths=0.7, 
                                 showmeans=True, showmedians=True)
            
            # Customize violin plot colors
            for pc in parts['bodies']:
                pc.set_facecolor('#8B9DC3')
                pc.set_alpha(0.7)
            
            # Add individual points
            y = data.values
            x = np.random.normal(0, 0.04, size=len(y))
            colors = plt.cm.Set3(np.linspace(0, 1, len(y)))
            
            for i, (xi, yi, model) in enumerate(zip(x, y, data.index)):
                ax.scatter(xi, yi, s=150, alpha=0.8, color=colors[i], 
                          edgecolors='black', linewidth=1.5, zorder=3)
                ax.text(xi + 0.15, yi, model, fontsize=8, va='center')
            
            ax.set_ylabel(metric, fontsize=12, fontweight='bold')
            ax.set_title(f'Distribution of {metric}', fontsize=12, fontweight='bold')
            ax.set_xticks([])
            ax.grid(True, alpha=0.3, axis='y')
            
            # Add statistics
            mean_val = data.mean()
            median_val = data.median()
            std_val = data.std()
            
            stats_text = f'Mean: {mean_val:.6f}\nMedian: {median_val:.6f}\nStd: {std_val:.6f}'
            ax.text(0.5, 0.05, stats_text, transform=ax.transAxes, 
                   fontsize=9, verticalalignment='bottom',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.suptitle('Metrics Distribution Across All Models', 
                    fontsize=16, fontweight='bold', y=0.995)
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/metrics_distribution.png', dpi=300, bbox_inches='tight')
        print(f"Saved: {self.output_dir}/metrics_distribution.png")
        plt.show()
    
    def plot_pareto_chart(self):
        """Create Pareto chart showing cumulative performance"""
        fig, ax1 = plt.subplots(figsize=(14, 8))
        
        # Sort by Test R²
        sorted_df = self.results_df.sort_values('Test R²', ascending=False)
        models = sorted_df.index
        test_r2 = sorted_df['Test R²']
        
        # Calculate cumulative percentage
        cumulative = np.cumsum(test_r2) / np.sum(test_r2) * 100
        
        # Bar chart
        x_pos = np.arange(len(models))
        colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(models)))
        bars = ax1.bar(x_pos, test_r2, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
        
        ax1.set_xlabel('Models', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Test R² Score', fontsize=12, fontweight='bold')
        ax1.set_xticks(x_pos)
        ax1.set_xticklabels(models, rotation=45, ha='right')
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for i, (bar, val) in enumerate(zip(bars, test_r2)):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{val:.4f}',
                    ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        # Cumulative line
        ax2 = ax1.twinx()
        line = ax2.plot(x_pos, cumulative, 'ro-', linewidth=3, markersize=10, 
                       label='Cumulative %', color='darkred')
        ax2.set_ylabel('Cumulative Percentage (%)', fontsize=12, fontweight='bold', color='darkred')
        ax2.tick_params(axis='y', labelcolor='darkred')
        ax2.set_ylim(0, 110)
        
        # Add percentage labels on line
        for i, (x, y) in enumerate(zip(x_pos, cumulative)):
            ax2.text(x, y + 3, f'{y:.1f}%', ha='center', fontsize=9, 
                    color='darkred', fontweight='bold')
        
        # Add 80% line
        ax2.axhline(y=80, color='blue', linestyle='--', linewidth=2, alpha=0.5, label='80% Line')
        
        ax1.set_title('Pareto Chart - Model Performance Contribution', 
                     fontsize=14, fontweight='bold', pad=20)
        
        # Combined legend
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines2, labels2, loc='center right', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/pareto_chart.png', dpi=300, bbox_inches='tight')
        print(f"Saved: {self.output_dir}/pareto_chart.png")
        plt.show()
    
    def plot_performance_quadrant(self):
        """Create quadrant analysis of performance vs stability"""
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Metrics for quadrant analysis
        x_metric = self.results_df['Test R²']
        y_metric = 1 / (self.results_df['Test RMSE'] + 1e-10)  # Inverse RMSE (higher is better)
        
        # Calculate medians for quadrant lines
        x_median = x_metric.median()
        y_median = y_metric.median()
        
        # Plot quadrant lines
        ax.axvline(x=x_median, color='gray', linestyle='--', linewidth=2, alpha=0.5)
        ax.axhline(y=y_median, color='gray', linestyle='--', linewidth=2, alpha=0.5)
        
        # Color code by CV stability
        cv_std = self.results_df['CV R² Std']
        colors = plt.cm.RdYlGn_r(cv_std / cv_std.max())
        
        # Scatter plot
        scatter = ax.scatter(x_metric, y_metric, s=300, c=cv_std, 
                           cmap='RdYlGn_r', alpha=0.7, edgecolors='black', linewidth=2)
        
        # Add model labels
        for i, model in enumerate(self.results_df.index):
            ax.annotate(model, (x_metric[i], y_metric[i]), 
                       fontsize=10, ha='center', va='center', fontweight='bold')
        
        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('CV Standard Deviation\n(Lower is Better)', 
                      fontsize=11, fontweight='bold')
        
        # Quadrant labels
        ax.text(0.02, 0.98, 'High Accuracy\nLow Precision', 
               transform=ax.transAxes, fontsize=11, va='top', ha='left',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))
        
        ax.text(0.98, 0.98, 'High Accuracy\nHigh Precision\n⭐ BEST', 
               transform=ax.transAxes, fontsize=11, va='top', ha='right',
               bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))
        
        ax.text(0.02, 0.02, 'Low Accuracy\nLow Precision\n❌ WORST', 
               transform=ax.transAxes, fontsize=11, va='bottom', ha='left',
               bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.5))
        
        ax.text(0.98, 0.02, 'Low Accuracy\nHigh Precision', 
               transform=ax.transAxes, fontsize=11, va='bottom', ha='right',
               bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.3))
        
        ax.set_xlabel('Test R² Score (Higher is Better)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Inverse RMSE (Higher is Better)', fontsize=12, fontweight='bold')
        ax.set_title('Performance Quadrant Analysis', fontsize=14, fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{self.output_dir}/performance_quadrant.png', dpi=300, bbox_inches='tight')
        print(f"Saved: {self.output_dir}/performance_quadrant.png")
        plt.show()
    
    def generate_comparison_report(self):
        """Generate detailed comparison report"""
        report_path = f'{self.output_dir}/model_comparison_report.txt'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("MODEL COMPARISON REPORT\n")
            f.write(f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")
            
            # Overall Statistics
            f.write("OVERALL STATISTICS\n")
            f.write("-"*80 + "\n")
            f.write(f"Total Models Evaluated: {len(self.results_df)}\n")
            f.write(f"Best Test R²: {self.results_df['Test R²'].max():.6f}\n")
            f.write(f"Worst Test R²: {self.results_df['Test R²'].min():.6f}\n")
            f.write(f"Average Test R²: {self.results_df['Test R²'].mean():.6f}\n")
            f.write(f"Std Dev Test R²: {self.results_df['Test R²'].std():.6f}\n\n")
            
            # Individual Model Details
            f.write("DETAILED MODEL PERFORMANCE\n")
            f.write("-"*80 + "\n\n")
            
            for idx, model in enumerate(self.results_df.index, 1):
                row = self.results_df.loc[model]
                f.write(f"{idx}. {model}\n")
                f.write(f"   {'─'*70}\n")
                f.write(f"   Train R²:        {row['Train R²']:.6f}\n")
                f.write(f"   Test R²:         {row['Test R²']:.6f}\n")
                f.write(f"   CV R² Mean:      {row['CV R² Mean']:.6f} ± {row['CV R² Std']:.6f}\n")
                f.write(f"   Test RMSE:       {row['Test RMSE']:.6f}\n")
                f.write(f"   Test MAE:        {row['Test MAE']:.6f}\n")
                f.write(f"   Overfit Gap:     {row['Train R²'] - row['Test R²']:.6f}\n")
                
                # Performance assessment
                if row['Test R²'] > 0.99:
                    perf = "⭐ EXCELLENT"
                elif row['Test R²'] > 0.95:
                    perf = "✓ VERY GOOD"
                elif row['Test R²'] > 0.90:
                    perf = "○ GOOD"
                else:
                    perf = "△ NEEDS IMPROVEMENT"
                
                f.write(f"   Assessment:      {perf}\n\n")
            
            # Ranking
            f.write("MODELS RANKED BY TEST R²\n")
            f.write("-"*80 + "\n")
            sorted_models = self.results_df.sort_values('Test R²', ascending=False)
            for rank, (model, row) in enumerate(sorted_models.iterrows(), 1):
                f.write(f"{rank}. {model:20s} - R²: {row['Test R²']:.6f}, "
                       f"RMSE: {row['Test RMSE']:.6f}\n")
            
            f.write("\n" + "="*80 + "\n")
            f.write("END OF REPORT\n")
            f.write("="*80 + "\n")
        
        print(f"Saved: {report_path}")
        
        # Print summary to console
        print("\n" + "="*80)
        print("📄 COMPARISON REPORT SUMMARY")
        print("="*80)
        with open(report_path, 'r', encoding='utf-8') as f:
            print(f.read())
    
    def print_metrics_description(self):
        """Print detailed description of metrics and analysis"""
        print("\n" + "="*80)
        print("📊 MÔ TẢ CÁC CHỈ SỐ ĐÁNH GIÁ MODEL")
        print("="*80 + "\n")
        
        print("1. R² SCORE (Coefficient of Determination)")
        print("   " + "─"*70)
        print("   • Ý nghĩa: Đo lường khả năng model giải thích biến thiên của dữ liệu")
        print("   • Khoảng giá trị: -∞ đến 1 (lý tưởng = 1)")
        print("   • Train R²: Hiệu suất trên tập huấn luyện")
        print("   • Test R²: Hiệu suất trên tập kiểm tra (quan trọng nhất)")
        print("   • CV R² Mean: Trung bình R² qua cross-validation")
        print("   • Đánh giá:")
        print("     - R² > 0.99: ⭐ EXCELLENT (Xuất sắc)")
        print("     - R² > 0.95: ✓ VERY GOOD (Rất tốt)")
        print("     - R² > 0.90: ○ GOOD (Tốt)")
        print("     - R² < 0.90: △ NEEDS IMPROVEMENT (Cần cải thiện)")
        print()
        
        print("2. RMSE (Root Mean Squared Error)")
        print("   " + "─"*70)
        print("   • Ý nghĩa: Sai số trung bình bình phương giữa dự đoán và thực tế")
        print("   • Đơn vị: Cùng đơn vị với biến mục tiêu")
        print("   • Đặc điểm: Phạt nặng các sai số lớn hơn MAE")
        print("   • Mục tiêu: Càng nhỏ càng tốt (gần 0)")
        print("   • Ứng dụng: Đánh giá độ chính xác tổng thể, nhạy cảm với outliers")
        print()
        
        print("3. MAE (Mean Absolute Error)")
        print("   " + "─"*70)
        print("   • Ý nghĩa: Sai số tuyệt đối trung bình")
        print("   • Đơn vị: Cùng đơn vị với biến mục tiêu")
        print("   • Đặc điểm: Ít nhạy cảm với outliers hơn RMSE")
        print("   • Mục tiêu: Càng nhỏ càng tốt (gần 0)")
        print("   • Ứng dụng: Đo lường sai số trung bình thực tế")
        print()
        
        print("4. CV R² Std (Cross-Validation Standard Deviation)")
        print("   " + "─"*70)
        print("   • Ý nghĩa: Độ ổn định của model qua các fold cross-validation")
        print("   • Mục tiêu: Càng nhỏ càng tốt")
        print("   • Đánh giá:")
        print("     - Std < 0.001: Rất ổn định")
        print("     - Std < 0.005: Ổn định")
        print("     - Std > 0.005: Không ổn định")
        print("   • Ứng dụng: Đánh giá khả năng tổng quát hóa")
        print()
        
        print("5. OVERFITTING GAP (Train R² - Test R²)")
        print("   " + "─"*70)
        print("   • Ý nghĩa: Mức độ overfitting của model")
        print("   • Đánh giá:")
        print("     - Gap < 0.01: ✓ Không overfitting")
        print("     - Gap 0.01-0.05: ⚠ Overfitting nhẹ")
        print("     - Gap > 0.05: ❌ Overfitting nghiêm trọng")
        print("   • Lưu ý: Gap âm (Test > Train) có thể do regularization mạnh")
        print()
        
        print("6. COMPOSITE SCORE (Điểm Tổng Hợp)")
        print("   " + "─"*70)
        print("   • Công thức: 40% Test R² + 30% RMSE⁻¹ + 20% MAE⁻¹ + 10% CV Stability")
        print("   • Khoảng giá trị: 0 đến 1")
        print("   • Mục đích: Xếp hạng tổng thể các model dựa trên nhiều tiêu chí")
        print("   • Ứng dụng: Chọn model tốt nhất cân bằng accuracy và stability")
        print()
        print("="*80 + "\n")
    
    def print_analysis_summary(self):
        """Print analysis and recommendations based on results"""
        print("\n" + "="*80)
        print("📈 PHÂN TÍCH KẾT QUẢ SO SÁNH")
        print("="*80 + "\n")
        
        # Get sorted models
        sorted_by_r2 = self.results_df.sort_values('Test R²', ascending=False)
        
        print("TOP PERFORMERS:")
        print("─"*80)
        for i, (model, row) in enumerate(sorted_by_r2.head(3).iterrows()):
            print(f"\n• {model}: Test R² = {row['Test R²']:.6f}")
            
            # Characteristics
            if row['Test RMSE'] < 0.01:
                print(f"  - Sai số cực thấp (RMSE={row['Test RMSE']:.6f}, MAE={row['Test MAE']:.6f})")
            else:
                print(f"  - Sai số thấp (RMSE={row['Test RMSE']:.6f}, MAE={row['Test MAE']:.6f})")
            
            if row['CV R² Std'] < 0.001:
                print(f"  - Rất ổn định (CV Std={row['CV R² Std']:.6f})")
            elif row['CV R² Std'] < 0.005:
                print(f"  - Ổn định (CV Std={row['CV R² Std']:.6f})")
            else:
                print(f"  - Độ ổn định trung bình (CV Std={row['CV R² Std']:.6f})")
            
            overfit_gap = row['Train R²'] - row['Test R²']
            if abs(overfit_gap) < 0.01:
                print(f"  - Không có overfitting (Gap={overfit_gap:.6f})")
            elif overfit_gap < 0.05:
                print(f"  - Overfitting nhẹ (Gap={overfit_gap:.6f})")
            else:
                print(f"  - Có dấu hiệu overfitting (Gap={overfit_gap:.6f})")
            
            # Recommendations
            if i == 0:
                print("  → Best choice cho production")
            elif i == 1:
                print("  → Alternative tốt, có thể làm backup model")
            else:
                print("  → Phù hợp cho các trường hợp đặc biệt")
        
        # Medium performers
        if len(sorted_by_r2) > 3:
            print("\n\nMEDIUM PERFORMERS:")
            print("─"*80)
            medium_models = sorted_by_r2.iloc[3:6]
            for model, row in medium_models.iterrows():
                print(f"• {model}: Test R² = {row['Test R²']:.6f}")
            print("  → Phù hợp cho các bài toán chuẩn, có thể cần tuning thêm")
        
        # Poor performers
        if len(sorted_by_r2) > 6:
            print("\n\nPOOR PERFORMERS:")
            print("─"*80)
            poor_models = sorted_by_r2.iloc[6:]
            for model, row in poor_models.iterrows():
                print(f"• {model}: Test R² = {row['Test R²']:.6f}")
            print("  → Không nên sử dụng cho dataset này")
        
        print("\n" + "="*80 + "\n")
        
        # Recommendations
        print("\n" + "="*80)
        print("🎯 KHUYẾN NGHỊ SỬ DỤNG")
        print("="*80 + "\n")
        
        best_model = sorted_by_r2.index[0]
        best_r2 = sorted_by_r2.iloc[0]['Test R²']
        best_rmse = sorted_by_r2.iloc[0]['Test RMSE']
        
        print(f"1. SỬ DỤNG CHO PRODUCTION:")
        print(f"   → {best_model}")
        print(f"   R² = {best_r2:.4f}, RMSE = {best_rmse:.6f}")
        print(f"   Lý do: Accuracy cao nhất, phù hợp cho môi trường production")
        print()
        
        if len(sorted_by_r2) > 1:
            backup_model = sorted_by_r2.index[1]
            backup_r2 = sorted_by_r2.iloc[1]['Test R²']
            backup_rmse = sorted_by_r2.iloc[1]['Test RMSE']
            
            print(f"2. BACKUP MODEL:")
            print(f"   → {backup_model}")
            print(f"   R² = {backup_r2:.4f}, RMSE = {backup_rmse:.6f}")
            print(f"   Lý do: Hiệu suất tuyệt vời, có thể thay thế khi cần")
            print()
        
        if len(sorted_by_r2) > 2:
            third_model = sorted_by_r2.index[2]
            third_r2 = sorted_by_r2.iloc[2]['Test R²']
            
            print(f"3. ALTERNATIVE OPTION:")
            print(f"   → {third_model}")
            print(f"   R² = {third_r2:.4f}")
            print(f"   Lý do: Cân bằng giữa performance và các yếu tố khác")
            print()
        
        # Models to avoid
        worst_models = sorted_by_r2[sorted_by_r2['Test R²'] < 0.9]
        if len(worst_models) > 0:
            print(f"4. TRÁNH SỬ DỤNG:")
            for model in worst_models.index:
                print(f"   → {model}")
            print(f"   Lý do: Hiệu suất không đạt yêu cầu với dataset này")
            print()
        
        print("="*80 + "\n")
    
    def generate_all_visualizations(self):
        """Generate all visualizations"""
        print("\n" + "="*60)
        print("GENERATING ALL VISUALIZATIONS")
        print("="*60 + "\n")
        
        self.load_results()
        
        # Print metrics description first
        self.print_metrics_description()
        
        print("\n[1/13] Generating R² comparison...")
        self.plot_r2_comparison()
        
        print("\n[2/13] Generating error metrics...")
        self.plot_error_metrics()
        
        print("\n[3/13] Generating overfitting analysis...")
        self.plot_overfitting_analysis()
        
        print("\n[4/13] Generating CV stability plot...")
        self.plot_cv_stability()
        
        print("\n[5/13] Generating radar chart...")
        self.plot_radar_chart()
        
        print("\n[6/13] Generating performance heatmap...")
        self.plot_heatmap()
        
        print("\n[7/13] Generating model ranking...")
        ranking = self.plot_ranking()
        
        print("\n[8/13] Generating performance summary...")
        self.plot_performance_summary()
        
        print("\n[9/13] Generating scatter predictions...")
        self.plot_scatter_predictions()
        
        print("\n[10/13] Generating training efficiency analysis...")
        self.plot_training_efficiency()
        
        print("\n[11/13] Generating metrics distribution...")
        self.plot_metrics_distribution()
        
        print("\n[12/13] Generating Pareto chart...")
        self.plot_pareto_chart()
        
        print("\n[13/13] Generating performance quadrant...")
        self.plot_performance_quadrant()
        
        print("\n[BONUS] Generating comparison report...")
        self.generate_comparison_report()
        
        print("\n" + "="*60)
        print("ALL VISUALIZATIONS COMPLETED!")
        print(f"Output directory: {self.output_dir}/")
        print("="*60 + "\n")
        
        print("\n📊 MODEL RANKING:")
        print("="*60)
        print(ranking.to_string())
        print("="*60 + "\n")
        
        # Best model summary
        best_model = self.results_df['Test R²'].idxmax()
        best_r2 = self.results_df.loc[best_model, 'Test R²']
        best_rmse = self.results_df.loc[best_model, 'Test RMSE']
        best_mae = self.results_df.loc[best_model, 'Test MAE']
        
        print("\n🏆 BEST MODEL:")
        print(f"   Model: {best_model}")
        print(f"   Test R²: {best_r2:.6f}")
        print(f"   Test RMSE: {best_rmse:.6f}")
        print(f"   Test MAE: {best_mae:.6f}")
        print("="*60 + "\n")
        
        # Print detailed analysis
        self.print_analysis_summary()


def main():
    """Main execution function"""
    # Initialize comparator
    comparator = ModelComparator('model_comparison_results.csv')
    
    # Generate all visualizations
    comparator.generate_all_visualizations()
    
    print("\n✅ All visualizations have been saved successfully!")
    print(f"📁 Check the '{comparator.output_dir}' folder for all charts.\n")


if __name__ == "__main__":
    main()
