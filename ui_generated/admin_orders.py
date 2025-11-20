"""
Auto-generated UI file for Admin Orders Management
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QLineEdit, QComboBox, QTableWidget,
                             QDateEdit)
from PyQt6.QtCore import Qt, QDate


class Ui_AdminOrdersWidget:
    """UI class for admin orders management"""

    def setupUi(self, AdminOrdersWidget):
        """Setup UI"""
        AdminOrdersWidget.setObjectName("AdminOrdersWidget")

        main_layout = QVBoxLayout(AdminOrdersWidget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Header
        header_layout = QHBoxLayout()

        header_label = QLabel("📦 Quản lý đơn hàng")
        header_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        header_layout.addWidget(header_label)

        header_layout.addStretch()

        # Refresh button
        self.refreshButton = QPushButton("🔄 Làm mới")
        self.refreshButton.setMinimumHeight(35)
        header_layout.addWidget(self.refreshButton)

        main_layout.addLayout(header_layout)

        # Filters
        filter_layout = QHBoxLayout()

        # Search
        search_label = QLabel("Tìm kiếm:")
        search_label.setStyleSheet("color: #333;")
        filter_layout.addWidget(search_label)

        self.searchLineEdit = QLineEdit()
        self.searchLineEdit.setPlaceholderText("Mã đơn, tên khách hàng, email, SĐT...")
        self.searchLineEdit.setMinimumWidth(300)
        self.searchLineEdit.setMinimumHeight(35)
        filter_layout.addWidget(self.searchLineEdit)

        # Status filter
        status_label = QLabel("Trạng thái:")
        status_label.setStyleSheet("color: #333;")
        filter_layout.addWidget(status_label)

        self.statusComboBox = QComboBox()
        self.statusComboBox.addItem("Tất cả", "")
        self.statusComboBox.addItem("⏳ Chờ xác nhận", "pending")
        self.statusComboBox.addItem("✅ Đã xác nhận", "confirmed")
        self.statusComboBox.addItem("👨‍🍳 Đang pha chế", "preparing")
        self.statusComboBox.addItem("📦 Sẵn sàng", "ready")
        self.statusComboBox.addItem("🚚 Đang giao", "delivering")
        self.statusComboBox.addItem("✅ Hoàn thành", "completed")
        self.statusComboBox.addItem("❌ Đã hủy", "cancelled")
        self.statusComboBox.setMinimumHeight(35)
        filter_layout.addWidget(self.statusComboBox)

        # Date filter
        date_label = QLabel("Từ:")
        date_label.setStyleSheet("color: #333;")
        filter_layout.addWidget(date_label)

        self.dateFromEdit = QDateEdit()
        self.dateFromEdit.setDate(QDate.currentDate().addDays(-30))
        self.dateFromEdit.setCalendarPopup(True)
        self.dateFromEdit.setMinimumHeight(35)
        filter_layout.addWidget(self.dateFromEdit)

        to_label = QLabel("Đến:")
        to_label.setStyleSheet("color: #333;")
        filter_layout.addWidget(to_label)

        self.dateToEdit = QDateEdit()
        self.dateToEdit.setDate(QDate.currentDate())
        self.dateToEdit.setCalendarPopup(True)
        self.dateToEdit.setMinimumHeight(35)
        filter_layout.addWidget(self.dateToEdit)

        filter_layout.addStretch()

        main_layout.addLayout(filter_layout)

        # Orders table
        self.ordersTable = QTableWidget()
        self.ordersTable.setObjectName("ordersTable")
        self.ordersTable.setColumnCount(9)
        self.ordersTable.setHorizontalHeaderLabels([
            "Mã đơn", "Khách hàng", "SĐT", "Cửa hàng",
            "Loại", "Tổng tiền", "Trạng thái", "Ngày tạo", "Thao tác"
        ])
        self.ordersTable.horizontalHeader().setStretchLastSection(True)
        self.ordersTable.setAlternatingRowColors(True)
        self.ordersTable.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.ordersTable.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        main_layout.addWidget(self.ordersTable)
