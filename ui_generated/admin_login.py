"""
Auto-generated UI file for Admin Login
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QFrame, QCheckBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap


class Ui_AdminLoginWidget:
    """UI class for admin login widget"""

    def setupUi(self, AdminLoginWidget):
        """Setup UI"""
        AdminLoginWidget.setObjectName("AdminLoginWidget")
        AdminLoginWidget.resize(400, 500)

        # Main layout
        main_layout = QVBoxLayout(AdminLoginWidget)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(10)

        # Add stretch at top
        main_layout.addStretch()

        # Logo
        logo_label = QLabel()
        logo_pixmap = QPixmap("resources/images/logo.png")
        if not logo_pixmap.isNull():
            scaled_logo = logo_pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_logo)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("margin-bottom: 0px;")
        main_layout.addWidget(logo_label)

        subtitle_label = QLabel("Quản trị hệ thống")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: #A31E25; font-size: 16px; font-weight: bold; margin-top: 0px; padding-top: 0px;")
        main_layout.addWidget(subtitle_label)

        main_layout.addSpacing(20)

        # Login form container
        form_container = QFrame()
        form_container.setObjectName("formContainer")
        form_container.setFrameShape(QFrame.Shape.StyledPanel)
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(15)

        # Username
        username_label = QLabel("Tên đăng nhập:")
        username_label.setStyleSheet("font-weight: bold; color: #333;")
        form_layout.addWidget(username_label)

        self.usernameLineEdit = QLineEdit()
        self.usernameLineEdit.setObjectName("usernameLineEdit")
        self.usernameLineEdit.setPlaceholderText("Nhập tên đăng nhập")
        self.usernameLineEdit.setMinimumHeight(40)
        form_layout.addWidget(self.usernameLineEdit)

        # Password
        password_label = QLabel("Mật khẩu:")
        password_label.setStyleSheet("font-weight: bold; color: #333;")
        form_layout.addWidget(password_label)

        self.passwordLineEdit = QLineEdit()
        self.passwordLineEdit.setObjectName("passwordLineEdit")
        self.passwordLineEdit.setPlaceholderText("Nhập mật khẩu")
        self.passwordLineEdit.setEchoMode(QLineEdit.EchoMode.Password)
        self.passwordLineEdit.setMinimumHeight(40)
        form_layout.addWidget(self.passwordLineEdit)

        # Remember me
        self.rememberCheckBox = QCheckBox("Ghi nhớ đăng nhập")
        self.rememberCheckBox.setObjectName("rememberCheckBox")
        form_layout.addWidget(self.rememberCheckBox)

        # Login button
        self.loginButton = QPushButton("Đăng nhập")
        self.loginButton.setObjectName("loginButton")
        self.loginButton.setMinimumHeight(45)
        self.loginButton.setStyleSheet("""
            QPushButton {
                background-color: #c7a17a;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #b39168;
            }
            QPushButton:pressed {
                background-color: #a07856;
            }
        """)
        form_layout.addWidget(self.loginButton)

        main_layout.addWidget(form_container)

        # Error label
        self.errorLabel = QLabel()
        self.errorLabel.setObjectName("errorLabel")
        self.errorLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.errorLabel.setStyleSheet("color: #d32f2f; font-size: 12px;")
        self.errorLabel.setWordWrap(True)
        self.errorLabel.hide()
        main_layout.addWidget(self.errorLabel)

        # Add stretch at bottom
        main_layout.addStretch()

        # Footer
        footer_label = QLabel("Coffee Shop Management System v1.0")
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_label.setStyleSheet("color: #999; font-size: 11px;")
        main_layout.addWidget(footer_label)
