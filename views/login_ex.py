"""
Login Window - Extended Logic
Inherits from generated UI file
"""
from PyQt6.QtWidgets import QWidget, QMessageBox, QLabel
from PyQt6.QtCore import pyqtSignal
from ui_generated.login import Ui_LoginWindow
from controllers.auth_controller import AuthController


class LoginWindow(QWidget, Ui_LoginWindow):
    """Login window with business logic"""

    # Signals
    login_successful = pyqtSignal(dict)  # Emits user data on successful login
    switch_to_register = pyqtSignal()
    switch_to_forgot_password = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.auth_controller = AuthController()

        # Pre-fill login credentials
        self.emailLineEdit.setText("test@example.com")
        self.passwordLineEdit.setText("Test12345")

        # Connect signals
        self.loginButton.clicked.connect(self.handle_login)
        self.registerButton.clicked.connect(self.switch_to_register.emit)
        self.forgotPasswordButton.clicked.connect(self.switch_to_forgot_password.emit)
        self.googleLoginButton.clicked.connect(self.handle_google_login)
        self.appleLoginButton.clicked.connect(self.handle_apple_login)

        # Enable return key press to login
        self.emailLineEdit.returnPressed.connect(self.handle_login)
        self.passwordLineEdit.returnPressed.connect(self.handle_login)

        # --- UI Customization ---
        # 1. Change Title
        self.titleLabel.setText("Highlands ở đây rồi — Hôm nay uống gì nào ?")
        
        # 2. Style Login Button (Red, Rounded)
        self.loginButton.setStyleSheet("""
            QPushButton {
                background-color: #b22830;
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:pressed {
                background-color: #9a0007;
            }
        """)
        
        # 3. Style Register Button (Text only)
        self.registerButton.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #b22830;
                border: none;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
        """)
        
        # 4. Remove Version Label
        for label in self.findChildren(QLabel):
            if "Coffee Shop Management System" in label.text():
                label.hide()
                break

    def handle_login(self):
        """Handle login button click"""
        email = self.emailLineEdit.text().strip()
        password = self.passwordLineEdit.text()

        # Validate inputs
        if not email:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập email")
            self.emailLineEdit.setFocus()
            return

        if not password:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập mật khẩu")
            self.passwordLineEdit.setFocus()
            return

        # Disable login button during processing
        self.loginButton.setEnabled(False)
        self.loginButton.setText("Đang đăng nhập...")

        # Attempt login
        success, message, user_data = self.auth_controller.login(email, password)

        # Re-enable button
        self.loginButton.setEnabled(True)
        self.loginButton.setText("Đăng nhập")

        if success:
            QMessageBox.information(self, "Thành công", message)
            self.login_successful.emit(user_data)
        else:
            QMessageBox.warning(self, "Lỗi", message)
            self.passwordLineEdit.clear()
            self.passwordLineEdit.setFocus()

    def handle_google_login(self):
        """Handle Google login (placeholder)"""
        QMessageBox.information(
            self,
            "Thông báo",
            "Tính năng đăng nhập bằng Google sẽ được cập nhật trong phiên bản tiếp theo."
        )

    def handle_apple_login(self):
        """Handle Apple login (placeholder)"""
        QMessageBox.information(
            self,
            "Thông báo",
            "Tính năng đăng nhập bằng Apple ID sẽ được cập nhật trong phiên bản tiếp theo."
        )

    def clear_form(self):
        """Clear all form fields"""
        self.emailLineEdit.clear()
        self.passwordLineEdit.clear()
        self.rememberMeCheckBox.setChecked(False)
