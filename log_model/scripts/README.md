# 📁 Scripts Directory

Thư mục này chứa các scripts quản lý dự án Logistics KPI Prediction.

---

## 📜 Danh sách Scripts

### 1. **startup.bat** 🚀

**Chức năng:** Khởi động toàn bộ hệ thống (API + Dashboard)

**Cách dùng:**

```bash
# Double-click hoặc:
scripts\startup.bat
```

**Thực hiện:**

- ✅ Kiểm tra Python installation
- ✅ Kích hoạt virtual environment (tự tạo nếu chưa có)
- ✅ Kiểm tra model files
- ✅ Khởi động API Server (port 8000)
- ✅ Khởi động Dashboard (port 8501)
- ✅ Tự động mở browser

**Kết quả:**

- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Dashboard: http://localhost:8501

---

### 2. **shutdown.bat** 🛑

**Chức năng:** Dừng tất cả services đang chạy

**Cách dùng:**

```bash
scripts\shutdown.bat
```

**Thực hiện:**

- ✅ Dừng API Server (3 methods: window title, PID, port)
- ✅ Dừng Dashboard
- ✅ Xóa PID files
- ✅ Verify ports đã được giải phóng

---

### 3. **status.bat** 📊

**Chức năng:** Kiểm tra trạng thái hệ thống

**Cách dùng:**

```bash
scripts\status.bat
```

**Hiển thị:**

- ✅ API Server status (running/stopped)
- ✅ Dashboard status
- ✅ Process IDs và memory usage
- ✅ Health check results
- ✅ Model files status
- ✅ Log files size
- ✅ Virtual environment status

---

### 4. **restart.bat** 🔄

**Chức năng:** Restart toàn bộ hệ thống

**Cách dùng:**

```bash
scripts\restart.bat
```

**Thực hiện:**

1. Chạy shutdown.bat
2. Đợi 3 giây
3. Chạy startup.bat

---

## 📂 Cấu trúc Project sau khi chạy

```
log_model/
│
├── scripts/               # ← Thư mục này (quản lý scripts)
│   ├── startup.bat       # Khởi động
│   ├── shutdown.bat      # Dừng
│   ├── status.bat        # Kiểm tra
│   ├── restart.bat       # Khởi động lại
│   └── README.md         # File này
│
├── logs/                 # ← Logs của services
│   ├── api.log          # API server logs
│   └── dashboard.log    # Dashboard logs
│
├── models/              # Model artifacts
│   ├── Ridge_Regression_*.pkl
│   ├── scaler_*.pkl
│   └── encoders_*.pkl
│
├── backups/             # Backups (tương lai)
│
├── data/                # Datasets
├── doc/                 # Documentation
├── venv/                # Virtual environment
│
├── app.py               # API server
├── dashboard.py         # Streamlit dashboard
├── monitoring.py        # Monitoring system
├── predict.py           # Prediction functions
├── train_model.py       # Training script
├── test_model.py        # Unit tests
└── requirements.txt     # Dependencies
```

---

## 🎯 Quick Commands

```bash
# Khởi động dự án
scripts\startup.bat

# Kiểm tra trạng thái
scripts\status.bat

# Khởi động lại
scripts\restart.bat

# Dừng dự án
scripts\shutdown.bat
```

---

## 💡 Tips

1. **Lần đầu chạy:** Script sẽ tự động tạo venv và cài dependencies
2. **Logs:** Xem logs tại `logs\api.log` và `logs\dashboard.log`
3. **Minimized:** Windows được minimize để không che màn hình
4. **Browser:** Tự động mở http://localhost:8000/docs và http://localhost:8501
5. **PID tracking:** Scripts tự động track process IDs để shutdown chính xác

---

## 🆘 Troubleshooting

### Port đã được sử dụng

```bash
# Chạy shutdown.bat trước
scripts\shutdown.bat

# Hoặc kill manual
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Lỗi virtual environment

```bash
# Xóa venv cũ
rmdir /s /q venv

# Chạy lại startup (sẽ tự tạo mới)
scripts\startup.bat
```

### Model files not found

```bash
# Train model
python train_model.py

# Verify
dir models\
```

---

## 📝 Ghi chú

- Scripts được tối ưu cho **Windows PowerShell/CMD**
- Tương thích với Python 3.8+
- Yêu cầu có model files trained trước
- Log rotation: Xem logs\ để troubleshoot

---

**🎉 Hãy sử dụng `startup.bat` để bắt đầu làm việc!**
