# 📋 Logs Directory

Thư mục này lưu trữ tất cả log files của hệ thống Logistics KPI Prediction.

---

## 📁 Log Files

### **api.log**

- **Nguồn:** FastAPI server (app.py)
- **Nội dung:**
  - API requests/responses
  - Prediction logs
  - Error traces
  - Performance metrics

### **dashboard.log**

- **Nguồn:** Streamlit dashboard (dashboard.py)
- **Nội dung:**
  - Dashboard sessions
  - User interactions
  - Widget events
  - Errors

### **../monitoring_logs.log** (root level)

- **Nguồn:** Monitoring system (monitoring.py)
- **Nội dung:**
  - System health checks
  - Data drift detection
  - Performance monitoring
  - Alerts

### **../predictions_history.csv** (root level)

- **Nguồn:** Prediction logger
- **Format:** CSV
- **Columns:** timestamp, item_id, category, predicted_kpi, confidence, response_time, model_version

---

## 🔍 Xem Logs

```bash
# Windows:
type logs\api.log
type logs\dashboard.log

# Xem 50 dòng cuối
powershell Get-Content logs\api.log -Tail 50

# Xem real-time
powershell Get-Content logs\api.log -Wait -Tail 10
```

---

## 🧹 Log Rotation

Logs có thể tăng kích thước theo thời gian. Khuyến nghị:

### **Manual rotation:**

```bash
# Backup logs cũ
mkdir logs\archive\%date:~-4,4%%date:~-10,2%%date:~-7,2%
move logs\*.log logs\archive\%date:~-4,4%%date:~-10,2%%date:~-7,2%\
```

### **Auto rotation (tương lai):**

- Cấu hình trong monitoring.py
- Rotate hàng tuần/tháng
- Keep 30 days only

---

## 📊 Log Levels

Logs sử dụng Python logging levels:

- `DEBUG`: Chi tiết debug
- `INFO`: Thông tin chung
- `WARNING`: Cảnh báo
- `ERROR`: Lỗi
- `CRITICAL`: Lỗi nghiêm trọng

---

**💡 Tip:** Kiểm tra logs khi có vấn đề!
