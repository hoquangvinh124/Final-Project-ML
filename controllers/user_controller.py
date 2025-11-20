"""
User Controller
Handles user profile, preferences, and loyalty management
"""
from typing import Optional, Dict, Any, List, Tuple
from models.user import User
from models.voucher import Voucher
from models.notification import Notification
from utils.validators import validate_full_name, validate_phone


class UserController:
    """User profile and management controller"""

    @staticmethod
    def get_profile(user_id: int) -> Optional[Dict[str, Any]]:
        """Get user profile"""
        return User.get_by_id(user_id)

    @staticmethod
    def update_profile(
        user_id: int,
        full_name: Optional[str] = None,
        phone: Optional[str] = None,
        date_of_birth: Optional[str] = None,
        avatar: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Update user profile
        Returns: (success, message)
        """
        update_data = {}

        if full_name:
            is_valid, error = validate_full_name(full_name)
            if not is_valid:
                return False, error
            update_data['full_name'] = full_name

        if phone:
            is_valid, error = validate_phone(phone)
            if not is_valid:
                return False, error

            # Check if phone is already used by another user
            existing_user = User.get_by_phone(phone)
            if existing_user and existing_user['id'] != user_id:
                return False, "Số điện thoại đã được sử dụng"

            update_data['phone'] = phone

        if date_of_birth:
            update_data['date_of_birth'] = date_of_birth

        if avatar:
            update_data['avatar'] = avatar

        if not update_data:
            return False, "Không có thông tin để cập nhật"

        success = User.update_profile(user_id, **update_data)

        if success:
            return True, "Cập nhật thông tin thành công!"
        else:
            return False, "Không thể cập nhật thông tin"

    @staticmethod
    def get_preferences(user_id: int) -> Optional[Dict[str, Any]]:
        """Get user preferences"""
        return User.get_preferences(user_id)

    @staticmethod
    def update_preferences(user_id: int, **kwargs) -> Tuple[bool, str]:
        """
        Update user preferences
        Returns: (success, message)
        """
        success = User.update_preferences(user_id, **kwargs)

        if success:
            return True, "Đã cập nhật tùy chọn"
        else:
            return False, "Không thể cập nhật tùy chọn"

    @staticmethod
    def get_order_history(user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user's order history"""
        return User.get_order_history(user_id, limit)

    @staticmethod
    def get_loyalty_info(user_id: int) -> Dict[str, Any]:
        """Get user's loyalty program info"""
        user = User.get_by_id(user_id)

        if not user:
            return {}

        # Calculate points to next tier
        current_tier = user['membership_tier']
        current_points = user['loyalty_points']

        next_tier = None
        points_to_next = 0

        if current_tier == 'Bronze':
            next_tier = 'Silver'
            points_to_next = 1000 - current_points
        elif current_tier == 'Silver':
            next_tier = 'Gold'
            points_to_next = 5000 - current_points

        return {
            'current_tier': current_tier,
            'points': current_points,
            'next_tier': next_tier,
            'points_to_next': max(0, points_to_next) if next_tier else 0
        }

    @staticmethod
    def get_available_vouchers(user_id: int) -> List[Dict[str, Any]]:
        """Get available vouchers for user"""
        return Voucher.get_available_for_user(user_id)

    @staticmethod
    def get_notifications(user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Get user notifications"""
        return Notification.get_user_notifications(user_id, limit)

    @staticmethod
    def get_unread_notification_count(user_id: int) -> int:
        """Get unread notification count"""
        return Notification.get_unread_count(user_id)

    @staticmethod
    def mark_notification_read(notification_id: int, user_id: int) -> bool:
        """Mark notification as read"""
        return Notification.mark_as_read(notification_id, user_id)

    @staticmethod
    def mark_all_notifications_read(user_id: int) -> bool:
        """Mark all notifications as read"""
        return Notification.mark_all_as_read(user_id)


    @staticmethod
    def get_points_history(user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Get loyalty points transaction history"""
        from utils.database import db
        query = """
            SELECT * FROM loyalty_points_history
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """
        return db.fetch_all(query, (user_id, limit))
