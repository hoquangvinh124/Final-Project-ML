"""
Auto-generated UI file for Admin Dashboard
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QFrame, QGridLayout, QScrollArea, QTableWidget)
from PyQt6.QtCore import Qt


class Ui_AdminDashboardWidget:
    """UI class for admin dashboard"""

    def setupUi(self, AdminDashboardWidget):
        """Setup UI"""
        AdminDashboardWidget.setObjectName("AdminDashboardWidget")

        main_layout = QVBoxLayout(AdminDashboardWidget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Header
        header_label = QLabel("Dashboard")
        header_label.setObjectName("headerLabel")
        header_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        main_layout.addWidget(header_label)

        # Stats grid
        stats_grid = QGridLayout()
        stats_grid.setSpacing(15)

        # Stat cards
        self.totalRevenueCard = self.create_stat_card()
        stats_grid.addWidget(self.totalRevenueCard, 0, 0)

        self.todayRevenueCard = self.create_stat_card()
        stats_grid.addWidget(self.todayRevenueCard, 0, 1)

        self.monthRevenueCard = self.create_stat_card()
        stats_grid.addWidget(self.monthRevenueCard, 0, 2)

        self.totalOrdersCard = self.create_stat_card()
        stats_grid.addWidget(self.totalOrdersCard, 1, 0)

        self.todayOrdersCard = self.create_stat_card()
        stats_grid.addWidget(self.todayOrdersCard, 1, 1)

        self.pendingOrdersCard = self.create_stat_card()
        stats_grid.addWidget(self.pendingOrdersCard, 1, 2)

        self.totalCustomersCard = self.create_stat_card()
        stats_grid.addWidget(self.totalCustomersCard, 2, 0)

        self.totalProductsCard = self.create_stat_card()
        stats_grid.addWidget(self.totalProductsCard, 2, 1)

        main_layout.addLayout(stats_grid)

        # Recent orders section
        recent_orders_label = QLabel("Đơn hàng gần đây")
        recent_orders_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333; margin-top: 10px;")
        main_layout.addWidget(recent_orders_label)

        # Recent orders table
        self.recentOrdersTable = QTableWidget()
        self.recentOrdersTable.setObjectName("recentOrdersTable")
        self.recentOrdersTable.setColumnCount(7)
        self.recentOrdersTable.setHorizontalHeaderLabels([
            "Mã đơn", "Khách hàng", "Cửa hàng", "Tổng tiền", "Trạng thái", "Ngày tạo", "Thao tác"
        ])
        self.recentOrdersTable.horizontalHeader().setStretchLastSection(True)
        self.recentOrdersTable.setAlternatingRowColors(True)
        self.recentOrdersTable.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.recentOrdersTable.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        main_layout.addWidget(self.recentOrdersTable)

    def create_stat_card(self):
        """Create a stat card widget"""
        card = QFrame()
        card.setFrameShape(QFrame.Shape.StyledPanel)
        card.setMinimumHeight(130)
        card.setStyleSheet("""
            QFrame {
                background-color: #F9F3EF;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        layout.setContentsMargins(15, 15, 15, 15)

        # Title
        title_label = QLabel("Title")
        title_label.setObjectName("titleLabel")
        title_label.setStyleSheet("font-size: 13px; color: #666; font-weight: normal;")
        title_label.setWordWrap(True)
        title_label.setSizePolicy(QLabel().sizePolicy().horizontalPolicy(),
                                   QLabel().sizePolicy().verticalPolicy())
        layout.addWidget(title_label)

        # Value
        value_label = QLabel("0")
        value_label.setObjectName("valueLabel")
        value_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #c7a17a;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        value_label.setWordWrap(True)
        value_label.setTextFormat(Qt.TextFormat.PlainText)
        value_label.setSizePolicy(QLabel().sizePolicy().horizontalPolicy(),
                                   QLabel().sizePolicy().verticalPolicy())
        layout.addWidget(value_label)

        layout.addStretch()

        card.valueLabel = value_label
        card.titleLabel = title_label

        return card
