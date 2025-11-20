"""
Notification Model
"""
from typing import Optional, Dict, Any, List
from utils.database import db


class Notification:
    """Notification model"""

    @staticmethod
    def create(
        user_id: int,
        title: str,
        message: str,
        notification_type: str = 'system',
        related_order_id: Optional[int] = None
    ) -> Optional[int]:
        """Create a new notification"""
        query = """
            INSERT INTO notifications (user_id, title, message, notification_type, related_order_id)
            VALUES (%s, %s, %s, %s, %s)
        """
        return db.insert(query, (user_id, title, message, notification_type, related_order_id))

    @staticmethod
    def get_user_notifications(user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Get notifications for a user"""
        query = """
            SELECT * FROM notifications
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """
        return db.fetch_all(query, (user_id, limit))

    @staticmethod
    def get_unread_count(user_id: int) -> int:
        """Get unread notification count"""
        query = "SELECT COUNT(*) as count FROM notifications WHERE user_id = %s AND is_read = FALSE"
        result = db.fetch_one(query, (user_id,))
        return result['count'] if result else 0

    @staticmethod
    def mark_as_read(notification_id: int, user_id: int) -> bool:
        """Mark notification as read"""
        query = "UPDATE notifications SET is_read = TRUE WHERE id = %s AND user_id = %s"
        return db.execute_query(query, (notification_id, user_id))

    @staticmethod
    def mark_all_as_read(user_id: int) -> bool:
        """Mark all notifications as read"""
        query = "UPDATE notifications SET is_read = TRUE WHERE user_id = %s"
        return db.execute_query(query, (user_id,))
