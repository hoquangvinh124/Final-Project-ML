"""
Register Window - Extended Logic
"""
from PyQt6.QtWidgets import QWidget, QMessageBox, QSizePolicy
from PyQt6.QtCore import pyqtSignal, Qt
from ui_generated.register import Ui_RegisterWindow
from controllers.auth_controller import AuthController


class RegisterWindow(QWidget, Ui_RegisterWindow):
    """Register window with business logic"""

    # Signals
    register_successful = pyqtSignal()
    switch_to_login = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.auth_controller = AuthController()

        # Connect signals
        self.registerButton.clicked.connect(self.handle_register)
        self.backToLoginButton.clicked.connect(self.switch_to_login.emit)

        # --- UI Customization ---
        # Common style for buttons
        button_style = """
            QPushButton {
                background-color: #b22830;
                color: white;
                border: none;
                border-radius: 20px;
                font-size: 14px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:pressed {
                background-color: #9a0007;
            }
        """

        # 1. Register Button (Smaller)
        self.registerButton.setStyleSheet(button_style)
        self.registerButton.setFixedWidth(200)  # Make it smaller (width)

        # Center the button (requires layout manipulation or container, but let's try setting alignment in layout if possible)
        # Since we can't easily change the layout item alignment without accessing the layout,
        # we'll rely on the fact that it's in a VBoxLayout.
        # To center a fixed width widget in VBoxLayout, we usually need to add alignment to the addWidget call.
        # But the widget is already added.
        # We can try to set the size policy.
        self.registerButton.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # We need to center it in the layout.
        # The layout is self.verticalLayout.
        # We can find the index and set alignment.
        index = self.verticalLayout.indexOf(self.registerButton)
        if index != -1:
            self.verticalLayout.setAlignment(self.registerButton, Qt.AlignmentFlag.AlignCenter)

        # 2. Back to Login Button (Red, Rounded, Same size)
        self.backToLoginButton.setStyleSheet(button_style)
        self.backToLoginButton.setFixedWidth(200)
        self.backToLoginButton.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
        index_login = self.verticalLayout.indexOf(self.backToLoginButton)
        if index_login != -1:
            self.verticalLayout.setAlignment(self.backToLoginButton, Qt.AlignmentFlag.AlignCenter)

    def handle_register(self):
        """Handle register button click"""
        # Get form data
        full_name = self.fullNameLineEdit.text().strip()
        email = self.emailLineEdit.text().strip()
        phone = self.phoneLineEdit.text().strip()
        password = self.passwordLineEdit.text()
        confirm_password = self.confirmPasswordLineEdit.text()

        # Validate inputs
        if not full_name:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập họ và tên")
            self.fullNameLineEdit.setFocus()
            return

        if not email:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập email")
            self.emailLineEdit.setFocus()
            return

        if not password:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập mật khẩu")
            self.passwordLineEdit.setFocus()
            return

        if password != confirm_password:
            QMessageBox.warning(self, "Lỗi", "Mật khẩu xác nhận không khớp")
            self.confirmPasswordLineEdit.clear()
            self.confirmPasswordLineEdit.setFocus()
            return

        if not self.termsCheckBox.isChecked():
            QMessageBox.warning(self, "Lỗi", "Vui lòng đồng ý với Điều khoản sử dụng")
            return

        # Disable register button during processing
        self.registerButton.setEnabled(False)
        self.registerButton.setText("Đang đăng ký...")

        # Attempt registration
        phone_value = phone if phone else None
        success, message, user_id = self.auth_controller.register(
            email, password, full_name, phone_value
        )

        # Re-enable button
        self.registerButton.setEnabled(True)
        self.registerButton.setText("Đăng ký")

        if success:
            QMessageBox.information(self, "Thành công", message)
            self.clear_form()
            self.register_successful.emit()
            self.switch_to_login.emit()
        else:
            QMessageBox.warning(self, "Lỗi", message)

    def clear_form(self):
        """Clear all form fields"""
        self.fullNameLineEdit.clear()
        self.emailLineEdit.clear()
        self.phoneLineEdit.clear()
        self.passwordLineEdit.clear()
        self.confirmPasswordLineEdit.clear()
        self.termsCheckBox.setChecked(False)
