"""
Authentication Controller
Handles login, registration, password reset, OTP verification
"""
from typing import Optional, Dict, Any, Tuple
from models.user import User
from utils.validators import (validate_email, validate_password, validate_phone,
                              validate_full_name, validate_otp)
from utils.helpers import generate_otp, session
from utils.database import db
from datetime import datetime, timedelta
from utils.config import OTP_EXPIRY_MINUTES


class AuthController:
    """Authentication controller"""

    @staticmethod
    def register(email: str, password: str, full_name: str, phone: Optional[str] = None) -> Tuple[bool, str, Optional[int]]:
        """
        Register a new user
        Returns: (success, message, user_id)
        """
        # Validate email
        is_valid, error = validate_email(email)
        if not is_valid:
            return False, error, None

        # Validate password
        is_valid, error = validate_password(password)
        if not is_valid:
            return False, error, None

        # Validate full name
        is_valid, error = validate_full_name(full_name)
        if not is_valid:
            return False, error, None

        # Validate phone if provided
        if phone:
            is_valid, error = validate_phone(phone)
            if not is_valid:
                return False, error, None

            # Check if phone exists
            if User.phone_exists(phone):
                return False, "Số điện thoại đã được sử dụng", None

        # Check if email exists
        if User.email_exists(email):
            return False, "Email đã được sử dụng", None

        # Create user
        user_id = User.create(email, password, full_name, phone)

        if user_id:
            return True, "Đăng ký thành công!", user_id
        else:
            return False, "Đăng ký thất bại. Vui lòng thử lại.", None

    @staticmethod
    def login(email: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Login user
        Returns: (success, message, user_data)
        """
        # Validate email
        is_valid, error = validate_email(email)
        if not is_valid:
            return False, error, None

        # Authenticate
        user = User.authenticate(email, password)

        if user:
            # Update session
            session.login(user)
            return True, "Đăng nhập thành công!", user
        else:
            return False, "Email hoặc mật khẩu không đúng", None

    @staticmethod
    def logout():
        """Logout user"""
        session.logout()

    @staticmethod
    def send_otp(identifier: str, purpose: str = 'registration') -> Tuple[bool, str]:
        """
        Send OTP to email or phone - DEPRECATED: OTP feature removed
        Returns: (success, message)
        """
        # OTP functionality has been removed from the system
        return False, "Tính năng OTP đã bị xóa khỏi hệ thống"

    @staticmethod
    def verify_otp(identifier: str, otp_code: str, purpose: str = 'registration') -> Tuple[bool, str]:
        """
        Verify OTP code - DEPRECATED: OTP feature removed
        Returns: (success, message)
        """
        # OTP functionality has been removed from the system
        return False, "Tính năng OTP đã bị xóa khỏi hệ thống"

    @staticmethod
    def reset_password(email: str, new_password: str) -> Tuple[bool, str]:
        """
        Reset password (simplified - OTP removed)
        Returns: (success, message)
        """
        # Validate new password
        is_valid, error = validate_password(new_password)
        if not is_valid:
            return False, error

        # Get user
        user = User.get_by_email(email)
        if not user:
            return False, "Không tìm thấy tài khoản"

        # Update password
        if User.update_password(user['id'], new_password):
            return True, "Đặt lại mật khẩu thành công!"
        else:
            return False, "Không thể đặt lại mật khẩu. Vui lòng thử lại."

    @staticmethod
    def change_password(user_id: int, old_password: str, new_password: str) -> Tuple[bool, str]:
        """
        Change password (requires old password)
        Returns: (success, message)
        """
        # Get user
        user = User.get_by_id(user_id)
        if not user:
            return False, "Không tìm thấy tài khoản"

        # Verify old password
        from utils.helpers import verify_password
        user_full = db.fetch_one("SELECT password_hash FROM users WHERE id = %s", (user_id,))
        if not user_full or not verify_password(old_password, user_full['password_hash']):
            return False, "Mật khẩu hiện tại không đúng"

        # Validate new password
        is_valid, error = validate_password(new_password)
        if not is_valid:
            return False, error

        # Update password
        if User.update_password(user_id, new_password):
            return True, "Đổi mật khẩu thành công!"
        else:
            return False, "Không thể đổi mật khẩu. Vui lòng thử lại."

    @staticmethod
    def is_logged_in() -> bool:
        """Check if user is logged in"""
        return session.is_logged_in

    @staticmethod
    def get_current_user() -> Optional[Dict[str, Any]]:
        """Get current logged in user"""
        return session.user_data

    @staticmethod
    def get_current_user_id() -> Optional[int]:
        """Get current user ID"""
        return session.user_id
