"""
Admin Category Controller
Handles category management from admin side
"""
from utils.database import db


class AdminCategoryController:
    """Controller for admin category operations"""

    def get_all_categories(self):
        """Get all categories with product counts"""
        try:
            categories = db.fetch_all(
                """SELECT
                    c.*,
                    COUNT(p.id) as product_count
                FROM categories c
                LEFT JOIN products p ON c.id = p.category_id AND p.is_available = 1
                GROUP BY c.id
                ORDER BY c.display_order ASC, c.name ASC"""
            )
            return categories if categories else []

        except Exception as e:
            print(f"Error getting categories: {e}")
            return []

    def get_category_by_id(self, category_id):
        """Get category by ID"""
        try:
            category = db.fetch_one(
                """SELECT c.*, COUNT(p.id) as product_count
                   FROM categories c
                   LEFT JOIN products p ON c.id = p.category_id
                   WHERE c.id = %s
                   GROUP BY c.id""",
                (category_id,)
            )
            return category

        except Exception as e:
            print(f"Error getting category: {e}")
            return None

    def create_category(self, data, admin_id):
        """Create new category"""
        try:
            # Required fields
            if 'name' not in data or not data['name']:
                return False, "Thiếu tên danh mục"

            # Check if name exists
            existing = db.fetch_one(
                "SELECT id FROM categories WHERE name = %s",
                (data['name'],)
            )

            if existing:
                return False, "Tên danh mục đã tồn tại"

            # Get max display order
            max_order = db.fetch_one(
                "SELECT COALESCE(MAX(display_order), 0) as max_order FROM categories"
            )
            display_order = (max_order['max_order'] if max_order else 0) + 1

            # Insert category
            category_id = db.insert(
                """INSERT INTO categories
                   (name, description, display_order, is_active, created_at, updated_at)
                   VALUES (%s, %s, %s, %s, NOW(), NOW())""",
                (
                    data['name'],
                    data.get('description', ''),
                    data.get('display_order', display_order),
                    data.get('is_active', True)
                )
            )

            # Log activity
            from controllers.admin_controller import AdminController
            admin_controller = AdminController()
            admin_controller.log_activity(admin_id, 'create_category', 'categories', category_id,
                                         None, {'name': data['name']})

            return True, f"Tạo danh mục thành công (ID: {category_id})"

        except Exception as e:
            return False, f"Lỗi: {str(e)}"

    def update_category(self, category_id, data, admin_id):
        """Update category"""
        try:
            # Get old data
            old_category = self.get_category_by_id(category_id)

            if not old_category:
                return False, "Không tìm thấy danh mục"

            # Check if new name exists (excluding current)
            if data['name'] != old_category['name']:
                existing = db.fetch_one(
                    "SELECT id FROM categories WHERE name = %s AND id != %s",
                    (data['name'], category_id)
                )

                if existing:
                    return False, "Tên danh mục đã tồn tại"

            # Update category
            db.execute_query(
                """UPDATE categories SET
                   name = %s, description = %s,
                   display_order = %s, is_active = %s, updated_at = NOW()
                   WHERE id = %s""",
                (
                    data['name'],
                    data.get('description', ''),
                    data.get('display_order', old_category['display_order']),
                    data.get('is_active', True),
                    category_id
                )
            )

            # Log activity
            from controllers.admin_controller import AdminController
            admin_controller = AdminController()
            admin_controller.log_activity(admin_id, 'update_category', 'categories', category_id,
                                         {'name': old_category['name']},
                                         {'name': data['name']})

            return True, "Cập nhật danh mục thành công"

        except Exception as e:
            return False, f"Lỗi: {str(e)}"

    def delete_category(self, category_id, admin_id):
        """Delete category"""
        try:
            # Check if category has products
            category = self.get_category_by_id(category_id)

            if not category:
                return False, "Không tìm thấy danh mục"

            if category['product_count'] > 0:
                return False, f"Không thể xóa danh mục có {category['product_count']} sản phẩm"

            # Delete category
            db.execute_query(
                "DELETE FROM categories WHERE id = %s",
                (category_id,)
            )

            # Log activity
            from controllers.admin_controller import AdminController
            admin_controller = AdminController()
            admin_controller.log_activity(admin_id, 'delete_category', 'categories', category_id,
                                         {'name': category['name']}, None)

            return True, "Xóa danh mục thành công"

        except Exception as e:
            return False, f"Lỗi: {str(e)}"

    def toggle_category_status(self, category_id, admin_id):
        """Toggle category active status"""
        try:
            category = self.get_category_by_id(category_id)

            if not category:
                return False, "Không tìm thấy danh mục"

            new_status = not category['is_active']

            db.execute_query(
                "UPDATE categories SET is_active = %s, updated_at = NOW() WHERE id = %s",
                (new_status, category_id)
            )

            # Log activity
            from controllers.admin_controller import AdminController
            admin_controller = AdminController()
            admin_controller.log_activity(admin_id, 'toggle_category_status', 'categories', category_id,
                                         {'is_active': category['is_active']},
                                         {'is_active': new_status})

            status_text = "hiển thị" if new_status else "ẩn"
            return True, f"Đã {status_text} danh mục"

        except Exception as e:
            return False, f"Lỗi: {str(e)}"

    def reorder_categories(self, category_orders, admin_id):
        """Reorder categories"""
        try:
            # Update display order for each category
            for category_id, order in category_orders.items():
                db.execute_query(
                    "UPDATE categories SET display_order = %s WHERE id = %s",
                    (order, category_id)
                )

            # Log activity
            from controllers.admin_controller import AdminController
            admin_controller = AdminController()
            admin_controller.log_activity(admin_id, 'reorder_categories', 'categories', None,
                                         None, {'orders': category_orders})

            return True, "Sắp xếp danh mục thành công"

        except Exception as e:
            return False, f"Lỗi: {str(e)}"
