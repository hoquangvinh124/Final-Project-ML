"""
Admin Order Controller
Handles order management from admin side
"""
from utils.database import db


class AdminOrderController:
    """Controller for admin order operations"""

    def get_all_orders(self, status=None, date_from=None, date_to=None, limit=100, offset=0):
        """Get all orders with filters"""
        try:
            query = """
                SELECT
                    o.*,
                    u.full_name as customer_name,
                    u.email as customer_email,
                    u.phone as customer_phone,
                    s.name as store_name,
                    s.address as store_address
                FROM orders o
                LEFT JOIN users u ON o.user_id = u.id
                LEFT JOIN stores s ON o.store_id = s.id
                WHERE 1=1
            """
            params = []

            # Filter by status
            if status:
                query += " AND o.status = %s"
                params.append(status)

            # Filter by date range
            if date_from:
                query += " AND DATE(o.created_at) >= %s"
                params.append(date_from)

            if date_to:
                query += " AND DATE(o.created_at) <= %s"
                params.append(date_to)

            query += " ORDER BY o.created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, offset])

            orders = db.fetch_all(query, tuple(params))
            return orders if orders else []

        except Exception as e:
            print(f"Error getting orders: {e}")
            return []

    def get_order_details(self, order_id):
        """Get detailed order information"""
        try:
            # Get order info
            order = db.fetch_one(
                """SELECT
                    o.*,
                    u.full_name as customer_name,
                    u.email as customer_email,
                    u.phone as customer_phone,
                    s.name as store_name,
                    s.address as store_address,
                    s.phone as store_phone
                FROM orders o
                LEFT JOIN users u ON o.user_id = u.id
                LEFT JOIN stores s ON o.store_id = s.id
                WHERE o.id = %s""",
                (order_id,)
            )

            if not order:
                return None

            # Get order items
            items = db.fetch_all(
                """SELECT
                    oi.*,
                    p.name as product_name,
                    p.image_url as product_image
                FROM order_items oi
                LEFT JOIN products p ON oi.product_id = p.id
                WHERE oi.order_id = %s""",
                (order_id,)
            )

            order['items'] = items if items else []

            return order

        except Exception as e:
            print(f"Error getting order details: {e}")
            return None

    def update_order_status(self, order_id, new_status, admin_id, notes=None):
        """Update order status"""
        try:
            # Validate status
            valid_statuses = ['pending', 'confirmed', 'preparing', 'ready',
                            'delivering', 'completed', 'cancelled']

            if new_status not in valid_statuses:
                return False, "Trạng thái không hợp lệ"

            # Get current order
            order = db.fetch_one(
                "SELECT id, status, user_id FROM orders WHERE id = %s",
                (order_id,)
            )

            if not order:
                return False, "Không tìm thấy đơn hàng"

            old_status = order['status']

            # Update status
            db.execute_query(
                "UPDATE orders SET status = %s, updated_at = NOW() WHERE id = %s",
                (new_status, order_id)
            )

            # Add status change to order_status_history if table exists
            try:
                db.execute_query(
                    """INSERT INTO order_status_history
                       (order_id, old_status, new_status, changed_by_admin_id, notes, created_at)
                       VALUES (%s, %s, %s, %s, %s, NOW())""",
                    (order_id, old_status, new_status, admin_id, notes)
                )
            except:
                pass  # Table may not exist yet

            # Create notification for customer
            try:
                status_messages = {
                    'confirmed': f'Đơn hàng #{order_id} đã được xác nhận',
                    'preparing': f'Đơn hàng #{order_id} đang được pha chế',
                    'ready': f'Đơn hàng #{order_id} đã sẵn sàng để lấy',
                    'delivering': f'Đơn hàng #{order_id} đang được giao',
                    'completed': f'Đơn hàng #{order_id} đã hoàn thành',
                    'cancelled': f'Đơn hàng #{order_id} đã bị hủy'
                }

                message = status_messages.get(new_status,
                                             f'Đơn hàng #{order_id} đã cập nhật trạng thái')

                db.execute_query(
                    """INSERT INTO notifications
                       (user_id, type, title, message, created_at)
                       VALUES (%s, 'order_status', %s, %s, NOW())""",
                    (order['user_id'], f'Cập nhật đơn hàng #{order_id}', message)
                )
            except:
                pass  # Notifications optional

            return True, "Cập nhật trạng thái thành công"

        except Exception as e:
            return False, f"Lỗi: {str(e)}"

    def cancel_order(self, order_id, admin_id, reason):
        """Cancel an order"""
        return self.update_order_status(order_id, 'cancelled', admin_id, reason)

    def get_order_statistics(self, date_from=None, date_to=None):
        """Get order statistics"""
        try:
            stats = {}

            where_clause = "WHERE 1=1"
            params = []

            if date_from:
                where_clause += " AND DATE(created_at) >= %s"
                params.append(date_from)

            if date_to:
                where_clause += " AND DATE(created_at) <= %s"
                params.append(date_to)

            # Orders by status
            query = f"""
                SELECT status, COUNT(*) as count
                FROM orders
                {where_clause}
                GROUP BY status
            """
            result = db.fetch_all(query, tuple(params) if params else None)
            stats['by_status'] = {row['status']: row['count'] for row in result} if result else {}

            # Revenue by day
            query = f"""
                SELECT DATE(created_at) as date, SUM(total_amount) as revenue, COUNT(*) as orders
                FROM orders
                {where_clause} AND status != 'cancelled'
                GROUP BY DATE(created_at)
                ORDER BY date DESC
                LIMIT 30
            """
            result = db.fetch_all(query, tuple(params) if params else None)
            stats['by_date'] = result if result else []

            return stats

        except Exception as e:
            print(f"Error getting order statistics: {e}")
            return {}

    def search_orders(self, keyword):
        """Search orders by order ID, customer name, email, or phone"""
        try:
            query = """
                SELECT
                    o.*,
                    u.full_name as customer_name,
                    u.email as customer_email,
                    u.phone as customer_phone,
                    s.name as store_name
                FROM orders o
                LEFT JOIN users u ON o.user_id = u.id
                LEFT JOIN stores s ON o.store_id = s.id
                WHERE o.id LIKE %s
                   OR u.full_name LIKE %s
                   OR u.email LIKE %s
                   OR u.phone LIKE %s
                ORDER BY o.created_at DESC
                LIMIT 50
            """

            search_term = f"%{keyword}%"
            orders = db.fetch_all(query, (search_term, search_term, search_term, search_term))

            return orders if orders else []

        except Exception as e:
            print(f"Error searching orders: {e}")
            return []
