"""
Admin Orders Widget - Extended Logic
Order management from admin side
"""
from PyQt6.QtWidgets import (QWidget, QPushButton, QTableWidgetItem, QHBoxLayout,
                             QMessageBox, QDialog, QVBoxLayout, QLabel, QComboBox,
                             QTextEdit, QDialogButtonBox, QHeaderView)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor
from ui_generated.admin_orders import Ui_AdminOrdersWidget
from controllers.admin_order_controller import AdminOrderController
from controllers.admin_controller import AdminController
from utils.validators import format_currency
from datetime import datetime


class OrderStatusDialog(QDialog):
    """Dialog for updating order status"""

    def __init__(self, order, parent=None):
        super().__init__(parent)
        self.order = order
        self.setWindowTitle(f"Cập nhật trạng thái - Đơn hàng #{order['id']}")
        self.resize(400, 300)

        layout = QVBoxLayout(self)

        # Current status
        current_label = QLabel(f"Trạng thái hiện tại: {self.get_status_text(order['status'])}")
        current_label.setStyleSheet("font-weight: bold; color: #333; padding: 10px;")
        layout.addWidget(current_label)

        # New status
        new_status_label = QLabel("Trạng thái mới:")
        new_status_label.setStyleSheet("color: #333; padding-top: 10px;")
        layout.addWidget(new_status_label)

        self.statusComboBox = QComboBox()
        self.statusComboBox.addItem("Chờ xác nhận", "pending")
        self.statusComboBox.addItem("Đã xác nhận", "confirmed")
        self.statusComboBox.addItem("Đang pha chế", "preparing")
        self.statusComboBox.addItem("Sẵn sàng", "ready")
        self.statusComboBox.addItem("Đang giao", "delivering")
        self.statusComboBox.addItem("Hoàn thành", "completed")
        self.statusComboBox.addItem("Đã hủy", "cancelled")
        self.statusComboBox.setMinimumHeight(40)
        layout.addWidget(self.statusComboBox)

        # Set current status
        current_idx = self.statusComboBox.findData(order['status'])
        if current_idx >= 0:
            self.statusComboBox.setCurrentIndex(current_idx)

        # Notes
        notes_label = QLabel("Ghi chú (tùy chọn):")
        notes_label.setStyleSheet("color: #333; padding-top: 10px;")
        layout.addWidget(notes_label)

        self.notesTextEdit = QTextEdit()
        self.notesTextEdit.setPlaceholderText("Nhập ghi chú về thay đổi trạng thái...")
        self.notesTextEdit.setStyleSheet("""
            QTextEdit {
                border: 2px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                font-size: 13px;
            }
            QTextEdit:focus {
                border: 2px solid #c7a17a;
            }
        """)
        layout.addWidget(self.notesTextEdit)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

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

    def get_new_status(self):
        """Get selected new status"""
        return self.statusComboBox.currentData()

    def get_notes(self):
        """Get notes"""
        return self.notesTextEdit.toPlainText().strip()


class AdminOrdersWidget(QWidget, Ui_AdminOrdersWidget):
    """Admin orders management widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # Fix row height issue
        self.ordersTable.verticalHeader().setDefaultSectionSize(50)
        self.ordersTable.verticalHeader().setMinimumSectionSize(50)

        # Configure table header
        self.ordersTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        self.order_controller = AdminOrderController()
        self.admin_controller = AdminController()

        # Connect signals
        self.refreshButton.clicked.connect(self.load_orders)
        self.searchLineEdit.textChanged.connect(self.handle_search)
        self.statusComboBox.currentIndexChanged.connect(self.load_orders)
        self.dateFromEdit.dateChanged.connect(self.load_orders)
        self.dateToEdit.dateChanged.connect(self.load_orders)

        # Load orders
        self.load_orders()

    def load_orders(self):
        """Load and display orders"""
        # Get filters
        status = self.statusComboBox.currentData()
        date_from = self.dateFromEdit.date().toString("yyyy-MM-dd")
        date_to = self.dateToEdit.date().toString("yyyy-MM-dd")

        # Load orders
        orders = self.order_controller.get_all_orders(
            status=status if status else None,
            date_from=date_from,
            date_to=date_to,
            limit=200
        )

        self.display_orders(orders)

    def display_orders(self, orders):
        """Display orders in table"""
        self.ordersTable.setRowCount(len(orders))

        for row, order in enumerate(orders):
            # Order ID
            self.ordersTable.setItem(row, 0, QTableWidgetItem(f"#{order['id']}"))

            # Customer
            customer = order.get('customer_name', 'N/A')
            self.ordersTable.setItem(row, 1, QTableWidgetItem(customer))

            # Phone
            phone = order.get('customer_phone', 'N/A')
            self.ordersTable.setItem(row, 2, QTableWidgetItem(phone))

            # Store
            store = order.get('store_name', 'N/A')
            self.ordersTable.setItem(row, 3, QTableWidgetItem(store))

            # Order type
            order_type = self.get_order_type_text(order['order_type'])
            self.ordersTable.setItem(row, 4, QTableWidgetItem(order_type))

            # Total
            total = format_currency(order['total_amount'])
            self.ordersTable.setItem(row, 5, QTableWidgetItem(total))

            # Status
            status = self.get_status_text(order['status'])
            status_item = QTableWidgetItem(status)
            status_item.setForeground(self.get_status_color(order['status']))
            self.ordersTable.setItem(row, 6, status_item)

            # Date
            created_at = order['created_at']
            if isinstance(created_at, datetime):
                date_str = created_at.strftime("%d/%m/%Y %H:%M")
            else:
                date_str = str(created_at)
            self.ordersTable.setItem(row, 7, QTableWidgetItem(date_str))

            # Action buttons
            action_widget = QWidget()
            action_widget.setMinimumWidth(200)  # Prevent squashing
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 2, 5, 2)
            action_layout.setSpacing(5)

            # View button
            view_btn = QPushButton("Chi tiết")
            view_btn.setToolTip("Xem chi tiết đơn hàng")
            view_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 3px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """)
            view_btn.clicked.connect(lambda checked, o=order: self.handle_view_order(o))
            action_layout.addWidget(view_btn)

            # Update status button
            update_btn = QPushButton("Cập nhật")
            update_btn.setToolTip("Cập nhật trạng thái đơn hàng")
            update_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FF9800;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 3px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #F57C00;
                }
            """)
            update_btn.clicked.connect(lambda checked, o=order: self.handle_update_status(o))
            action_layout.addWidget(update_btn)

            self.ordersTable.setCellWidget(row, 8, action_widget)

            # Set row height to accommodate buttons
            self.ordersTable.setRowHeight(row, 50)

        # Resize columns
        QTimer.singleShot(100, self.adjust_columns)

    def adjust_columns(self):
        """Adjust column widths after layout"""
        header = self.ordersTable.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(8, QHeaderView.ResizeMode.Fixed)
        
        for i in [0, 2, 3, 4, 5, 6, 7]:
            self.ordersTable.resizeColumnToContents(i)
            
        self.ordersTable.setColumnWidth(8, 220)

    def get_order_type_text(self, order_type):
        """Get order type text"""
        type_map = {
            'pickup': 'Lấy tại cửa hàng',
            'delivery': 'Giao hàng',
            'dine_in': 'Tại quầy'
        }
        return type_map.get(order_type, order_type)

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

    def handle_search(self, keyword):
        """Handle search"""
        if not keyword.strip():
            self.load_orders()
            return

        orders = self.order_controller.search_orders(keyword)
        self.display_orders(orders)

    def handle_view_order(self, order):
        """Handle view order details"""
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

    def handle_update_status(self, order):
        """Handle update order status"""
        dialog = OrderStatusDialog(order, self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_status = dialog.get_new_status()
            notes = dialog.get_notes()

            admin_id = self.admin_controller.get_current_admin_id()

            if not admin_id:
                QMessageBox.warning(self, "Lỗi", "Vui lòng đăng nhập")
                return

            success, message = self.order_controller.update_order_status(
                order['id'], new_status, admin_id, notes
            )

            if success:
                QMessageBox.information(self, "Thành công", message)
                self.load_orders()
            else:
                QMessageBox.warning(self, "Lỗi", message)

    def refresh(self):
        """Refresh orders"""
        self.load_orders()
