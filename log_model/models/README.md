# ⚠️ KPI Prediction Model - Hướng dẫn Setup

## Vấn đề hiện tại

Tính năng **KPI Prediction** trong Admin Panel hiện chưa sẵn sàng vì **model chưa được train**.

## Giải pháp

### Cách 1: Train Model Mới (Khuyến nghị)

1. **Chuẩn bị dữ liệu:**

   ```bash
   cd log_model
   ```

2. **Kiểm tra dữ liệu training:**

   - Đảm bảo có file CSV data trong `log_model/data/`
   - Hoặc sử dụng data mẫu từ `log_model/notebooks/`

3. **Train model:**

   ```bash
   python src/ml/train_model.py
   ```

4. **Model sẽ được lưu tự động vào:**

   ```
   log_model/models/
   ├── Ridge_Regression_YYYYMMDD_HHMMSS.pkl
   ├── scaler_YYYYMMDD_HHMMSS.pkl
   └── encoders_YYYYMMDD_HHMMSS.pkl
   ```

5. **Khởi động lại Admin Panel**

### Cách 2: Sử dụng Pre-trained Model

Nếu bạn đã có model đã train sẵn:

1. Copy các file model vào thư mục:

   ```
   log_model/models/
   ```

2. Đảm bảo có đủ 3 file:

   - `Ridge_Regression_*.pkl` (model)
   - `scaler_*.pkl` (scaler)
   - `encoders_*.pkl` (encoders)

3. Khởi động lại Admin Panel

## Kiểm tra sau khi setup

1. Khởi động Admin Panel:

   ```bash
   python admin.py
   ```

2. Vào tab **KPI Prediction**

3. Nếu thành công, bạn sẽ thấy nút **"🔮 Dự đoán KPI"** có thể click

4. Nếu vẫn lỗi, check:
   - Thư mục `log_model/models/` có tồn tại không
   - Có đủ 3 file pkl không
   - Tên file có đúng format không

## Thông tin thêm

- **Model type:** Ridge Regression
- **Accuracy:** 99.99% (theo documentation)
- **Features:** 40+ engineered features
- **Input:** 22 thông tin về sản phẩm/logistics

## Hỗ trợ

Nếu gặp vấn đề, check log tại:

```
log_model/logs/
```

Hoặc xem chi tiết trong:

- `log_model/README.md`
- `log_model/QUICK_START.md`
