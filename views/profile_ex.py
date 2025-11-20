"""
Profile Widget - Extended Logic
User profile management with full features
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QLineEdit, QMessageBox, QScrollArea)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImageReader
from controllers.user_controller import UserController
from controllers.auth_controller import AuthController
from utils.validators import format_currency
import os


class ProfileWidget(QWidget):
    """User profile widget with full functionality"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.user_controller = UserController()
        self.auth_controller = AuthController()
        
        # Increase image allocation limit to 512MB
        QImageReader.setAllocationLimit(512)

        self.setup_ui()
        self.load_profile()

    def setup_ui(self):
        """Setup UI"""
        main_layout = QVBoxLayout(self)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)

        # Header
        title = QLabel("👤 Tài khoản của bạn")
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px 0;")
        layout.addWidget(title)

        # Avatar and basic info
        profile_frame = QFrame()
        profile_frame.setFrameShape(QFrame.Shape.StyledPanel)
        profile_frame.setStyleSheet("background-color: #f9f9f9; padding: 20px;")
        profile_layout = QVBoxLayout(profile_frame)
        profile_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Avatar image
        avatar_label = QLabel()
        avatar_label.setFixedSize(120, 120)
        avatar_label.setScaledContents(False)
        
        # Try to load avatar image
        avatar_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "images", "avatar.jpg")
        
        avatar_pixmap = QPixmap(avatar_path)
        
        if not avatar_pixmap.isNull():
            scaled_pixmap = avatar_pixmap.scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            avatar_label.setPixmap(scaled_pixmap)
        else:
            avatar_label.setText("👤")
            avatar_label.setStyleSheet("font-size: 60px;")
        
        avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        profile_layout.addWidget(avatar_label, 0, Qt.AlignmentFlag.AlignCenter)

        # Name
        self.name_label = QLabel()
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        profile_layout.addWidget(self.name_label)

        # Email
        self.email_label = QLabel()
        self.email_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.email_label.setStyleSheet("color: #666;")
        profile_layout.addWidget(self.email_label)

        layout.addWidget(profile_frame)

        # Membership section
        membership_frame = QFrame()
        membership_frame.setFrameShape(QFrame.Shape.StyledPanel)
        membership_layout = QVBoxLayout(membership_frame)

        membership_title = QLabel("Hạng thành viên")
        membership_title.setStyleSheet("font-weight: bold; font-size: 16px;")
        membership_layout.addWidget(membership_title)

        self.tier_label = QLabel()
        self.tier_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #c7a17a;")
        membership_layout.addWidget(self.tier_label)

        self.points_label = QLabel()
        self.points_label.setStyleSheet("font-size: 16px; color: #666;")
        membership_layout.addWidget(self.points_label)

        self.next_tier_label = QLabel()
        self.next_tier_label.setStyleSheet("font-size: 14px; color: #999;")
        membership_layout.addWidget(self.next_tier_label)

        layout.addWidget(membership_frame)

        # Statistics
        stats_frame = QFrame()
        stats_frame.setFrameShape(QFrame.Shape.StyledPanel)
        stats_layout = QVBoxLayout(stats_frame)

        stats_title = QLabel("Thống kê")
        stats_title.setStyleSheet("font-weight: bold; font-size: 16px;")
        stats_layout.addWidget(stats_title)

        self.stats_label = QLabel()
        self.stats_label.setWordWrap(True)
        stats_layout.addWidget(self.stats_label)

        layout.addWidget(stats_frame)

        # Action buttons
        actions_frame = QFrame()
        actions_frame.setFrameShape(QFrame.Shape.StyledPanel)
        actions_layout = QVBoxLayout(actions_frame)

        edit_btn = QPushButton("Chỉnh sửa thông tin")
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #A31E25;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8B181F;
            }
        """)
        edit_btn.clicked.connect(self.handle_edit_profile)
        actions_layout.addWidget(edit_btn)

        change_password_btn = QPushButton("Đổi mật khẩu")
        change_password_btn.setStyleSheet("""
            QPushButton {
                background-color: #A31E25;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8B181F;
            }
        """)
        change_password_btn.clicked.connect(self.handle_change_password)
        actions_layout.addWidget(change_password_btn)

        points_history_btn = QPushButton("Lịch sử điểm thưởng")
        points_history_btn.setStyleSheet("""
            QPushButton {
                background-color: #A31E25;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8B181F;
            }
        """)
        points_history_btn.clicked.connect(self.handle_points_history)
        actions_layout.addWidget(points_history_btn)

        vouchers_btn = QPushButton("Voucher của tôi")
        vouchers_btn.setStyleSheet("""
            QPushButton {
                background-color: #A31E25;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8B181F;
            }
        """)
        vouchers_btn.clicked.connect(self.handle_vouchers)
        actions_layout.addWidget(vouchers_btn)

        layout.addWidget(actions_frame)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

    def load_profile(self):
        """Load user profile data"""
        user_id = self.auth_controller.get_current_user_id()
        if not user_id:
            return

        # Get profile
        profile = self.user_controller.get_profile(user_id)
        if not profile:
            return

        # Update basic info
        self.name_label.setText(profile['full_name'])
        self.email_label.setText(profile['email'])

        # Update membership
        tier_icons = {
            'Bronze': '🥉',
            'Silver': '🥈',
            'Gold': '🥇'
        }
        icon = tier_icons.get(profile['membership_tier'], '🥉')
        self.tier_label.setText(f"{icon} {profile['membership_tier']} Member")

        points = profile.get('loyalty_points', 0)
        self.points_label.setText(f"Điểm thưởng: {points:,} điểm".replace(',', '.'))

        # Get loyalty info
        loyalty_info = self.user_controller.get_loyalty_info(user_id)
        if loyalty_info.get('next_tier'):
            points_to_next = loyalty_info.get('points_to_next', 0)
            next_tier = loyalty_info['next_tier']
            self.next_tier_label.setText(
                f"Cần thêm {points_to_next:,} điểm để lên hạng {next_tier}".replace(',', '.')
            )
        else:
            self.next_tier_label.setText("🎉 Bạn đã đạt hạng cao nhất!")

        # Get order history
        orders = self.user_controller.get_order_history(user_id, limit=100)
        total_orders = len(orders)
        total_spent = sum(order.get('total_amount', 0) for order in orders)

        stats_text = f"""
        <p><b>Tổng đơn hàng:</b> {total_orders} đơn</p>
        <p><b>Tổng chi tiêu:</b> {format_currency(total_spent)}</p>
        """
        self.stats_label.setText(stats_text)

    def handle_edit_profile(self):
        """Handle edit profile button"""
        from PyQt6.QtWidgets import QDialog, QFormLayout

        user_id = self.auth_controller.get_current_user_id()
        if not user_id:
            return

        profile = self.user_controller.get_profile(user_id)
        if not profile:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Chỉnh sửa thông tin")
        dialog.resize(400, 300)

        layout = QFormLayout(dialog)

        # Name
        name_edit = QLineEdit(profile['full_name'])
        layout.addRow("Họ và tên:", name_edit)

        # Phone
        phone_edit = QLineEdit(profile.get('phone', ''))
        layout.addRow("Số điện thoại:", phone_edit)

        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Lưu")
        cancel_btn = QPushButton("Hủy")
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

        cancel_btn.clicked.connect(dialog.reject)

        def save_changes():
            success, message = self.user_controller.update_profile(
                user_id,
                full_name=name_edit.text().strip(),
                phone=phone_edit.text().strip() if phone_edit.text().strip() else None
            )

            if success:
                QMessageBox.information(dialog, "Thành công", message)
                self.load_profile()
                dialog.accept()
            else:
                QMessageBox.warning(dialog, "Lỗi", message)

        save_btn.clicked.connect(save_changes)

        dialog.exec()

    def handle_change_password(self):
        """Handle change password button"""
        from PyQt6.QtWidgets import QDialog, QFormLayout

        user_id = self.auth_controller.get_current_user_id()
        if not user_id:
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Đổi mật khẩu")
        dialog.resize(400, 250)

        layout = QFormLayout(dialog)

        old_password = QLineEdit()
        old_password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("Mật khẩu hiện tại:", old_password)

        new_password = QLineEdit()
        new_password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("Mật khẩu mới:", new_password)

        confirm_password = QLineEdit()
        confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("Xác nhận mật khẩu:", confirm_password)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Đổi mật khẩu")
        cancel_btn = QPushButton("Hủy")
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addRow(btn_layout)

        cancel_btn.clicked.connect(dialog.reject)

        def change_password():
            if new_password.text() != confirm_password.text():
                QMessageBox.warning(dialog, "Lỗi", "Mật khẩu xác nhận không khớp")
                return

            success, message = self.auth_controller.change_password(
                user_id,
                old_password.text(),
                new_password.text()
            )

            if success:
                QMessageBox.information(dialog, "Thành công", message)
                dialog.accept()
            else:
                QMessageBox.warning(dialog, "Lỗi", message)

        save_btn.clicked.connect(change_password)

        dialog.exec()

    def handle_points_history(self):
        """Handle points history button"""
        user_id = self.auth_controller.get_current_user_id()
        if not user_id:
            return

        history = self.user_controller.get_points_history(user_id)

        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QListWidgetItem

        dialog = QDialog(self)
        dialog.setWindowTitle("Lịch sử điểm thưởng")
        dialog.resize(500, 600)

        layout = QVBoxLayout(dialog)

        title = QLabel("📈 Lịch sử tích điểm")
        title.setStyleSheet("font-weight: bold; font-size: 16px; padding: 10px;")
        layout.addWidget(title)

        list_widget = QListWidget()

        if not history:
            empty_item = QListWidgetItem("Chưa có lịch sử điểm thưởng")
            list_widget.addItem(empty_item)
        else:
            for record in history:
                from utils.helpers import time_ago
                sign = '+' if record['transaction_type'] == 'earn' else '-'
                text = f"{sign}{record['points']} điểm - {record['description']} ({time_ago(record['created_at'])})"
                item = QListWidgetItem(text)
                list_widget.addItem(item)

        layout.addWidget(list_widget)

        close_btn = QPushButton("Đóng")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.exec()

    def handle_vouchers(self):
        """Handle vouchers button"""
        user_id = self.auth_controller.get_current_user_id()
        if not user_id:
            return

        vouchers = self.user_controller.get_available_vouchers(user_id)

        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QListWidgetItem

        dialog = QDialog(self)
        dialog.setWindowTitle("Voucher của tôi")
        dialog.resize(500, 600)

        layout = QVBoxLayout(dialog)

        title = QLabel("🎟️ Voucher có thể sử dụng")
        title.setStyleSheet("font-weight: bold; font-size: 16px; padding: 10px;")
        layout.addWidget(title)

        list_widget = QListWidget()

        if not vouchers:
            empty_item = QListWidgetItem("Chưa có voucher nào")
            list_widget.addItem(empty_item)
        else:
            for voucher in vouchers:
                discount_text = f"{voucher['discount_value']}%"  if voucher['discount_type'] == 'percentage' else format_currency(voucher['discount_value'])
                text = f"{voucher['code']} - {voucher['name']} (Giảm {discount_text})"
                item = QListWidgetItem(text)
                list_widget.addItem(item)

        layout.addWidget(list_widget)

        close_btn = QPushButton("Đóng")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.exec()

    def refresh(self):
        """Refresh profile data"""
        self.load_profile()
