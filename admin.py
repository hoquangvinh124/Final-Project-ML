#!/usr/bin/env python3
"""
Coffee Shop Admin Panel - Main Entry Point
Admin interface for managing coffee shop operations
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QStackedWidget, QMessageBox
from PyQt6.QtCore import Qt

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from views.admin_login_ex import AdminLoginWidget
from views.admin_main_window_ex import AdminMainWindow
from views.admin_dashboard_ex import AdminDashboardWidget
from views.admin_orders_ex import AdminOrdersWidget
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout
from utils.database import db
from utils.config import STYLES_DIR, APP_NAME


class CoffeeShopAdminApp:
    """Main admin application class"""

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName(f"{APP_NAME} - Admin Panel")

        # Load stylesheet
        self.load_stylesheet()

        # Initialize windows
        self.login_window = None
        self.main_window = None

        # Create stacked widget for window management
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setWindowTitle(f"{APP_NAME} - Admin Panel")
        self.stacked_widget.resize(500, 600)

        # Test database connection
        self.check_database_connection()

        # Setup windows
        self.setup_windows()

        # Show login window
        self.show_login()

    def load_stylesheet(self):
        """Load application stylesheet"""
        try:
            style_file = STYLES_DIR / 'style.qss'
            if style_file.exists():
                with open(style_file, 'r', encoding='utf-8') as f:
                    self.app.setStyleSheet(f.read())
        except Exception as e:
            print(f"Warning: Could not load stylesheet: {e}")

    def check_database_connection(self):
        """Check database connection on startup"""
        try:
            if not db.test_connection():
                QMessageBox.critical(
                    None,
                    "Lỗi Kết Nối Database",
                    "Không thể kết nối đến database MySQL.\n\n"
                    "Vui lòng kiểm tra:\n"
                    "1. MySQL server đang chạy\n"
                    "2. Thông tin kết nối trong utils/config.py\n"
                    "3. Database 'coffee_shop' đã được tạo\n"
                    "4. Chạy file database/admin_schema.sql để tạo bảng admin"
                )
                sys.exit(1)

            # Check if admin tables exist
            result = db.fetch_one(
                "SELECT COUNT(*) as count FROM information_schema.tables "
                "WHERE table_schema = 'coffee_shop' AND table_name = 'admin_users'"
            )

            if not result or result['count'] == 0:
                reply = QMessageBox.question(
                    None,
                    "Thiếu bảng Admin",
                    "Chưa có bảng admin_users trong database.\n\n"
                    "Bạn có muốn tạo bảng admin ngay bây giờ không?\n"
                    "(File database/admin_schema.sql cần được chạy)",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )

                if reply == QMessageBox.StandardButton.Yes:
                    QMessageBox.information(
                        None,
                        "Hướng dẫn",
                        "Vui lòng chạy file database/admin_schema.sql trong MySQL:\n\n"
                        "mysql -u root -p coffee_shop < database/admin_schema.sql\n\n"
                        "Sau đó khởi động lại ứng dụng.\n\n"
                        "Tài khoản mặc định:\n"
                        "Username: admin\n"
                        "Password: admin123"
                    )
                sys.exit(0)

        except Exception as e:
            QMessageBox.critical(
                None,
                "Lỗi Database",
                f"Lỗi khi kiểm tra database: {str(e)}"
            )
            sys.exit(1)

    def setup_windows(self):
        """Setup all application windows"""
        # Login window
        self.login_window = AdminLoginWidget()
        self.login_window.login_successful.connect(self.handle_login_successful)
        self.stacked_widget.addWidget(self.login_window)

    def show_login(self):
        """Show login window"""
        self.stacked_widget.setCurrentWidget(self.login_window)
        self.stacked_widget.show()

    def handle_login_successful(self, admin_data):
        """Handle successful admin login"""
        # Create main window
        self.main_window = AdminMainWindow()
        self.main_window.logout_requested.connect(self.handle_logout)

        # Create and add dashboard
        dashboard_widget = AdminDashboardWidget()
        self.main_window.add_content_page(dashboard_widget)

        # Create and add orders management
        orders_widget = AdminOrdersWidget()
        self.main_window.add_content_page(orders_widget)

        # Products management
        from views.admin_products_ex import AdminProductsWidget
        products_widget = AdminProductsWidget()
        self.main_window.add_content_page(products_widget)

        # Users management
        from views.admin_users_ex import AdminUsersWidget
        users_widget = AdminUsersWidget()
        self.main_window.add_content_page(users_widget)

        # Categories management
        from views.admin_categories_ex import AdminCategoriesWidget
        categories_widget = AdminCategoriesWidget()
        self.main_window.add_content_page(categories_widget)

        # Vouchers management
        from views.admin_vouchers_ex import AdminVouchersWidget
        vouchers_widget = AdminVouchersWidget()
        self.main_window.add_content_page(vouchers_widget)

        # KPI Prediction
        from views.admin_logistic_kpi_ex import AdminLogisticKPIWidget
        kpi_widget = AdminLogisticKPIWidget()
        self.main_window.add_content_page(kpi_widget)

        # Reports (placeholder for now)
        reports_page = QWidget()
        reports_layout = QVBoxLayout(reports_page)
        reports_layout.addWidget(QLabel("📈 Báo cáo - Đang phát triển"))
        self.main_window.add_content_page(reports_page)

        # Store references
        self.dashboard_widget = dashboard_widget
        self.orders_widget = orders_widget

        # Switch to dashboard
        self.main_window.switch_page(0)

        # Hide stacked widget and show main window
        self.stacked_widget.hide()
        self.main_window.showMaximized()

    def handle_logout(self):
        """Handle admin logout"""
        # Close main window
        if self.main_window:
            self.main_window.close()
            self.main_window = None

        # Clear login form and show login window
        self.login_window.clear_form()
        self.show_login()

    def run(self):
        """Run the application"""
        return self.app.exec()


def main():
    """Main entry point"""
    try:
        app = CoffeeShopAdminApp()
        sys.exit(app.run())
    except Exception as e:
        print(f"Critical error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
