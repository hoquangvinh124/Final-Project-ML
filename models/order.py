"""
Order Model
"""
from typing import Optional, Dict, Any, List
from utils.database import db
from utils.helpers import generate_order_number, get_estimated_ready_time
from models.cart import Cart
import json


class Order:
    """Order model"""

    @staticmethod
    def create_from_cart(
        user_id: int,
        order_type: str,
        payment_method: str,
        store_id: Optional[int] = None,
        delivery_address: Optional[str] = None,
        table_number: Optional[str] = None,
        notes: Optional[str] = None,
        voucher_code: Optional[str] = None
    ) -> Optional[int]:
        """Create order from cart items"""
        # Get cart items
        cart_data = Cart.get_cart_total(user_id)
        if not cart_data['items']:
            return None

        # Calculate totals
        subtotal = cart_data['subtotal']
        discount_amount = 0

        # Apply voucher if provided
        if voucher_code:
            from models.voucher import Voucher
            voucher = Voucher.get_by_code(voucher_code)
            if voucher and Voucher.can_use(user_id, voucher['id'], subtotal):
                from utils.helpers import calculate_discount
                discount_amount = calculate_discount(
                    subtotal,
                    voucher['discount_type'],
                    float(voucher['discount_value']),
                    float(voucher['max_discount_amount']) if voucher['max_discount_amount'] else None
                )

        # Calculate delivery fee
        delivery_fee = 0
        if order_type == 'delivery':
            from utils.helpers import calculate_delivery_fee
            delivery_fee = calculate_delivery_fee(5, subtotal)  # Assume 5km for now

        total_amount = subtotal - discount_amount + delivery_fee

        # Generate order number
        order_number = generate_order_number()

        # Estimate ready time
        estimated_ready_time = get_estimated_ready_time(order_type, cart_data['item_count'])

        # Create order
        order_query = """
            INSERT INTO orders (
                user_id, order_number, store_id, order_type, status,
                subtotal, discount_amount, delivery_fee, total_amount,
                payment_method, delivery_address, table_number, notes,
                estimated_ready_time
            ) VALUES (%s, %s, %s, %s, 'pending', %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        order_id = db.insert(order_query, (
            user_id, order_number, store_id, order_type,
            subtotal, discount_amount, delivery_fee, total_amount,
            payment_method, delivery_address, table_number, notes,
            estimated_ready_time
        ))

        if not order_id:
            return None

        # Create order items from cart
        for item in cart_data['items']:
            topping_ids = json.loads(item['toppings']) if item['toppings'] else []
            topping_cost = 0

            if topping_ids:
                from models.topping import Topping
                topping_cost = Topping.calculate_total_price(topping_ids)

            item_query = """
                INSERT INTO order_items (
                    order_id, product_id, product_name, size, quantity,
                    unit_price, sugar_level, ice_level, temperature,
                    toppings, topping_cost, subtotal
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            db.insert(item_query, (
                order_id, item['product_id'], item['product_name'],
                item['size'], item['quantity'], item['unit_price'],
                item['sugar_level'], item['ice_level'], item['temperature'],
                item['toppings'], topping_cost, item['subtotal']
            ))

        # Mark voucher as used
        if voucher_code:
            from models.voucher import Voucher
            voucher = Voucher.get_by_code(voucher_code)
            if voucher:
                Voucher.use_voucher(user_id, voucher['id'])

        # Clear cart
        Cart.clear_cart(user_id)

        # Add loyalty points
        from utils.helpers import calculate_points_earned
        from models.user import User
        points = calculate_points_earned(total_amount)
        User.add_loyalty_points(user_id, points, f"Đơn hàng #{order_number}", order_id)

        return order_id

    @staticmethod
    def get_by_id(order_id: int) -> Optional[Dict[str, Any]]:
        """Get order by ID with full details"""
        query = """
            SELECT o.*, s.name as store_name, s.address as store_address,
                   u.full_name as customer_name, u.phone as customer_phone
            FROM orders o
            LEFT JOIN stores s ON o.store_id = s.id
            LEFT JOIN users u ON o.user_id = u.id
            WHERE o.id = %s
        """
        order = db.fetch_one(query, (order_id,))

        if order:
            # Get order items
            items_query = """
                SELECT oi.*, p.image
                FROM order_items oi
                LEFT JOIN products p ON oi.product_id = p.id
                WHERE oi.order_id = %s
            """
            order['items'] = db.fetch_all(items_query, (order_id,))

        return order

    @staticmethod
    def get_by_order_number(order_number: str) -> Optional[Dict[str, Any]]:
        """Get order by order number"""
        query = "SELECT * FROM orders WHERE order_number = %s"
        order = db.fetch_one(query, (order_number,))

        if order:
            # Get order items
            items_query = "SELECT * FROM order_items WHERE order_id = %s"
            order['items'] = db.fetch_all(items_query, (order['id'],))

        return order

    @staticmethod
    def get_user_orders(user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Get all orders for a user"""
        query = """
            SELECT o.*, s.name as store_name
            FROM orders o
            LEFT JOIN stores s ON o.store_id = s.id
            WHERE o.user_id = %s
            ORDER BY o.created_at DESC
            LIMIT %s
        """
        orders = db.fetch_all(query, (user_id, limit))

        # Get items count for each order
        for order in orders:
            count_query = """
                SELECT COUNT(*) as item_count, SUM(quantity) as total_quantity
                FROM order_items WHERE order_id = %s
            """
            count = db.fetch_one(count_query, (order['id'],))
            order['item_count'] = count['item_count'] if count else 0
            order['total_quantity'] = count['total_quantity'] if count else 0

        return orders

    @staticmethod
    def update_status(order_id: int, status: str) -> bool:
        """Update order status"""
        valid_statuses = ['pending', 'confirmed', 'preparing', 'ready',
                         'delivering', 'completed', 'cancelled']

        if status not in valid_statuses:
            return False

        query = "UPDATE orders SET status = %s WHERE id = %s"
        success = db.execute_query(query, (status, order_id))

        if success:
            # If completed, update completed_at
            if status == 'completed':
                db.execute_query("UPDATE orders SET completed_at = NOW() WHERE id = %s", (order_id,))
            # If cancelled, update cancelled_at
            elif status == 'cancelled':
                db.execute_query("UPDATE orders SET cancelled_at = NOW() WHERE id = %s", (order_id,))

            # Send notification to user
            order = Order.get_by_id(order_id)
            if order:
                from models.notification import Notification
                status_messages = {
                    'confirmed': 'Đơn hàng của bạn đã được xác nhận',
                    'preparing': 'Đơn hàng đang được chuẩn bị',
                    'ready': 'Đơn hàng của bạn đã sẵn sàng',
                    'delivering': 'Đơn hàng đang được giao',
                    'completed': 'Đơn hàng đã hoàn thành',
                    'cancelled': 'Đơn hàng đã bị hủy'
                }
                message = status_messages.get(status, f'Trạng thái đơn hàng: {status}')
                Notification.create(
                    order['user_id'],
                    f"Cập nhật đơn hàng #{order['order_number']}",
                    message,
                    'order_update',
                    order_id
                )

        return success

    @staticmethod
    def update_payment_status(order_id: int, payment_status: str) -> bool:
        """Update payment status"""
        valid_statuses = ['pending', 'paid', 'failed', 'refunded']

        if payment_status not in valid_statuses:
            return False

        query = "UPDATE orders SET payment_status = %s WHERE id = %s"
        return db.execute_query(query, (payment_status, order_id))

    @staticmethod
    def cancel_order(order_id: int, user_id: int, reason: Optional[str] = None) -> bool:
        """Cancel an order"""
        # Check if order belongs to user
        order = Order.get_by_id(order_id)
        if not order or order['user_id'] != user_id:
            return False

        # Can only cancel if status is pending or confirmed
        if order['status'] not in ['pending', 'confirmed']:
            return False

        query = """
            UPDATE orders
            SET status = 'cancelled', cancelled_at = NOW(), cancellation_reason = %s
            WHERE id = %s
        """
        return db.execute_query(query, (reason, order_id))

    @staticmethod
    def get_order_items(order_id: int) -> List[Dict[str, Any]]:
        """Get all items in an order"""
        query = """
            SELECT oi.*, p.image
            FROM order_items oi
            LEFT JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = %s
        """
        return db.fetch_all(query, (order_id,))
