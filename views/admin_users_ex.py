"""Admin Users Management"""
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor
from controllers.admin_user_controller import AdminUserController
from controllers.admin_controller import AdminController
from utils.validators import format_currency
from datetime import datetime

class AdminUsersWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.user_controller = AdminUserController()
        self.admin_controller = AdminController()
        self.setup_ui()
        self.load_users()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QHBoxLayout()
        header.addWidget(QLabel("<h2>👥 Quản lý khách hàng</h2>"))
        header.addStretch()
        refresh_btn = QPushButton("🔄 Làm mới")
        refresh_btn.clicked.connect(self.load_users)
        header.addWidget(refresh_btn)
        layout.addLayout(header)

        # Filters
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Tìm kiếm:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Tên, email, SĐT...")
        self.search_edit.textChanged.connect(self.load_users)
        filter_layout.addWidget(self.search_edit)

        filter_layout.addWidget(QLabel("Tier:"))
        self.tier_combo = QComboBox()
        self.tier_combo.addItem("Tất cả", None)
        for tier in ['Bronze', 'Silver', 'Gold']:
            self.tier_combo.addItem(tier, tier)
        self.tier_combo.currentIndexChanged.connect(self.load_users)
        filter_layout.addWidget(self.tier_combo)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Tên", "Email", "SĐT", "Tier", "Điểm", "Tổng chi", "Thao tác"
        ])
        # self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        # Fix row height issue
        self.table.verticalHeader().setDefaultSectionSize(50)
        self.table.verticalHeader().setMinimumSectionSize(50)
        
        layout.addWidget(self.table)

    def load_users(self):
        search = self.search_edit.text().strip()
        tier = self.tier_combo.currentData()
        users = self.user_controller.get_all_users(
            search=search if search else None,
            tier=tier
        )
        self.display_users(users)

    def display_users(self, users):
        self.table.setRowCount(len(users))
        for row, user in enumerate(users):
            self.table.setItem(row, 0, QTableWidgetItem(str(user['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(user['full_name']))
            self.table.setItem(row, 2, QTableWidgetItem(user.get('email', 'N/A')))
            self.table.setItem(row, 3, QTableWidgetItem(user.get('phone', 'N/A')))
            
            tier_icons = {'Bronze': '🥉', 'Silver': '🥈', 'Gold': '🥇'}
            tier_text = f"{tier_icons.get(user['membership_tier'], '')} {user['membership_tier']}"
            self.table.setItem(row, 4, QTableWidgetItem(tier_text))
            
            self.table.setItem(row, 5, QTableWidgetItem(str(user.get('loyalty_points', 0))))
            self.table.setItem(row, 6, QTableWidgetItem(format_currency(user.get('total_spent', 0))))

            # Actions
            action_widget = QWidget()
            action_widget.setMinimumWidth(200)
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 2, 5, 2)
            action_layout.setSpacing(5)

            tier_btn = QPushButton("Tier")
            tier_btn.setToolTip("Đổi tier khách hàng")
            tier_btn.setStyleSheet("background-color: #FF9800; color: white; border: none; padding: 6px 12px; border-radius: 3px; font-size: 12px;")
            tier_btn.clicked.connect(lambda checked, u=user: self.change_tier(u))
            action_layout.addWidget(tier_btn)

            points_btn = QPushButton("Điểm")
            points_btn.setToolTip("Điều chỉnh điểm tích lũy")
            points_btn.setStyleSheet("background-color: #4CAF50; color: white; border: none; padding: 6px 12px; border-radius: 3px; font-size: 12px;")
            points_btn.clicked.connect(lambda checked, u=user: self.adjust_points(u))
            action_layout.addWidget(points_btn)

            self.table.setCellWidget(row, 7, action_widget)

            # Set row height to accommodate buttons
            self.table.setRowHeight(row, 50)

        QTimer.singleShot(100, self.adjust_columns)

    def adjust_columns(self):
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)
        
        for i in [0, 2, 3, 4, 5, 6]:
            self.table.resizeColumnToContents(i)
            
        self.table.setColumnWidth(7, 220)

    def change_tier(self, user):
        tiers = ['Bronze', 'Silver', 'Gold']
        tier, ok = QInputDialog.getItem(self, "Đổi Tier", f"Chọn tier cho {user['full_name']}:", tiers, tiers.index(user['membership_tier']), False)
        if ok:
            admin_id = self.admin_controller.get_current_admin_id()
            success, msg = self.user_controller.update_user_tier(user['id'], tier, admin_id)
            if success:
                QMessageBox.information(self, "Thành công", msg)
                self.load_users()
            else:
                QMessageBox.warning(self, "Lỗi", msg)

    def adjust_points(self, user):
        points, ok = QInputDialog.getInt(self, "Điều chỉnh điểm", f"Nhập số điểm cộng/trừ cho {user['full_name']}:\n(Số âm để trừ)", 0, -100000, 100000, 1)
        if ok and points != 0:
            admin_id = self.admin_controller.get_current_admin_id()
            success, msg = self.user_controller.update_loyalty_points(user['id'], points, admin_id)
            if success:
                QMessageBox.information(self, "Thành công", msg)
                self.load_users()
            else:
                QMessageBox.warning(self, "Lỗi", msg)

    def refresh(self):
        self.load_users()
