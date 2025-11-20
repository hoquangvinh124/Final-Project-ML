#!/usr/bin/env python3
"""
Script to add products with automatic base64 image conversion
Usage: python scripts/add_product.py
"""
import sys
import os
import base64
from pathlib import Path

# Add parent directory to path to import models
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.database import db
from models.product import Category


def image_to_base64(image_path: str) -> str:
    """Convert image file to base64 string"""
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
    except FileNotFoundError:
        print(f"❌ Lỗi: Không tìm thấy file ảnh '{image_path}'")
        return None
    except Exception as e:
        print(f"❌ Lỗi khi đọc ảnh: {e}")
        return None


def get_categories():
    """Get all categories"""
    categories = Category.get_all(active_only=False)
    return categories


def display_categories(categories):
    """Display available categories"""
    print("\n📂 DANH MỤC CÓ SẴN:")
    print("-" * 50)
    for cat in categories:
        icon = cat.get('icon', '☕')
        print(f"  [{cat['id']}] {icon} {cat['name']} ({cat['name_en']})")
    print("-" * 50)


def get_input(prompt, default=None, input_type=str):
    """Get user input with default value"""
    if default is not None:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "

    value = input(prompt).strip()

    if not value and default is not None:
        return default

    if value and input_type != str:
        try:
            return input_type(value)
        except ValueError:
            print(f"❌ Giá trị không hợp lệ! Vui lòng nhập {input_type.__name__}")
            return get_input(prompt, default, input_type)

    return value if value else None


def get_yes_no(prompt, default=True):
    """Get yes/no input"""
    default_str = "Y/n" if default else "y/N"
    value = input(f"{prompt} [{default_str}]: ").strip().lower()

    if not value:
        return default

    return value in ['y', 'yes', 'có', 'c']


def add_product():
    """Interactive function to add a product"""
    print("\n" + "="*60)
    print("🍵 THÊM SẢN PHẨM MỚI VÀO DATABASE")
    print("="*60)

    # Get categories
    categories = get_categories()
    if not categories:
        print("❌ Không tìm thấy danh mục nào! Vui lòng tạo danh mục trước.")
        return False

    display_categories(categories)

    # Get product info
    print("\n📝 THÔNG TIN SẢN PHẨM:")
    print("-" * 50)

    # Category
    category_id = get_input("Chọn ID danh mục", input_type=int)
    if not any(cat['id'] == category_id for cat in categories):
        print("❌ Danh mục không tồn tại!")
        return False

    # Basic info
    name = get_input("Tên sản phẩm (Tiếng Việt)")
    if not name:
        print("❌ Tên sản phẩm không được để trống!")
        return False

    name_en = get_input("Tên sản phẩm (English)", default=name)
    description = get_input("Mô tả sản phẩm")
    ingredients = get_input("Thành phần")

    # Price
    base_price = get_input("Giá cơ bản (VND)", default=45000, input_type=float)

    # Image
    print("\n🖼️  HÌNH ẢNH SẢN PHẨM:")
    print("-" * 50)
    image_path = get_input("Đường dẫn đến file ảnh (để trống nếu không có)")

    image_base64 = None
    if image_path:
        if not os.path.exists(image_path):
            print(f"⚠️  Cảnh báo: File '{image_path}' không tồn tại!")
            if not get_yes_no("Tiếp tục không có ảnh?", default=True):
                return False
        else:
            print("🔄 Đang chuyển đổi ảnh sang base64...")
            image_base64 = image_to_base64(image_path)
            if image_base64:
                size_kb = len(image_base64) / 1024
                print(f"✅ Chuyển đổi thành công! (Kích thước: {size_kb:.2f} KB)")
            else:
                return False

    # Calories
    print("\n🔥 CALORIES:")
    print("-" * 50)
    calories_small = get_input("Calories (Size S)", default=0, input_type=int)
    calories_medium = get_input("Calories (Size M)", default=0, input_type=int)
    calories_large = get_input("Calories (Size L)", default=0, input_type=int)

    # Attributes
    print("\n⚙️  THUỘC TÍNH:")
    print("-" * 50)
    is_hot = get_yes_no("Có phục vụ nóng?", default=True)
    is_cold = get_yes_no("Có phục vụ lạnh?", default=True)
    is_caffeine_free = get_yes_no("Không chứa caffeine?", default=False)
    is_available = get_yes_no("Đang bán?", default=True)
    is_featured = get_yes_no("Sản phẩm nổi bật?", default=False)
    is_new = get_yes_no("Sản phẩm mới?", default=False)
    is_bestseller = get_yes_no("Bán chạy?", default=False)
    is_seasonal = get_yes_no("Theo mùa?", default=False)

    # Confirm
    print("\n" + "="*60)
    print("📋 XÁC NHẬN THÔNG TIN:")
    print("-" * 60)
    print(f"Tên: {name}")
    print(f"Tên (EN): {name_en}")
    print(f"Danh mục ID: {category_id}")
    print(f"Giá: {base_price:,.0f} VND")
    print(f"Hình ảnh: {'Có (' + str(len(image_base64)) + ' ký tự)' if image_base64 else 'Không có'}")
    print(f"Nóng/Lạnh: {'Nóng' if is_hot else ''}{' & ' if is_hot and is_cold else ''}{'Lạnh' if is_cold else ''}")
    print(f"Trạng thái: {'Đang bán' if is_available else 'Không bán'}")
    print("-" * 60)

    if not get_yes_no("\nXác nhận thêm sản phẩm?", default=True):
        print("❌ Đã hủy!")
        return False

    # Insert to database
    print("\n💾 Đang thêm vào database...")
    try:
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
            print(f"\n✅ THÀNH CÔNG! Đã thêm sản phẩm ID: {product_id}")
            print(f"   Tên: {name}")
            return True
        else:
            print("\n❌ Lỗi: Không thể thêm sản phẩm vào database!")
            return False

    except Exception as e:
        print(f"\n❌ Lỗi database: {e}")
        return False


def main():
    """Main function"""
    try:
        while True:
            success = add_product()

            print("\n" + "="*60)
            if not get_yes_no("\n➕ Thêm sản phẩm khác?", default=False):
                break
            print("\n")

        print("\n👋 Hoàn tất! Tạm biệt!")

    except KeyboardInterrupt:
        print("\n\n⚠️  Đã hủy bởi người dùng!")
    except Exception as e:
        print(f"\n❌ Lỗi không mong muốn: {e}")


if __name__ == "__main__":
    main()
