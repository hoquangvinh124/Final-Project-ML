# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'login.ui'
##
## Created by: Qt User Interface Compiler version 6.0.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt


class Ui_LoginWindow(object):
    def setupUi(self, LoginWindow):
        LoginWindow.setObjectName("LoginWindow")
        LoginWindow.resize(500, 600)
        
        # Main layout
        self.verticalLayout = QtWidgets.QVBoxLayout(LoginWindow)
        self.verticalLayout.setContentsMargins(40, 40, 40, 40)
        self.verticalLayout.setSpacing(10)

        # Add stretch at top
        self.verticalLayout.addStretch()

        # Logo
        self.logoLabel = QtWidgets.QLabel(LoginWindow)
        logo_pixmap = QPixmap("resources/images/logo.png")
        if not logo_pixmap.isNull():
            scaled_logo = logo_pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.logoLabel.setPixmap(scaled_logo)
        self.logoLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logoLabel.setStyleSheet("margin-bottom: 0px;")
        self.verticalLayout.addWidget(self.logoLabel)

        # Title
        self.titleLabel = QtWidgets.QLabel("Đăng nhập hệ thống", LoginWindow)
        self.titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.titleLabel.setStyleSheet("color: #A31E25; font-size: 16px; font-weight: bold; margin-top: 0px; padding-top: 0px;")
        self.verticalLayout.addWidget(self.titleLabel)

        self.verticalLayout.addSpacing(20)

        # Login form container
        form_container = QtWidgets.QFrame(LoginWindow)
        form_container.setObjectName("formContainer")
        form_container.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        form_layout = QtWidgets.QVBoxLayout(form_container)
        form_layout.setSpacing(15)

        # Email
        email_label = QtWidgets.QLabel("Email:", form_container)
        email_label.setStyleSheet("font-weight: bold; color: #333;")
        form_layout.addWidget(email_label)

        self.emailLineEdit = QtWidgets.QLineEdit(form_container)
        self.emailLineEdit.setObjectName("emailLineEdit")
        self.emailLineEdit.setPlaceholderText("Nhập email")
        self.emailLineEdit.setMinimumHeight(40)
        form_layout.addWidget(self.emailLineEdit)

        # Password
        password_label = QtWidgets.QLabel("Mật khẩu:", form_container)
        password_label.setStyleSheet("font-weight: bold; color: #333;")
        form_layout.addWidget(password_label)

        self.passwordLineEdit = QtWidgets.QLineEdit(form_container)
        self.passwordLineEdit.setObjectName("passwordLineEdit")
        self.passwordLineEdit.setPlaceholderText("Nhập mật khẩu")
        self.passwordLineEdit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.passwordLineEdit.setMinimumHeight(40)
        form_layout.addWidget(self.passwordLineEdit)

        # Remember me & Forgot Password row
        row_layout = QtWidgets.QHBoxLayout()
        self.rememberMeCheckBox = QtWidgets.QCheckBox("Ghi nhớ đăng nhập", form_container)
        self.rememberMeCheckBox.setObjectName("rememberMeCheckBox")
        row_layout.addWidget(self.rememberMeCheckBox)
        
        row_layout.addStretch()
        
        self.forgotPasswordButton = QtWidgets.QPushButton("Quên mật khẩu?", form_container)
        self.forgotPasswordButton.setObjectName("forgotPasswordButton")
        self.forgotPasswordButton.setFlat(True)
        self.forgotPasswordButton.setStyleSheet("color: #666; text-align: right;")
        self.forgotPasswordButton.setCursor(Qt.CursorShape.PointingHandCursor)
        row_layout.addWidget(self.forgotPasswordButton)
        
        form_layout.addLayout(row_layout)

        # Login button
        self.loginButton = QtWidgets.QPushButton("Đăng nhập", form_container)
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

        # Register button (styled as secondary action)
        self.registerButton = QtWidgets.QPushButton("Chưa có tài khoản? Đăng ký ngay", form_container)
        self.registerButton.setObjectName("registerButton")
        self.registerButton.setFlat(True)
        self.registerButton.setStyleSheet("color: #A31E25; font-weight: bold;")
        self.registerButton.setCursor(Qt.CursorShape.PointingHandCursor)
        form_layout.addWidget(self.registerButton)

        self.verticalLayout.addWidget(form_container)

        # Social Login (Hidden to match admin style)
        self.googleLoginButton = QtWidgets.QPushButton("Google", LoginWindow)
        self.googleLoginButton.setObjectName("googleLoginButton")
        self.googleLoginButton.hide()
        
        self.appleLoginButton = QtWidgets.QPushButton("Apple", LoginWindow)
        self.appleLoginButton.setObjectName("appleLoginButton")
        self.appleLoginButton.hide()
        
        # Add stretch at bottom
        self.verticalLayout.addStretch()

        # Footer
        footer_label = QtWidgets.QLabel("Coffee Shop Management System v1.0", LoginWindow)
        footer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_label.setStyleSheet("color: #999; font-size: 11px;")
        self.verticalLayout.addWidget(footer_label)
        
        # Dummy widgets to prevent errors if referenced
        self.orLabel = QtWidgets.QLabel(LoginWindow)
        self.registerLabel = QtWidgets.QLabel(LoginWindow)

        self.retranslateUi(LoginWindow)
        QtCore.QMetaObject.connectSlotsByName(LoginWindow)

    def retranslateUi(self, LoginWindow):
        _translate = QtCore.QCoreApplication.translate
        LoginWindow.setWindowTitle(_translate("LoginWindow", "Đăng nhập - Highlands Coffee"))
        self.titleLabel.setText(_translate("LoginWindow", "Đăng nhập hệ thống"))
        self.emailLineEdit.setPlaceholderText(_translate("LoginWindow", "Nhập email"))
        self.passwordLineEdit.setPlaceholderText(_translate("LoginWindow", "Nhập mật khẩu"))
        self.rememberMeCheckBox.setText(_translate("LoginWindow", "Ghi nhớ đăng nhập"))
        self.loginButton.setText(_translate("LoginWindow", "Đăng nhập"))
        self.forgotPasswordButton.setText(_translate("LoginWindow", "Quên mật khẩu?"))
        self.registerButton.setText(_translate("LoginWindow", "Chưa có tài khoản? Đăng ký ngay"))
