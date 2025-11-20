"""
Checkout Dialog
Complete checkout flow with order type selection and payment
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QRadioButton, QComboBox, QTextEdit, QPushButton,
                             QButtonGroup, QFrame, QMessageBox, QLineEdit)
from PyQt6.QtCore import Qt, pyqtSignal
from controllers.order_controller import OrderController
from controllers.auth_controller import AuthController
from controllers.cart_controller import CartController
from utils.validators import format_currency


class CheckoutDialog(QDialog):
    """Checkout dialog for placing orders"""

    order_placed = pyqtSignal(int)  # order_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Thanh toán")
        self.setMinimumSize(600, 750)
        self.resize(600, 800)

        self.order_controller = OrderController()
        self.auth_controller = AuthController()
        self.cart_controller = CartController()

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Setup UI"""
        from PyQt6.QtWidgets import QScrollArea, QWidget
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        # Content widget
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(20, 10, 20, 10)

        # Title
        title = QLabel("Hoàn tất đơn hàng")
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        # Order type section
        type_frame = QFrame()
        type_frame.setFrameShape(QFrame.Shape.StyledPanel)
        type_layout = QVBoxLayout(type_frame)

        type_label = QLabel("Phương thức nhận hàng:")
        type_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        type_layout.addWidget(type_label)

        self.order_type_group = QButtonGroup()

        self.pickup_radio = QRadioButton("Nhận tại cửa hàng (Pickup)")
        self.pickup_radio.setChecked(True)
        self.pickup_radio.toggled.connect(self.on_order_type_changed)
        self.order_type_group.addButton(self.pickup_radio, 1)
        type_layout.addWidget(self.pickup_radio)

        self.delivery_radio = QRadioButton("Giao hàng tận nơi (Delivery)")
        self.delivery_radio.toggled.connect(self.on_order_type_changed)
        self.order_type_group.addButton(self.delivery_radio, 2)
        type_layout.addWidget(self.delivery_radio)

        self.dinein_radio = QRadioButton("Dùng tại chỗ (Dine-in)")
        self.dinein_radio.toggled.connect(self.on_order_type_changed)
        self.order_type_group.addButton(self.dinein_radio, 3)
        type_layout.addWidget(self.dinein_radio)

        layout.addWidget(type_frame)

        # Store selection (for pickup)
        self.store_frame = QFrame()
        self.store_frame.setFrameShape(QFrame.Shape.StyledPanel)
        store_layout = QVBoxLayout(self.store_frame)

        store_label = QLabel("Chọn cửa hàng:")
        store_label.setStyleSheet("font-weight: bold;")
        store_layout.addWidget(store_label)

        self.store_combo = QComboBox()
        self.store_combo.setMinimumHeight(40)
        store_layout.addWidget(self.store_combo)

        layout.addWidget(self.store_frame)

        # Delivery address (for delivery)
        self.delivery_frame = QFrame()
        self.delivery_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.delivery_frame.setVisible(False)
        delivery_layout = QVBoxLayout(self.delivery_frame)

        address_label = QLabel("Địa chỉ giao hàng:")
        address_label.setStyleSheet("font-weight: bold;")
        delivery_layout.addWidget(address_label)

        self.address_edit = QLineEdit()
        self.address_edit.setPlaceholderText("Nhập địa chỉ giao hàng...")
        self.address_edit.setMinimumHeight(40)
        delivery_layout.addWidget(self.address_edit)

        layout.addWidget(self.delivery_frame)

        # Table number (for dine-in)
        self.table_frame = QFrame()
        self.table_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.table_frame.setVisible(False)
        table_layout = QVBoxLayout(self.table_frame)

        table_label = QLabel("Số bàn:")
        table_label.setStyleSheet("font-weight: bold;")
        table_layout.addWidget(table_label)

        self.table_edit = QLineEdit()
        self.table_edit.setPlaceholderText("Nhập số bàn...")
        self.table_edit.setMinimumHeight(40)
        table_layout.addWidget(self.table_edit)

        layout.addWidget(self.table_frame)

        # Payment method section
        payment_frame = QFrame()
        payment_frame.setFrameShape(QFrame.Shape.StyledPanel)
        payment_layout = QVBoxLayout(payment_frame)

        payment_label = QLabel("Phương thức thanh toán:")
        payment_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        payment_layout.addWidget(payment_label)

        self.payment_combo = QComboBox()
        self.payment_combo.setMinimumHeight(40)
        self.payment_combo.addItem("Tiền mặt (Cash)", "cash")
        self.payment_combo.addItem("MoMo", "momo")
        self.payment_combo.addItem("ShopeePay", "shopeepay")
        self.payment_combo.addItem("ZaloPay", "zalopay")
        self.payment_combo.addItem("Apple Pay", "applepay")
        self.payment_combo.addItem("Google Pay", "googlepay")
        self.payment_combo.addItem("Thẻ ngân hàng", "card")
        payment_layout.addWidget(self.payment_combo)

        layout.addWidget(payment_frame)

        # Notes section
        notes_frame = QFrame()
        notes_frame.setFrameShape(QFrame.Shape.StyledPanel)
        notes_layout = QVBoxLayout(notes_frame)
        notes_layout.setContentsMargins(10, 5, 10, 5)
        notes_layout.setSpacing(5)

        notes_label = QLabel("Ghi chú:")
        notes_label.setStyleSheet("font-weight: bold;")
        notes_layout.addWidget(notes_label)

        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Ghi chú cho đơn hàng (tùy chọn)...")
        self.notes_edit.setMinimumHeight(60)
        self.notes_edit.setMaximumHeight(80)
        notes_layout.addWidget(self.notes_edit, 1)

        layout.addWidget(notes_frame)

        # Order summary
        summary_frame = QFrame()
        summary_frame.setFrameShape(QFrame.Shape.StyledPanel)
        summary_frame.setStyleSheet("background-color: #f9f9f9;")
        summary_layout = QVBoxLayout(summary_frame)

        summary_title = QLabel("Tóm tắt đơn hàng")
        summary_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        summary_layout.addWidget(summary_title)

        self.summary_label = QLabel()
        self.summary_label.setStyleSheet("padding: 10px;")
        summary_layout.addWidget(self.summary_label)

        layout.addWidget(summary_frame)
        
        # Set scroll area content
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

        # Buttons (outside scroll area, always visible)
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(20, 10, 20, 10)

        cancel_btn = QPushButton("Hủy")
        cancel_btn.setMinimumHeight(45)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #666666;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        self.place_order_btn = QPushButton("Đặt hàng")
        self.place_order_btn.setMinimumHeight(45)
        self.place_order_btn.setStyleSheet("""
            QPushButton {
                background-color: #A31E25;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #8B1A1F;
            }
        """)
        self.place_order_btn.clicked.connect(self.handle_place_order)
        button_layout.addWidget(self.place_order_btn)

        main_layout.addLayout(button_layout)

    def load_data(self):
        """Load stores and order summary"""
        # Load stores
        stores = self.order_controller.get_available_stores()
        for store in stores:
            self.store_combo.addItem(
                f"{store['name']} - {store['address']}",
                store['id']
            )

        # Update summary
        self.update_summary()

    def on_order_type_changed(self):
        """Handle order type change"""
        if self.pickup_radio.isChecked():
            self.store_frame.setVisible(True)
            self.delivery_frame.setVisible(False)
            self.table_frame.setVisible(False)
        elif self.delivery_radio.isChecked():
            self.store_frame.setVisible(False)
            self.delivery_frame.setVisible(True)
            self.table_frame.setVisible(False)
        elif self.dinein_radio.isChecked():
            self.store_frame.setVisible(True)
            self.delivery_frame.setVisible(False)
            self.table_frame.setVisible(True)

        self.update_summary()

    def update_summary(self):
        """Update order summary"""
        user_id = self.auth_controller.get_current_user_id()
        if not user_id:
            return

        # Get order type
        order_type = 'pickup'
        if self.delivery_radio.isChecked():
            order_type = 'delivery'
        elif self.dinein_radio.isChecked():
            order_type = 'dine_in'

        # Get cart summary
        summary = self.cart_controller.get_cart_summary(user_id, None, order_type)

        text = f"""
        <p><b>Số món:</b> {summary['item_count']}</p>
        <p><b>Tạm tính:</b> {format_currency(summary['subtotal'])}</p>
        <p><b>Giảm giá:</b> -{format_currency(summary['discount_amount'])}</p>
        <p><b>Phí giao hàng:</b> {format_currency(summary['delivery_fee'])}</p>
        <hr>
        <p style="font-size: 16px;"><b>Tổng cộng:</b> <span style="color: #c7a17a;">{format_currency(summary['total'])}</span></p>
        """

        self.summary_label.setText(text)

    def handle_place_order(self):
        """Handle place order button"""
        user_id = self.auth_controller.get_current_user_id()
        if not user_id:
            return

        # Get order type
        if self.pickup_radio.isChecked():
            order_type = 'pickup'
        elif self.delivery_radio.isChecked():
            order_type = 'delivery'
        else:
            order_type = 'dine_in'

        # Get store ID
        store_id = None
        if order_type in ['pickup', 'dine_in']:
            store_id = self.store_combo.currentData()

        # Get delivery address
        delivery_address = None
        if order_type == 'delivery':
            delivery_address = self.address_edit.text().strip()
            if not delivery_address:
                QMessageBox.warning(self, "Lỗi", "Vui lòng nhập địa chỉ giao hàng")
                return

        # Get table number
        table_number = None
        if order_type == 'dine_in':
            table_number = self.table_edit.text().strip()
            if not table_number:
                QMessageBox.warning(self, "Lỗi", "Vui lòng nhập số bàn")
                return

        # Get payment method
        payment_method = self.payment_combo.currentData()

        # Get notes
        notes = self.notes_edit.toPlainText().strip() or None

        # Disable button
        self.place_order_btn.setEnabled(False)
        self.place_order_btn.setText("Đang xử lý...")

        # Create order
        success, message, order_id = self.order_controller.create_order(
            user_id=user_id,
            order_type=order_type,
            payment_method=payment_method,
            store_id=store_id,
            delivery_address=delivery_address,
            table_number=table_number,
            notes=notes
        )

        # Re-enable button
        self.place_order_btn.setEnabled(True)
        self.place_order_btn.setText("Đặt hàng")

        if success:
            QMessageBox.information(self, "Thành công", message)
            self.order_placed.emit(order_id)
            self.accept()
        else:
            QMessageBox.warning(self, "Lỗi", message)
