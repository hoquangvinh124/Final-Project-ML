"""
Admin Products Management - Complete Implementation
Product CRUD operations
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
                             QMessageBox, QDialog, QTextEdit, QDoubleSpinBox,
                             QCheckBox, QDialogButtonBox, QSpinBox, QFormLayout,
                             QFileDialog, QHeaderView)
from PyQt6.QtCore import Qt, QByteArray, QTimer
from PyQt6.QtGui import QColor, QPixmap
from controllers.admin_product_controller import AdminProductController
from controllers.admin_category_controller import AdminCategoryController
from controllers.admin_controller import AdminController
from utils.validators import format_currency
import base64


class ProductDialog(QDialog):
    """Dialog for creating/editing product"""

    def __init__(self, product=None, parent=None):
        super().__init__(parent)
        self.product = product
        self.is_edit = product is not None
        self.image_base64 = None  # Store base64 image data

        self.setWindowTitle("Sửa sản phẩm" if self.is_edit else "Thêm sản phẩm mới")
        self.resize(600, 750)

        self.category_controller = AdminCategoryController()
        self.setup_ui()

        if self.is_edit:
            self.load_product_data()

    def setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout(self)

        # Form
        form_layout = QFormLayout()

        # Name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Tên sản phẩm...")
        form_layout.addRow("Tên sản phẩm:", self.name_edit)

        # Category
        self.category_combo = QComboBox()
        categories = self.category_controller.get_all_categories()
        for cat in categories:
            self.category_combo.addItem(cat['name'], cat['id'])
        form_layout.addRow("Danh mục:", self.category_combo)

        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Mô tả sản phẩm...")
        self.description_edit.setMaximumHeight(100)
        self.description_edit.setStyleSheet("""
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
        form_layout.addRow("Mô tả:", self.description_edit)

        # Image upload
        image_layout = QVBoxLayout()

        # Image preview
        self.image_preview = QLabel()
        self.image_preview.setFixedSize(150, 150)
        self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_preview.setStyleSheet("""
            QLabel {
                border: 2px dashed #ccc;
                border-radius: 8px;
                background-color: #f5f5f5;
                font-size: 48px;
            }
        """)
        self.image_preview.setText("📷")

        # Button layout
        button_layout = QHBoxLayout()

        self.select_image_btn = QPushButton("📁 Chọn ảnh")
        self.select_image_btn.setMinimumHeight(35)
        self.select_image_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.select_image_btn.clicked.connect(self.select_image)
        button_layout.addWidget(self.select_image_btn)

        self.clear_image_btn = QPushButton("🗑️ Xóa ảnh")
        self.clear_image_btn.setMinimumHeight(35)
        self.clear_image_btn.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #D32F2F;
            }
        """)
        self.clear_image_btn.clicked.connect(self.clear_image)
        button_layout.addWidget(self.clear_image_btn)

        image_layout.addWidget(self.image_preview)
        image_layout.addLayout(button_layout)

        form_layout.addRow("Ảnh sản phẩm:", image_layout)

        # Base Price
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0, 1000000)
        self.price_spin.setSuffix(" đ")
        self.price_spin.setDecimals(0)
        form_layout.addRow("Giá cơ bản:", self.price_spin)

        # Ingredients
        self.ingredients_edit = QLineEdit()
        self.ingredients_edit.setPlaceholderText("Cà phê, sữa, đường...")
        form_layout.addRow("Thành phần:", self.ingredients_edit)

        # Calories
        calories_layout = QHBoxLayout()

        self.calories_s_spin = QSpinBox()
        self.calories_s_spin.setRange(0, 1000)
        self.calories_s_spin.setSuffix(" kcal")
        calories_layout.addWidget(QLabel("S:"))
        calories_layout.addWidget(self.calories_s_spin)

        self.calories_m_spin = QSpinBox()
        self.calories_m_spin.setRange(0, 1000)
        self.calories_m_spin.setSuffix(" kcal")
        calories_layout.addWidget(QLabel("M:"))
        calories_layout.addWidget(self.calories_m_spin)

        self.calories_l_spin = QSpinBox()
        self.calories_l_spin.setRange(0, 1000)
        self.calories_l_spin.setSuffix(" kcal")
        calories_layout.addWidget(QLabel("L:"))
        calories_layout.addWidget(self.calories_l_spin)

        form_layout.addRow("Calories:", calories_layout)

        # Checkboxes
        self.hot_check = QCheckBox("Có phiên bản nóng")
        self.hot_check.setChecked(True)
        form_layout.addRow("Nhiệt độ:", self.hot_check)

        self.cold_check = QCheckBox("Có phiên bản lạnh")
        self.cold_check.setChecked(True)
        form_layout.addRow("", self.cold_check)

        self.new_check = QCheckBox("Sản phẩm mới")
        form_layout.addRow("Đánh dấu:", self.new_check)

        self.bestseller_check = QCheckBox("Bán chạy")
        form_layout.addRow("", self.bestseller_check)

        self.seasonal_check = QCheckBox("Theo mùa")
        form_layout.addRow("", self.seasonal_check)

        self.available_check = QCheckBox("Đang bán")
        self.available_check.setChecked(True)
        form_layout.addRow("Trạng thái:", self.available_check)

        layout.addLayout(form_layout)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def select_image(self):
        """Select and convert image to base64"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Chọn ảnh sản phẩm",
            "",
            "Images (*.png *.jpg *.jpeg *.gif *.bmp *.webp)"
        )

        if file_path:
            try:
                # Read image file
                with open(file_path, 'rb') as image_file:
                    image_data = image_file.read()

                # Convert to base64
                self.image_base64 = base64.b64encode(image_data).decode('utf-8')

                # Determine image format
                if file_path.lower().endswith('.png'):
                    image_format = 'png'
                elif file_path.lower().endswith(('.jpg', '.jpeg')):
                    image_format = 'jpeg'
                elif file_path.lower().endswith('.gif'):
                    image_format = 'gif'
                elif file_path.lower().endswith('.webp'):
                    image_format = 'webp'
                else:
                    image_format = 'jpeg'

                # Create data URI
                self.image_base64 = f"data:image/{image_format};base64,{self.image_base64}"

                # Show preview
                pixmap = QPixmap(file_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        150, 150,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.image_preview.setPixmap(scaled_pixmap)
                    self.image_preview.setStyleSheet("""
                        QLabel {
                            border: 2px solid #4CAF50;
                            border-radius: 8px;
                            background-color: #f5f5f5;
                        }
                    """)

                QMessageBox.information(self, "Thành công", "Đã tải ảnh lên thành công!")

            except Exception as e:
                QMessageBox.warning(self, "Lỗi", f"Không thể đọc file ảnh: {str(e)}")

    def clear_image(self):
        """Clear image"""
        self.image_base64 = None
        self.image_preview.clear()
        self.image_preview.setText("📷")
        self.image_preview.setStyleSheet("""
            QLabel {
                border: 2px dashed #ccc;
                border-radius: 8px;
                background-color: #f5f5f5;
                font-size: 48px;
            }
        """)

    def load_product_data(self):
        """Load product data for editing"""
        self.name_edit.setText(self.product['name'])

        # Set category
        idx = self.category_combo.findData(self.product['category_id'])
        if idx >= 0:
            self.category_combo.setCurrentIndex(idx)

        self.description_edit.setPlainText(self.product.get('description', ''))

        # Load image if exists
        if self.product.get('image'):
            image_str = self.product['image']
            self.image_base64 = image_str

            # Check if it's base64 data URI
            if image_str.startswith('data:image'):
                try:
                    # Extract base64 data
                    base64_data = image_str.split(',')[1]
                    image_bytes = base64.b64decode(base64_data)

                    # Create pixmap from bytes
                    pixmap = QPixmap()
                    pixmap.loadFromData(QByteArray(image_bytes))

                    if not pixmap.isNull():
                        scaled_pixmap = pixmap.scaled(
                            150, 150,
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation
                        )
                        self.image_preview.setPixmap(scaled_pixmap)
                        self.image_preview.setStyleSheet("""
                            QLabel {
                                border: 2px solid #4CAF50;
                                border-radius: 8px;
                                background-color: #f5f5f5;
                            }
                        """)
                except Exception as e:
                    print(f"Error loading image: {e}")

        self.price_spin.setValue(float(self.product['base_price']))
        self.ingredients_edit.setText(self.product.get('ingredients', ''))

        self.calories_s_spin.setValue(self.product.get('calories_small') or 0)
        self.calories_m_spin.setValue(self.product.get('calories_medium') or 0)
        self.calories_l_spin.setValue(self.product.get('calories_large') or 0)

        self.hot_check.setChecked(self.product['is_hot'])
        self.cold_check.setChecked(self.product['is_cold'])
        self.new_check.setChecked(self.product.get('is_new', False))
        self.bestseller_check.setChecked(self.product.get('is_bestseller', False))
        self.seasonal_check.setChecked(self.product.get('is_seasonal', False))
        self.available_check.setChecked(self.product['is_available'])

    def get_data(self):
        """Get form data"""
        data = {
            'name': self.name_edit.text().strip(),
            'category_id': self.category_combo.currentData(),
            'description': self.description_edit.toPlainText().strip(),
            'base_price': self.price_spin.value(),
            'ingredients': self.ingredients_edit.text().strip(),
            'calories_small': self.calories_s_spin.value(),
            'calories_medium': self.calories_m_spin.value(),
            'calories_large': self.calories_l_spin.value(),
            'is_hot': self.hot_check.isChecked(),
            'is_cold': self.cold_check.isChecked(),
            'is_new': self.new_check.isChecked(),
            'is_bestseller': self.bestseller_check.isChecked(),
            'is_seasonal': self.seasonal_check.isChecked(),
            'is_available': self.available_check.isChecked()
        }

        # Add image if uploaded
        if self.image_base64:
            data['image'] = self.image_base64

        return data


class AdminProductsWidget(QWidget):
    """Admin products management widget"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.product_controller = AdminProductController()
        self.category_controller = AdminCategoryController()
        self.admin_controller = AdminController()

        self.setup_ui()
        self.load_products()

    def setup_ui(self):
        """Setup UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Header
        header_layout = QHBoxLayout()

        header_label = QLabel("☕ Quản lý sản phẩm")
        header_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        header_layout.addWidget(header_label)

        header_layout.addStretch()

        # Add button
        self.add_button = QPushButton("➕ Thêm sản phẩm")
        self.add_button.setMinimumHeight(35)
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.add_button.clicked.connect(self.handle_add_product)
        header_layout.addWidget(self.add_button)

        # Refresh button
        self.refresh_button = QPushButton("🔄 Làm mới")
        self.refresh_button.setMinimumHeight(35)
        self.refresh_button.clicked.connect(self.load_products)
        header_layout.addWidget(self.refresh_button)

        main_layout.addLayout(header_layout)

        # Filters
        filter_layout = QHBoxLayout()

        search_label = QLabel("Tìm kiếm:")
        search_label.setStyleSheet("color: #333;")
        filter_layout.addWidget(search_label)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Tên sản phẩm...")
        self.search_edit.setMinimumWidth(300)
        self.search_edit.setMinimumHeight(35)
        self.search_edit.textChanged.connect(self.handle_search)
        filter_layout.addWidget(self.search_edit)

        category_label = QLabel("Danh mục:")
        category_label.setStyleSheet("color: #333;")
        filter_layout.addWidget(category_label)

        self.category_combo = QComboBox()
        self.category_combo.addItem("Tất cả", None)
        categories = self.category_controller.get_all_categories()
        for cat in categories:
            self.category_combo.addItem(cat['name'], cat['id'])
        self.category_combo.setMinimumHeight(35)
        self.category_combo.currentIndexChanged.connect(self.load_products)
        filter_layout.addWidget(self.category_combo)

        filter_layout.addStretch()

        main_layout.addLayout(filter_layout)

        # Products table
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(8)
        self.products_table.setHorizontalHeaderLabels([
            "ID", "Tên sản phẩm", "Danh mục", "Giá", "Nhiệt độ", "Trạng thái", "Ngày tạo", "Thao tác"
        ])
        # self.products_table.horizontalHeader().setStretchLastSection(True)
        self.products_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.products_table.setAlternatingRowColors(True)
        self.products_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.products_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Fix row height issue
        self.products_table.verticalHeader().setDefaultSectionSize(50)
        self.products_table.verticalHeader().setMinimumSectionSize(50)
        
        main_layout.addWidget(self.products_table)

    def load_products(self):
        """Load and display products"""
        category_id = self.category_combo.currentData()
        search = self.search_edit.text().strip()

        products = self.product_controller.get_all_products(
            category_id=category_id if category_id else None,
            search=search if search else None
        )

        self.display_products(products)

    def display_products(self, products):
        """Display products in table"""
        self.products_table.setRowCount(len(products))

        for row, product in enumerate(products):
            # ID
            self.products_table.setItem(row, 0, QTableWidgetItem(str(product['id'])))

            # Name
            self.products_table.setItem(row, 1, QTableWidgetItem(product['name']))

            # Category
            self.products_table.setItem(row, 2, QTableWidgetItem(product.get('category_name', 'N/A')))

            # Price
            self.products_table.setItem(row, 3, QTableWidgetItem(format_currency(product['base_price'])))

            # Temperature
            temp = []
            if product['is_hot']:
                temp.append("🔥 Nóng")
            if product['is_cold']:
                temp.append("❄️ Lạnh")
            self.products_table.setItem(row, 4, QTableWidgetItem(" | ".join(temp)))

            # Status
            status = "✅ Đang bán" if product['is_available'] else "❌ Ngừng bán"
            status_item = QTableWidgetItem(status)
            status_item.setForeground(QColor('#4CAF50' if product['is_available'] else '#F44336'))
            self.products_table.setItem(row, 5, status_item)

            # Date
            from datetime import datetime
            created_at = product['created_at']
            if isinstance(created_at, datetime):
                date_str = created_at.strftime("%d/%m/%Y")
            else:
                date_str = str(created_at)
            self.products_table.setItem(row, 6, QTableWidgetItem(date_str))

            # Action buttons
            action_widget = QWidget()
            action_widget.setMinimumWidth(200)
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 2, 5, 2)
            action_layout.setSpacing(5)

            # Edit button
            edit_btn = QPushButton("Sửa")
            edit_btn.setToolTip("Sửa sản phẩm")
            edit_btn.setStyleSheet("background-color: #2196F3; color: white; border: none; padding: 6px 12px; border-radius: 3px; font-size: 12px;")
            edit_btn.clicked.connect(lambda checked, p=product: self.handle_edit_product(p))
            action_layout.addWidget(edit_btn)

            # Toggle button
            toggle_btn = QPushButton("Ẩn" if product['is_available'] else "Hiện")
            toggle_btn.setToolTip("Ẩn/Hiện sản phẩm")
            toggle_btn.setStyleSheet("background-color: #FF9800; color: white; border: none; padding: 6px 12px; border-radius: 3px; font-size: 12px;")
            toggle_btn.clicked.connect(lambda checked, p=product: self.handle_toggle_product(p))
            action_layout.addWidget(toggle_btn)

            # Delete button (hard delete)
            delete_btn = QPushButton("Xóa")
            delete_btn.setToolTip("Xóa vĩnh viễn sản phẩm khỏi hệ thống")
            delete_btn.setStyleSheet("background-color: #F44336; color: white; border: none; padding: 6px 12px; border-radius: 3px; font-size: 12px;")
            delete_btn.clicked.connect(lambda checked, p=product: self.handle_delete_product(p))
            action_layout.addWidget(delete_btn)

            self.products_table.setCellWidget(row, 7, action_widget)

            # Set row height to accommodate buttons
            self.products_table.setRowHeight(row, 50)

        QTimer.singleShot(100, self.adjust_columns)

    def adjust_columns(self):
        header = self.products_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)
        
        for i in [0, 2, 3, 4, 5, 6]:
            self.products_table.resizeColumnToContents(i)
            
        self.products_table.setColumnWidth(7, 220)

    def handle_search(self, query):
        """Handle search"""
        self.load_products()

    def handle_add_product(self):
        """Handle add product"""
        dialog = ProductDialog(parent=self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()

            admin_id = self.admin_controller.get_current_admin_id()
            if not admin_id:
                QMessageBox.warning(self, "Lỗi", "Vui lòng đăng nhập")
                return

            success, message = self.product_controller.create_product(data, admin_id)

            if success:
                QMessageBox.information(self, "Thành công", message)
                self.load_products()
            else:
                QMessageBox.warning(self, "Lỗi", message)

    def handle_edit_product(self, product):
        """Handle edit product"""
        dialog = ProductDialog(product, self)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()

            admin_id = self.admin_controller.get_current_admin_id()
            if not admin_id:
                QMessageBox.warning(self, "Lỗi", "Vui lòng đăng nhập")
                return

            success, message = self.product_controller.update_product(product['id'], data, admin_id)

            if success:
                QMessageBox.information(self, "Thành công", message)
                self.load_products()
            else:
                QMessageBox.warning(self, "Lỗi", message)

    def handle_toggle_product(self, product):
        """Handle toggle product availability"""
        admin_id = self.admin_controller.get_current_admin_id()
        if not admin_id:
            QMessageBox.warning(self, "Lỗi", "Vui lòng đăng nhập")
            return

        success, message = self.product_controller.toggle_availability(product['id'], admin_id)

        if success:
            self.load_products()
        else:
            QMessageBox.warning(self, "Lỗi", message)

    def handle_delete_product(self, product):
        """Handle delete product"""
        reply = QMessageBox.question(
            self,
            "Xác nhận xóa",
            f"Bạn có chắc chắn muốn XÓA VĨNH VIỄN sản phẩm '{product['name']}'?\n\n"
            f"CẢNH BÁO: Hành động này KHÔNG THỂ HOÀN TÁC!\n"
            f"Sản phẩm sẽ bị xóa hoàn toàn khỏi hệ thống.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            admin_id = self.admin_controller.get_current_admin_id()
            if not admin_id:
                QMessageBox.warning(self, "Lỗi", "Vui lòng đăng nhập")
                return

            success, message = self.product_controller.delete_product(product['id'], admin_id)

            if success:
                QMessageBox.information(self, "Thành công", message)
                self.load_products()
            else:
                QMessageBox.warning(self, "Lỗi", message)

    def refresh(self):
        """Refresh products"""
        self.load_products()
