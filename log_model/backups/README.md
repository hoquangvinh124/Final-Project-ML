# Backups Directory

Thư mục này dùng để lưu trữ backups của models và data quan trọng.

---

## Nên Backup

### **Models (Ưu tiên cao)**

```bash
# Backup models hiện tại
xcopy /E /I models backups\models_%date:~-4,4%%date:~-10,2%%date:~-7,2%
```

Files cần backup:

- `Ridge_Regression_*.pkl` - Model chính
- `scaler_*.pkl` - Feature scaler
- `encoders_*.pkl` - Categorical encoders

### **Data**

```bash
# Backup dataset
copy data\logistics_dataset.csv backups\
```

### **Predictions History**

```bash
# Backup predictions
copy predictions_history.csv backups\predictions_history_%date%.csv
```

### **Performance Metrics**

```bash
# Backup metrics
copy performance_metrics.json backups\
```

---

## Backup Strategy

### **Hàng ngày (nếu production):**

- Predictions history
- Performance metrics

### **Hàng tuần:**

- Models (nếu retrain)
- Monitoring logs

### **Hàng tháng:**

- Full dataset
- All logs
- Configurations

---

## Backup Naming Convention

```
models_YYYYMMDD/
├── Ridge_Regression_YYYYMMDD_HHMMSS.pkl
├── scaler_YYYYMMDD_HHMMSS.pkl
└── encoders_YYYYMMDD_HHMMSS.pkl

predictions_history_YYYYMMDD.csv
performance_metrics_YYYYMMDD.json
```

---

## 🔙 Restore from Backup

```bash
# Restore models
xcopy /E /Y backups\models_YYYYMMDD\* models\

# Verify
python -c "import joblib; m = joblib.load('models/Ridge_Regression_*.pkl'); print('Model OK')"
```

---

**💡 Luôn backup trước khi retrain model!**
