"""
Admin Product Controller
Handles product management from admin side
"""
from utils.database import db


class AdminProductController:
    """Controller for admin product operations"""

    def get_all_products(self, category_id=None, search=None, limit=100, offset=0):
        """Get all products with filters"""
        try:
            query = """
                SELECT
                    p.*,
                    c.name as category_name
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE 1=1
            """
            params = []

            if category_id:
                query += " AND p.category_id = %s"
                params.append(category_id)

            if search:
                query += " AND (p.name LIKE %s OR p.description LIKE %s)"
                search_term = f"%{search}%"
                params.extend([search_term, search_term])

            query += " ORDER BY p.created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])

            products = db.fetch_all(query, tuple(params))
            return products if products else []

        except Exception as e:
            print(f"Error getting products: {e}")
            return []

    def get_product_by_id(self, product_id):
        """Get product by ID"""
        try:
            product = db.fetch_one(
                """SELECT p.*, c.name as category_name
                   FROM products p
                   LEFT JOIN categories c ON p.category_id = c.id
                   WHERE p.id = %s""",
                (product_id,)
            )
            return product

        except Exception as e:
            print(f"Error getting product: {e}")
            return None

    def create_product(self, data, admin_id):
        """Create new product"""
        try:
            # Required fields
            required = ['name', 'category_id', 'base_price']
            for field in required:
                if field not in data or not data[field]:
                    return False, f"Thiếu trường {field}"

            # Insert product
            product_id = db.insert(
                """INSERT INTO products
                   (name, category_id, description, base_price, image,
                    is_hot, is_cold, is_seasonal, is_new, is_bestseller,
                    is_available, ingredients, calories_small, calories_medium,
                    calories_large, created_at, updated_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())""",
                (
                    data['name'],
                    data['category_id'],
                    data.get('description', ''),
                    data['base_price'],
                    data.get('image', ''),
                    data.get('is_hot', True),
                    data.get('is_cold', True),
                    data.get('is_seasonal', False),
                    data.get('is_new', False),
                    data.get('is_bestseller', False),
                    data.get('is_available', True),
                    data.get('ingredients', ''),
                    data.get('calories_small', 0),
                    data.get('calories_medium', 0),
                    data.get('calories_large', 0)
                )
            )

            return True, f"Tạo sản phẩm thành công (ID: {product_id})"

        except Exception as e:
            return False, f"Lỗi: {str(e)}"

    def update_product(self, product_id, data, admin_id):
        """Update product"""
        try:
            # Get old data for logging
            old_product = self.get_product_by_id(product_id)

            if not old_product:
                return False, "Không tìm thấy sản phẩm"

            # Update product
            db.execute_query(
                """UPDATE products SET
                   name = %s, category_id = %s, description = %s, base_price = %s,
                   image = %s, is_hot = %s, is_cold = %s, is_seasonal = %s,
                   is_new = %s, is_bestseller = %s, is_available = %s,
                   ingredients = %s, calories_small = %s, calories_medium = %s,
                   calories_large = %s, updated_at = NOW()
                   WHERE id = %s""",
                (
                    data['name'],
                    data['category_id'],
                    data.get('description', ''),
                    data['base_price'],
                    data.get('image', ''),
                    data.get('is_hot', True),
                    data.get('is_cold', True),
                    data.get('is_seasonal', False),
                    data.get('is_new', False),
                    data.get('is_bestseller', False),
                    data.get('is_available', True),
                    data.get('ingredients', ''),
                    data.get('calories_small', 0),
                    data.get('calories_medium', 0),
                    data.get('calories_large', 0),
                    product_id
                )
            )

            return True, "Cập nhật sản phẩm thành công"

        except Exception as e:
            return False, f"Lỗi: {str(e)}"

    def delete_product(self, product_id, admin_id):
        """Delete product (hard delete - remove from database)"""
        try:
            # Get product for logging
            product = self.get_product_by_id(product_id)

            if not product:
                return False, "Không tìm thấy sản phẩm"

            # Hard delete - actually remove from database
            db.execute_query(
                "DELETE FROM products WHERE id = %s",
                (product_id,)
            )

            return True, "Đã xóa sản phẩm khỏi hệ thống"

        except Exception as e:
            return False, f"Lỗi: {str(e)}"

    def toggle_availability(self, product_id, admin_id):
        """Toggle product availability"""
        try:
            product = self.get_product_by_id(product_id)

            if not product:
                return False, "Không tìm thấy sản phẩm"

            new_status = not product['is_available']

            db.execute_query(
                "UPDATE products SET is_available = %s, updated_at = NOW() WHERE id = %s",
                (new_status, product_id)
            )

            status_text = "hiển thị" if new_status else "ẩn"
            return True, f"Đã {status_text} sản phẩm"

        except Exception as e:
            return False, f"Lỗi: {str(e)}"

    def get_product_statistics(self):
        """Get product statistics"""
        try:
            stats = {}

            # Total products
            result = db.fetch_one("SELECT COUNT(*) as count FROM products")
            stats['total'] = result['count'] if result else 0

            # Available products
            result = db.fetch_one("SELECT COUNT(*) as count FROM products WHERE is_available = 1")
            stats['available'] = result['count'] if result else 0

            # Products by category
            result = db.fetch_all(
                """SELECT c.name, COUNT(p.id) as count
                   FROM categories c
                   LEFT JOIN products p ON c.id = p.category_id
                   GROUP BY c.id, c.name"""
            )
            stats['by_category'] = {row['name']: row['count'] for row in result} if result else {}

            return stats

        except Exception as e:
            print(f"Error getting product stats: {e}")
            return {}
