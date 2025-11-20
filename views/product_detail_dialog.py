"""
Product Detail Dialog
Detailed product view with full customization options
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QRadioButton, QCheckBox, QSlider,
                             QButtonGroup, QFrame, QScrollArea, QWidget,
                             QSpinBox, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QByteArray
from PyQt6.QtGui import QPixmap
from controllers.menu_controller import MenuController
from controllers.cart_controller import CartController
from controllers.auth_controller import AuthController
from utils.validators import format_currency
import base64


class ProductDetailDialog(QDialog):
    """Product detail dialog with customization"""

    product_added = pyqtSignal()

    def __init__(self, product_id, parent=None):
        super().__init__(parent)
        self.product_id = product_id
        self.setWindowTitle("Chi tiết sản phẩm")
        self.resize(700, 800)

        self.menu_controller = MenuController()
        self.cart_controller = CartController()
        self.auth_controller = AuthController()

        self.product = None
        self.selected_toppings = []

        self.setup_ui()
        self.load_product()

    def setup_ui(self):
        """Setup UI"""
        main_layout = QVBoxLayout(self)

        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        scroll_content = QWidget()
        layout = QVBoxLayout(scroll_content)

        # Product image
        self.image_label = QLabel()
        self.image_label.setFixedHeight(300)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("""
            background-color: #f5f5f5;
            border-radius: 12px;
            font-size: 100px;
        """)
        layout.addWidget(self.image_label)

        # Product name
        self.name_label = QLabel()
        self.name_label.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px 0;")
        self.name_label.setWordWrap(True)
        layout.addWidget(self.name_label)

        # Price
        self.price_label = QLabel()
        self.price_label.setStyleSheet("font-size: 18px; color: #d4691e; font-weight: bold;")
        layout.addWidget(self.price_label)

        # Rating
        self.rating_label = QLabel()
        self.rating_label.setStyleSheet("color: #666; padding: 5px 0;")
        layout.addWidget(self.rating_label)

        # Description
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("padding: 10px 0; line-height: 1.5; color: #333;")
        layout.addWidget(self.description_label)

        # Ingredients
        ingredients_frame = QFrame()
        ingredients_frame.setFrameShape(QFrame.Shape.StyledPanel)
        ingredients_layout = QVBoxLayout(ingredients_frame)

        ingredients_title = QLabel("📝 Thành phần:")
        ingredients_title.setStyleSheet("font-weight: bold; color: #333;")
        ingredients_layout.addWidget(ingredients_title)

        self.ingredients_label = QLabel()
        self.ingredients_label.setWordWrap(True)
        self.ingredients_label.setStyleSheet("color: #555;")
        ingredients_layout.addWidget(self.ingredients_label)

        layout.addWidget(ingredients_frame)

        # Calories
        self.calories_label = QLabel()
        self.calories_label.setStyleSheet("padding: 10px 0; color: #666;")
        layout.addWidget(self.calories_label)

        # Size selection
        size_frame = QFrame()
        size_frame.setFrameShape(QFrame.Shape.StyledPanel)
        size_layout = QVBoxLayout(size_frame)

        size_label = QLabel("📏 Kích thước:")
        size_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #333;")
        size_layout.addWidget(size_label)

        self.size_group = QButtonGroup()
        size_buttons_layout = QHBoxLayout()

        self.size_s = QRadioButton("S (Nhỏ)")
        self.size_group.addButton(self.size_s, 1)
        size_buttons_layout.addWidget(self.size_s)

        self.size_m = QRadioButton("M (Vừa)")
        self.size_m.setChecked(True)
        self.size_group.addButton(self.size_m, 2)
        size_buttons_layout.addWidget(self.size_m)

        self.size_l = QRadioButton("L (Lớn)")
        self.size_group.addButton(self.size_l, 3)
        size_buttons_layout.addWidget(self.size_l)

        size_layout.addLayout(size_buttons_layout)
        layout.addWidget(size_frame)

        # Connect size change to price update
        for button in [self.size_s, self.size_m, self.size_l]:
            button.toggled.connect(self.update_price)

        # Temperature
        temp_frame = QFrame()
        temp_frame.setFrameShape(QFrame.Shape.StyledPanel)
        temp_layout = QVBoxLayout(temp_frame)

        temp_label = QLabel("🌡️ Nhiệt độ:")
        temp_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #333;")
        temp_layout.addWidget(temp_label)

        self.temp_group = QButtonGroup()
        temp_buttons_layout = QHBoxLayout()

        self.temp_hot = QRadioButton("🔥 Nóng")
        self.temp_group.addButton(self.temp_hot, 1)
        temp_buttons_layout.addWidget(self.temp_hot)

        self.temp_cold = QRadioButton("❄️ Lạnh")
        self.temp_cold.setChecked(True)
        self.temp_group.addButton(self.temp_cold, 2)
        temp_buttons_layout.addWidget(self.temp_cold)

        temp_layout.addLayout(temp_buttons_layout)
        layout.addWidget(temp_frame)

        # Sugar level
        sugar_frame = QFrame()
        sugar_frame.setFrameShape(QFrame.Shape.StyledPanel)
        sugar_layout = QVBoxLayout(sugar_frame)

        sugar_label = QLabel("🍬 Độ ngọt:")
        sugar_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #333;")
        sugar_layout.addWidget(sugar_label)

        sugar_control_layout = QHBoxLayout()

        self.sugar_slider = QSlider(Qt.Orientation.Horizontal)
        self.sugar_slider.setMinimum(0)
        self.sugar_slider.setMaximum(100)
        self.sugar_slider.setValue(50)
        self.sugar_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.sugar_slider.setTickInterval(25)
        self.sugar_slider.valueChanged.connect(self.update_sugar_label)
        sugar_control_layout.addWidget(self.sugar_slider)

        self.sugar_value_label = QLabel("50%")
        self.sugar_value_label.setMinimumWidth(50)
        self.sugar_value_label.setStyleSheet("font-weight: bold; color: #333;")
        sugar_control_layout.addWidget(self.sugar_value_label)

        sugar_layout.addLayout(sugar_control_layout)
        layout.addWidget(sugar_frame)

        # Ice level
        ice_frame = QFrame()
        ice_frame.setFrameShape(QFrame.Shape.StyledPanel)
        ice_layout = QVBoxLayout(ice_frame)

        ice_label = QLabel("🧊 Lượng đá:")
        ice_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #333;")
        ice_layout.addWidget(ice_label)

        ice_control_layout = QHBoxLayout()

        self.ice_slider = QSlider(Qt.Orientation.Horizontal)
        self.ice_slider.setMinimum(0)
        self.ice_slider.setMaximum(100)
        self.ice_slider.setValue(50)
        self.ice_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.ice_slider.setTickInterval(25)
        self.ice_slider.valueChanged.connect(self.update_ice_label)
        ice_control_layout.addWidget(self.ice_slider)

        self.ice_value_label = QLabel("50%")
        self.ice_value_label.setMinimumWidth(50)
        self.ice_value_label.setStyleSheet("font-weight: bold; color: #333;")
        ice_control_layout.addWidget(self.ice_value_label)

        ice_layout.addLayout(ice_control_layout)
        layout.addWidget(ice_frame)

        # Toppings
        toppings_frame = QFrame()
        toppings_frame.setFrameShape(QFrame.Shape.StyledPanel)
        toppings_layout = QVBoxLayout(toppings_frame)

        toppings_label = QLabel("🧋 Topping:")
        toppings_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #333;")
        toppings_layout.addWidget(toppings_label)

        self.toppings_checkboxes_layout = QVBoxLayout()
        toppings_layout.addLayout(self.toppings_checkboxes_layout)

        layout.addWidget(toppings_frame)

        # Quantity
        quantity_frame = QFrame()
        quantity_frame.setFrameShape(QFrame.Shape.StyledPanel)
        quantity_layout = QHBoxLayout(quantity_frame)

        quantity_label = QLabel("Số lượng:")
        quantity_label.setStyleSheet("font-weight: bold; color: #333;")
        quantity_layout.addWidget(quantity_label)

        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(100)
        self.quantity_spin.setValue(1)
        self.quantity_spin.setMinimumWidth(100)
        self.quantity_spin.setMinimumHeight(35)
        self.quantity_spin.valueChanged.connect(self.update_total_price)
        quantity_layout.addWidget(self.quantity_spin)

        quantity_layout.addStretch()

        layout.addWidget(quantity_frame)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)

        # Bottom bar with total and add button
        bottom_bar = QFrame()
        bottom_bar.setFrameShape(QFrame.Shape.StyledPanel)
        bottom_bar.setStyleSheet("background-color: #ffffff; padding: 10px;")
        bottom_layout = QHBoxLayout(bottom_bar)

        self.total_price_label = QLabel("Tổng: 0đ")
        self.total_price_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #c7a17a;")
        bottom_layout.addWidget(self.total_price_label)

        bottom_layout.addStretch()

        self.add_to_cart_btn = QPushButton("Thêm vào giỏ hàng")
        self.add_to_cart_btn.setMinimumHeight(45)
        self.add_to_cart_btn.setMinimumWidth(200)
        self.add_to_cart_btn.setStyleSheet("""
            QPushButton {
                background-color: #A31E25;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #8B181F;
            }
            QPushButton:pressed {
                background-color: #6d1218;
            }
        """)
        self.add_to_cart_btn.clicked.connect(self.handle_add_to_cart)
        bottom_layout.addWidget(self.add_to_cart_btn)

        main_layout.addWidget(bottom_bar)

    def load_product(self):
        """Load product details"""
        self.product = self.menu_controller.get_product_detail(self.product_id)

        if not self.product:
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy sản phẩm")
            self.reject()
            return

        # Set product info
        # Load product image from base64 if available
        product_image = self.product.get('image', '')
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
                        600, 300,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.image_label.setPixmap(scaled_pixmap)
                else:
                    # Fallback to emoji
                    self.image_label.setText(product_image if len(product_image) < 5 else "☕")
            except Exception as e:
                print(f"Error loading product image: {e}")
                self.image_label.setText(product_image if len(product_image) < 5 else "☕")
        else:
            # Use emoji as fallback
            self.image_label.setText(product_image if product_image and len(product_image) < 5 else "☕")

        self.name_label.setText(self.product['name'])
        self.description_label.setText(self.product.get('description', 'Chưa có mô tả'))
        self.ingredients_label.setText(self.product.get('ingredients', 'Chưa có thông tin'))

        # Rating
        rating = self.product.get('rating', 0)
        total_reviews = self.product.get('total_reviews', 0)
        self.rating_label.setText(f"⭐ {rating:.1f} ({total_reviews} đánh giá)")

        # Load toppings
        toppings = self.product.get('available_toppings', [])
        for topping in toppings:
            cb = QCheckBox(f"{topping['name']} (+{format_currency(topping['price'])})")
            cb.setProperty('topping_id', topping['id'])
            cb.setProperty('topping_price', topping['price'])
            cb.stateChanged.connect(self.update_price)
            self.toppings_checkboxes_layout.addWidget(cb)

        # Set temperature options based on product
        if not self.product.get('is_hot'):
            self.temp_hot.setEnabled(False)
        if not self.product.get('is_cold'):
            self.temp_cold.setEnabled(False)

        # Update price
        self.update_price()
        self.update_calories()

    def get_selected_size(self):
        """Get selected size"""
        if self.size_s.isChecked():
            return 'S'
        elif self.size_l.isChecked():
            return 'L'
        else:
            return 'M'

    def get_selected_toppings(self):
        """Get selected topping IDs"""
        topping_ids = []
        for i in range(self.toppings_checkboxes_layout.count()):
            widget = self.toppings_checkboxes_layout.itemAt(i).widget()
            if isinstance(widget, QCheckBox) and widget.isChecked():
                topping_ids.append(widget.property('topping_id'))
        return topping_ids

    def update_price(self):
        """Update price based on selections"""
        size = self.get_selected_size()
        topping_ids = self.get_selected_toppings()

        price_info = self.menu_controller.calculate_product_price(
            self.product_id, size, topping_ids
        )

        unit_price = price_info['total']
        self.price_label.setText(f"Giá: {format_currency(unit_price)}")

        self.update_total_price()
        self.update_calories()

    def update_total_price(self):
        """Update total price with quantity"""
        size = self.get_selected_size()
        topping_ids = self.get_selected_toppings()

        price_info = self.menu_controller.calculate_product_price(
            self.product_id, size, topping_ids
        )

        unit_price = price_info['total']
        quantity = self.quantity_spin.value()
        total = unit_price * quantity

        self.total_price_label.setText(f"Tổng: {format_currency(total)}")

    def update_calories(self):
        """Update calories display"""
        size = self.get_selected_size()
        calories = self.menu_controller.get_product_detail(self.product_id)

        if calories:
            cal_value = 0
            if size == 'S':
                cal_value = self.product.get('calories_small', 0)
            elif size == 'M':
                cal_value = self.product.get('calories_medium', 0)
            else:
                cal_value = self.product.get('calories_large', 0)

            self.calories_label.setText(f"🔥 Calories: {cal_value} kcal")

    def update_sugar_label(self, value):
        """Update sugar level label"""
        self.sugar_value_label.setText(f"{value}%")

    def update_ice_label(self, value):
        """Update ice level label"""
        self.ice_value_label.setText(f"{value}%")

    def handle_add_to_cart(self):
        """Handle add to cart button"""
        user_id = self.auth_controller.get_current_user_id()
        if not user_id:
            QMessageBox.warning(self, "Lỗi", "Vui lòng đăng nhập")
            return

        # Get all selections
        size = self.get_selected_size()
        quantity = self.quantity_spin.value()
        sugar_level = self.sugar_slider.value()
        ice_level = self.ice_slider.value()
        temperature = 'hot' if self.temp_hot.isChecked() else 'cold'
        topping_ids = self.get_selected_toppings()

        # Add to cart
        success, message = self.cart_controller.add_to_cart(
            user_id=user_id,
            product_id=self.product_id,
            size=size,
            quantity=quantity,
            sugar_level=sugar_level,
            ice_level=ice_level,
            temperature=temperature,
            topping_ids=topping_ids if topping_ids else None
        )

        if success:
            QMessageBox.information(self, "Thành công", message)
            self.product_added.emit()
            self.accept()
        else:
            QMessageBox.warning(self, "Lỗi", message)
