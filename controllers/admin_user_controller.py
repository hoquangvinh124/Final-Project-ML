"""
Admin User Controller
Handles user management from admin side
"""
from utils.database import db


class AdminUserController:
    """Controller for admin user operations"""

    def get_all_users(self, search=None, tier=None, limit=100, offset=0):
        """Get all users with filters"""
        try:
            query = """
                SELECT
                    u.*,
                    COUNT(DISTINCT o.id) as total_orders,
                    COALESCE(SUM(CASE WHEN o.status != 'cancelled' THEN o.total_amount ELSE 0 END), 0) as total_spent
                FROM users u
                LEFT JOIN orders o ON u.id = o.user_id
                WHERE 1=1
            """
            params = []

            if search:
                query += """ AND (u.full_name LIKE %s OR u.email LIKE %s OR u.phone LIKE %s)"""
                search_term = f"%{search}%"
                params.extend([search_term, search_term, search_term])

            if tier:
                query += " AND u.membership_tier = %s"
                params.append(tier)

            query += """ GROUP BY u.id
                        ORDER BY u.created_at DESC
                        LIMIT %s OFFSET %s"""
            params.extend([limit, offset])

            users = db.fetch_all(query, tuple(params))
            return users if users else []

        except Exception as e:
            print(f"Error getting users: {e}")
            return []

    def get_user_by_id(self, user_id):
        """Get user by ID with statistics"""
        try:
            user = db.fetch_one(
                """SELECT
                    u.*,
                    COUNT(DISTINCT o.id) as total_orders,
                    COALESCE(SUM(CASE WHEN o.status != 'cancelled' THEN o.total_amount ELSE 0 END), 0) as total_spent,
                    COUNT(DISTINCT f.id) as total_favorites,
                    COUNT(DISTINCT r.id) as total_reviews
                FROM users u
                LEFT JOIN orders o ON u.id = o.user_id
                LEFT JOIN favorites f ON u.id = f.user_id
                LEFT JOIN reviews r ON u.id = r.user_id
                WHERE u.id = %s
                GROUP BY u.id""",
                (user_id,)
            )
            return user

        except Exception as e:
            print(f"Error getting user: {e}")
            return None

    def update_user_tier(self, user_id, new_tier, admin_id):
        """Update user membership tier"""
        try:
            # Validate tier
            valid_tiers = ['Bronze', 'Silver', 'Gold']
            if new_tier not in valid_tiers:
                return False, "Tier không hợp lệ"

            # Get old user data
            user = self.get_user_by_id(user_id)
            if not user:
                return False, "Không tìm thấy người dùng"

            old_tier = user['membership_tier']

            # Update tier
            db.execute_query(
                "UPDATE users SET membership_tier = %s, updated_at = NOW() WHERE id = %s",
                (new_tier, user_id)
            )

            # Log activity
            from controllers.admin_controller import AdminController
            admin_controller = AdminController()
            admin_controller.log_activity(admin_id, 'update_user_tier', 'users', user_id,
                                         {'tier': old_tier}, {'tier': new_tier})

            return True, f"Cập nhật tier thành công: {old_tier} → {new_tier}"

        except Exception as e:
            return False, f"Lỗi: {str(e)}"

    def update_loyalty_points(self, user_id, points, admin_id, reason=None):
        """Update user loyalty points"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False, "Không tìm thấy người dùng"

            old_points = user['loyalty_points']
            new_points = old_points + points

            if new_points < 0:
                return False, "Số điểm không được âm"

            # Update points
            db.execute_query(
                "UPDATE users SET loyalty_points = %s, updated_at = NOW() WHERE id = %s",
                (new_points, user_id)
            )

            # Add to points history
            try:
                db.execute_query(
                    """INSERT INTO loyalty_points_history
                       (user_id, points_change, transaction_type, description, created_at)
                       VALUES (%s, %s, 'admin_adjustment', %s, NOW())""",
                    (user_id, points, reason or 'Admin adjustment')
                )
            except:
                pass  # Table may not exist

            # Log activity
            from controllers.admin_controller import AdminController
            admin_controller = AdminController()
            admin_controller.log_activity(admin_id, 'update_loyalty_points', 'users', user_id,
                                         {'points': old_points}, {'points': new_points})

            return True, f"Cập nhật điểm thành công: {old_points} → {new_points}"

        except Exception as e:
            return False, f"Lỗi: {str(e)}"

    def toggle_user_status(self, user_id, admin_id):
        """Toggle user active status"""
        try:
            user = self.get_user_by_id(user_id)
            if not user:
                return False, "Không tìm thấy người dùng"

            new_status = not user['is_active']

            db.execute_query(
                "UPDATE users SET is_active = %s, updated_at = NOW() WHERE id = %s",
                (new_status, user_id)
            )

            # Log activity
            from controllers.admin_controller import AdminController
            admin_controller = AdminController()
            admin_controller.log_activity(admin_id, 'toggle_user_status', 'users', user_id,
                                         {'is_active': user['is_active']},
                                         {'is_active': new_status})

            status_text = "kích hoạt" if new_status else "khóa"
            return True, f"Đã {status_text} tài khoản"

        except Exception as e:
            return False, f"Lỗi: {str(e)}"

    def get_user_orders(self, user_id, limit=20):
        """Get user's orders"""
        try:
            orders = db.fetch_all(
                """SELECT o.*, s.name as store_name
                   FROM orders o
                   LEFT JOIN stores s ON o.store_id = s.id
                   WHERE o.user_id = %s
                   ORDER BY o.created_at DESC
                   LIMIT %s""",
                (user_id, limit)
            )
            return orders if orders else []

        except Exception as e:
            print(f"Error getting user orders: {e}")
            return []

    def get_user_statistics(self):
        """Get user statistics"""
        try:
            stats = {}

            # Total users
            result = db.fetch_one("SELECT COUNT(*) as count FROM users")
            stats['total'] = result['count'] if result else 0

            # Active users
            result = db.fetch_one("SELECT COUNT(*) as count FROM users WHERE is_active = 1")
            stats['active'] = result['count'] if result else 0

            # Users by tier
            result = db.fetch_all(
                """SELECT membership_tier, COUNT(*) as count
                   FROM users
                   GROUP BY membership_tier"""
            )
            stats['by_tier'] = {row['membership_tier']: row['count'] for row in result} if result else {}

            # New users this month
            result = db.fetch_one(
                """SELECT COUNT(*) as count FROM users
                   WHERE YEAR(created_at) = YEAR(CURDATE())
                   AND MONTH(created_at) = MONTH(CURDATE())"""
            )
            stats['new_this_month'] = result['count'] if result else 0

            return stats

        except Exception as e:
            print(f"Error getting user stats: {e}")
            return {}
