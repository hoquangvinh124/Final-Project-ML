"""
Order Controller
Handles order creation and management
"""
from typing import Optional, Dict, Any, List, Tuple
from models.order import Order
from models.store import Store
from models.review import Review


class OrderController:
    """Order management controller"""

    @staticmethod
    def create_order(
        user_id: int,
        order_type: str,  # 'pickup', 'delivery', 'dine_in'
        payment_method: str,
        store_id: Optional[int] = None,
        delivery_address: Optional[str] = None,
        table_number: Optional[str] = None,
        notes: Optional[str] = None,
        voucher_code: Optional[str] = None
    ) -> Tuple[bool, str, Optional[int]]:
        """
        Create order from cart
        Returns: (success, message, order_id)
        """
        # Validate order type
        if order_type not in ['pickup', 'delivery', 'dine_in']:
            return False, "Loại đơn hàng không hợp lệ", None

        # Validate payment method
        valid_payment_methods = ['cash', 'momo', 'shopeepay', 'zalopay', 'applepay', 'googlepay', 'card']
        if payment_method not in valid_payment_methods:
            return False, "Phương thức thanh toán không hợp lệ", None

        # Validate required fields based on order type
        if order_type == 'pickup' and not store_id:
            return False, "Vui lòng chọn cửa hàng", None

        if order_type == 'delivery' and not delivery_address:
            return False, "Vui lòng nhập địa chỉ giao hàng", None

        if order_type == 'dine_in' and not table_number:
            return False, "Vui lòng nhập số bàn", None

        # Create order
        order_id = Order.create_from_cart(
            user_id=user_id,
            order_type=order_type,
            payment_method=payment_method,
            store_id=store_id,
            delivery_address=delivery_address,
            table_number=table_number,
            notes=notes,
            voucher_code=voucher_code
        )

        if order_id:
            return True, "Đặt hàng thành công!", order_id
        else:
            return False, "Không thể đặt hàng. Vui lòng thử lại.", None

    @staticmethod
    def get_order_detail(order_id: int, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Get order details"""
        order = Order.get_by_id(order_id)

        # Check if order belongs to user (if user_id provided)
        if order and user_id and order['user_id'] != user_id:
            return None

        return order

    @staticmethod
    def get_user_orders(user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Get user's order history"""
        return Order.get_user_orders(user_id, limit)

    @staticmethod
    def track_order(order_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Get order tracking information"""
        order = Order.get_by_id(order_id)

        if not order or order['user_id'] != user_id:
            return None

        # Build tracking info
        status_timeline = {
            'pending': {'label': 'Đã tiếp nhận', 'completed': False},
            'confirmed': {'label': 'Đã xác nhận', 'completed': False},
            'preparing': {'label': 'Đang pha chế', 'completed': False},
            'ready': {'label': 'Đã hoàn thành', 'completed': False},
            'delivering': {'label': 'Đang giao hàng', 'completed': False},
            'completed': {'label': 'Hoàn thành', 'completed': False}
        }

        # Mark completed statuses
        current_status = order['status']
        status_order = ['pending', 'confirmed', 'preparing', 'ready', 'delivering', 'completed']

        if current_status == 'cancelled':
            return {
                'order': order,
                'status': 'Đã hủy',
                'timeline': []
            }

        current_index = status_order.index(current_status) if current_status in status_order else -1

        for i, status in enumerate(status_order):
            if i <= current_index:
                status_timeline[status]['completed'] = True

        # Skip 'delivering' for non-delivery orders
        timeline = []
        for status, info in status_timeline.items():
            if status == 'delivering' and order['order_type'] != 'delivery':
                continue
            timeline.append({
                'status': status,
                'label': info['label'],
                'completed': info['completed']
            })

        return {
            'order': order,
            'current_status': current_status,
            'timeline': timeline,
            'estimated_ready_time': order.get('estimated_ready_time')
        }

    @staticmethod
    def cancel_order(order_id: int, user_id: int, reason: Optional[str] = None) -> Tuple[bool, str]:
        """
        Cancel an order
        Returns: (success, message)
        """
        success = Order.cancel_order(order_id, user_id, reason)

        if success:
            return True, "Đơn hàng đã được hủy"
        else:
            return False, "Không thể hủy đơn hàng này"

    @staticmethod
    def get_available_stores() -> List[Dict[str, Any]]:
        """Get all available stores for pickup"""
        return Store.get_all()

    @staticmethod
    def get_stores_by_city(city: str) -> List[Dict[str, Any]]:
        """Get stores by city"""
        return Store.get_by_city(city)

    @staticmethod
    def submit_review(
        user_id: int,
        product_id: int,
        order_id: int,
        rating: int,
        comment: Optional[str] = None,
        service_rating: Optional[int] = None
    ) -> Tuple[bool, str]:
        """
        Submit product review
        Returns: (success, message)
        """
        # Validate rating
        if rating < 1 or rating > 5:
            return False, "Đánh giá phải từ 1-5 sao"

        if service_rating and (service_rating < 1 or service_rating > 5):
            return False, "Đánh giá dịch vụ phải từ 1-5 sao"

        # Create review
        review_id = Review.create(
            user_id=user_id,
            product_id=product_id,
            order_id=order_id,
            rating=rating,
            comment=comment,
            service_rating=service_rating
        )

        if review_id:
            return True, "Cảm ơn bạn đã đánh giá!"
        else:
            return False, "Không thể gửi đánh giá"

    @staticmethod
    def reorder(order_id: int, user_id: int) -> Tuple[bool, str]:
        """
        Reorder items from a previous order
        Returns: (success, message)
        """
        order = Order.get_by_id(order_id)

        if not order or order['user_id'] != user_id:
            return False, "Không tìm thấy đơn hàng"

        # Get order items
        items = Order.get_order_items(order_id)

        # Add items to cart
        from controllers.cart_controller import CartController
        import json

        for item in items:
            topping_ids = json.loads(item['toppings']) if item['toppings'] else None

            success, _ = CartController.add_to_cart(
                user_id=user_id,
                product_id=item['product_id'],
                size=item['size'],
                quantity=item['quantity'],
                sugar_level=item['sugar_level'],
                ice_level=item['ice_level'],
                temperature=item['temperature'],
                topping_ids=topping_ids
            )

            if not success:
                return False, "Không thể thêm một số sản phẩm vào giỏ hàng"

        return True, "Đã thêm vào giỏ hàng"
