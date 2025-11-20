"""
User Model
"""
from typing import Optional, Dict, Any, List
from utils.database import db
from utils.helpers import hash_password, verify_password
from datetime import datetime


class User:
    """User model for authentication and profile management"""

    @staticmethod
    def create(email: str, password: str, full_name: str, phone: Optional[str] = None) -> Optional[int]:
        """Create a new user"""
        query = """
            INSERT INTO users (email, password_hash, full_name, phone, membership_tier, loyalty_points)
            VALUES (%s, %s, %s, %s, 'Bronze', 0)
        """
        password_hash = hash_password(password)
        user_id = db.insert(query, (email, password_hash, full_name, phone))

        if user_id:
            # Create default preferences
            pref_query = """
                INSERT INTO user_preferences (user_id, favorite_size, favorite_sugar_level, favorite_ice_level)
                VALUES (%s, 'M', 50, 50)
            """
            db.execute_query(pref_query, (user_id,))

        return user_id

    @staticmethod
    def authenticate(email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with email and password"""
        query = """
            SELECT id, email, phone, password_hash, full_name, membership_tier,
                   loyalty_points, avatar, is_active
            FROM users
            WHERE email = %s AND is_active = TRUE
        """
        user = db.fetch_one(query, (email,))

        if user and verify_password(password, user['password_hash']):
            # Update last login
            update_query = "UPDATE users SET last_login = NOW() WHERE id = %s"
            db.execute_query(update_query, (user['id'],))

            # Remove password hash from returned data
            del user['password_hash']
            return user

        return None

    @staticmethod
    def get_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        query = """
            SELECT id, email, phone, full_name, date_of_birth, avatar,
                   membership_tier, loyalty_points, created_at
            FROM users
            WHERE id = %s AND is_active = TRUE
        """
        return db.fetch_one(query, (user_id,))

    @staticmethod
    def get_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        query = """
            SELECT id, email, phone, full_name, membership_tier, loyalty_points
            FROM users
            WHERE email = %s AND is_active = TRUE
        """
        return db.fetch_one(query, (email,))

    @staticmethod
    def get_by_phone(phone: str) -> Optional[Dict[str, Any]]:
        """Get user by phone"""
        query = """
            SELECT id, email, phone, full_name, membership_tier, loyalty_points
            FROM users
            WHERE phone = %s AND is_active = TRUE
        """
        return db.fetch_one(query, (phone,))

    @staticmethod
    def email_exists(email: str) -> bool:
        """Check if email already exists"""
        query = "SELECT COUNT(*) as count FROM users WHERE email = %s"
        result = db.fetch_one(query, (email,))
        return result['count'] > 0 if result else False

    @staticmethod
    def phone_exists(phone: str) -> bool:
        """Check if phone already exists"""
        query = "SELECT COUNT(*) as count FROM users WHERE phone = %s"
        result = db.fetch_one(query, (phone,))
        return result['count'] > 0 if result else False

    @staticmethod
    def update_profile(user_id: int, **kwargs) -> bool:
        """Update user profile"""
        allowed_fields = ['full_name', 'phone', 'date_of_birth', 'avatar']
        update_fields = []
        values = []

        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                update_fields.append(f"{field} = %s")
                values.append(value)

        if not update_fields:
            return False

        values.append(user_id)
        query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s"
        return db.execute_query(query, tuple(values))

    @staticmethod
    def update_password(user_id: int, new_password: str) -> bool:
        """Update user password"""
        password_hash = hash_password(new_password)
        query = "UPDATE users SET password_hash = %s WHERE id = %s"
        return db.execute_query(query, (password_hash, user_id))

    @staticmethod
    def add_loyalty_points(user_id: int, points: int, description: str, order_id: Optional[int] = None) -> bool:
        """Add loyalty points to user"""
        # Update user points
        update_query = "UPDATE users SET loyalty_points = loyalty_points + %s WHERE id = %s"
        if not db.execute_query(update_query, (points, user_id)):
            return False

        # Record transaction
        history_query = """
            INSERT INTO loyalty_points_history (user_id, points, transaction_type, description, order_id)
            VALUES (%s, %s, 'earn', %s, %s)
        """
        db.execute_query(history_query, (user_id, points, description, order_id))

        # Check and update membership tier
        user = User.get_by_id(user_id)
        if user:
            from utils.helpers import calculate_membership_tier
            new_tier = calculate_membership_tier(user['loyalty_points'])
            if new_tier != user['membership_tier']:
                db.execute_query("UPDATE users SET membership_tier = %s WHERE id = %s", (new_tier, user_id))

        return True

    @staticmethod
    def redeem_points(user_id: int, points: int, description: str) -> bool:
        """Redeem loyalty points"""
        # Check if user has enough points
        user = User.get_by_id(user_id)
        if not user or user['loyalty_points'] < points:
            return False

        # Deduct points
        update_query = "UPDATE users SET loyalty_points = loyalty_points - %s WHERE id = %s"
        if not db.execute_query(update_query, (points, user_id)):
            return False

        # Record transaction
        history_query = """
            INSERT INTO loyalty_points_history (user_id, points, transaction_type, description)
            VALUES (%s, %s, 'redeem', %s)
        """
        db.execute_query(history_query, (user_id, points, description))

        return True

    @staticmethod
    def get_preferences(user_id: int) -> Optional[Dict[str, Any]]:
        """Get user preferences"""
        query = "SELECT * FROM user_preferences WHERE user_id = %s"
        return db.fetch_one(query, (user_id,))

    @staticmethod
    def update_preferences(user_id: int, **kwargs) -> bool:
        """Update user preferences"""
        allowed_fields = ['favorite_size', 'favorite_sugar_level', 'favorite_ice_level',
                         'preferred_toppings', 'allergies']
        update_fields = []
        values = []

        for field, value in kwargs.items():
            if field in allowed_fields:
                update_fields.append(f"{field} = %s")
                values.append(value)

        if not update_fields:
            return False

        values.append(user_id)
        query = f"UPDATE user_preferences SET {', '.join(update_fields)} WHERE user_id = %s"
        return db.execute_query(query, tuple(values))

    @staticmethod
    def get_order_history(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user's order history"""
        query = """
            SELECT o.*, s.name as store_name, s.address as store_address
            FROM orders o
            LEFT JOIN stores s ON o.store_id = s.id
            WHERE o.user_id = %s
            ORDER BY o.created_at DESC
            LIMIT %s
        """
        return db.fetch_all(query, (user_id, limit))

