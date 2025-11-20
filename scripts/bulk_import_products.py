#!/usr/bin/env python3
"""
Script to bulk import products from CSV with automatic base64 image conversion
CSV Format: name,name_en,category_id,description,base_price,image_path,is_hot,is_cold,is_available

Usage: python scripts/bulk_import_products.py products.csv
"""
import sys
import os
import csv
import base64
from pathlib import Path

# Add parent directory to path to import models
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.database import db


def image_to_base64(image_path: str) -> str:
    """Convert image file to base64 string"""
    if not image_path or not os.path.exists(image_path):
        return None

    try:
        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()
            base64_string = base64.b64encode(image_data).decode('utf-8')

            # Get file extension to add proper data URI prefix
            ext = Path(image_path).suffix.lower()
            mime_types = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp',
                '.svg': 'image/svg+xml'
            }

            mime_type = mime_types.get(ext, 'image/jpeg')
            return f"data:{mime_type};base64,{base64_string}"
    except Exception as e:
        print(f"  ⚠️  Lỗi đọc ảnh '{image_path}': {e}")
        return None


def str_to_bool(value):
    """Convert string to boolean"""
    if isinstance(value, bool):
        return value
    return str(value).lower() in ['true', '1', 'yes', 'có', 'y']


def import_products_from_csv(csv_path: str):
    """Import products from CSV file"""
    if not os.path.exists(csv_path):
        print(f"❌ File không tồn tại: {csv_path}")
        return False

    print(f"\n📂 Đang đọc file: {csv_path}")
    print("="*60)

    success_count = 0
    error_count = 0
    total_count = 0

    try:
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            # Validate headers
            required_headers = ['name', 'category_id', 'base_price']
            if not all(h in reader.fieldnames for h in required_headers):
                print(f"❌ CSV thiếu các cột bắt buộc: {', '.join(required_headers)}")
                print(f"   Các cột hiện có: {', '.join(reader.fieldnames)}")
                return False

            for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                total_count += 1
                name = row['name'].strip()

                print(f"\n[{total_count}] {name}...", end=" ")

                try:
                    # Extract data from CSV
                    category_id = int(row['category_id'])
                    name_en = row.get('name_en', name).strip()
                    description = row.get('description', '').strip()
                    ingredients = row.get('ingredients', '').strip()
                    base_price = float(row['base_price'])

                    # Image conversion
                    image_path = row.get('image_path', '').strip()
                    image_base64 = None
                    if image_path:
                        # If relative path, make it relative to CSV file location
                        if not os.path.isabs(image_path):
                            csv_dir = os.path.dirname(os.path.abspath(csv_path))
                            image_path = os.path.join(csv_dir, image_path)

                        image_base64 = image_to_base64(image_path)

                    # Calories
                    calories_small = int(row.get('calories_small', 0) or 0)
                    calories_medium = int(row.get('calories_medium', 0) or 0)
                    calories_large = int(row.get('calories_large', 0) or 0)

                    # Boolean attributes
                    is_hot = str_to_bool(row.get('is_hot', 'true'))
                    is_cold = str_to_bool(row.get('is_cold', 'true'))
                    is_caffeine_free = str_to_bool(row.get('is_caffeine_free', 'false'))
                    is_available = str_to_bool(row.get('is_available', 'true'))
                    is_featured = str_to_bool(row.get('is_featured', 'false'))
                    is_new = str_to_bool(row.get('is_new', 'false'))
                    is_bestseller = str_to_bool(row.get('is_bestseller', 'false'))
                    is_seasonal = str_to_bool(row.get('is_seasonal', 'false'))

                    # Insert to database
                    query = """
                        INSERT INTO products
                        (category_id, name, name_en, description, ingredients, image,
                         base_price, calories_small, calories_medium, calories_large,
                         is_hot, is_cold, is_caffeine_free, is_available, is_featured,
                         is_new, is_bestseller, is_seasonal, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                    """

                    product_id = db.insert(query, (
                        category_id, name, name_en, description, ingredients, image_base64,
                        base_price, calories_small, calories_medium, calories_large,
                        is_hot, is_cold, is_caffeine_free, is_available, is_featured,
                        is_new, is_bestseller, is_seasonal
                    ))

                    if product_id:
                        print(f"✅ (ID: {product_id})")
                        success_count += 1
                    else:
                        print(f"❌ Lỗi insert")
                        error_count += 1

                except KeyError as e:
                    print(f"❌ Thiếu cột: {e}")
                    error_count += 1
                except ValueError as e:
                    print(f"❌ Giá trị không hợp lệ: {e}")
                    error_count += 1
                except Exception as e:
                    print(f"❌ Lỗi: {e}")
                    error_count += 1

    except Exception as e:
        print(f"\n❌ Lỗi đọc file CSV: {e}")
        return False

    # Summary
    print("\n" + "="*60)
    print("📊 KẾT QUẢ:")
    print(f"   Tổng số: {total_count}")
    print(f"   ✅ Thành công: {success_count}")
    print(f"   ❌ Lỗi: {error_count}")
    print("="*60)

    return error_count == 0


def create_sample_csv():
    """Create a sample CSV file"""
    sample_path = "products_sample.csv"

    sample_data = """name,name_en,category_id,description,base_price,image_path,calories_small,calories_medium,calories_large,is_hot,is_cold,is_available,is_featured,is_new,is_bestseller
Cà Phê Đen Đá,Black Coffee,1,Cà phê đen truyền thống,35000,images/black_coffee.jpg,5,10,15,true,true,true,false,false,false
Cà Phê Sữa,Milk Coffee,1,Cà phê sữa đặc ngọt dịu,40000,images/milk_coffee.jpg,150,200,280,true,true,true,true,false,true
Trà Sữa Trân Châu,Bubble Tea,2,Trà sữa với trân châu đen,55000,images/bubble_tea.jpg,300,380,450,false,true,true,false,true,true"""

    with open(sample_path, 'w', encoding='utf-8') as f:
        f.write(sample_data)

    print(f"✅ Đã tạo file mẫu: {sample_path}")
    return sample_path


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("="*60)
        print("📦 BULK IMPORT SẢN PHẨM TỪ CSV")
        print("="*60)
        print("\n📖 Cách dùng:")
        print(f"   python {sys.argv[0]} <file.csv>")
        print("\n📋 Format CSV (các cột bắt buộc):")
        print("   - name: Tên sản phẩm (Tiếng Việt)")
        print("   - category_id: ID danh mục")
        print("   - base_price: Giá cơ bản (VND)")
        print("\n📋 Format CSV (các cột tùy chọn):")
        print("   - name_en: Tên tiếng Anh")
        print("   - description: Mô tả")
        print("   - ingredients: Thành phần")
        print("   - image_path: Đường dẫn file ảnh")
        print("   - calories_small/medium/large: Calories")
        print("   - is_hot, is_cold, is_available, etc.: true/false")

        print("\n" + "-"*60)
        choice = input("\n💡 Tạo file CSV mẫu? [Y/n]: ").strip().lower()
        if choice in ['', 'y', 'yes', 'có']:
            sample_file = create_sample_csv()
            print(f"\n📝 Bạn có thể chỉnh sửa file '{sample_file}' và chạy lại:")
            print(f"   python {sys.argv[0]} {sample_file}")
        return

    csv_path = sys.argv[1]
    import_products_from_csv(csv_path)


if __name__ == "__main__":
    main()
