"""
Store/Branch Model
"""
from typing import Optional, Dict, Any, List
from utils.database import db


class Store:
    """Store/Branch model"""

    @staticmethod
    def get_all(active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all stores"""
        query = """
            SELECT * FROM stores
            WHERE is_active = TRUE
            ORDER BY name
        """ if active_only else """
            SELECT * FROM stores
            ORDER BY name
        """
        return db.fetch_all(query)

    @staticmethod
    def get_by_id(store_id: int) -> Optional[Dict[str, Any]]:
        """Get store by ID"""
        query = "SELECT * FROM stores WHERE id = %s"
        return db.fetch_one(query, (store_id,))

    @staticmethod
    def get_by_city(city: str) -> List[Dict[str, Any]]:
        """Get stores by city"""
        query = """
            SELECT * FROM stores
            WHERE city = %s AND is_active = TRUE
            ORDER BY name
        """
        return db.fetch_all(query, (city,))

    @staticmethod
    def search_nearby(latitude: float, longitude: float, radius_km: float = 10) -> List[Dict[str, Any]]:
        """Search stores near a location (simplified - actual implementation would use spatial queries)"""
        # Placeholder for proximity search
        # In production, use proper geospatial queries
        query = """
            SELECT *,
                   (6371 * acos(cos(radians(%s)) * cos(radians(latitude)) *
                   cos(radians(longitude) - radians(%s)) +
                   sin(radians(%s)) * sin(radians(latitude)))) AS distance
            FROM stores
            WHERE is_active = TRUE
              AND latitude IS NOT NULL
              AND longitude IS NOT NULL
            HAVING distance < %s
            ORDER BY distance
        """
        return db.fetch_all(query, (latitude, longitude, latitude, radius_km))
