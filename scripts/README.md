# 🛠️ Scripts - Coffee Shop Database Tools

Bộ công cụ scripts để quản lý database, hỗ trợ tự động chuyển đổi ảnh sang base64.

---

## 📦 **Cài Đặt**

```bash
# Cài đặt dependencies
pip install -r requirements.txt

# Hoặc cài riêng openpyxl cho Excel import
pip install openpyxl
```

---

## 📦 **Danh Sách Scripts**

### 1️⃣ **add_category.py** - Thêm Danh Mục
Thêm danh mục mới với ảnh base64 một cách tương tác.

**Cách dùng:**
```bash
python scripts/add_category.py
```

**Tính năng:**
- ✅ Nhập thông tin danh mục tương tác
- ✅ Tự động chuyển ảnh sang base64
- ✅ Hỗ trợ emoji icon làm placeholder
- ✅ Validate dữ liệu đầu vào

**Ví dụ:**
```bash
$ python scripts/add_category.py

📂 THÊM DANH MỤC MỚI VÀO DATABASE
================================================================

📝 THÔNG TIN DANH MỤC:
--------------------------------------------------
Tên danh mục (Tiếng Việt): Cà Phê
Tên danh mục (English) [Cà Phê]: Coffee
Mô tả danh mục: Các loại cà phê truyền thống

🎨 ICON:
--------------------------------------------------
Icon (emoji) [☕]: ☕

🖼️  HÌNH ẢNH:
--------------------------------------------------
Đường dẫn đến file ảnh (để trống nếu chỉ dùng icon): images/coffee.jpg
🔄 Đang chuyển đổi ảnh sang base64...
✅ Chuyển đổi thành công! (Kích thước: 45.32 KB)

✅ THÀNH CÔNG! Đã thêm danh mục ID: 1
```

---

### 2️⃣ **add_product.py** - Thêm Sản Phẩm
Thêm sản phẩm mới với ảnh base64 một cách tương tác.

**Cách dùng:**
```bash
python scripts/add_product.py
```

**Tính năng:**
- ✅ Hiển thị danh sách categories có sẵn
- ✅ Nhập đầy đủ thông tin sản phẩm
- ✅ Tự động chuyển ảnh sang base64
- ✅ Hỗ trợ calories, attributes (hot/cold/featured/...)
- ✅ Confirm trước khi insert

**Ví dụ:**
```bash
$ python scripts/add_product.py

🍵 THÊM SẢN PHẨM MỚI VÀO DATABASE
================================================================

📂 DANH MỤC CÓ SẴN:
--------------------------------------------------
  [1] ☕ Cà Phê (Coffee)
  [2] 🧋 Trà (Tea)
  [3] 🍰 Bánh Ngọt (Pastries)
--------------------------------------------------

📝 THÔNG TIN SẢN PHẨM:
--------------------------------------------------
Chọn ID danh mục: 1
Tên sản phẩm (Tiếng Việt): Phin Cà Phê Sữa Đá
Tên sản phẩm (English) [Phin Cà Phê Sữa Đá]: Iced Milk Coffee
Mô tả sản phẩm: Cà phê phin truyền thống với sữa đặc
Giá cơ bản (VND) [45000]: 45000

🖼️  HÌNH ẢNH SẢN PHẨM:
--------------------------------------------------
Đường dẫn đến file ảnh: images/iced_coffee.jpg
✅ Chuyển đổi thành công! (Kích thước: 52.18 KB)

✅ THÀNH CÔNG! Đã thêm sản phẩm ID: 1
```

---

### 3️⃣ **bulk_import_products_excel.py** - Import Hàng Loạt từ Excel ⭐ KHUYẾN NGHỊ
Import nhiều sản phẩm cùng lúc từ file Excel (.xlsx) - **Không bị lỗi UTF-8!**

**Cách dùng:**
```bash
# Tạo file Excel template
python scripts/create_excel_template.py

# Import từ Excel
python scripts/bulk_import_products_excel.py products_template.xlsx
```

**Tính năng:**
- ✅ **Hỗ trợ tiếng Việt hoàn hảo** (không lỗi UTF-8)
- ✅ Import nhiều sản phẩm cùng lúc
- ✅ Tự động convert ảnh sang base64
- ✅ Hỗ trợ relative path cho ảnh
- ✅ File template có 16 sản phẩm mẫu + sheet Hướng Dẫn
- ✅ Báo cáo chi tiết: thành công/lỗi

**Ví dụ:**
```bash
$ python scripts/create_excel_template.py
✅ Đã tạo file Excel template: products_template.xlsx
   - Sheet 'Products': 16 sản phẩm mẫu
   - Sheet 'Hướng Dẫn': Hướng dẫn sử dụng

$ python scripts/bulk_import_products_excel.py products_template.xlsx
📂 Đang đọc file: products_template.xlsx
================================================================

[1] Phin Cà Phê Sữa Đá... ✅ (ID: 1)
[2] Bạc Xỉu... ✅ (ID: 2)
[3] Americano... ✅ (ID: 3)
...

📊 KẾT QUẢ:
   Tổng số: 16
   ✅ Thành công: 16
   ❌ Lỗi: 0
```

---

### 4️⃣ **bulk_import_products.py** - Import Hàng Loạt từ CSV
Import nhiều sản phẩm cùng lúc từ file CSV với ảnh base64.

**Cách dùng:**
```bash
python scripts/bulk_import_products.py products.csv
```

**Tạo file CSV mẫu:**
```bash
python scripts/bulk_import_products.py
# Chọn Y để tạo products_sample.csv
```

**Format CSV:**

| Cột | Bắt buộc | Mô tả |
|-----|----------|-------|
| `name` | ✅ | Tên sản phẩm (Tiếng Việt) |
| `category_id` | ✅ | ID danh mục |
| `base_price` | ✅ | Giá cơ bản (VND) |
| `name_en` | ❌ | Tên tiếng Anh |
| `description` | ❌ | Mô tả sản phẩm |
| `ingredients` | ❌ | Thành phần |
| `image_path` | ❌ | Đường dẫn file ảnh |
| `calories_small` | ❌ | Calories size S |
| `calories_medium` | ❌ | Calories size M |
| `calories_large` | ❌ | Calories size L |
| `is_hot` | ❌ | true/false |
| `is_cold` | ❌ | true/false |
| `is_available` | ❌ | true/false |
| `is_featured` | ❌ | true/false |
| `is_new` | ❌ | true/false |
| `is_bestseller` | ❌ | true/false |
| `is_seasonal` | ❌ | true/false |

**Ví dụ CSV:**
```csv
name,name_en,category_id,description,base_price,image_path,is_hot,is_cold,is_available
Cà Phê Đen,Black Coffee,1,Cà phê đen truyền thống,35000,images/black_coffee.jpg,true,true,true
Cappuccino,Cappuccino,1,Espresso với sữa tươi,55000,images/cappuccino.jpg,true,true,true
Trà Sữa,Milk Tea,2,Trà sữa trân châu,50000,images/milk_tea.jpg,false,true,true
```

**Ví dụ chạy:**
```bash
$ python scripts/bulk_import_products.py products.csv

📂 Đang đọc file: products.csv
================================================================

[1] Cà Phê Đen... ✅ (ID: 1)
[2] Cappuccino... ✅ (ID: 2)
[3] Trà Sữa... ✅ (ID: 3)

================================================================
📊 KẾT QUẢ:
   Tổng số: 3
   ✅ Thành công: 3
   ❌ Lỗi: 0
================================================================
```

---

## 🖼️ **Xử Lý Ảnh**

### Định dạng hỗ trợ:
- ✅ JPG/JPEG
- ✅ PNG
- ✅ GIF
- ✅ WebP
- ✅ SVG

### Cách thức hoạt động:
1. Script đọc file ảnh dưới dạng binary
2. Convert sang base64 string
3. Thêm data URI prefix (ví dụ: `data:image/jpeg;base64,`)
4. Lưu vào database dưới dạng TEXT

### Ví dụ kết quả:
```
data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJ...
```

---

## 🔧 **Yêu Cầu Hệ Thống**

### Python packages:
- `mysql-connector-python` hoặc `pymysql`
- Các dependencies từ `requirements.txt`

### Database:
- MySQL 5.7+ hoặc MariaDB 10.0+
- Database `coffee_shop` đã được tạo
- Schema v2.0 đã được apply

---

## 💡 **Lưu Ý**

### Đường dẫn ảnh:
- **Absolute path**: `/home/user/images/coffee.jpg`
- **Relative path** (trong bulk import): `images/coffee.jpg` (tương đối với file CSV)
- **Relative path** (interactive): Tương đối với thư mục hiện tại

### Kích thước ảnh:
- ⚠️ Base64 tăng kích thước ảnh ~33%
- 💡 Nên optimize ảnh trước khi import
- 💡 Khuyến nghị: < 200KB/ảnh

### Performance:
- Bulk import nhanh hơn nhiều so với thêm từng sản phẩm
- Với 100+ sản phẩm, nên dùng `bulk_import_products.py`

---

---

## 📊 **So Sánh CSV vs Excel**

| Tính năng | CSV | Excel (.xlsx) |
|-----------|-----|---------------|
| **Tiếng Việt** | ⚠️ Có thể lỗi UTF-8 | ✅ Hoàn hảo |
| **Dễ chỉnh sửa** | ❌ Cần text editor | ✅ Excel/LibreOffice |
| **Template** | ✅ Có | ✅ Có (với hướng dẫn) |
| **Tốc độ** | ✅ Nhanh hơn | ⚠️ Hơi chậm |
| **Khuyến nghị** | ❌ | ✅ **KHUYẾN NGHỊ** |

**💡 Nên dùng Excel để tránh lỗi UTF-8 với tiếng Việt!**

---

## 🚀 **Quick Start**

### 1. Thêm danh mục:
```bash
python scripts/add_category.py
```

### 2. Thêm vài sản phẩm thủ công:
```bash
python scripts/add_product.py
```

### 3. Bulk import từ Excel (KHUYẾN NGHỊ):
```bash
# Tạo Excel template
python scripts/create_excel_template.py

# Mở và chỉnh sửa products_template.xlsx bằng Excel
# Thêm ảnh vào folder images/ nếu cần

# Import
python scripts/bulk_import_products_excel.py products_template.xlsx
```

### 4. Hoặc bulk import từ CSV:
```bash
# Tạo CSV mẫu
python scripts/bulk_import_products.py

# Chỉnh sửa products_sample.csv
nano products_sample.csv

# Import
python scripts/bulk_import_products.py products_sample.csv
```

---

## 🐛 **Troubleshooting**

### Lỗi "Module not found":
```bash
# Đảm bảo đang ở thư mục root của project
cd /path/to/Coffee-shop
python scripts/add_product.py
```

### Lỗi "Database connection":
```bash
# Kiểm tra config database trong utils/config.py
# Đảm bảo MySQL đang chạy
sudo systemctl status mysql
```

### Lỗi "File not found" khi import ảnh:
```bash
# Kiểm tra đường dẫn ảnh
ls -la images/

# Hoặc dùng absolute path
python scripts/add_product.py
# Nhập: /home/user/Coffee-shop/images/coffee.jpg
```

---

## 📞 **Hỗ Trợ**

Nếu gặp vấn đề, hãy kiểm tra:
1. ✅ Python version >= 3.6
2. ✅ Database schema v2.0 đã được apply
3. ✅ File ảnh tồn tại và có quyền đọc
4. ✅ MySQL connection config đúng

Happy coding! ☕
