"""
Orders Widget - Extended Logic
Order history and tracking with timeline
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QScrollArea, QMessageBox, QDialog)
from PyQt6.QtCore import Qt, pyqtSignal
from controllers.order_controller import OrderController
from controllers.auth_controller import AuthController
from utils.validators import format_currency
from utils.helpers import time_ago


class OrderTimelineWidget(QFrame):
    """Order tracking timeline widget"""

    def __init__(self, timeline_data, parent=None):
        super().__init__(parent)
        self.timeline_data = timeline_data
        self.setup_ui()

    def setup_ui(self):
        """Setup timeline UI"""
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("background-color: #f9f9f9; padding: 15px;")

        main_layout = QVBoxLayout(self)

        title = QLabel("Trạng thái đơn hàng")
        title.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        main_layout.addWidget(title)

        # Horizontal timeline layout
        timeline_layout = QHBoxLayout()
        timeline_layout.setSpacing(5)

        # Timeline steps
        for i, step in enumerate(self.timeline_data['timeline']):
            # Status indicator
            indicator = QLabel("✓" if step['completed'] else "○")
            indicator.setFixedWidth(30)
            indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
            indicator.setStyleSheet(f"""
                font-size: 20px;
                font-weight: bold;
                color: {'#4CAF50' if step['completed'] else '#ccc'};
            """)
            timeline_layout.addWidget(indicator)

            # Add connecting line except for last item
            if i < len(self.timeline_data['timeline']) - 1:
                line = QLabel("—")
                line.setFixedWidth(40)
                line.setAlignment(Qt.AlignmentFlag.AlignCenter)
                line.setStyleSheet(f"color: {'#4CAF50' if step['completed'] else '#ccc'}; font-weight: bold;")
                timeline_layout.addWidget(line)

        main_layout.addLayout(timeline_layout)

        # Labels layout (horizontal)
        labels_layout = QHBoxLayout()
        labels_layout.setSpacing(5)
        
        for i, step in enumerate(self.timeline_data['timeline']):
            # Status label
            label = QLabel(step['label'])
            label.setFixedWidth(70)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setWordWrap(True)
            label.setStyleSheet(f"""
                font-size: 11px;
                color: {'#333' if step['completed'] else '#999'};
                {'font-weight: bold;' if step['completed'] else ''}
            """)
            labels_layout.addWidget(label)
            
            # Add spacer for the connecting line
            if i < len(self.timeline_data['timeline']) - 1:
                labels_layout.addSpacing(40)
        
        main_layout.addLayout(labels_layout)


class OrderItemWidget(QFrame):
    """Single order item widget"""

    view_details_clicked = pyqtSignal(dict)
    reorder_clicked = pyqtSignal(int)
    cancel_clicked = pyqtSignal(int)

    def __init__(self, order_data, parent=None):
        super().__init__(parent)
        self.order_data = order_data
        self.setup_ui()

    def setup_ui(self):
        """Setup order item UI"""
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setMinimumHeight(150)

        main_layout = QHBoxLayout(self)

        # Order info
        info_layout = QVBoxLayout()

        # Order number and date
        header_layout = QHBoxLayout()

        order_num = QLabel(f"Đơn hàng #{self.order_data['order_number']}")
        order_num.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(order_num)

        header_layout.addStretch()

        date_label = QLabel(time_ago(self.order_data['created_at']))
        date_label.setStyleSheet("color: #666; font-size: 12px;")
        header_layout.addWidget(date_label)

        info_layout.addLayout(header_layout)

        # Store info
        if self.order_data.get('store_name'):
            store_label = QLabel(f"{self.order_data['store_name']}")
            store_label.setStyleSheet("color: #666; font-size: 12px;")
            info_layout.addWidget(store_label)

        # Order type and payment
        details_text = f"{self.get_order_type_label()} | "
        details_text += f"{self.get_payment_method_label()}"
        details_label = QLabel(details_text)
        details_label.setStyleSheet("color: #666; font-size: 12px;")
        info_layout.addWidget(details_label)

        # Items summary
        items_label = QLabel(f"{self.order_data['item_count']} món | {self.order_data['total_quantity']} sản phẩm")
        items_label.setStyleSheet("color: #666; font-size: 12px;")
        info_layout.addWidget(items_label)

        # Status
        status_label = QLabel(self.get_status_label())
        status_label.setStyleSheet(f"""
            background-color: {self.get_status_color()};
            color: white;
            padding: 4px 12px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 12px;
        """)
        status_label.setMaximumWidth(150)
        info_layout.addWidget(status_label)

        info_layout.addStretch()
        main_layout.addLayout(info_layout, stretch=1)

        # Total and actions
        action_layout = QVBoxLayout()

        total_label = QLabel(format_currency(self.order_data['total_amount']))
        total_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #c7a17a;")
        total_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        action_layout.addWidget(total_label)

        action_layout.addStretch()

        # Action buttons
        buttons_layout = QVBoxLayout()

        view_btn = QPushButton("Xem chi tiết")
        view_btn.setMinimumWidth(140)
        view_btn.clicked.connect(lambda: self.view_details_clicked.emit(self.order_data))
        buttons_layout.addWidget(view_btn)

        if self.order_data['status'] == 'completed':
            reorder_btn = QPushButton("Đặt lại")
            reorder_btn.setMinimumWidth(140)
            reorder_btn.clicked.connect(lambda: self.reorder_clicked.emit(self.order_data['id']))
            buttons_layout.addWidget(reorder_btn)

        if self.order_data['status'] in ['pending', 'confirmed']:
            cancel_btn = QPushButton("Hủy đơn")
            cancel_btn.setMinimumWidth(140)
            cancel_btn.setStyleSheet("background-color: #f44336;")
            cancel_btn.clicked.connect(lambda: self.cancel_clicked.emit(self.order_data['id']))
            buttons_layout.addWidget(cancel_btn)

        action_layout.addLayout(buttons_layout)

        main_layout.addLayout(action_layout)

    def get_order_type_icon(self):
        """Get order type icon"""
        icons = {
            'pickup': '🏪',
            'delivery': '🚚',
            'dine_in': '🍽️'
        }
        return icons.get(self.order_data['order_type'], '📦')

    def get_order_type_label(self):
        """Get order type label"""
        labels = {
            'pickup': 'Nhận tại cửa hàng',
            'delivery': 'Giao hàng',
            'dine_in': 'Dùng tại chỗ'
        }
        return labels.get(self.order_data['order_type'], 'Không xác định')

    def get_payment_method_label(self):
        """Get payment method label"""
        labels = {
            'cash': 'Tiền mặt',
            'momo': 'MoMo',
            'shopeepay': 'ShopeePay',
            'zalopay': 'ZaloPay',
            'applepay': 'Apple Pay',
            'googlepay': 'Google Pay',
            'card': 'Thẻ ngân hàng'
        }
        return labels.get(self.order_data['payment_method'], 'Không xác định')

    def get_status_label(self):
        """Get status label in Vietnamese"""
        labels = {
            'pending': 'Chờ xác nhận',
            'confirmed': 'Đã xác nhận',
            'preparing': 'Đang pha chế',
            'ready': 'Đã hoàn thành',
            'delivering': 'Đang giao hàng',
            'completed': 'Hoàn thành',
            'cancelled': 'Đã hủy'
        }
        return labels.get(self.order_data['status'], 'Không xác định')

    def get_status_color(self):
        """Get status color"""
        colors = {
            'pending': '#FF9800',
            'confirmed': '#2196F3',
            'preparing': '#9C27B0',
            'ready': '#4CAF50',
            'delivering': '#00BCD4',
            'completed': '#4CAF50',
            'cancelled': '#F44336'
        }
        return colors.get(self.order_data['status'], '#757575')


class OrdersWidget(QWidget):
    """Orders history widget with full functionality"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.order_controller = OrderController()
        self.auth_controller = AuthController()

        self.setup_ui()
        self.load_orders()

    def setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout(self)

        # Header
        header_layout = QHBoxLayout()

        title = QLabel("📦 Đơn hàng của bạn")
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px 0;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        refresh_btn = QPushButton("🔄 Làm mới")
        refresh_btn.clicked.connect(self.load_orders)
        header_layout.addWidget(refresh_btn)

        layout.addLayout(header_layout)

        # Orders scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        scroll_content = QWidget()
        self.orders_layout = QVBoxLayout(scroll_content)

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

    def load_orders(self):
        """Load user orders"""
        user_id = self.auth_controller.get_current_user_id()
        if not user_id:
            return

        # Clear existing orders
        while self.orders_layout.count():
            item = self.orders_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Get orders
        orders = self.order_controller.get_user_orders(user_id)

        if not orders:
            # Show empty state
            empty_label = QLabel("📦\n\nChưa có đơn hàng nào\n\nHãy đặt món ngay!")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("font-size: 16px; color: #999; padding: 50px;")
            self.orders_layout.addWidget(empty_label)
            return

        # Add order items
        for order in orders:
            order_widget = OrderItemWidget(order)
            order_widget.view_details_clicked.connect(self.handle_view_details)
            order_widget.reorder_clicked.connect(self.handle_reorder)
            order_widget.cancel_clicked.connect(self.handle_cancel)
            self.orders_layout.addWidget(order_widget)

        # Add stretch at the end
        self.orders_layout.addStretch()

    def handle_view_details(self, order_data):
        """Handle view details button"""
        # Show order detail dialog with tracking
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Chi tiết đơn hàng #{order_data['order_number']}")
        dialog.resize(600, 700)

        layout = QVBoxLayout(dialog)

        # Order info
        info_text = f"""
        <h3>Đơn hàng #{order_data['order_number']}</h3>
        <p><b>Thời gian:</b> {time_ago(order_data['created_at'])}</p>
        <p><b>Trạng thái:</b> {OrderItemWidget(order_data).get_status_label()}</p>
        <p><b>Loại đơn:</b> {OrderItemWidget(order_data).get_order_type_label()}</p>
        <p><b>Thanh toán:</b> {OrderItemWidget(order_data).get_payment_method_label()}</p>
        <p><b>Tổng tiền:</b> <span style="color: #c7a17a; font-size: 18px;">{format_currency(order_data['total_amount'])}</span></p>
        """

        if order_data.get('store_name'):
            info_text += f"<p><b>Cửa hàng:</b> {order_data['store_name']}</p>"

        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Tracking timeline
        tracking = self.order_controller.track_order(order_data['id'], self.auth_controller.get_current_user_id())
        if tracking:
            timeline_widget = OrderTimelineWidget(tracking)
            layout.addWidget(timeline_widget)

        # Close button
        close_btn = QPushButton("Đóng")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.exec()

    def handle_reorder(self, order_id):
        """Handle reorder button"""
        user_id = self.auth_controller.get_current_user_id()
        if not user_id:
            return

        success, message = self.order_controller.reorder(order_id, user_id)

        if success:
            QMessageBox.information(self, "Thành công", message)
        else:
            QMessageBox.warning(self, "Lỗi", message)

    def handle_cancel(self, order_id):
        """Handle cancel button"""
        reply = QMessageBox.question(
            self,
            "Xác nhận",
            "Bạn có chắc muốn hủy đơn hàng này?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            user_id = self.auth_controller.get_current_user_id()
            if not user_id:
                return

            success, message = self.order_controller.cancel_order(order_id, user_id, "Khách hàng hủy")

            if success:
                QMessageBox.information(self, "Thành công", message)
                self.load_orders()
            else:
                QMessageBox.warning(self, "Lỗi", message)

    def refresh(self):
        """Refresh orders list"""
        self.load_orders()
