"""
Review Model
"""
from typing import Optional, Dict, Any, List
from utils.database import db
import json


class Review:
    """Product review model"""

    @staticmethod
    def create(
        user_id: int,
        product_id: int,
        order_id: int,
        rating: int,
        comment: Optional[str] = None,
        service_rating: Optional[int] = None
    ) -> Optional[int]:
        """Create a review"""
        query = """
            INSERT INTO reviews (user_id, product_id, order_id, rating, comment, service_rating)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        review_id = db.insert(query, (user_id, product_id, order_id, rating, comment, service_rating))

        if review_id:
            # Update product rating
            from models.product import Product
            Product.update_rating(product_id)

        return review_id

    @staticmethod
    def get_product_reviews(product_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get reviews for a product"""
        query = """
            SELECT r.*, u.full_name as user_name, u.avatar as user_avatar
            FROM reviews r
            JOIN users u ON r.user_id = u.id
            WHERE r.product_id = %s AND r.is_approved = TRUE
            ORDER BY r.created_at DESC
            LIMIT %s
        """
        return db.fetch_all(query, (product_id, limit))

    @staticmethod
    def get_user_reviews(user_id: int) -> List[Dict[str, Any]]:
        """Get reviews by a user"""
        query = """
            SELECT r.*, p.name as product_name, p.image as product_image
            FROM reviews r
            JOIN products p ON r.product_id = p.id
            WHERE r.user_id = %s
            ORDER BY r.created_at DESC
        """
        return db.fetch_all(query, (user_id,))
