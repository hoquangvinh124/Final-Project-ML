"""
Admin Controller
Handles admin authentication and operations
"""
import hashlib
from datetime import datetime
from utils.database import db


class AdminController:
    """Controller for admin operations - Singleton pattern"""
    
    _instance = None
    _current_admin = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AdminController, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        # Don't reset current_admin if already initialized
        pass
    
    @property
    def current_admin(self):
        return self._current_admin
    
    @current_admin.setter
    def current_admin(self, value):
        self._current_admin = value

    def login(self, username, password):
        """Admin login"""
        try:
            # Hash password
            password_hash = hashlib.sha256(password.encode()).hexdigest()

            # Check credentials
            admin = db.fetch_one(
                """SELECT id, username, email, full_name, role, is_active
                   FROM admin_users
                   WHERE username = %s AND password_hash = %s""",
                (username, password_hash)
            )

            if not admin:
                return False, "Tên đăng nhập hoặc mật khẩu không đúng"

            if not admin['is_active']:
                return False, "Tài khoản đã bị khóa"

            # Update last login
            db.execute_query(
                "UPDATE admin_users SET last_login = NOW() WHERE id = %s",
                (admin['id'],)
            )

            # Store admin session
            self.current_admin = admin

            return True, admin

        except Exception as e:
            return False, f"Lỗi đăng nhập: {str(e)}"

    def logout(self):
        """Admin logout"""
        if self._current_admin:
            self._current_admin = None

    def get_current_admin(self):
        """Get current logged in admin"""
        return self._current_admin

    def get_current_admin_id(self):
        """Get current admin ID"""
        return self._current_admin['id'] if self._current_admin else None

    def log_activity(self, admin_id, action, table_name=None, record_id=None, old_value=None, new_value=None):
        """Log admin activity - DEPRECATED: admin_activity_log table removed"""
        # Activity logging has been removed from the database schema
        pass

    def get_dashboard_stats(self):
        """Get dashboard statistics"""
        try:
            stats = {}

            # Total orders
            result = db.fetch_one("SELECT COUNT(*) as count FROM orders")
            stats['total_orders'] = result['count'] if result else 0

            # Total revenue
            result = db.fetch_one("SELECT SUM(total_amount) as total FROM orders WHERE status != 'cancelled'")
            stats['total_revenue'] = float(result['total']) if result and result['total'] else 0

            # Total customers
            result = db.fetch_one("SELECT COUNT(*) as count FROM users WHERE is_active = 1")
            stats['total_customers'] = result['count'] if result else 0

            # Total products
            result = db.fetch_one("SELECT COUNT(*) as count FROM products WHERE is_available = 1")
            stats['total_products'] = result['count'] if result else 0

            # Pending orders
            result = db.fetch_one("SELECT COUNT(*) as count FROM orders WHERE status = 'pending'")
            stats['pending_orders'] = result['count'] if result else 0

            # Today's orders
            result = db.fetch_one(
                "SELECT COUNT(*) as count FROM orders WHERE DATE(created_at) = CURDATE()"
            )
            stats['today_orders'] = result['count'] if result else 0

            # Today's revenue
            result = db.fetch_one(
                """SELECT SUM(total_amount) as total FROM orders
                   WHERE DATE(created_at) = CURDATE() AND status != 'cancelled'"""
            )
            stats['today_revenue'] = float(result['total']) if result and result['total'] else 0

            # This month's revenue
            result = db.fetch_one(
                """SELECT SUM(total_amount) as total FROM orders
                   WHERE YEAR(created_at) = YEAR(CURDATE())
                   AND MONTH(created_at) = MONTH(CURDATE())
                   AND status != 'cancelled'"""
            )
            stats['month_revenue'] = float(result['total']) if result and result['total'] else 0

            return stats

        except Exception as e:
            print(f"Error getting dashboard stats: {e}")
            return {}

    def get_recent_orders(self, limit=10):
        """Get recent orders"""
        try:
            query = """
                SELECT
                    o.*,
                    u.full_name as customer_name,
                    u.email as customer_email,
                    s.name as store_name
                FROM orders o
                LEFT JOIN users u ON o.user_id = u.id
                LEFT JOIN stores s ON o.store_id = s.id
                ORDER BY o.created_at DESC
                LIMIT %s
            """

            orders = db.fetch_all(query, (limit,))
            return orders if orders else []

        except Exception as e:
            print(f"Error getting recent orders: {e}")
            return []

    def change_password(self, admin_id, old_password, new_password):
        """Change admin password"""
        try:
            # Verify old password
            old_hash = hashlib.sha256(old_password.encode()).hexdigest()
            admin = db.fetch_one(
                "SELECT id FROM admin_users WHERE id = %s AND password_hash = %s",
                (admin_id, old_hash)
            )

            if not admin:
                return False, "Mật khẩu cũ không đúng"

            # Update password
            new_hash = hashlib.sha256(new_password.encode()).hexdigest()
            db.execute_query(
                "UPDATE admin_users SET password_hash = %s WHERE id = %s",
                (new_hash, admin_id)
            )

            return True, "Đổi mật khẩu thành công"

        except Exception as e:
            return False, f"Lỗi: {str(e)}"
