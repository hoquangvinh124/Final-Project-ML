#!/usr/bin/env python3
"""
Script to add categories with automatic base64 image conversion
Usage: python scripts/add_category.py
"""
import sys
import os
import base64
from pathlib import Path

# Add parent directory to path to import models
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.database import db


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


def add_category():
    """Interactive function to add a category"""
    print("\n" + "="*60)
    print("📂 THÊM DANH MỤC MỚI VÀO DATABASE")
    print("="*60)

    # Get category info
    print("\n📝 THÔNG TIN DANH MỤC:")
    print("-" * 50)

    # Basic info
    name = get_input("Tên danh mục (Tiếng Việt)")
    if not name:
        print("❌ Tên danh mục không được để trống!")
        return False

    name_en = get_input("Tên danh mục (English)", default=name)
    description = get_input("Mô tả danh mục")

    # Icon (emoji as placeholder)
    print("\n🎨 ICON:")
    print("-" * 50)
    print("💡 Icon là emoji làm placeholder khi chưa có ảnh")
    print("   Ví dụ: ☕ (cafe), 🧋 (trà sữa), 🍰 (bánh), 🥤 (nước), 🍹 (cocktail)")
    icon = get_input("Icon (emoji)", default="☕")

    # Image (base64)
    print("\n🖼️  HÌNH ẢNH:")
    print("-" * 50)
    print("💡 Nếu có ảnh, ảnh sẽ được hiển thị thay vì icon emoji")
    image_path = get_input("Đường dẫn đến file ảnh (để trống nếu chỉ dùng icon)")

    image_base64 = None
    if image_path:
        if not os.path.exists(image_path):
            print(f"⚠️  Cảnh báo: File '{image_path}' không tồn tại!")
            if not get_yes_no("Tiếp tục chỉ với icon emoji?", default=True):
                return False
        else:
            print("🔄 Đang chuyển đổi ảnh sang base64...")
            image_base64 = image_to_base64(image_path)
            if image_base64:
                size_kb = len(image_base64) / 1024
                print(f"✅ Chuyển đổi thành công! (Kích thước: {size_kb:.2f} KB)")
            else:
                return False

    # Display order
    display_order = get_input("Thứ tự hiển thị", default=0, input_type=int)

    # Active status
    is_active = get_yes_no("Kích hoạt ngay?", default=True)

    # Confirm
    print("\n" + "="*60)
    print("📋 XÁC NHẬN THÔNG TIN:")
    print("-" * 60)
    print(f"Tên: {name}")
    print(f"Tên (EN): {name_en}")
    print(f"Mô tả: {description or '(Không có)'}")
    print(f"Icon: {icon}")
    print(f"Hình ảnh: {'Có (' + str(len(image_base64)) + ' ký tự)' if image_base64 else 'Không có (dùng icon)'}")
    print(f"Thứ tự: {display_order}")
    print(f"Trạng thái: {'Kích hoạt' if is_active else 'Ẩn'}")
    print("-" * 60)

    if not get_yes_no("\nXác nhận thêm danh mục?", default=True):
        print("❌ Đã hủy!")
        return False

    # Insert to database
    print("\n💾 Đang thêm vào database...")
    try:
        query = """
            INSERT INTO categories
            (name, name_en, description, icon, image, display_order, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        """

        category_id = db.insert(query, (
            name, name_en, description, icon, image_base64, display_order, is_active
        ))

        if category_id:
            print(f"\n✅ THÀNH CÔNG! Đã thêm danh mục ID: {category_id}")
            print(f"   Tên: {icon} {name}")
            return True
        else:
            print("\n❌ Lỗi: Không thể thêm danh mục vào database!")
            return False

    except Exception as e:
        print(f"\n❌ Lỗi database: {e}")
        return False


def main():
    """Main function"""
    try:
        while True:
            success = add_category()

            print("\n" + "="*60)
            if not get_yes_no("\n➕ Thêm danh mục khác?", default=False):
                break
            print("\n")

        print("\n👋 Hoàn tất! Tạm biệt!")

    except KeyboardInterrupt:
        print("\n\n⚠️  Đã hủy bởi người dùng!")
    except Exception as e:
        print(f"\n❌ Lỗi không mong muốn: {e}")


if __name__ == "__main__":
    main()
