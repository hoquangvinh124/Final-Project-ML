"""
Admin Main Window - Extended Logic
Main admin window with navigation
"""
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import pyqtSignal
from ui_generated.admin_main_window import Ui_AdminMainWindow
from controllers.admin_controller import AdminController
from views.admin_ml_analytics_ex import AdminMLAnalyticsWidget


class AdminMainWindow(QMainWindow, Ui_AdminMainWindow):
    """Admin main window"""

    logout_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        
        # Hide status bar to remove bottom white space
        self.statusbar.hide()

        self.admin_controller = AdminController()

        # Apply sidebar styling
        self.apply_sidebar_style()

        # Connect navigation buttons
        self.dashboardButton.clicked.connect(lambda: self.switch_page(0))
        self.ordersButton.clicked.connect(lambda: self.switch_page(1))
        self.productsButton.clicked.connect(lambda: self.switch_page(2))
        self.usersButton.clicked.connect(lambda: self.switch_page(3))
        self.categoriesButton.clicked.connect(lambda: self.switch_page(4))
        self.vouchersButton.clicked.connect(lambda: self.switch_page(5))
        self.reportsButton.clicked.connect(lambda: self.switch_page(6))
        self.mlAnalyticsButton.clicked.connect(lambda: self.switch_page(7))
        self.logoutButton.clicked.connect(self.handle_logout)

        # Load admin data
        self.load_admin_info()

    def apply_sidebar_style(self):
        """Apply styling to sidebar"""
        self.sidebarWidget.setStyleSheet("""
            #sidebarWidget {
                background-color: #2c2c2c;
                border-right: 1px solid #444444;
            }
            #sidebarWidget QLabel {
                color: #ffffff;
            }
            #sidebarWidget QPushButton {
                background-color: transparent;
                color: #ffffff;
                text-align: left;
                padding: 12px 20px;
                border: none;
                border-radius: 8px;
                margin: 4px 8px;
                font-size: 14px;
            }
            #sidebarWidget QPushButton:hover {
                background-color: #3c3c3c;
            }
            #sidebarWidget QPushButton:pressed {
                background-color: #4c4c4c;
            }
            #sidebarWidget QPushButton[active="true"] {
                background-color: #c7a17a;
                color: #ffffff;
            }
            #adminInfoWidget {
                background-color: #3c3c3c;
                border-radius: 8px;
                padding: 10px;
                margin: 8px;
            }
        """)

    def load_admin_info(self):
        """Load and display admin information"""
        # Set explicit styles
        self.adminNameLabel.setStyleSheet("color: #ffffff; font-weight: bold;")
        self.adminRoleLabel.setStyleSheet("color: #ffffff;")

        admin = self.admin_controller.get_current_admin()

        if admin:
            self.adminNameLabel.setText(admin.get('full_name', 'Admin'))

            # Display role
            role = admin.get('role', 'staff')
            role_names = {
                'super_admin': 'System Administrator',
                'admin': 'Admin',
                'manager': 'Manager',
                'staff': 'Staff'
            }
            name = role_names.get(role, 'Staff')
            self.adminRoleLabel.setText(name)

    def switch_page(self, index: int):
        """Switch to different page"""
        if index < self.contentStackedWidget.count():
            self.contentStackedWidget.setCurrentIndex(index)

            # Update button styles
            buttons = [
                self.dashboardButton,
                self.ordersButton,
                self.productsButton,
                self.usersButton,
                self.categoriesButton,
                self.vouchersButton,
                self.reportsButton,
                self.mlAnalyticsButton
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
        """Handle logout"""
        reply = QMessageBox.question(
            self,
            "Đăng xuất",
            "Bạn có chắc chắn muốn đăng xuất?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.admin_controller.logout()
            self.logout_requested.emit()
