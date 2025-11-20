# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'menu.ui'
################################################################################

from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MenuWidget(object):
    def setupUi(self, MenuWidget):
        MenuWidget.setObjectName("MenuWidget")
        MenuWidget.resize(900, 700)

        self.mainLayout = QtWidgets.QVBoxLayout(MenuWidget)
        self.mainLayout.setObjectName("mainLayout")
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)

        # Main scroll area for entire page
        self.mainScrollArea = QtWidgets.QScrollArea(MenuWidget)
        self.mainScrollArea.setWidgetResizable(True)
        self.mainScrollArea.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.mainScrollArea.setObjectName("mainScrollArea")

        self.scrollContent = QtWidgets.QWidget()
        self.scrollContent.setObjectName("scrollContent")
        self.scrollContent.setStyleSheet("QWidget#scrollContent { background-color: #F9F3EF; }")

        self.contentLayout = QtWidgets.QVBoxLayout(self.scrollContent)
        self.contentLayout.setObjectName("contentLayout")
        self.contentLayout.setContentsMargins(10, 10, 10, 10)
        self.contentLayout.setSpacing(10)

        # Header
        self.headerWidget = QtWidgets.QWidget(self.scrollContent)
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

        # Search box
        self.searchLineEdit = QtWidgets.QLineEdit(self.headerWidget)
        self.searchLineEdit.setMinimumWidth(300)
        self.searchLineEdit.setMinimumHeight(35)
        self.searchLineEdit.setObjectName("searchLineEdit")
        self.headerLayout.addWidget(self.searchLineEdit)

        self.contentLayout.addWidget(self.headerWidget)

        # Category tabs
        self.categoryTabWidget = QtWidgets.QTabWidget(self.scrollContent)
        self.categoryTabWidget.setObjectName("categoryTabWidget")
        self.categoryTabWidget.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                top: 0px;
                padding: 0px;
            }
            QTabWidget::tab-bar {
                alignment: left;
            }
            QTabBar::tab {
                padding: 8px 16px;
                margin-right: 2px;
            }
        """)
        self.categoryTabWidget.setDocumentMode(True)
        self.contentLayout.addWidget(self.categoryTabWidget)

        # Filter widget
        self.filterWidget = QtWidgets.QWidget(self.scrollContent)
        self.filterWidget.setMaximumHeight(50)
        self.filterWidget.setObjectName("filterWidget")

        self.filterLayout = QtWidgets.QHBoxLayout(self.filterWidget)
        self.filterLayout.setObjectName("filterLayout")

        # Filter label
        self.filterLabel = QtWidgets.QLabel(self.filterWidget)
        self.filterLabel.setObjectName("filterLabel")
        self.filterLayout.addWidget(self.filterLabel)

        # Temperature filter
        self.hotCheckBox = QtWidgets.QCheckBox(self.filterWidget)
        self.hotCheckBox.setObjectName("hotCheckBox")
        self.filterLayout.addWidget(self.hotCheckBox)

        self.coldCheckBox = QtWidgets.QCheckBox(self.filterWidget)
        self.coldCheckBox.setObjectName("coldCheckBox")
        self.filterLayout.addWidget(self.coldCheckBox)

        # Caffeine filter
        self.caffeineCheckBox = QtWidgets.QCheckBox(self.filterWidget)
        self.caffeineCheckBox.setObjectName("caffeineCheckBox")
        self.filterLayout.addWidget(self.caffeineCheckBox)

        # Spacer
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding,
                                            QtWidgets.QSizePolicy.Policy.Minimum)
        self.filterLayout.addItem(spacerItem2)

        self.contentLayout.addWidget(self.filterWidget)

        # Products container widget
        self.productsWidget = QtWidgets.QWidget(self.scrollContent)
        self.productsWidget.setObjectName("productsWidget")

        # Grid layout for products
        self.productsGridLayout = QtWidgets.QGridLayout(self.productsWidget)
        self.productsGridLayout.setObjectName("productsGridLayout")

        self.contentLayout.addWidget(self.productsWidget)

        # Pagination widget
        self.paginationWidget = QtWidgets.QWidget(self.scrollContent)
        self.paginationWidget.setMaximumHeight(60)
        self.paginationWidget.setObjectName("paginationWidget")

        self.paginationLayout = QtWidgets.QHBoxLayout(self.paginationWidget)
        self.paginationLayout.setObjectName("paginationLayout")

        # Add spacer
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding,
                                            QtWidgets.QSizePolicy.Policy.Minimum)
        self.paginationLayout.addItem(spacerItem3)

        # Previous button
        self.prevButton = QtWidgets.QPushButton(self.paginationWidget)
        self.prevButton.setObjectName("prevButton")
        self.prevButton.setMinimumSize(80, 35)
        self.paginationLayout.addWidget(self.prevButton)

        # Page info label
        self.pageInfoLabel = QtWidgets.QLabel(self.paginationWidget)
        self.pageInfoLabel.setObjectName("pageInfoLabel")
        self.pageInfoLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.pageInfoLabel.setMinimumWidth(150)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pageInfoLabel.setFont(font)
        self.paginationLayout.addWidget(self.pageInfoLabel)

        # Next button
        self.nextButton = QtWidgets.QPushButton(self.paginationWidget)
        self.nextButton.setObjectName("nextButton")
        self.nextButton.setMinimumSize(80, 35)
        self.paginationLayout.addWidget(self.nextButton)

        # Add spacer
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding,
                                            QtWidgets.QSizePolicy.Policy.Minimum)
        self.paginationLayout.addItem(spacerItem4)

        self.contentLayout.addWidget(self.paginationWidget)

        # Set scroll content
        self.mainScrollArea.setWidget(self.scrollContent)
        self.mainLayout.addWidget(self.mainScrollArea)

        self.retranslateUi(MenuWidget)
        QtCore.QMetaObject.connectSlotsByName(MenuWidget)

    def retranslateUi(self, MenuWidget):
        _translate = QtCore.QCoreApplication.translate
        MenuWidget.setWindowTitle(_translate("MenuWidget", "Menu"))
        self.titleLabel.setText(_translate("MenuWidget", "📋 Menu"))
        self.searchLineEdit.setPlaceholderText(_translate("MenuWidget", "🔍 Tìm kiếm sản phẩm..."))
        self.filterLabel.setText(_translate("MenuWidget", "Lọc:"))
        self.hotCheckBox.setText(_translate("MenuWidget", "🔥 Nóng"))
        self.coldCheckBox.setText(_translate("MenuWidget", "❄️ Lạnh"))
        self.caffeineCheckBox.setText(_translate("MenuWidget", "☕ Không caffeine"))
        self.prevButton.setText(_translate("MenuWidget", "← Trước"))
        self.nextButton.setText(_translate("MenuWidget", "Sau →"))
        self.pageInfoLabel.setText(_translate("MenuWidget", "Trang 1 / 1"))
