"""
Admin Voucher Controller
Handles voucher management from admin side
"""
from utils.database import db
from datetime import datetime


class AdminVoucherController:
    """Controller for admin voucher operations"""

    def get_all_vouchers(self, status=None, search=None, limit=100, offset=0):
        """Get all vouchers with filters"""
        try:
            query = """
                SELECT
                    v.*,
                    COUNT(DISTINCT vu.id) as usage_count
                FROM vouchers v
                LEFT JOIN voucher_usage vu ON v.id = vu.voucher_id
                WHERE 1=1
            """
            params = []

            if status == 'active':
                query += " AND v.is_active = 1 AND v.start_date <= NOW() AND v.end_date >= NOW()"
            elif status == 'expired':
                query += " AND v.end_date < NOW()"
            elif status == 'inactive':
                query += " AND v.is_active = 0"

            if search:
                query += " AND (v.code LIKE %s OR v.name LIKE %s)"
                search_term = f"%{search}%"
                params.extend([search_term, search_term])

            query += """ GROUP BY v.id
                        ORDER BY v.created_at DESC
                        LIMIT %s OFFSET %s"""
            params.extend([limit, offset])

            vouchers = db.fetch_all(query, tuple(params))
            return vouchers if vouchers else []

        except Exception as e:
            print(f"Error getting vouchers: {e}")
            return []

    def get_voucher_by_id(self, voucher_id):
        """Get voucher by ID"""
        try:
            voucher = db.fetch_one(
                """SELECT v.*, COUNT(DISTINCT vu.id) as usage_count
                   FROM vouchers v
                   LEFT JOIN voucher_usage vu ON v.id = vu.voucher_id
                   WHERE v.id = %s
                   GROUP BY v.id""",
                (voucher_id,)
            )
            return voucher

        except Exception as e:
            print(f"Error getting voucher: {e}")
            return None

    def create_voucher(self, data, admin_id):
        """Create new voucher"""
        try:
            # Required fields
            required = ['code', 'name', 'discount_type', 'discount_value', 'start_date', 'end_date']
            for field in required:
                if field not in data or data[field] is None or data[field] == '':
                    return False, f"Thiếu trường {field}"

            # Check if code exists
            existing = db.fetch_one(
                "SELECT id FROM vouchers WHERE code = %s",
                (data['code'],)
            )

            if existing:
                return False, "Mã voucher đã tồn tại"

            # Validate discount type
            if data['discount_type'] not in ['percentage', 'fixed']:
                return False, "Loại giảm giá không hợp lệ"

            # Validate percentage
            if data['discount_type'] == 'percentage' and (data['discount_value'] < 0 or data['discount_value'] > 100):
                return False, "Phần trăm giảm giá phải từ 0-100"

            # Insert voucher
            voucher_id = db.insert(
                """INSERT INTO vouchers
                   (code, name, description, discount_type, discount_value,
                    min_order_amount, max_discount_amount, usage_limit,
                    start_date, end_date, is_active, created_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())""",
                (
                    data['code'].upper(),
                    data['name'],
                    data.get('description', ''),
                    data['discount_type'],
                    data['discount_value'],
                    data.get('min_order_amount', 0),
                    data.get('max_discount_amount', None),
                    data.get('usage_limit', None),
                    data['start_date'],
                    data['end_date'],
                    data.get('is_active', True)
                )
            )

            # Log activity
            from controllers.admin_controller import AdminController
            admin_controller = AdminController()
            admin_controller.log_activity(admin_id, 'create_voucher', 'vouchers', voucher_id,
                                         None, {'code': data['code']})

            return True, f"Tạo voucher thành công (ID: {voucher_id})"

        except Exception as e:
            return False, f"Lỗi: {str(e)}"

    def update_voucher(self, voucher_id, data, admin_id):
        """Update voucher"""
        try:
            # Get old data
            old_voucher = self.get_voucher_by_id(voucher_id)

            if not old_voucher:
                return False, "Không tìm thấy voucher"

            # Required fields validation
            required = ['code', 'name', 'discount_type', 'discount_value', 'start_date', 'end_date']
            for field in required:
                if field not in data or data[field] is None or data[field] == '':
                    return False, f"Thiếu trường {field}"

            # Check if code exists (excluding current)
            if data['code'] != old_voucher['code']:
                existing = db.fetch_one(
                    "SELECT id FROM vouchers WHERE code = %s AND id != %s",
                    (data['code'], voucher_id)
                )

                if existing:
                    return False, "Mã voucher đã tồn tại"

            # Validate discount type
            if data['discount_type'] not in ['percentage', 'fixed']:
                return False, "Loại giảm giá không hợp lệ"

            # Validate percentage
            if data['discount_type'] == 'percentage' and (data['discount_value'] < 0 or data['discount_value'] > 100):
                return False, "Phần trăm giảm giá phải từ 0-100"

            # Update voucher
            db.execute_query(
                """UPDATE vouchers SET
                   code = %s, name = %s, description = %s, discount_type = %s,
                   discount_value = %s, min_order_amount = %s, max_discount_amount = %s,
                   usage_limit = %s, start_date = %s, end_date = %s,
                   is_active = %s
                   WHERE id = %s""",
                (
                    data['code'].upper(),
                    data['name'],
                    data.get('description', ''),
                    data['discount_type'],
                    data['discount_value'],
                    data.get('min_order_amount', 0),
                    data.get('max_discount_amount', None),
                    data.get('usage_limit', None),
                    data['start_date'],
                    data['end_date'],
                    data.get('is_active', True),
                    voucher_id
                )
            )

            # Log activity
            from controllers.admin_controller import AdminController
            admin_controller = AdminController()
            admin_controller.log_activity(admin_id, 'update_voucher', 'vouchers', voucher_id,
                                         {'code': old_voucher['code']},
                                         {'code': data['code']})

            return True, "Cập nhật voucher thành công"

        except Exception as e:
            return False, f"Lỗi: {str(e)}"

    def delete_voucher(self, voucher_id, admin_id):
        """Delete voucher"""
        try:
            # Check if voucher has been used
            voucher = self.get_voucher_by_id(voucher_id)

            if not voucher:
                return False, "Không tìm thấy voucher"

            if voucher['usage_count'] > 0:
                return False, f"Không thể xóa voucher đã được sử dụng {voucher['usage_count']} lần"

            # Delete voucher
            db.execute_query(
                "DELETE FROM vouchers WHERE id = %s",
                (voucher_id,)
            )

            # Log activity
            from controllers.admin_controller import AdminController
            admin_controller = AdminController()
            admin_controller.log_activity(admin_id, 'delete_voucher', 'vouchers', voucher_id,
                                         {'code': voucher['code']}, None)

            return True, "Xóa voucher thành công"

        except Exception as e:
            return False, f"Lỗi: {str(e)}"

    def toggle_voucher_status(self, voucher_id, admin_id):
        """Toggle voucher active status"""
        try:
            voucher = self.get_voucher_by_id(voucher_id)

            if not voucher:
                return False, "Không tìm thấy voucher"

            new_status = not voucher['is_active']

            db.execute_query(
                "UPDATE vouchers SET is_active = %s WHERE id = %s",
                (new_status, voucher_id)
            )

            # Log activity
            from controllers.admin_controller import AdminController
            admin_controller = AdminController()
            admin_controller.log_activity(admin_id, 'toggle_voucher_status', 'vouchers', voucher_id,
                                         {'is_active': voucher['is_active']},
                                         {'is_active': new_status})

            status_text = "kích hoạt" if new_status else "vô hiệu hóa"
            return True, f"Đã {status_text} voucher"

        except Exception as e:
            return False, f"Lỗi: {str(e)}"

    def get_voucher_usage_history(self, voucher_id, limit=50):
        """Get voucher usage history"""
        try:
            usage = db.fetch_all(
                """SELECT
                    vu.*,
                    u.full_name as user_name,
                    u.email as user_email,
                    o.id as order_id,
                    o.total_amount as order_total
                FROM voucher_usage vu
                LEFT JOIN users u ON vu.user_id = u.id
                LEFT JOIN orders o ON vu.order_id = o.id
                WHERE vu.voucher_id = %s
                ORDER BY vu.used_at DESC
                LIMIT %s""",
                (voucher_id, limit)
            )
            return usage if usage else []

        except Exception as e:
            print(f"Error getting voucher usage: {e}")
            return []

    def get_voucher_statistics(self):
        """Get voucher statistics"""
        try:
            stats = {}

            # Total vouchers
            result = db.fetch_one("SELECT COUNT(*) as count FROM vouchers")
            stats['total'] = result['count'] if result else 0

            # Active vouchers
            result = db.fetch_one(
                """SELECT COUNT(*) as count FROM vouchers
                   WHERE is_active = 1 AND start_date <= NOW() AND end_date >= NOW()"""
            )
            stats['active'] = result['count'] if result else 0

            # Expired vouchers
            result = db.fetch_one(
                "SELECT COUNT(*) as count FROM vouchers WHERE end_date < NOW()"
            )
            stats['expired'] = result['count'] if result else 0

            # Total usage
            result = db.fetch_one("SELECT COUNT(*) as count FROM voucher_usage")
            stats['total_usage'] = result['count'] if result else 0

            return stats

        except Exception as e:
            print(f"Error getting voucher stats: {e}")
            return {}
