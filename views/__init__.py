"""
Views package initialization
"""
from .login_ex import LoginWindow
from .register_ex import RegisterWindow
from .main_window_ex import MainWindow
from .menu_ex import MenuWidget

# Placeholders for other views will be imported here
# from .cart_ex import CartWidget
# from .profile_ex import ProfileWidget
# from .orders_ex import OrdersWidget

__all__ = [
    'LoginWindow',
    'RegisterWindow',
    'MainWindow',
    'MenuWidget'
]
