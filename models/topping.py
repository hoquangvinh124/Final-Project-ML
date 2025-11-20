"""
Topping Model
"""
from typing import Optional, Dict, Any, List
from utils.database import db


class Topping:
    """Topping model"""

    @staticmethod
    def get_all(available_only: bool = True) -> List[Dict[str, Any]]:
        """Get all toppings"""
        query = """
            SELECT * FROM toppings
            WHERE is_available = TRUE
            ORDER BY name
        """ if available_only else """
            SELECT * FROM toppings
            ORDER BY name
        """
        return db.fetch_all(query)

    @staticmethod
    def get_by_id(topping_id: int) -> Optional[Dict[str, Any]]:
        """Get topping by ID"""
        query = "SELECT * FROM toppings WHERE id = %s"
        return db.fetch_one(query, (topping_id,))

    @staticmethod
    def get_by_ids(topping_ids: List[int]) -> List[Dict[str, Any]]:
        """Get multiple toppings by IDs"""
        if not topping_ids:
            return []

        placeholders = ', '.join(['%s'] * len(topping_ids))
        query = f"""
            SELECT * FROM toppings
            WHERE id IN ({placeholders})
            ORDER BY name
        """
        return db.fetch_all(query, tuple(topping_ids))

    @staticmethod
    def calculate_total_price(topping_ids: List[int]) -> float:
        """Calculate total price for selected toppings"""
        if not topping_ids:
            return 0

        toppings = Topping.get_by_ids(topping_ids)
        return sum(float(t['price']) for t in toppings)

    @staticmethod
    def calculate_total_calories(topping_ids: List[int]) -> int:
        """Calculate total calories for selected toppings"""
        if not topping_ids:
            return 0

        toppings = Topping.get_by_ids(topping_ids)
        return sum(int(t['calories']) for t in toppings)
