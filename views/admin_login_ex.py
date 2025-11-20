"""
Admin Login Widget - Extended Logic
Admin authentication
"""
from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6.QtCore import pyqtSignal, Qt
from ui_generated.admin_login import Ui_AdminLoginWidget
from controllers.admin_controller import AdminController


class AdminLoginWidget(QWidget, Ui_AdminLoginWidget):
    """Admin login widget"""

    login_successful = pyqtSignal(dict)  # Emit admin data on successful login

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.admin_controller = AdminController()

        # Connect signals
        self.loginButton.clicked.connect(self.handle_login)
        self.usernameLineEdit.returnPressed.connect(self.handle_login)
        self.passwordLineEdit.returnPressed.connect(self.handle_login)

        # Auto-fill admin credentials
        self.usernameLineEdit.setText("admin")
        self.passwordLineEdit.setText("admin123")

        # Focus on username field
        self.usernameLineEdit.setFocus()

    def handle_login(self):
        """Handle login button click"""
        # Get credentials
        username = self.usernameLineEdit.text().strip()
        password = self.passwordLineEdit.text()

        # Validate
        if not username:
            self.show_error("Vui lòng nhập tên đăng nhập")
            self.usernameLineEdit.setFocus()
            return

        if not password:
            self.show_error("Vui lòng nhập mật khẩu")
            self.passwordLineEdit.setFocus()
            return

        # Disable login button
        self.loginButton.setEnabled(False)
        self.loginButton.setText("Đang đăng nhập...")

        # Attempt login
        success, result = self.admin_controller.login(username, password)

        if success:
            # Hide error
            self.errorLabel.hide()

            # Clear password
            self.passwordLineEdit.clear()

            # Emit success signal
            self.login_successful.emit(result)

        else:
            # Show error
            self.show_error(result)

            # Re-enable login button
            self.loginButton.setEnabled(True)
            self.loginButton.setText("Đăng nhập")

            # Clear password and focus
            self.passwordLineEdit.clear()
            self.passwordLineEdit.setFocus()

    def show_error(self, message):
        """Show error message"""
        self.errorLabel.setText(message)
        self.errorLabel.show()

    def clear_form(self):
        """Clear login form"""
        self.usernameLineEdit.clear()
        self.passwordLineEdit.clear()
        self.rememberCheckBox.setChecked(False)
        self.errorLabel.hide()
        self.loginButton.setEnabled(True)
        self.loginButton.setText("Đăng nhập")
        self.usernameLineEdit.setFocus()

    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_Escape:
            self.clear_form()
        super().keyPressEvent(event)
