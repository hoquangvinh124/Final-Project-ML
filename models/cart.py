"""
Shopping Cart Model
"""
from typing import Optional, Dict, Any, List
from utils.database import db
from models.product import Product
from models.topping import Topping
import json


class Cart:
    """Shopping cart model"""

    @staticmethod
    def add_item(
        user_id: int,
        product_id: int,
        size: str,
        quantity: int,
        sugar_level: int = 50,
        ice_level: int = 50,
        temperature: str = 'cold',
        topping_ids: Optional[List[int]] = None
    ) -> bool:
        """Add item to cart"""
        toppings_json = json.dumps(topping_ids) if topping_ids else None

        # Check if exact same item exists (same product, size, customizations)
        check_query = """
            SELECT id, quantity FROM cart
            WHERE user_id = %s AND product_id = %s AND size = %s
              AND sugar_level = %s AND ice_level = %s AND temperature = %s
              AND toppings = %s
        """
        existing = db.fetch_one(check_query, (user_id, product_id, size, sugar_level,
                                              ice_level, temperature, toppings_json))

        if existing:
            # Update quantity
            update_query = "UPDATE cart SET quantity = quantity + %s WHERE id = %s"
            return db.execute_query(update_query, (quantity, existing['id']))
        else:
            # Insert new item
            insert_query = """
                INSERT INTO cart (user_id, product_id, size, quantity, sugar_level,
                                ice_level, temperature, toppings)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cart_id = db.insert(insert_query, (user_id, product_id, size, quantity,
                                              sugar_level, ice_level, temperature, toppings_json))
            return cart_id is not None

    @staticmethod
    def get_cart_items(user_id: int) -> List[Dict[str, Any]]:
        """Get all cart items for a user with product details"""
        query = """
            SELECT c.*, p.name as product_name, p.name_en as product_name_en,
                   p.image as product_image, p.base_price, p.is_available
            FROM cart c
            JOIN products p ON c.product_id = p.id
            WHERE c.user_id = %s
            ORDER BY c.created_at DESC
        """
        items = db.fetch_all(query, (user_id,))

        # Calculate prices for each item
        for item in items:
            # Parse toppings JSON
            topping_ids = json.loads(item['toppings']) if item['toppings'] else []

            # Calculate item price
            item_price = Product.calculate_price(item['product_id'], item['size'], topping_ids)
            item['unit_price'] = item_price
            item['subtotal'] = item_price * item['quantity']
            item['topping_ids'] = topping_ids

            # Get topping details
            if topping_ids:
                item['topping_details'] = Topping.get_by_ids(topping_ids)
            else:
                item['topping_details'] = []

        return items

    @staticmethod
    def update_quantity(cart_id: int, quantity: int, user_id: int) -> bool:
        """Update cart item quantity"""
        if quantity <= 0:
            return Cart.remove_item(cart_id, user_id)

        query = "UPDATE cart SET quantity = %s WHERE id = %s AND user_id = %s"
        return db.execute_query(query, (quantity, cart_id, user_id))

    @staticmethod
    def remove_item(cart_id: int, user_id: int) -> bool:
        """Remove item from cart"""
        query = "DELETE FROM cart WHERE id = %s AND user_id = %s"
        return db.execute_query(query, (cart_id, user_id))

    @staticmethod
    def clear_cart(user_id: int) -> bool:
        """Clear all items from cart"""
        query = "DELETE FROM cart WHERE user_id = %s"
        return db.execute_query(query, (user_id,))

    @staticmethod
    def get_cart_count(user_id: int) -> int:
        """Get total number of items in cart"""
        query = "SELECT COALESCE(SUM(quantity), 0) as count FROM cart WHERE user_id = %s"
        result = db.fetch_one(query, (user_id,))
        return int(result['count']) if result else 0

    @staticmethod
    def get_cart_total(user_id: int) -> Dict[str, float]:
        """Get cart totals"""
        items = Cart.get_cart_items(user_id)

        subtotal = sum(item['subtotal'] for item in items)
        item_count = sum(item['quantity'] for item in items)

        return {
            'subtotal': subtotal,
            'item_count': item_count,
            'items': items
        }

    @staticmethod
    def update_item(
        cart_id: int,
        user_id: int,
        size: Optional[str] = None,
        quantity: Optional[int] = None,
        sugar_level: Optional[int] = None,
        ice_level: Optional[int] = None,
        temperature: Optional[str] = None,
        topping_ids: Optional[List[int]] = None
    ) -> bool:
        """Update cart item customization"""
        update_fields = []
        values = []

        if size:
            update_fields.append("size = %s")
            values.append(size)

        if quantity is not None:
            update_fields.append("quantity = %s")
            values.append(quantity)

        if sugar_level is not None:
            update_fields.append("sugar_level = %s")
            values.append(sugar_level)

        if ice_level is not None:
            update_fields.append("ice_level = %s")
            values.append(ice_level)

        if temperature:
            update_fields.append("temperature = %s")
            values.append(temperature)

        if topping_ids is not None:
            update_fields.append("toppings = %s")
            values.append(json.dumps(topping_ids))

        if not update_fields:
            return False

        values.extend([cart_id, user_id])
        query = f"UPDATE cart SET {', '.join(update_fields)} WHERE id = %s AND user_id = %s"
        return db.execute_query(query, tuple(values))
