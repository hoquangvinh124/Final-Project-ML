"""
Auto-generated UI file for Favorites Widget
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QScrollArea, QFrame, QGridLayout)
from PyQt6.QtCore import Qt


class Ui_FavoritesWidget:
    """UI class for favorites widget"""

    def setupUi(self, FavoritesWidget):
        """Setup UI"""
        FavoritesWidget.setObjectName("FavoritesWidget")

        # Main layout
        main_layout = QVBoxLayout(FavoritesWidget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Header
        header_layout = QHBoxLayout()

        title_label = QLabel("❤️ Sản phẩm yêu thích")
        title_label.setObjectName("titleLabel")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        self.favoritesCountLabel = QLabel("0 sản phẩm")
        self.favoritesCountLabel.setObjectName("favoritesCountLabel")
        self.favoritesCountLabel.setStyleSheet("font-size: 14px; color: #666;")
        header_layout.addWidget(self.favoritesCountLabel)

        main_layout.addLayout(header_layout)

        # Scroll area for favorites
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background-color: #F9F3EF;")

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: #F9F3EF;")
        self.favoritesGridLayout = QGridLayout(scroll_content)
        self.favoritesGridLayout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.favoritesGridLayout.setSpacing(20)
        self.favoritesGridLayout.setContentsMargins(20, 20, 20, 20)

        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
