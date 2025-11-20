"""
Menu Controller
Handles product browsing, filtering, searching
"""
from typing import Optional, Dict, Any, List
from models.product import Product, Category
from models.topping import Topping
from models.user import User


class MenuController:
    """Menu and product controller"""

    @staticmethod
    def get_categories() -> List[Dict[str, Any]]:
        """Get all categories"""
        return Category.get_all()

    @staticmethod
    def get_products_by_category(category_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get products by category"""
        return Product.get_all(category_id)

    @staticmethod
    def get_product_detail(product_id: int) -> Optional[Dict[str, Any]]:
        """Get product details with sizes and toppings"""
        product = Product.get_by_id(product_id)
        if not product:
            return None

        # Add sizes
        product['sizes'] = Product.get_product_sizes(product_id)

        # Add available toppings
        product['available_toppings'] = Topping.get_all()

        return product

    @staticmethod
    def search_products(query: str) -> List[Dict[str, Any]]:
        """Search products"""
        return Product.search(query)

    @staticmethod
    def filter_products(
        category_id: Optional[int] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        temperature: Optional[str] = None,  # 'hot' or 'cold'
        is_caffeine_free: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """Filter products with multiple criteria"""
        is_hot = temperature == 'hot' if temperature else None
        is_cold = temperature == 'cold' if temperature else None

        return Product.filter_products(
            category_id=category_id,
            min_price=min_price,
            max_price=max_price,
            is_hot=is_hot,
            is_cold=is_cold,
            is_caffeine_free=is_caffeine_free
        )

    @staticmethod
    def get_featured_products(limit: int = 6) -> List[Dict[str, Any]]:
        """Get featured products"""
        return Product.get_featured_products(limit)

    @staticmethod
    def get_popular_products(limit: int = 6) -> List[Dict[str, Any]]:
        """Get popular products"""
        return Product.get_popular_products(limit)

    @staticmethod
    def get_recommended_products(user_id: Optional[int] = None, limit: int = 6) -> List[Dict[str, Any]]:
        """
        Get recommended products for user
        (Simplified - in production, use ML-based recommendations)
        """
        if user_id:
            # Get user's order history
            orders = User.get_order_history(user_id, limit=5)

            # For now, just return popular products
            # In production, analyze order patterns and recommend similar items
            return Product.get_popular_products(limit)
        else:
            return Product.get_featured_products(limit)

    @staticmethod
    def calculate_product_price(
        product_id: int,
        size: str,
        topping_ids: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """Calculate product price with customizations"""
        product = Product.get_by_id(product_id)
        if not product:
            return {'total': 0, 'breakdown': {}}

        base_price = float(product['base_price'])

        # Get size adjustment
        sizes = Product.get_product_sizes(product_id)
        size_adjustment = 0
        for s in sizes:
            if s['size'] == size:
                size_adjustment = float(s['price_adjustment'])
                break

        # Calculate topping cost
        topping_cost = 0
        topping_details = []
        if topping_ids:
            toppings = Topping.get_by_ids(topping_ids)
            topping_cost = sum(float(t['price']) for t in toppings)
            topping_details = toppings

        total = base_price + size_adjustment + topping_cost

        return {
            'base_price': base_price,
            'size_adjustment': size_adjustment,
            'topping_cost': topping_cost,
            'total': total,
            'toppings': topping_details
        }

    @staticmethod
    def get_all_toppings() -> List[Dict[str, Any]]:
        """Get all available toppings"""
        return Topping.get_all()

    @staticmethod
    def add_to_favorites(user_id: int, product_id: int) -> bool:
        """Add product to favorites"""
        from utils.database import db
        query = """
            INSERT IGNORE INTO user_favorites (user_id, product_id)
            VALUES (%s, %s)
        """
        return db.insert(query, (user_id, product_id)) is not None

    @staticmethod
    def remove_from_favorites(user_id: int, product_id: int) -> bool:
        """Remove product from favorites"""
        from utils.database import db
        query = "DELETE FROM user_favorites WHERE user_id = %s AND product_id = %s"
        return db.execute_query(query, (user_id, product_id))

    @staticmethod
    def get_user_favorites(user_id: int) -> List[Dict[str, Any]]:
        """Get user's favorite products"""
        from utils.database import db
        query = """
            SELECT p.*, c.name as category_name
            FROM user_favorites uf
            JOIN products p ON uf.product_id = p.id
            JOIN categories c ON p.category_id = c.id
            WHERE uf.user_id = %s AND p.is_available = TRUE
            ORDER BY uf.created_at DESC
        """
        return db.fetch_all(query, (user_id,))

    @staticmethod
    def is_favorite(user_id: int, product_id: int) -> bool:
        """Check if product is in favorites"""
        from utils.database import db
        query = "SELECT COUNT(*) as count FROM user_favorites WHERE user_id = %s AND product_id = %s"
        result = db.fetch_one(query, (user_id, product_id))
        return result['count'] > 0 if result else False
