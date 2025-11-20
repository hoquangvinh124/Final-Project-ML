"""
Helper utilities for Coffee Shop Application
"""
import hashlib
import random
import string
from datetime import datetime, timedelta
from typing import Optional


def hash_password(password: str) -> str:
    """
    Hash password using SHA-256
    """
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """
    Verify password against hash
    """
    return hash_password(password) == hashed


def generate_otp(length: int = 6) -> str:
    """
    Generate random OTP code
    """
    return ''.join(random.choices(string.digits, k=length))


def generate_order_number() -> str:
    """
    Generate unique order number
    Format: ORD-YYYYMMDD-XXXXXX
    """
    date_str = datetime.now().strftime('%Y%m%d')
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"ORD-{date_str}-{random_str}"


def calculate_age(birth_date: datetime) -> int:
    """
    Calculate age from birth date
    """
    today = datetime.now()
    age = today.year - birth_date.year
    if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
        age -= 1
    return age


def is_birthday_today(birth_date: datetime) -> bool:
    """
    Check if today is the person's birthday
    """
    today = datetime.now()
    return today.month == birth_date.month and today.day == birth_date.day


def calculate_points_earned(total_amount: float, points_per_vnd: float = 0.01) -> int:
    """
    Calculate loyalty points earned from purchase
    """
    return int(total_amount * points_per_vnd)


def calculate_membership_tier(total_points: int) -> str:
    """
    Calculate membership tier based on total points
    """
    if total_points >= 5000:
        return 'Gold'
    elif total_points >= 1000:
        return 'Silver'
    else:
        return 'Bronze'


def calculate_delivery_fee(distance_km: float, total_amount: float, free_shipping_threshold: float = 200000) -> float:
    """
    Calculate delivery fee based on distance and order total
    """
    if total_amount >= free_shipping_threshold:
        return 0

    base_fee = 20000  # 20k VND base fee
    if distance_km <= 3:
        return base_fee
    elif distance_km <= 5:
        return base_fee + 10000
    elif distance_km <= 10:
        return base_fee + 20000
    else:
        return base_fee + 30000


def calculate_discount(subtotal: float, discount_type: str, discount_value: float, max_discount: Optional[float] = None) -> float:
    """
    Calculate discount amount
    """
    if discount_type == 'percentage':
        discount = subtotal * (discount_value / 100)
        if max_discount:
            discount = min(discount, max_discount)
    else:  # fixed
        discount = discount_value

    return min(discount, subtotal)  # Discount can't exceed subtotal


def get_estimated_ready_time(order_type: str, item_count: int) -> datetime:
    """
    Estimate order ready time based on order type and item count
    """
    base_minutes = 15  # Base preparation time

    # Add time based on item count
    prep_minutes = base_minutes + (item_count * 3)

    # Adjust based on order type
    if order_type == 'delivery':
        prep_minutes += 30  # Add delivery time
    elif order_type == 'pickup':
        prep_minutes += 5

    return datetime.now() + timedelta(minutes=prep_minutes)


def format_datetime_vietnamese(dt: datetime) -> str:
    """
    Format datetime in Vietnamese format
    """
    return dt.strftime('%d/%m/%Y %H:%M')


def time_ago(dt: datetime) -> str:
    """
    Convert datetime to relative time (e.g., "2 giờ trước")
    """
    now = datetime.now()
    diff = now - dt

    seconds = diff.total_seconds()
    if seconds < 60:
        return "Vừa xong"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} phút trước"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} giờ trước"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days} ngày trước"
    else:
        return format_datetime_vietnamese(dt)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to specified length
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def validate_voucher_code(code: str) -> bool:
    """
    Validate voucher code format
    """
    # Voucher codes should be alphanumeric and 6-20 characters
    return bool(re.match(r'^[A-Z0-9]{6,20}$', code.upper()))


import re


def search_query_match(query: str, text: str) -> bool:
    """
    Check if search query matches text (case-insensitive)
    """
    query = query.lower().strip()
    text = text.lower()
    return query in text


def calculate_rating_summary(reviews: list) -> dict:
    """
    Calculate rating summary from reviews
    """
    if not reviews:
        return {
            'average': 0,
            'total': 0,
            'distribution': {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
        }

    total = len(reviews)
    total_rating = sum(r['rating'] for r in reviews)
    average = round(total_rating / total, 2)

    distribution = {5: 0, 4: 0, 3: 0, 2: 0, 1: 0}
    for review in reviews:
        rating = review['rating']
        distribution[rating] += 1

    return {
        'average': average,
        'total': total,
        'distribution': distribution
    }


class SessionManager:
    """Manage user session"""

    def __init__(self):
        self.user_id = None
        self.user_data = None
        self.cart_count = 0
        self.is_logged_in = False

    def login(self, user_data: dict):
        """Login user"""
        self.user_id = user_data['id']
        self.user_data = user_data
        self.is_logged_in = True

    def logout(self):
        """Logout user"""
        self.user_id = None
        self.user_data = None
        self.cart_count = 0
        self.is_logged_in = False

    def update_cart_count(self, count: int):
        """Update cart item count"""
        self.cart_count = count


# Global session instance
session = SessionManager()
