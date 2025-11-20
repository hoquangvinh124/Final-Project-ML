"""
Favorites Widget - Extended Logic
Display and manage favorite products
"""
from PyQt6.QtWidgets import (QWidget, QFrame, QVBoxLayout, QHBoxLayout,
                             QLabel, QPushButton, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QByteArray
from PyQt6.QtGui import QPixmap
import base64
from ui_generated.favorites import Ui_FavoritesWidget
from controllers.favorites_controller import FavoritesController
from controllers.auth_controller import AuthController
from controllers.cart_controller import CartController
from utils.validators import format_currency


class FavoriteProductCard(QFrame):
    """Favorite product card widget"""

    remove_clicked = pyqtSignal(dict)
    product_clicked = pyqtSignal(dict)
    add_to_cart_clicked = pyqtSignal(dict)

    def __init__(self, product_data, parent=None):
        super().__init__(parent)
        self.product_data = product_data
        self.setup_ui()

    def setup_ui(self):
        """Setup product card UI"""
        self.setFrameShape(QFrame.Shape.Box)
        self.setMaximumWidth(250)
        self.setMinimumHeight(350)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Card styling with white background on hover
        self.setStyleSheet("""
            FavoriteProductCard {
                background-color: #F9F3EF;
                border: 1px solid #EAEAEA;
                border-radius: 12px;
                padding: 10px;
            }
            FavoriteProductCard:hover {
                background-color: #FFFFFF;
                border: 2px solid #A31E25;
            }
        """)

        layout = QVBoxLayout(self)

        # Product image
        image_label = QLabel()
        image_label.setFixedSize(220, 220)
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setStyleSheet("""
            background-color: #f0f0f0;
            border-radius: 8px;
            font-size: 80px;
        """)
        
        # Load image from base64 if available (same as menu_ex.py)
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
                    image_label.setText("☕")
            except Exception as e:
                # Fallback to emoji on error
                print(f"Error loading favorite product image: {e}")
                image_label.setText("☕")
        else:
            # Use emoji as fallback
            image_label.setText(product_image if product_image and len(product_image) < 5 else "☕")
        
        layout.addWidget(image_label)

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

        # Buttons layout
        buttons_layout = QHBoxLayout()

        # Add to cart button
        add_btn = QPushButton("Thêm vào giỏ")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #A31E25;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8B181F;
            }
        """)
        add_btn.clicked.connect(lambda: self.add_to_cart_clicked.emit(self.product_data))
        buttons_layout.addWidget(add_btn)

        # Remove from favorites button - white background with red heart
        remove_btn = QPushButton("❤️")
        remove_btn.setFixedWidth(40)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #A31E25;
                border: 2px solid #A31E25;
                padding: 8px;
                border-radius: 4px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #FFF0F0;
                border: 2px solid #8B181F;
            }
        """)
        remove_btn.clicked.connect(lambda: self.remove_clicked.emit(self.product_data))
        buttons_layout.addWidget(remove_btn)

        layout.addLayout(buttons_layout)

    def mousePressEvent(self, event):
        """Handle card click"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Don't trigger if clicked on buttons
            if not self.childAt(event.pos()) or not isinstance(self.childAt(event.pos()), QPushButton):
                self.product_clicked.emit(self.product_data)


class FavoritesWidget(QWidget, Ui_FavoritesWidget):
    """Favorites widget with product display"""

    favorites_updated = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.favorites_controller = FavoritesController()
        self.auth_controller = AuthController()
        self.cart_controller = CartController()

        # Load favorites
        self.load_favorites()

    def load_favorites(self):
        """Load and display favorite products"""
        user_id = self.auth_controller.get_current_user_id()
        if not user_id:
            return

        # Clear existing products
        while self.favoritesGridLayout.count():
            item = self.favoritesGridLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Get favorite products
        products = self.favorites_controller.get_favorite_products(user_id)

        # Update count
        self.favoritesCountLabel.setText(f"{len(products)} sản phẩm")

        if not products:
            # Show empty state - centered in the entire scroll area
            # Clear grid layout alignment to allow proper centering
            self.favoritesGridLayout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            empty_label = QLabel("❤️\n\nChưa có sản phẩm yêu thích\n\nHãy thêm sản phẩm yêu thích từ menu!")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("font-size: 18px; color: #999; padding: 50px;")
            
            # Add to grid layout at center position
            self.favoritesGridLayout.addWidget(empty_label, 0, 0, Qt.AlignmentFlag.AlignCenter)
            return

        # Add products to grid - dynamic columns based on available width
        # Reset alignment to left for products
        self.favoritesGridLayout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        row = 0
        col = 0
        # Calculate max columns based on card width (250) + spacing (20)
        # Will allow more products per row on wider screens
        max_cols = max(4, int(self.width() / 270))  # At least 4 columns

        for product in products:
            card = FavoriteProductCard(product)
            card.remove_clicked.connect(self.handle_remove_favorite)
            card.product_clicked.connect(self.handle_product_click)
            card.add_to_cart_clicked.connect(self.handle_add_to_cart)

            self.favoritesGridLayout.addWidget(card, row, col)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def handle_remove_favorite(self, product):
        """Handle remove from favorites"""
        user_id = self.auth_controller.get_current_user_id()
        if not user_id:
            return

        # Confirm removal
        reply = QMessageBox.question(
            self,
            "Xác nhận",
            f"Bạn có muốn xóa '{product['name']}' khỏi danh sách yêu thích?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            success, message = self.favorites_controller.remove_favorite(user_id, product['id'])

            if success:
                # Reload favorites
                self.load_favorites()
                self.favorites_updated.emit()
            else:
                QMessageBox.warning(self, "Lỗi", message)

    def handle_product_click(self, product):
        """Handle product card click - show detail dialog"""
        from views.product_detail_dialog import ProductDetailDialog

        dialog = ProductDetailDialog(product['id'], self)
        dialog.product_added.connect(self.favorites_updated.emit)
        dialog.exec()

    def handle_add_to_cart(self, product):
        """Handle add to cart button - open product detail dialog"""
        # Mở dialog chi tiết sản phẩm để người dùng chọn tùy chọn
        self.handle_product_click(product)

    def refresh(self):
        """Refresh favorites display"""
        self.load_favorites()
