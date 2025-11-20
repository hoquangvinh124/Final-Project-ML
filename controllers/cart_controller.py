"""
Cart Controller
Handles shopping cart operations
"""
from typing import Optional, Dict, Any, List, Tuple
from models.cart import Cart
from models.voucher import Voucher
from utils.validators import validate_quantity
from utils.helpers import calculate_delivery_fee, calculate_discount, session


class CartController:
    """Shopping cart controller"""

    @staticmethod
    def add_to_cart(
        user_id: int,
        product_id: int,
        size: str,
        quantity: int = 1,
        sugar_level: int = 50,
        ice_level: int = 50,
        temperature: str = 'cold',
        topping_ids: Optional[List[int]] = None
    ) -> Tuple[bool, str]:
        """
        Add item to cart
        Returns: (success, message)
        """
        # Validate quantity
        is_valid, error = validate_quantity(quantity)
        if not is_valid:
            return False, error

        # Add to cart
        success = Cart.add_item(
            user_id, product_id, size, quantity,
            sugar_level, ice_level, temperature, topping_ids
        )

        if success:
            # Update session cart count
            count = Cart.get_cart_count(user_id)
            session.update_cart_count(count)
            return True, "Đã thêm vào giỏ hàng"
        else:
            return False, "Không thể thêm vào giỏ hàng"

    @staticmethod
    def get_cart_items(user_id: int) -> List[Dict[str, Any]]:
        """Get all cart items"""
        return Cart.get_cart_items(user_id)

    @staticmethod
    def update_quantity(cart_id: int, user_id: int, quantity: int) -> Tuple[bool, str]:
        """
        Update cart item quantity
        Returns: (success, message)
        """
        if quantity <= 0:
            return CartController.remove_item(cart_id, user_id)

        # Validate quantity
        is_valid, error = validate_quantity(quantity)
        if not is_valid:
            return False, error

        success = Cart.update_quantity(cart_id, quantity, user_id)

        if success:
            # Update session cart count
            count = Cart.get_cart_count(user_id)
            session.update_cart_count(count)
            return True, "Đã cập nhật số lượng"
        else:
            return False, "Không thể cập nhật số lượng"

    @staticmethod
    def remove_item(cart_id: int, user_id: int) -> Tuple[bool, str]:
        """
        Remove item from cart
        Returns: (success, message)
        """
        success = Cart.remove_item(cart_id, user_id)

        if success:
            # Update session cart count
            count = Cart.get_cart_count(user_id)
            session.update_cart_count(count)
            return True, "Đã xóa khỏi giỏ hàng"
        else:
            return False, "Không thể xóa khỏi giỏ hàng"

    @staticmethod
    def clear_cart(user_id: int) -> Tuple[bool, str]:
        """
        Clear all items from cart
        Returns: (success, message)
        """
        success = Cart.clear_cart(user_id)

        if success:
            session.update_cart_count(0)
            return True, "Đã xóa tất cả sản phẩm"
        else:
            return False, "Không thể xóa giỏ hàng"

    @staticmethod
    def get_cart_summary(user_id: int, voucher_code: Optional[str] = None, order_type: str = 'pickup') -> Dict[str, Any]:
        """
        Get cart summary with totals
        Returns: cart summary with breakdown
        """
        cart_data = Cart.get_cart_total(user_id)

        subtotal = cart_data['subtotal']
        item_count = cart_data['item_count']
        items = cart_data['items']

        # Calculate discount
        discount_amount = 0
        voucher_info = None

        if voucher_code:
            voucher = Voucher.get_by_code(voucher_code)
            if voucher and Voucher.can_use(user_id, voucher['id'], subtotal):
                discount_amount = calculate_discount(
                    subtotal,
                    voucher['discount_type'],
                    float(voucher['discount_value']),
                    float(voucher['max_discount_amount']) if voucher['max_discount_amount'] else None
                )
                voucher_info = voucher

        # Calculate delivery fee
        delivery_fee = 0
        if order_type == 'delivery':
            delivery_fee = calculate_delivery_fee(5, subtotal)  # Assume 5km

        # Calculate total
        total = subtotal - discount_amount + delivery_fee

        return {
            'items': items,
            'item_count': item_count,
            'subtotal': subtotal,
            'discount_amount': discount_amount,
            'delivery_fee': delivery_fee,
            'total': total,
            'voucher': voucher_info
        }

    @staticmethod
    def validate_voucher(user_id: int, voucher_code: str, subtotal: float) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Validate voucher code
        Returns: (is_valid, message, voucher_data)
        """
        voucher = Voucher.get_by_code(voucher_code)

        if not voucher:
            return False, "Mã giảm giá không tồn tại", None

        if not Voucher.can_use(user_id, voucher['id'], subtotal):
            min_amount = float(voucher['min_order_amount'])
            if subtotal < min_amount:
                from utils.validators import format_currency
                return False, f"Đơn hàng tối thiểu {format_currency(min_amount)}", None
            else:
                return False, "Bạn đã sử dụng hết lượt dùng mã này", None

        return True, "Mã giảm giá hợp lệ", voucher

    @staticmethod
    def get_cart_count(user_id: int) -> int:
        """Get cart item count"""
        return Cart.get_cart_count(user_id)

    @staticmethod
    def update_item_customization(
        cart_id: int,
        user_id: int,
        **kwargs
    ) -> Tuple[bool, str]:
        """
        Update cart item customization
        Returns: (success, message)
        """
        success = Cart.update_item(cart_id, user_id, **kwargs)

        if success:
            return True, "Đã cập nhật tùy chọn"
        else:
            return False, "Không thể cập nhật"
