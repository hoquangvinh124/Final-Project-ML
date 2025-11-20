"""
Voucher Model
"""
from typing import Optional, Dict, Any, List
from utils.database import db
from datetime import datetime


class Voucher:
    """Voucher model"""

    @staticmethod
    def get_by_code(code: str) -> Optional[Dict[str, Any]]:
        """Get voucher by code"""
        query = """
            SELECT * FROM vouchers
            WHERE code = %s AND is_active = TRUE
              AND (start_date IS NULL OR start_date <= NOW())
              AND (end_date IS NULL OR end_date >= NOW())
        """
        return db.fetch_one(query, (code.upper(),))

    @staticmethod
    def get_available_for_user(user_id: int) -> List[Dict[str, Any]]:
        """Get all available vouchers for user"""
        query = """
            SELECT v.*, COALESCE(uv.times_used, 0) as times_used
            FROM vouchers v
            LEFT JOIN user_vouchers uv ON v.id = uv.voucher_id AND uv.user_id = %s
            WHERE v.is_active = TRUE
              AND (v.start_date IS NULL OR v.start_date <= NOW())
              AND (v.end_date IS NULL OR v.end_date >= NOW())
              AND (v.usage_limit IS NULL OR v.current_usage < v.usage_limit)
              AND (uv.times_used IS NULL OR uv.times_used < v.usage_per_user)
            ORDER BY v.discount_value DESC
        """
        return db.fetch_all(query, (user_id,))

    @staticmethod
    def can_use(user_id: int, voucher_id: int, order_amount: float) -> bool:
        """Check if user can use voucher"""
        voucher = db.fetch_one("SELECT * FROM vouchers WHERE id = %s", (voucher_id,))
        if not voucher or not voucher['is_active']:
            return False

        # Check min order amount
        if order_amount < float(voucher['min_order_amount']):
            return False

        # Check usage limit
        if voucher['usage_limit'] and voucher['current_usage'] >= voucher['usage_limit']:
            return False

        # Check user usage
        user_usage = db.fetch_one(
            "SELECT times_used FROM user_vouchers WHERE user_id = %s AND voucher_id = %s",
            (user_id, voucher_id)
        )
        if user_usage and user_usage['times_used'] >= voucher['usage_per_user']:
            return False

        return True

    @staticmethod
    def use_voucher(user_id: int, voucher_id: int) -> bool:
        """Mark voucher as used by user"""
        # Update voucher usage
        db.execute_query("UPDATE vouchers SET current_usage = current_usage + 1 WHERE id = %s", (voucher_id,))

        # Update user voucher usage
        existing = db.fetch_one(
            "SELECT id FROM user_vouchers WHERE user_id = %s AND voucher_id = %s",
            (user_id, voucher_id)
        )

        if existing:
            query = """
                UPDATE user_vouchers
                SET times_used = times_used + 1, last_used_at = NOW()
                WHERE user_id = %s AND voucher_id = %s
            """
            return db.execute_query(query, (user_id, voucher_id))
        else:
            query = """
                INSERT INTO user_vouchers (user_id, voucher_id, times_used, last_used_at)
                VALUES (%s, %s, 1, NOW())
            """
            return db.insert(query, (user_id, voucher_id)) is not None
