"""
Favorites Controller
Handles user favorite products
"""
from utils.database import db


class FavoritesController:
    """Controller for favorite products"""

    def add_favorite(self, user_id, product_id):
        """Add product to favorites"""
        try:
            # Check if already in favorites
            existing = db.fetch_one(
                "SELECT id FROM favorites WHERE user_id = %s AND product_id = %s",
                (user_id, product_id)
            )

            if existing:
                return False, "Sản phẩm đã có trong danh sách yêu thích"

            # Add to favorites
            db.execute_query(
                "INSERT INTO favorites (user_id, product_id, created_at) VALUES (%s, %s, NOW())",
                (user_id, product_id)
            )

            return True, "Đã thêm vào yêu thích"

        except Exception as e:
            return False, f"Lỗi: {str(e)}"

    def remove_favorite(self, user_id, product_id):
        """Remove product from favorites"""
        try:
            db.execute_query(
                "DELETE FROM favorites WHERE user_id = %s AND product_id = %s",
                (user_id, product_id)
            )
            return True, "Đã xóa khỏi yêu thích"

        except Exception as e:
            return False, f"Lỗi: {str(e)}"

    def is_favorite(self, user_id, product_id):
        """Check if product is in favorites"""
        try:
            result = db.fetch_one(
                "SELECT id FROM favorites WHERE user_id = %s AND product_id = %s",
                (user_id, product_id)
            )
            return result is not None

        except Exception as e:
            return False

    def get_favorite_products(self, user_id):
        """Get all favorite products for a user"""
        try:
            query = """
                SELECT
                    p.*,
                    c.name as category_name,
                    COALESCE(AVG(r.rating), 0) as rating,
                    COUNT(DISTINCT r.id) as total_reviews,
                    f.created_at as favorited_at
                FROM favorites f
                JOIN products p ON f.product_id = p.id
                LEFT JOIN categories c ON p.category_id = c.id
                LEFT JOIN reviews r ON p.id = r.product_id
                WHERE f.user_id = %s AND p.is_available = 1
                GROUP BY p.id, c.name, f.created_at
                ORDER BY f.created_at DESC
            """

            products = db.fetch_all(query, (user_id,))

            if not products:
                return []

            # Format products
            result = []
            for product in products:
                result.append({
                    'id': product['id'],
                    'name': product['name'],
                    'description': product['description'],
                    'base_price': float(product['base_price']),
                    'image': product['image'],
                    'category_name': product['category_name'],
                    'rating': float(product['rating']),
                    'total_reviews': product['total_reviews'],
                    'is_hot': bool(product['is_hot']),
                    'is_cold': bool(product['is_cold']),
                    'is_seasonal': bool(product['is_seasonal']),
                    'is_new': bool(product['is_new']),
                    'is_bestseller': bool(product['is_bestseller']),
                    'favorited_at': product['favorited_at']
                })

            return result

        except Exception as e:
            print(f"Error getting favorite products: {e}")
            return []

    def get_favorites_count(self, user_id):
        """Get total number of favorites"""
        try:
            result = db.fetch_one(
                "SELECT COUNT(*) as count FROM favorites WHERE user_id = %s",
                (user_id,)
            )
            return result['count'] if result else 0

        except Exception as e:
            return 0

    def toggle_favorite(self, user_id, product_id):
        """Toggle favorite status (add if not exists, remove if exists)"""
        if self.is_favorite(user_id, product_id):
            return self.remove_favorite(user_id, product_id)
        else:
            return self.add_favorite(user_id, product_id)
