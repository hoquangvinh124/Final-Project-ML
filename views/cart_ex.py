"""
Cart Widget - Extended Logic
Full shopping cart implementation
"""
from PyQt6.QtWidgets import (QWidget, QFrame, QHBoxLayout, QVBoxLayout, QLabel,
                             QPushButton, QSpinBox, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QByteArray
from PyQt6.QtGui import QPixmap
from ui_generated.cart import Ui_CartWidget
from controllers.cart_controller import CartController
from controllers.auth_controller import AuthController
from utils.validators import format_currency
import base64


class CartItemWidget(QFrame):
    """Single cart item widget"""

    quantity_changed = pyqtSignal(int, int)  # cart_id, new_quantity
    item_removed = pyqtSignal(int)  # cart_id

    def __init__(self, item_data, parent=None):
        super().__init__(parent)
        self.item_data = item_data
        self.setup_ui()

    def setup_ui(self):
        """Setup cart item UI"""
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setMaximumHeight(150)

        main_layout = QHBoxLayout(self)

        # Product image
        image_label = QLabel()
        image_label.setFixedSize(100, 100)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setStyleSheet("""
            background-color: #f0f0f0;
            border-radius: 8px;
            font-size: 40px;
        """)

        # Load image from base64 if available
        product_image = self.item_data.get('product_image', '')
        if product_image and product_image.startswith('data:image'):
            try:
                # Extract base64 data
                base64_data = product_image.split(',')[1]
                image_bytes = base64.b64decode(base64_data)

                # Create pixmap from bytes
                pixmap = QPixmap()
                pixmap.loadFromData(QByteArray(image_bytes))

                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        100, 100,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    image_label.setPixmap(scaled_pixmap)
                else:
                    # Fallback to emoji
                    image_label.setText(product_image if len(product_image) < 5 else "☕")
            except Exception as e:
                print(f"Error loading cart item image: {e}")
                image_label.setText(product_image if len(product_image) < 5 else "☕")
        else:
            # Use emoji as fallback
            image_label.setText(product_image if product_image and len(product_image) < 5 else "☕")

        main_layout.addWidget(image_label)

        # Product info
        info_layout = QVBoxLayout()

        # Product name
        name_label = QLabel(self.item_data['product_name'])
        name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        info_layout.addWidget(name_label)

        # Customization details
        details = []
        details.append(f"Size: {self.item_data['size']}")
        details.append(f"Đường: {self.item_data['sugar_level']}%")
        details.append(f"Đá: {self.item_data['ice_level']}%")
        details.append(f"Nhiệt độ: {'Nóng' if self.item_data['temperature'] == 'hot' else 'Lạnh'}")

        if self.item_data.get('topping_details'):
            topping_names = [t['name'] for t in self.item_data['topping_details']]
            details.append(f"Topping: {', '.join(topping_names)}")

        details_label = QLabel(" | ".join(details))
        details_label.setStyleSheet("color: #666; font-size: 12px;")
        details_label.setWordWrap(True)
        info_layout.addWidget(details_label)

        # Price
        price_label = QLabel(f"Đơn giá: {format_currency(self.item_data['unit_price'])}")
        price_label.setStyleSheet("color: #d4691e; font-weight: bold;")
        info_layout.addWidget(price_label)

        info_layout.addStretch()
        main_layout.addLayout(info_layout, stretch=1)

        # Quantity control
        quantity_layout = QVBoxLayout()
        quantity_layout.addStretch()

        qty_label = QLabel("Số lượng:")
        quantity_layout.addWidget(qty_label)

        qty_control = QHBoxLayout()

        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(0)
        self.quantity_spin.setMaximum(100)
        self.quantity_spin.setValue(self.item_data['quantity'])
        self.quantity_spin.setFixedWidth(80)
        self.quantity_spin.valueChanged.connect(self.on_quantity_changed)
        qty_control.addWidget(self.quantity_spin)

        quantity_layout.addLayout(qty_control)
        quantity_layout.addStretch()
        main_layout.addLayout(quantity_layout)

        # Subtotal and remove
        action_layout = QVBoxLayout()
        action_layout.setSpacing(20)

        subtotal_label = QLabel(format_currency(self.item_data['subtotal']))
        subtotal_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #c7a17a;")
        subtotal_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        action_layout.addWidget(subtotal_label)

        # Add more space before button
        action_layout.addSpacing(15)
        action_layout.addStretch()

        remove_btn = QPushButton("🗑️ Xóa")
        remove_btn.setMaximumWidth(100)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #A31E25;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8B181F;
            }
        """)
        remove_btn.clicked.connect(self.on_remove_clicked)
        action_layout.addWidget(remove_btn, 0, Qt.AlignmentFlag.AlignBottom)

        main_layout.addLayout(action_layout)

    def on_quantity_changed(self, value):
        """Handle quantity change"""
        self.quantity_changed.emit(self.item_data['id'], value)

    def on_remove_clicked(self):
        """Handle remove button click"""
        self.item_removed.emit(self.item_data['id'])


class CartWidget(QWidget, Ui_CartWidget):
    """Shopping cart widget with full functionality"""

    cart_updated = pyqtSignal()
    checkout_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.cart_controller = CartController()
        self.auth_controller = AuthController()
        self.current_voucher = None

        # Connect signals
        self.clearCartButton.clicked.connect(self.handle_clear_cart)
        self.applyVoucherButton.clicked.connect(self.handle_apply_voucher)
        self.checkoutButton.clicked.connect(self.handle_checkout)

        # Load cart
        self.load_cart()

    def load_cart(self):
        """Load and display cart items"""
        user_id = self.auth_controller.get_current_user_id()
        if not user_id:
            return

        # Clear existing items
        while self.cartItemsLayout.count():
            item = self.cartItemsLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Get cart items
        items = self.cart_controller.get_cart_items(user_id)

        if not items:
            # Show empty cart message
            empty_label = QLabel("🛒\n\nGiỏ hàng trống\n\nHãy thêm sản phẩm vào giỏ hàng!")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("font-size: 16px; color: #999; padding: 50px;")
            self.cartItemsLayout.addWidget(empty_label)

            # Disable checkout
            self.checkoutButton.setEnabled(False)
            # Update summary to show zero
            self.subtotalLabel.setText("Tạm tính: 0đ")
            self.discountLabel.setText("Giảm giá: 0đ")
            self.discountLabel.setVisible(False)
            self.deliveryFeeLabel.setText("Phí giao hàng: 0đ")
            self.totalLabel.setText("Tổng: 0đ")
            return

        # Enable checkout
        self.checkoutButton.setEnabled(True)

        # Add cart items
        for item in items:
            item_widget = CartItemWidget(item)
            item_widget.quantity_changed.connect(self.handle_quantity_changed)
            item_widget.item_removed.connect(self.handle_item_removed)
            self.cartItemsLayout.addWidget(item_widget)

        # Add stretch at the end
        self.cartItemsLayout.addStretch()

        # Update summary
        self.update_summary()

    def update_summary(self):
        """Update order summary"""
        user_id = self.auth_controller.get_current_user_id()
        if not user_id:
            return

        # Get voucher code if any
        voucher_code = self.voucherLineEdit.text().strip() if self.current_voucher else None

        # Get cart summary
        summary = self.cart_controller.get_cart_summary(user_id, voucher_code, 'pickup')

        subtotal = summary['subtotal']
        discount = summary['discount_amount']
        delivery_fee = summary['delivery_fee']
        total = summary['total']

        # Update labels
        self.subtotalLabel.setText(f"Tạm tính: {format_currency(subtotal)}")
        self.discountLabel.setText(f"Giảm giá: -{format_currency(discount)}")
        self.deliveryFeeLabel.setText(f"Phí giao hàng: {format_currency(delivery_fee)}")
        self.totalLabel.setText(f"Tổng: {format_currency(total)}")

        # Show/hide discount label
        self.discountLabel.setVisible(discount > 0)

    def handle_quantity_changed(self, cart_id, quantity):
        """Handle quantity change"""
        user_id = self.auth_controller.get_current_user_id()
        if not user_id:
            return

        success, message = self.cart_controller.update_quantity(cart_id, user_id, quantity)

        if success:
            self.load_cart()
            self.cart_updated.emit()
        else:
            QMessageBox.warning(self, "Lỗi", message)

    def handle_item_removed(self, cart_id):
        """Handle item removal"""
        reply = QMessageBox.question(
            self,
            "Xác nhận",
            "Bạn có chắc muốn xóa sản phẩm này khỏi giỏ hàng?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            user_id = self.auth_controller.get_current_user_id()
            if not user_id:
                return

            success, message = self.cart_controller.remove_item(cart_id, user_id)

            if success:
                self.load_cart()
                self.cart_updated.emit()
            else:
                QMessageBox.warning(self, "Lỗi", message)

    def handle_clear_cart(self):
        """Handle clear cart button"""
        user_id = self.auth_controller.get_current_user_id()
        if not user_id:
            return

        # Check if cart is empty
        count = self.cart_controller.get_cart_count(user_id)
        if count == 0:
            QMessageBox.information(self, "Thông báo", "Giỏ hàng đã trống")
            return

        reply = QMessageBox.question(
            self,
            "Xác nhận",
            "Bạn có chắc muốn xóa tất cả sản phẩm khỏi giỏ hàng?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            success, message = self.cart_controller.clear_cart(user_id)

            if success:
                self.load_cart()
                self.cart_updated.emit()
                QMessageBox.information(self, "Thành công", message)
            else:
                QMessageBox.warning(self, "Lỗi", message)

    def handle_apply_voucher(self):
        """Handle apply voucher button"""
        user_id = self.auth_controller.get_current_user_id()
        if not user_id:
            return

        voucher_code = self.voucherLineEdit.text().strip().upper()
        if not voucher_code:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập mã giảm giá")
            return

        # Get current subtotal
        summary = self.cart_controller.get_cart_summary(user_id)
        subtotal = summary['subtotal']

        # Validate voucher
        is_valid, message, voucher_data = self.cart_controller.validate_voucher(
            user_id, voucher_code, subtotal
        )

        if is_valid:
            self.current_voucher = voucher_data
            self.voucherLineEdit.setStyleSheet("border-color: #4CAF50;")
            self.update_summary()
            QMessageBox.information(self, "Thành công", message)
        else:
            self.current_voucher = None
            self.voucherLineEdit.setStyleSheet("border-color: #f44336;")
            QMessageBox.warning(self, "Lỗi", message)

    def handle_checkout(self):
        """Handle checkout button"""
        user_id = self.auth_controller.get_current_user_id()
        if not user_id:
            return

        # Check if cart is empty
        count = self.cart_controller.get_cart_count(user_id)
        if count == 0:
            QMessageBox.warning(self, "Lỗi", "Giỏ hàng trống")
            return

        # Emit checkout signal
        self.checkout_requested.emit()

    def refresh(self):
        """Refresh cart display"""
        self.load_cart()
