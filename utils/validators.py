"""
Validation utilities for Coffee Shop Application
"""
import re
from typing import Optional, Tuple


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Validate email format
    Returns: (is_valid, error_message)
    """
    if not email:
        return False, "Email không được để trống"

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Email không hợp lệ"

    return True, None


def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
    """
    Validate Vietnamese phone number
    Returns: (is_valid, error_message)
    """
    if not phone:
        return False, "Số điện thoại không được để trống"

    # Remove spaces and dashes
    phone = phone.replace(" ", "").replace("-", "")

    # Vietnamese phone numbers: 10 digits, starts with 0
    pattern = r'^0[0-9]{9}$'
    if not re.match(pattern, phone):
        return False, "Số điện thoại không hợp lệ (phải có 10 chữ số và bắt đầu bằng 0)"

    return True, None


def validate_password(password: str) -> Tuple[bool, Optional[str]]:
    """
    Validate password strength
    Requirements:
    - At least 8 characters
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 digit
    Returns: (is_valid, error_message)
    """
    if not password:
        return False, "Mật khẩu không được để trống"

    if len(password) < 8:
        return False, "Mật khẩu phải có ít nhất 8 ký tự"

    if not re.search(r'[A-Z]', password):
        return False, "Mật khẩu phải có ít nhất 1 chữ hoa"

    if not re.search(r'[a-z]', password):
        return False, "Mật khẩu phải có ít nhất 1 chữ thường"

    if not re.search(r'\d', password):
        return False, "Mật khẩu phải có ít nhất 1 chữ số"

    return True, None


def validate_full_name(name: str) -> Tuple[bool, Optional[str]]:
    """
    Validate full name
    Returns: (is_valid, error_message)
    """
    if not name:
        return False, "Họ và tên không được để trống"

    if len(name.strip()) < 2:
        return False, "Họ và tên phải có ít nhất 2 ký tự"

    # Allow Vietnamese characters, spaces, and common name characters
    pattern = r'^[a-zA-ZàáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ\s]+$'
    if not re.match(pattern, name):
        return False, "Họ và tên chỉ được chứa chữ cái và khoảng trắng"

    return True, None


def validate_otp(otp: str) -> Tuple[bool, Optional[str]]:
    """
    Validate OTP code
    Returns: (is_valid, error_message)
    """
    if not otp:
        return False, "Mã OTP không được để trống"

    if not re.match(r'^\d{6}$', otp):
        return False, "Mã OTP phải có 6 chữ số"

    return True, None


def validate_price(price: float) -> Tuple[bool, Optional[str]]:
    """
    Validate price value
    Returns: (is_valid, error_message)
    """
    if price < 0:
        return False, "Giá không được âm"

    if price > 10000000:  # 10 million VND
        return False, "Giá quá cao"

    return True, None


def validate_quantity(quantity: int) -> Tuple[bool, Optional[str]]:
    """
    Validate quantity
    Returns: (is_valid, error_message)
    """
    if quantity <= 0:
        return False, "Số lượng phải lớn hơn 0"

    if quantity > 100:
        return False, "Số lượng không được vượt quá 100"

    return True, None


def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent XSS and SQL injection
    """
    if not text:
        return ""

    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '\\', ';', '--', '/*', '*/']
    sanitized = text
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')

    return sanitized.strip()


def format_currency(amount: float) -> str:
    """
    Format currency in VND
    """
    return f"{int(amount):,}đ".replace(',', '.')


def format_phone_display(phone: str) -> str:
    """
    Format phone number for display
    0123456789 -> 012 345 6789
    """
    if len(phone) == 10:
        return f"{phone[:3]} {phone[3:6]} {phone[6:]}"
    return phone
