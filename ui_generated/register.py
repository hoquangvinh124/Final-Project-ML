# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'register.ui'
################################################################################

from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_RegisterWindow(object):
    def setupUi(self, RegisterWindow):
        RegisterWindow.setObjectName("RegisterWindow")
        RegisterWindow.resize(400, 700)

        self.verticalLayout = QtWidgets.QVBoxLayout(RegisterWindow)
        self.verticalLayout.setObjectName("verticalLayout")

        # Title
        self.titleLabel = QtWidgets.QLabel(RegisterWindow)
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        self.titleLabel.setFont(font)
        self.titleLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.titleLabel.setObjectName("titleLabel")
        self.verticalLayout.addWidget(self.titleLabel)

        # Full name
        self.fullNameLineEdit = QtWidgets.QLineEdit(RegisterWindow)
        self.fullNameLineEdit.setMinimumHeight(40)
        self.fullNameLineEdit.setObjectName("fullNameLineEdit")
        self.verticalLayout.addWidget(self.fullNameLineEdit)

        # Email
        self.emailLineEdit = QtWidgets.QLineEdit(RegisterWindow)
        self.emailLineEdit.setMinimumHeight(40)
        self.emailLineEdit.setObjectName("emailLineEdit")
        self.verticalLayout.addWidget(self.emailLineEdit)

        # Phone
        self.phoneLineEdit = QtWidgets.QLineEdit(RegisterWindow)
        self.phoneLineEdit.setMinimumHeight(40)
        self.phoneLineEdit.setObjectName("phoneLineEdit")
        self.verticalLayout.addWidget(self.phoneLineEdit)

        # Password
        self.passwordLineEdit = QtWidgets.QLineEdit(RegisterWindow)
        self.passwordLineEdit.setMinimumHeight(40)
        self.passwordLineEdit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.passwordLineEdit.setObjectName("passwordLineEdit")
        self.verticalLayout.addWidget(self.passwordLineEdit)

        # Confirm password
        self.confirmPasswordLineEdit = QtWidgets.QLineEdit(RegisterWindow)
        self.confirmPasswordLineEdit.setMinimumHeight(40)
        self.confirmPasswordLineEdit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.confirmPasswordLineEdit.setObjectName("confirmPasswordLineEdit")
        self.verticalLayout.addWidget(self.confirmPasswordLineEdit)

        # Terms checkbox
        self.termsCheckBox = QtWidgets.QCheckBox(RegisterWindow)
        self.termsCheckBox.setObjectName("termsCheckBox")
        self.verticalLayout.addWidget(self.termsCheckBox)

        # Register button
        self.registerButton = QtWidgets.QPushButton(RegisterWindow)
        self.registerButton.setMinimumHeight(45)
        self.registerButton.setObjectName("registerButton")
        self.verticalLayout.addWidget(self.registerButton)

        # Spacer
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum,
                                           QtWidgets.QSizePolicy.Policy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        # Login label
        self.loginLabel = QtWidgets.QLabel(RegisterWindow)
        self.loginLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.loginLabel.setObjectName("loginLabel")
        self.verticalLayout.addWidget(self.loginLabel)

        # Back to login button
        self.backToLoginButton = QtWidgets.QPushButton(RegisterWindow)
        self.backToLoginButton.setMinimumHeight(40)
        self.backToLoginButton.setObjectName("backToLoginButton")
        self.verticalLayout.addWidget(self.backToLoginButton)

        self.retranslateUi(RegisterWindow)
        QtCore.QMetaObject.connectSlotsByName(RegisterWindow)

    def retranslateUi(self, RegisterWindow):
        _translate = QtCore.QCoreApplication.translate
        RegisterWindow.setWindowTitle(_translate("RegisterWindow", "Đăng ký - Highlands Coffee"))
        self.titleLabel.setText(_translate("RegisterWindow", "Đăng ký tài khoản"))
        self.fullNameLineEdit.setPlaceholderText(_translate("RegisterWindow", "Họ và tên"))
        self.emailLineEdit.setPlaceholderText(_translate("RegisterWindow", "Email"))
        self.phoneLineEdit.setPlaceholderText(_translate("RegisterWindow", "Số điện thoại"))
        self.passwordLineEdit.setPlaceholderText(_translate("RegisterWindow", "Mật khẩu"))
        self.confirmPasswordLineEdit.setPlaceholderText(_translate("RegisterWindow", "Xác nhận mật khẩu"))
        self.termsCheckBox.setText(_translate("RegisterWindow", "Tôi đồng ý với Điều khoản sử dụng và Chính sách bảo mật"))
        self.registerButton.setText(_translate("RegisterWindow", "Đăng ký"))
        self.loginLabel.setText(_translate("RegisterWindow", "Đã có tài khoản?"))
        self.backToLoginButton.setText(_translate("RegisterWindow", "Đăng nhập ngay"))
