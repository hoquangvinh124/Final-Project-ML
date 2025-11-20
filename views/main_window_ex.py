"""
Main Window - Extended Logic
Main application window with navigation
"""
from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.QtCore import pyqtSignal
from ui_generated.main_window import Ui_MainWindow
from controllers.auth_controller import AuthController
from controllers.user_controller import UserController
from controllers.cart_controller import CartController
from utils.helpers import session


class MainWindow(QMainWindow, Ui_MainWindow):
    """Main window with navigation and content management"""

    # Signals
    logout_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        
        # Hide status bar to remove bottom white space
        self.statusbar.hide()

        self.auth_controller = AuthController()
        self.user_controller = UserController()
        self.cart_controller = CartController()

        # Connect navigation buttons
        self.menuButton.clicked.connect(lambda: self.switch_page(0))
        self.cartButton.clicked.connect(lambda: self.switch_page(1))
        self.ordersButton.clicked.connect(lambda: self.switch_page(2))
        self.favoritesButton.clicked.connect(lambda: self.switch_page(3))
        self.profileButton.clicked.connect(lambda: self.switch_page(4))
        self.logoutButton.clicked.connect(self.handle_logout)

        # Load user data
        self.load_user_info()

        # Update cart count
        self.update_cart_count()

    def load_user_info(self):
        """Load and display user information"""
        # Set explicit styles for user info labels to ensure visibility
        self.userNameLabel.setStyleSheet("color: #ffffff; font-weight: bold;")
        self.userTierLabel.setStyleSheet("color: #ffffff;")
        self.userPointsLabel.setStyleSheet("color: #ffffff;")

        user_data = self.auth_controller.get_current_user()

        if user_data:
            self.userNameLabel.setText(f"Xin chào, {user_data.get('full_name', 'User')}!")

            # Display membership tier
            tier = user_data.get('membership_tier', 'Bronze')
            self.userTierLabel.setText(f"{tier} Member")

            # Display points
            points = user_data.get('loyalty_points', 0)
            self.userPointsLabel.setText(f"{points:,} điểm".replace(',', '.'))

    def update_cart_count(self):
        """Update cart item count in navigation"""
        user_id = self.auth_controller.get_current_user_id()
        if user_id:
            count = self.cart_controller.get_cart_count(user_id)
            self.cartButton.setText(f"Giỏ hàng ({count})")

    def switch_page(self, index: int):
        """Switch to different page in stacked widget"""
        # Check if page exists
        if index < self.contentStackedWidget.count():
            self.contentStackedWidget.setCurrentIndex(index)

            # Update button styles to show active page
            buttons = [
                self.menuButton,
                self.cartButton,
                self.ordersButton,
                self.favoritesButton,
                self.profileButton
            ]

            for i, btn in enumerate(buttons):
                if i == index:
                    btn.setProperty("active", True)
                else:
                    btn.setProperty("active", False)
                btn.style().unpolish(btn)
                btn.style().polish(btn)

    def add_content_page(self, widget):
        """Add a new page to content area"""
        self.contentStackedWidget.addWidget(widget)

    def handle_logout(self):
        """Handle logout button click"""
        reply = QMessageBox.question(
            self,
            "Đăng xuất",
            "Bạn có chắc chắn muốn đăng xuất?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.auth_controller.logout()
            self.logout_requested.emit()
