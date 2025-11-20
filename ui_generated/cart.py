# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'cart.ui'
################################################################################

from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_CartWidget(object):
    def setupUi(self, CartWidget):
        CartWidget.setObjectName("CartWidget")
        CartWidget.resize(900, 700)

        self.mainLayout = QtWidgets.QVBoxLayout(CartWidget)
        self.mainLayout.setObjectName("mainLayout")

        # Header
        self.headerWidget = QtWidgets.QWidget(CartWidget)
        self.headerWidget.setObjectName("headerWidget")

        self.headerLayout = QtWidgets.QHBoxLayout(self.headerWidget)
        self.headerLayout.setObjectName("headerLayout")

        # Title
        self.titleLabel = QtWidgets.QLabel(self.headerWidget)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.titleLabel.setFont(font)
        self.titleLabel.setObjectName("titleLabel")
        self.headerLayout.addWidget(self.titleLabel)

        # Spacer
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding,
                                           QtWidgets.QSizePolicy.Policy.Minimum)
        self.headerLayout.addItem(spacerItem)

        # Clear cart button
        self.clearCartButton = QtWidgets.QPushButton(self.headerWidget)
        self.clearCartButton.setObjectName("clearCartButton")
        self.headerLayout.addWidget(self.clearCartButton)

        self.mainLayout.addWidget(self.headerWidget)

        # Main content area
        self.contentWidget = QtWidgets.QWidget(CartWidget)
        self.contentWidget.setObjectName("contentWidget")

        self.contentLayout = QtWidgets.QHBoxLayout(self.contentWidget)
        self.contentLayout.setObjectName("contentLayout")

        # Cart items scroll area
        self.cartScrollArea = QtWidgets.QScrollArea(self.contentWidget)
        self.cartScrollArea.setWidgetResizable(True)
        self.cartScrollArea.setObjectName("cartScrollArea")

        self.cartScrollContents = QtWidgets.QWidget()
        self.cartScrollContents.setObjectName("cartScrollContents")

        self.cartItemsLayout = QtWidgets.QVBoxLayout(self.cartScrollContents)
        self.cartItemsLayout.setObjectName("cartItemsLayout")

        self.cartScrollArea.setWidget(self.cartScrollContents)
        self.contentLayout.addWidget(self.cartScrollArea)

        # Summary panel
        self.summaryWidget = QtWidgets.QWidget(self.contentWidget)
        self.summaryWidget.setMaximumWidth(350)
        self.summaryWidget.setObjectName("summaryWidget")

        self.summaryLayout = QtWidgets.QVBoxLayout(self.summaryWidget)
        self.summaryLayout.setObjectName("summaryLayout")

        # Summary title
        self.summaryTitleLabel = QtWidgets.QLabel(self.summaryWidget)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.summaryTitleLabel.setFont(font)
        self.summaryTitleLabel.setObjectName("summaryTitleLabel")
        self.summaryLayout.addWidget(self.summaryTitleLabel)

        # Voucher section
        self.voucherFrame = QtWidgets.QFrame(self.summaryWidget)
        self.voucherFrame.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.voucherFrame.setObjectName("voucherFrame")

        self.voucherLayout = QtWidgets.QHBoxLayout(self.voucherFrame)
        self.voucherLayout.setObjectName("voucherLayout")

        self.voucherLineEdit = QtWidgets.QLineEdit(self.voucherFrame)
        self.voucherLineEdit.setObjectName("voucherLineEdit")
        self.voucherLayout.addWidget(self.voucherLineEdit)

        self.applyVoucherButton = QtWidgets.QPushButton(self.voucherFrame)
        self.applyVoucherButton.setObjectName("applyVoucherButton")
        self.voucherLayout.addWidget(self.applyVoucherButton)

        self.summaryLayout.addWidget(self.voucherFrame)

        # Price details
        self.subtotalLabel = QtWidgets.QLabel(self.summaryWidget)
        self.subtotalLabel.setObjectName("subtotalLabel")
        self.summaryLayout.addWidget(self.subtotalLabel)

        self.discountLabel = QtWidgets.QLabel(self.summaryWidget)
        self.discountLabel.setObjectName("discountLabel")
        self.summaryLayout.addWidget(self.discountLabel)

        self.deliveryFeeLabel = QtWidgets.QLabel(self.summaryWidget)
        self.deliveryFeeLabel.setObjectName("deliveryFeeLabel")
        self.summaryLayout.addWidget(self.deliveryFeeLabel)

        # Divider
        self.line = QtWidgets.QFrame(self.summaryWidget)
        self.line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line.setObjectName("line")
        self.summaryLayout.addWidget(self.line)

        # Total
        self.totalLabel = QtWidgets.QLabel(self.summaryWidget)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.totalLabel.setFont(font)
        self.totalLabel.setObjectName("totalLabel")
        self.summaryLayout.addWidget(self.totalLabel)

        # Spacer
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Policy.Minimum,
                                            QtWidgets.QSizePolicy.Policy.Expanding)
        self.summaryLayout.addItem(spacerItem2)

        # Checkout button
        self.checkoutButton = QtWidgets.QPushButton(self.summaryWidget)
        self.checkoutButton.setMinimumHeight(50)
        self.checkoutButton.setObjectName("checkoutButton")
        self.summaryLayout.addWidget(self.checkoutButton)

        self.contentLayout.addWidget(self.summaryWidget)

        self.mainLayout.addWidget(self.contentWidget)

        self.retranslateUi(CartWidget)
        QtCore.QMetaObject.connectSlotsByName(CartWidget)

    def retranslateUi(self, CartWidget):
        _translate = QtCore.QCoreApplication.translate
        CartWidget.setWindowTitle(_translate("CartWidget", "Giỏ hàng"))
        self.titleLabel.setText(_translate("CartWidget", "🛒 Giỏ hàng của bạn"))
        self.clearCartButton.setText(_translate("CartWidget", "Xóa tất cả"))
        self.summaryTitleLabel.setText(_translate("CartWidget", "Tóm tắt đơn hàng"))
        self.voucherLineEdit.setPlaceholderText(_translate("CartWidget", "Nhập mã giảm giá"))
        self.applyVoucherButton.setText(_translate("CartWidget", "Áp dụng"))
        self.subtotalLabel.setText(_translate("CartWidget", "Tạm tính: 0đ"))
        self.discountLabel.setText(_translate("CartWidget", "Giảm giá: 0đ"))
        self.deliveryFeeLabel.setText(_translate("CartWidget", "Phí giao hàng: 0đ"))
        self.totalLabel.setText(_translate("CartWidget", "Tổng: 0đ"))
        self.checkoutButton.setText(_translate("CartWidget", "Thanh toán"))
