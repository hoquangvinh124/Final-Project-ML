"""
Admin Dashboard Widget - Extended Logic
Display admin statistics and recent orders
"""
from PyQt6.QtWidgets import QWidget, QPushButton, QTableWidgetItem, QHBoxLayout, QHeaderView, QMessageBox
from PyQt6.QtCore import Qt, QTimer
from ui_generated.admin_dashboard import Ui_AdminDashboardWidget
from controllers.admin_controller import AdminController
from controllers.admin_order_controller import AdminOrderController
from utils.validators import format_currency
from datetime import datetime


class AdminDashboardWidget(QWidget, Ui_AdminDashboardWidget):
    """Admin dashboard widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # Fix row height issue
        self.recentOrdersTable.verticalHeader().setDefaultSectionSize(50)
        self.recentOrdersTable.verticalHeader().setMinimumSectionSize(50)

        # Configure table header
        self.recentOrdersTable.horizontalHeader().setStretchLastSection(False)
        self.recentOrdersTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        self.admin_controller = AdminController()
        self.order_controller = AdminOrderController()

        # Load data
        self.load_stats()
        self.load_recent_orders()

    def load_stats(self):
        """Load and display statistics"""
        stats = self.admin_controller.get_dashboard_stats()
        
        print(f"Dashboard stats: {stats}")  # Debug output

        # Update stat cards
        self.totalRevenueCard.valueLabel.setText(format_currency(stats.get('total_revenue', 0)))
        self.totalRevenueCard.titleLabel.setText("Tổng doanh thu")

        self.todayRevenueCard.valueLabel.setText(format_currency(stats.get('today_revenue', 0)))
        self.todayRevenueCard.titleLabel.setText("Doanh thu hôm nay")

        self.monthRevenueCard.valueLabel.setText(format_currency(stats.get('month_revenue', 0)))
        self.monthRevenueCard.titleLabel.setText("Doanh thu tháng này")

        self.totalOrdersCard.valueLabel.setText(str(stats.get('total_orders', 0)))
        self.totalOrdersCard.titleLabel.setText("Tổng đơn hàng")

        self.todayOrdersCard.valueLabel.setText(str(stats.get('today_orders', 0)))
        self.todayOrdersCard.titleLabel.setText("Đơn hàng hôm nay")

        self.pendingOrdersCard.valueLabel.setText(str(stats.get('pending_orders', 0)))
        self.pendingOrdersCard.titleLabel.setText("Đơn chờ xác nhận")

        self.totalCustomersCard.valueLabel.setText(str(stats.get('total_customers', 0)))
        self.totalCustomersCard.titleLabel.setText("Tổng khách hàng")

        self.totalProductsCard.valueLabel.setText(str(stats.get('total_products', 0)))
        self.totalProductsCard.titleLabel.setText("Tổng sản phẩm")

    def load_recent_orders(self):
        """Load and display recent orders"""
        orders = self.admin_controller.get_recent_orders(10)

        self.recentOrdersTable.setRowCount(len(orders))

        for row, order in enumerate(orders):
            # Order ID
            self.recentOrdersTable.setItem(row, 0, QTableWidgetItem(f"#{order['id']}"))

            # Customer
            customer = order.get('customer_name', 'N/A')
            self.recentOrdersTable.setItem(row, 1, QTableWidgetItem(customer))

            # Store
            store = order.get('store_name', 'N/A')
            self.recentOrdersTable.setItem(row, 2, QTableWidgetItem(store))

            # Total
            total = format_currency(order['total_amount'])
            self.recentOrdersTable.setItem(row, 3, QTableWidgetItem(total))

            # Status
            status = self.get_status_text(order['status'])
            status_item = QTableWidgetItem(status)
            status_item.setForeground(self.get_status_color(order['status']))
            self.recentOrdersTable.setItem(row, 4, status_item)

            # Date
            created_at = order['created_at']
            if isinstance(created_at, datetime):
                date_str = created_at.strftime("%d/%m/%Y %H:%M")
            else:
                date_str = str(created_at)
            self.recentOrdersTable.setItem(row, 5, QTableWidgetItem(date_str))

            # Action button
            action_widget = QWidget()
            action_widget.setMinimumWidth(100)
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 2, 5, 2)

            view_btn = QPushButton("Xem")
            view_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            view_btn.clicked.connect(lambda checked, o=order: self.handle_view_order(o))
            action_layout.addWidget(view_btn)

            self.recentOrdersTable.setCellWidget(row, 6, action_widget)

        # Resize columns to content
        QTimer.singleShot(100, self.adjust_columns)

    def adjust_columns(self):
        header = self.recentOrdersTable.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        
        for i in [0, 2, 3, 4, 5]:
            self.recentOrdersTable.resizeColumnToContents(i)
            
        self.recentOrdersTable.setColumnWidth(6, 100)

    def get_status_text(self, status):
        """Get Vietnamese status text"""
        status_map = {
            'pending': 'Chờ xác nhận',
            'confirmed': 'Đã xác nhận',
            'preparing': 'Đang pha chế',
            'ready': 'Sẵn sàng',
            'delivering': 'Đang giao',
            'completed': 'Hoàn thành',
            'cancelled': 'Đã hủy'
        }
        return status_map.get(status, status)

    def get_status_color(self, status):
        """Get color for status"""
        from PyQt6.QtGui import QColor

        color_map = {
            'pending': QColor('#FF9800'),
            'confirmed': QColor('#2196F3'),
            'preparing': QColor('#9C27B0'),
            'ready': QColor('#4CAF50'),
            'delivering': QColor('#00BCD4'),
            'completed': QColor('#4CAF50'),
            'cancelled': QColor('#F44336')
        }
        return color_map.get(status, QColor('#000000'))

    def get_order_type_text(self, order_type):
        """Get order type text"""
        type_map = {
            'pickup': 'Lấy tại cửa hàng',
            'delivery': 'Giao hàng',
            'dine_in': 'Tại quầy'
        }
        return type_map.get(order_type, order_type)

    def handle_view_order(self, order):
        """Handle view order button click"""
        # Get full order details
        order_details = self.order_controller.get_order_details(order['id'])

        if not order_details:
            QMessageBox.warning(self, "Lỗi", "Không thể tải thông tin đơn hàng")
            return

        # Show order details dialog
        msg = f"""
<h2>Đơn hàng #{order_details['id']}</h2>

<h3>Thông tin khách hàng:</h3>
<p>
Tên: {order_details.get('customer_name', 'N/A')}<br>
Email: {order_details.get('customer_email', 'N/A')}<br>
SĐT: {order_details.get('customer_phone', 'N/A')}
</p>

<h3>Thông tin đơn hàng:</h3>
<p>
Loại: {self.get_order_type_text(order_details['order_type'])}<br>
Cửa hàng: {order_details.get('store_name', 'N/A')}<br>
Trạng thái: {self.get_status_text(order_details['status'])}<br>
Tổng tiền: {format_currency(order_details['total_amount'])}<br>
Phương thức thanh toán: {order_details.get('payment_method', 'N/A')}
</p>
        """

        if order_details.get('delivery_address'):
            msg += f"<p>Địa chỉ giao: {order_details['delivery_address']}</p>"

        if order_details.get('notes'):
            msg += f"<p>Ghi chú: {order_details['notes']}</p>"

        msgbox = QMessageBox(self)
        msgbox.setWindowTitle("Chi tiết đơn hàng")
        msgbox.setText(msg)
        msgbox.exec()

    def refresh(self):
        """Refresh dashboard data"""
        self.load_stats()
        self.load_recent_orders()
