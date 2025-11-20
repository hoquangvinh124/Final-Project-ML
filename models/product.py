"""
Product and Category Models
"""
from typing import Optional, Dict, Any, List
from utils.database import db
import json


class Category:
    """Category model"""

    @staticmethod
    def get_all(active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all categories"""
        query = """
            SELECT * FROM categories
            WHERE is_active = TRUE
            ORDER BY display_order, name
        """ if active_only else """
            SELECT * FROM categories
            ORDER BY display_order, name
        """
        return db.fetch_all(query)

    @staticmethod
    def get_by_id(category_id: int) -> Optional[Dict[str, Any]]:
        """Get category by ID"""
        query = "SELECT * FROM categories WHERE id = %s"
        return db.fetch_one(query, (category_id,))


class Product:
    """Product model"""

    @staticmethod
    def get_all(category_id: Optional[int] = None, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all products, optionally filtered by category"""
        if category_id:
            query = """
                SELECT p.*, c.name as category_name
                FROM products p
                JOIN categories c ON p.category_id = c.id
                WHERE p.category_id = %s AND p.is_available = TRUE
                ORDER BY p.is_featured DESC, p.name
            """ if active_only else """
                SELECT p.*, c.name as category_name
                FROM products p
                JOIN categories c ON p.category_id = c.id
                WHERE p.category_id = %s
                ORDER BY p.is_featured DESC, p.name
            """
            return db.fetch_all(query, (category_id,))
        else:
            query = """
                SELECT p.*, c.name as category_name
                FROM products p
                JOIN categories c ON p.category_id = c.id
                WHERE p.is_available = TRUE
                ORDER BY p.is_featured DESC, p.name
            """ if active_only else """
                SELECT p.*, c.name as category_name
                FROM products p
                JOIN categories c ON p.category_id = c.id
                ORDER BY p.is_featured DESC, p.name
            """
            return db.fetch_all(query)

    @staticmethod
    def get_by_id(product_id: int) -> Optional[Dict[str, Any]]:
        """Get product by ID with full details"""
        query = """
            SELECT p.*, c.name as category_name, c.name_en as category_name_en
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE p.id = %s
        """
        product = db.fetch_one(query, (product_id,))

        if product:
            # Parse JSON fields
            if product.get('allergens'):
                product['allergens'] = json.loads(product['allergens'])

        return product

    @staticmethod
    def search(query_text: str) -> List[Dict[str, Any]]:
        """Search products by name or description"""
        query = """
            SELECT p.*, c.name as category_name
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE p.is_available = TRUE
              AND (p.name LIKE %s OR p.name_en LIKE %s OR p.description LIKE %s)
            ORDER BY p.is_featured DESC, p.name
        """
        search_term = f"%{query_text}%"
        return db.fetch_all(query, (search_term, search_term, search_term))

    @staticmethod
    def filter_products(
        category_id: Optional[int] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        is_hot: Optional[bool] = None,
        is_cold: Optional[bool] = None,
        is_caffeine_free: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """Filter products with multiple criteria"""
        conditions = ["p.is_available = TRUE"]
        params = []

        if category_id:
            conditions.append("p.category_id = %s")
            params.append(category_id)

        if min_price is not None:
            conditions.append("p.base_price >= %s")
            params.append(min_price)

        if max_price is not None:
            conditions.append("p.base_price <= %s")
            params.append(max_price)

        if is_hot is not None:
            conditions.append("p.is_hot = %s")
            params.append(is_hot)

        if is_cold is not None:
            conditions.append("p.is_cold = %s")
            params.append(is_cold)

        if is_caffeine_free is not None:
            conditions.append("p.is_caffeine_free = %s")
            params.append(is_caffeine_free)

        where_clause = " AND ".join(conditions)

        query = f"""
            SELECT p.*, c.name as category_name
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE {where_clause}
            ORDER BY p.is_featured DESC, p.name
        """

        return db.fetch_all(query, tuple(params))

    @staticmethod
    def get_featured_products(limit: int = 6) -> List[Dict[str, Any]]:
        """Get featured products"""
        query = """
            SELECT p.*, c.name as category_name
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE p.is_featured = TRUE AND p.is_available = TRUE
            ORDER BY p.rating DESC
            LIMIT %s
        """
        return db.fetch_all(query, (limit,))

    @staticmethod
    def get_popular_products(limit: int = 6) -> List[Dict[str, Any]]:
        """Get popular products based on reviews"""
        query = """
            SELECT p.*, c.name as category_name
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE p.is_available = TRUE
            ORDER BY p.total_reviews DESC, p.rating DESC
            LIMIT %s
        """
        return db.fetch_all(query, (limit,))

    @staticmethod
    def get_product_sizes(product_id: int) -> List[Dict[str, Any]]:
        """Get available sizes for a product"""
        query = """
            SELECT size, price_adjustment
            FROM product_sizes
            WHERE product_id = %s
            ORDER BY FIELD(size, 'S', 'M', 'L')
        """
        sizes = db.fetch_all(query, (product_id,))

        # If no sizes defined, return default sizes
        if not sizes:
            product = Product.get_by_id(product_id)
            if product:
                return [
                    {'size': 'S', 'price_adjustment': -5000},
                    {'size': 'M', 'price_adjustment': 0},
                    {'size': 'L', 'price_adjustment': 10000}
                ]

        return sizes

    @staticmethod
    def calculate_price(product_id: int, size: str, topping_ids: List[int] = None) -> float:
        """Calculate total price for product with size and toppings"""
        product = Product.get_by_id(product_id)
        if not product:
            return 0

        # Base price
        total_price = float(product['base_price'])

        # Add size adjustment
        sizes = Product.get_product_sizes(product_id)
        size_adjustment = 0
        for s in sizes:
            if s['size'] == size:
                size_adjustment = float(s['price_adjustment'])
                break

        total_price += size_adjustment

        # Add toppings
        if topping_ids:
            from models.topping import Topping
            for topping_id in topping_ids:
                topping = Topping.get_by_id(topping_id)
                if topping:
                    total_price += float(topping['price'])

        return total_price

    @staticmethod
    def get_calories(product_id: int, size: str) -> int:
        """Get calories for product with specific size"""
        product = Product.get_by_id(product_id)
        if not product:
            return 0

        if size == 'S':
            return product['calories_small'] or 0
        elif size == 'M':
            return product['calories_medium'] or 0
        elif size == 'L':
            return product['calories_large'] or 0

        return 0

    @staticmethod
    def update_rating(product_id: int):
        """Update product rating based on reviews"""
        query = """
            UPDATE products p
            SET rating = (
                SELECT COALESCE(AVG(rating), 0)
                FROM reviews
                WHERE product_id = p.id
            ),
            total_reviews = (
                SELECT COUNT(*)
                FROM reviews
                WHERE product_id = p.id
            )
            WHERE p.id = %s
        """
        return db.execute_query(query, (product_id,))
