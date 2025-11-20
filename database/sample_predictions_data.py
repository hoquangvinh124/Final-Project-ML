"""
Sample data generator for predictions table
Creates realistic prediction data for testing AI Agent
"""
from datetime import datetime, timedelta
import random
from utils.database import DatabaseManager

def generate_sample_predictions(num_days: int = 30, num_stores: int = 5):
    """
    Generate sample prediction data

    Args:
        num_days: Number of days to generate predictions for
        num_stores: Number of stores to generate data for
    """
    db = DatabaseManager()

    # Clear existing predictions (optional)
    print("Xóa dữ liệu cũ...")
    db.execute_query("DELETE FROM prediction_components")
    db.execute_query("DELETE FROM predictions")

    print(f"Tạo dữ liệu mẫu cho {num_stores} cửa hàng, {num_days} ngày...")

    # Base revenue for each store (VND)
    store_base_revenue = {
        1: 15000000,  # 15M VND/day
        2: 12000000,  # 12M VND/day
        3: 18000000,  # 18M VND/day
        4: 10000000,  # 10M VND/day
        5: 14000000,  # 14M VND/day
    }

    # Weekday multipliers (Monday=0, Sunday=6)
    weekday_multipliers = {
        0: 0.8,   # Monday - Thứ 2 thường ít khách
        1: 0.85,  # Tuesday
        2: 0.9,   # Wednesday
        3: 0.95,  # Thursday
        4: 1.1,   # Friday - Cuối tuần bắt đầu đông
        5: 1.3,   # Saturday - Cuối tuần đông nhất
        6: 1.25,  # Sunday - Chủ nhật đông
    }

    predictions_data = []
    components_data = []

    start_date = datetime.now().date()

    for store_id in range(1, num_stores + 1):
        base_revenue = store_base_revenue.get(store_id, 12000000)

        for day_offset in range(-15, num_days):  # Include some past data
            prediction_date = start_date + timedelta(days=day_offset)
            weekday = prediction_date.weekday()

            # Calculate predicted revenue with variations
            weekday_factor = weekday_multipliers.get(weekday, 1.0)

            # Add some randomness
            random_factor = random.uniform(0.9, 1.1)

            # Add trend (slight growth over time)
            trend_factor = 1 + (day_offset * 0.001)

            # Calculate final revenue
            predicted_revenue = base_revenue * weekday_factor * random_factor * trend_factor

            # Confidence score (higher for recent predictions)
            if day_offset < 0:  # Past data
                confidence_score = random.uniform(0.85, 0.95)
            elif day_offset <= 7:  # Near future
                confidence_score = random.uniform(0.75, 0.90)
            else:  # Far future
                confidence_score = random.uniform(0.60, 0.80)

            predictions_data.append((
                store_id,
                prediction_date,
                round(predicted_revenue, 2),
                round(confidence_score, 4),
                'daily',
                'prophet'
            ))

            # Generate prediction components
            trend = predicted_revenue * 0.6
            weekly_seasonality = predicted_revenue * (weekday_factor - 1) * 0.5
            yearly_seasonality = predicted_revenue * 0.1 * random.uniform(-0.5, 0.5)
            holidays = 0 if weekday < 5 else predicted_revenue * 0.1

            yhat_lower = predicted_revenue * 0.85
            yhat_upper = predicted_revenue * 1.15

            # Will be inserted after predictions
            components_data.append({
                'trend': round(trend, 2),
                'weekly_seasonality': round(weekly_seasonality, 2),
                'yearly_seasonality': round(yearly_seasonality, 2),
                'holidays': round(holidays, 2),
                'yhat_lower': round(yhat_lower, 2),
                'yhat_upper': round(yhat_upper, 2)
            })

    # Insert predictions
    insert_prediction_query = """
        INSERT INTO predictions
        (store_id, prediction_date, predicted_revenue, confidence_score, prediction_type, model_name)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    print(f"Đang insert {len(predictions_data)} predictions...")
    db.execute_many(insert_prediction_query, predictions_data)

    # Get all prediction IDs
    prediction_ids = db.fetch_all(
        "SELECT id FROM predictions ORDER BY id ASC"
    )

    # Insert prediction components
    insert_component_query = """
        INSERT INTO prediction_components
        (prediction_id, trend, weekly_seasonality, yearly_seasonality, holidays, yhat_lower, yhat_upper)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    components_tuples = [
        (
            prediction_ids[i]['id'],
            components_data[i]['trend'],
            components_data[i]['weekly_seasonality'],
            components_data[i]['yearly_seasonality'],
            components_data[i]['holidays'],
            components_data[i]['yhat_lower'],
            components_data[i]['yhat_upper']
        )
        for i in range(len(components_data))
    ]

    print(f"Đang insert {len(components_tuples)} components...")
    db.execute_many(insert_component_query, components_tuples)

    print("✓ Hoàn thành!")

    # Show summary
    total_predictions = db.fetch_one("SELECT COUNT(*) as total FROM predictions")
    print(f"\nTổng số predictions: {total_predictions['total']}")

    # Show sample data
    print("\nSample data (5 dòng đầu):")
    sample = db.fetch_all("""
        SELECT p.store_id, p.prediction_date, p.predicted_revenue,
               p.confidence_score, p.model_name
        FROM predictions p
        ORDER BY p.prediction_date DESC
        LIMIT 5
    """)

    for row in sample:
        print(f"  Store {row['store_id']}: {row['prediction_date']} - "
              f"{row['predicted_revenue']:,.0f} VNĐ (confidence: {row['confidence_score']:.2%})")


def generate_sample_insights():
    """Generate sample insights"""
    db = DatabaseManager()

    print("\nTạo sample insights...")

    # Clear old insights
    db.execute_query("DELETE FROM ai_insights")

    insights_data = [
        (
            'revenue_alert',
            1,
            'Doanh thu dự đoán cao vào cuối tuần',
            'Doanh thu cuối tuần này dự đoán tăng 30% so với ngày thường. '
            'Đề xuất tăng số lượng nhân viên và chuẩn bị đủ nguyên liệu.',
            'info',
            None,
            '{"percentage_increase": 30, "days": ["Saturday", "Sunday"]}'
        ),
        (
            'trend_change',
            2,
            'Xu hướng giảm tại cửa hàng 2',
            'Cửa hàng 2 có xu hướng giảm doanh thu trong 7 ngày qua. '
            'Cần kiểm tra chất lượng phục vụ và sản phẩm.',
            'warning',
            None,
            '{"trend": "decreasing", "percentage": -5.2}'
        ),
        (
            'recommendation',
            3,
            'Cửa hàng 3 hoạt động tốt nhất',
            'Cửa hàng 3 có doanh thu cao nhất và ổn định. '
            'Đề xuất áp dụng mô hình này cho các cửa hàng khác.',
            'info',
            None,
            '{"performance_score": 95, "ranking": 1}'
        ),
        (
            'revenue_alert',
            None,
            'Thứ 2 là ngày ít khách nhất',
            'Dữ liệu cho thấy thứ 2 thường có doanh thu thấp nhất trong tuần. '
            'Đề xuất chạy chương trình khuyến mãi vào thứ 2 để tăng khách.',
            'info',
            None,
            '{"weekday": "Monday", "avg_revenue_decrease": 20}'
        )
    ]

    insert_query = """
        INSERT INTO ai_insights
        (insight_type, store_id, title, description, severity, related_prediction_id, metadata)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    db.execute_many(insert_query, insights_data)

    print(f"✓ Đã tạo {len(insights_data)} insights")


if __name__ == "__main__":
    print("=" * 60)
    print("SAMPLE DATA GENERATOR FOR AI AGENT")
    print("=" * 60)

    try:
        # Generate predictions
        generate_sample_predictions(num_days=30, num_stores=5)

        # Generate insights
        generate_sample_insights()

        print("\n" + "=" * 60)
        print("✓ HOÀN THÀNH! Bạn có thể test AI Agent ngay bây giờ.")
        print("=" * 60)

        print("\nCâu hỏi mẫu để test:")
        print("  1. Doanh thu tuần tới dự đoán bao nhiêu?")
        print("  2. Cửa hàng nào có doanh thu cao nhất?")
        print("  3. So sánh doanh thu các cửa hàng")
        print("  4. Phân tích xu hướng 7 ngày qua")

    except Exception as e:
        print(f"\n✗ LỖI: {str(e)}")
        import traceback
        traceback.print_exc()
