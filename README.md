# Coffee Shop Management System

Hệ thống quản lý quán cà phê với tính năng AI dự báo doanh thu.

## Yêu cầu

- Python 3.8+
- MySQL 8.0+

## Cài đặt

1. **Clone repository**
```bash
git clone https://github.com/hoquangvinh124/Final-Project-ML.git
cd Final-Project-ML
```

2. **Tạo môi trường ảo và cài đặt thư viện**
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

3. **Thiết lập cơ sở dữ liệu**
- Import file `database/coffee-shop.sql` vào MySQL

4. **Cấu hình kết nối database**
Mở file `utils/config.py` và cập nhật thông tin:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password',  # Đổi mật khẩu của bạn
    'database': 'coffee_shop',
    'port': 3306
}
```

5. **Cấu hình API Key cho tính năng AI Chat**
- Tải file `api-key` từ Google Drive: [https://drive.google.com/drive/u/0/folders/16UOV6-p3NpStQkjXnVqBDE98ZC02jRae]
- Copy nội dung file và dán vào `utils/config.py`:
```python
OPENAI_API_KEY = "your-api-key-here"  # Dán API key vào đây
```

## Chạy ứng dụng

**Giao diện khách hàng:**
```bash
python customer.py
```

**Giao diện admin:**
```bash
python admin.py
```

## Tài khoản mặc định

**Admin:**
- Email: `admin@coffeeshop.com`
- Password: `admin`

**Customer:**
- Email: `test@example.com`
- Password: `Test12345`

## Tính năng chính

- Quản lý sản phẩm, danh mục, đơn hàng
- Giỏ hàng và thanh toán
- Dự báo doanh thu bằng AI (Prophet)
- Dashboard phân tích với AI chat

## Cấu trúc project

```
Final-Project-ML/
├── admin.py              # Chạy giao diện admin
├── customer.py           # Chạy giao diện khách hàng
├── controllers/          # Xử lý logic nghiệp vụ
├── models/               # Models dữ liệu
├── views/                # Giao diện PyQt6
├── database/             # File SQL
├── revenue_forecasting/  # Module dự báo AI
├── utils/                # Config và utilities
└── requirements.txt      # Thư viện cần thiết
```
