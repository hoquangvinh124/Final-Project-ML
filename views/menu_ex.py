"""
Menu Widget - Extended Logic
Display products with filtering and search
"""
from PyQt6.QtWidgets import (QWidget, QFrame, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QByteArray
from PyQt6.QtGui import QPixmap
from ui_generated.menu import Ui_MenuWidget
from controllers.menu_controller import MenuController
from controllers.cart_controller import CartController
from controllers.auth_controller import AuthController
from controllers.favorites_controller import FavoritesController
from utils.validators import format_currency
import base64


class ProductCard(QFrame):
    """Product card widget"""

    add_to_cart_clicked = pyqtSignal(dict)
    product_clicked = pyqtSignal(dict)
    favorite_toggled = pyqtSignal()

    def __init__(self, product_data, parent=None):
        super().__init__(parent)
        self.product_data = product_data
        self.favorites_controller = FavoritesController()
        self.auth_controller = AuthController()
        self.is_favorite = False
        self.setup_ui()
        self.check_favorite_status()

    def setup_ui(self):
        """Setup product card UI"""
        self.setFrameShape(QFrame.Shape.Box)
        self.setMaximumWidth(250)
        self.setMinimumHeight(320)

        layout = QVBoxLayout(self)

        # Image container with favorite button overlay
        image_container = QFrame()
        image_container.setFixedSize(220, 220)
        image_container_layout = QVBoxLayout(image_container)
        image_container_layout.setContentsMargins(0, 0, 0, 0)

        # Product image
        image_label = QLabel()
        image_label.setFixedSize(220, 220)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setStyleSheet("""
            background-color: #f0f0f0;
            border-radius: 8px;
            font-size: 80px;
        """)

        # Load image from base64 if available
        product_image = self.product_data.get('image', '')
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
                        220, 220,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    image_label.setPixmap(scaled_pixmap)
                else:
                    # Fallback to emoji if image load fails
                    image_label.setText(product_image if len(product_image) < 5 else "☕")
            except Exception as e:
                # Fallback to emoji on error
                print(f"Error loading product image: {e}")
                image_label.setText(product_image if len(product_image) < 5 else "☕")
        else:
            # Use emoji as fallback (for old products)
            image_label.setText(product_image if product_image and len(product_image) < 5 else "☕")

        image_container_layout.addWidget(image_label)

        # Favorite button overlay
        self.favorite_btn = QPushButton()
        self.favorite_btn.setFixedSize(35, 35)
        self.favorite_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.9);
                border: none;
                border-radius: 17px;
                font-size: 18px;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: white;
            }
        """)
        self.favorite_btn.clicked.connect(self.toggle_favorite)
        self.favorite_btn.setParent(image_container)
        self.favorite_btn.move(180, 5)  # Position in top-right corner

        layout.addWidget(image_container)

        # Product name
        name_label = QLabel(self.product_data['name'])
        name_label.setWordWrap(True)
        name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(name_label)

        # Price
        price = format_currency(self.product_data['base_price'])
        price_label = QLabel(price)
        price_label.setStyleSheet("color: #d4691e; font-size: 16px; font-weight: bold;")
        layout.addWidget(price_label)

        # Rating
        rating = self.product_data.get('rating', 0)
        total_reviews = self.product_data.get('total_reviews', 0)
        rating_label = QLabel(f"⭐ {rating:.1f} ({total_reviews} đánh giá)")
        rating_label.setStyleSheet("font-size: 12px; color: #666;")
        layout.addWidget(rating_label)

        # Add to cart button
        add_btn = QPushButton("Thêm vào giỏ")
        add_btn.clicked.connect(lambda: self.add_to_cart_clicked.emit(self.product_data))
        layout.addWidget(add_btn)

        # Make card clickable
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event):
        """Handle card click"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.product_clicked.emit(self.product_data)

    def check_favorite_status(self):
        """Check if product is in favorites"""
        user_id = self.auth_controller.get_current_user_id()
        if not user_id:
            self.is_favorite = False
        else:
            self.is_favorite = self.favorites_controller.is_favorite(user_id, self.product_data['id'])

        self.update_favorite_button()

    def update_favorite_button(self):
        """Update favorite button icon"""
        if self.is_favorite:
            self.favorite_btn.setText("❤️")
        else:
            self.favorite_btn.setText("🤍")

    def toggle_favorite(self):
        """Toggle favorite status"""
        user_id = self.auth_controller.get_current_user_id()
        if not user_id:
            QMessageBox.warning(self, "Lỗi", "Vui lòng đăng nhập")
            return

        success, message = self.favorites_controller.toggle_favorite(user_id, self.product_data['id'])

        if success:
            self.is_favorite = not self.is_favorite
            self.update_favorite_button()
            self.favorite_toggled.emit()
        else:
            QMessageBox.warning(self, "Lỗi", message)


class MenuWidget(QWidget, Ui_MenuWidget):
    """Menu widget with product display and filtering"""

    cart_updated = pyqtSignal()
    favorites_updated = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.menu_controller = MenuController()
        self.cart_controller = CartController()
        self.auth_controller = AuthController()

        # Pagination variables
        self.current_page = 1
        self.items_per_page = 15  # 5x3 grid
        self.total_pages = 1
        self.all_products = []  # Store all products for pagination

        # Connect signals
        self.searchLineEdit.textChanged.connect(self.handle_search)
        self.hotCheckBox.stateChanged.connect(self.apply_filters)
        self.coldCheckBox.stateChanged.connect(self.apply_filters)
        self.caffeineCheckBox.stateChanged.connect(self.apply_filters)
        self.prevButton.clicked.connect(self.prev_page)
        self.nextButton.clicked.connect(self.next_page)

        # Add Highlands Coffee banner
        self.add_banner()

        # Load categories and products
        self.load_categories()
        self.load_products()

    def add_banner(self):
        """Add a promotional banner to the top of the menu"""
        try:
            banner_path = "resources/images/banner.jpg"
            pixmap = QPixmap(banner_path)
            
            if not pixmap.isNull():
                banner_container = QLabel()
                banner_container.setPixmap(pixmap)
                banner_container.setScaledContents(True)
                banner_container.setMinimumHeight(200)
                banner_container.setMaximumHeight(250)
                
                # Insert at the top of content layout (index 0)
                self.contentLayout.insertWidget(0, banner_container)
            
        except Exception as e:
            pass

    def load_categories(self):
        """Load product categories as tabs"""
        categories = self.menu_controller.get_categories()

        # Clear existing tabs
        self.categoryTabWidget.clear()

        # Add "All" tab
        all_tab = QWidget()
        all_tab.setMaximumHeight(0)  # Hide tab content area
        self.categoryTabWidget.addTab(all_tab, "Tất cả")

        # Add category tabs
        for category in categories:
            tab = QWidget()
            tab.setMaximumHeight(0)  # Hide tab content area
            self.categoryTabWidget.addTab(tab, category['name'])

        # Connect tab change signal
        self.categoryTabWidget.currentChanged.connect(self.handle_category_change)

    def load_products(self, category_id=None):
        """Load and display products"""
        products = self.menu_controller.get_products_by_category(category_id)
        self.all_products = products
        self.current_page = 1
        self.update_pagination()
        self.display_current_page()

    def display_products(self, products):
        """Display products in grid layout (for internal use with pagination)"""
        # Clear existing products
        while self.productsGridLayout.count():
            item = self.productsGridLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add products to grid
        row = 0
        col = 0
        max_cols = 5

        for product in products:
            card = ProductCard(product)
            card.add_to_cart_clicked.connect(self.handle_add_to_cart)
            card.product_clicked.connect(self.handle_product_click)
            card.favorite_toggled.connect(self.favorites_updated.emit)

            self.productsGridLayout.addWidget(card, row, col)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        # Set vertical spacing between rows
        self.productsGridLayout.setVerticalSpacing(20)
        
        # Add stretch to fill remaining space
        self.productsGridLayout.setRowStretch(row + 1, 1)

    def update_pagination(self):
        """Update pagination info"""
        total_items = len(self.all_products)
        self.total_pages = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)
        
        # Update page info label
        self.pageInfoLabel.setText(f"Trang {self.current_page} / {self.total_pages}")
        
        # Enable/disable buttons
        self.prevButton.setEnabled(self.current_page > 1)
        self.nextButton.setEnabled(self.current_page < self.total_pages)

    def display_current_page(self):
        """Display products for current page"""
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = start_idx + self.items_per_page
        page_products = self.all_products[start_idx:end_idx]
        self.display_products(page_products)

    def prev_page(self):
        """Go to previous page"""
        if self.current_page > 1:
            self.current_page -= 1
            self.update_pagination()
            self.display_current_page()
            # Scroll to top of main scroll area
            self.mainScrollArea.verticalScrollBar().setValue(0)

    def next_page(self):
        """Go to next page"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.update_pagination()
            self.display_current_page()
            # Scroll to top of main scroll area
            self.mainScrollArea.verticalScrollBar().setValue(0)

    def handle_category_change(self, index):
        """Handle category tab change"""
        if index == 0:
            # All products
            self.load_products()
        else:
            # Get category ID
            categories = self.menu_controller.get_categories()
            if 0 <= index - 1 < len(categories):
                category_id = categories[index - 1]['id']
                self.load_products(category_id)

    def handle_search(self, query):
        """Handle product search"""
        if not query.strip():
            # If search is empty, reload current category
            current_index = self.categoryTabWidget.currentIndex()
            self.handle_category_change(current_index)
            return

        # Search products
        products = self.menu_controller.search_products(query)
        self.all_products = products
        self.current_page = 1
        self.update_pagination()
        self.display_current_page()

    def apply_filters(self):
        """Apply product filters"""
        # Get current category
        current_index = self.categoryTabWidget.currentIndex()
        category_id = None

        if current_index > 0:
            categories = self.menu_controller.get_categories()
            if 0 <= current_index - 1 < len(categories):
                category_id = categories[current_index - 1]['id']

        # Get filter values
        temperature = None
        if self.hotCheckBox.isChecked():
            temperature = 'hot'
        elif self.coldCheckBox.isChecked():
            temperature = 'cold'

        is_caffeine_free = self.caffeineCheckBox.isChecked() if self.caffeineCheckBox.isChecked() else None

        # Filter products
        products = self.menu_controller.filter_products(
            category_id=category_id,
            temperature=temperature,
            is_caffeine_free=is_caffeine_free
        )

        self.all_products = products
        self.current_page = 1
        self.update_pagination()
        self.display_current_page()

    def handle_add_to_cart(self, product):
        """Handle add to cart button click - show detail dialog"""
        # Show product detail dialog for customization
        self.handle_product_click(product)

    def handle_product_click(self, product):
        """Handle product card click - show detail dialog"""
        from views.product_detail_dialog import ProductDetailDialog

        dialog = ProductDetailDialog(product['id'], self)
        dialog.product_added.connect(self.cart_updated.emit)
        dialog.exec()
