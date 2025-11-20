"""Admin Categories Management"""
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QTimer
from controllers.admin_category_controller import AdminCategoryController
from controllers.admin_controller import AdminController

class CategoryDialog(QDialog):
    def __init__(self, category=None, parent=None):
        super().__init__(parent)
        self.category = category
        self.setWindowTitle("Sửa danh mục" if category else "Thêm danh mục")
        self.setup_ui()
        if category:
            self.load_data()

    def setup_ui(self):
        layout = QFormLayout(self)
        self.name_edit = QLineEdit()
        layout.addRow("Tên danh mục:", self.name_edit)
        
        self.desc_edit = QTextEdit()
        self.desc_edit.setMaximumHeight(80)
        self.desc_edit.setStyleSheet("""
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
        layout.addRow("Mô tả:", self.desc_edit)
        
        self.active_check = QCheckBox("Hiển thị")
        self.active_check.setChecked(True)
        layout.addRow("Trạng thái:", self.active_check)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def load_data(self):
        self.name_edit.setText(self.category['name'])
        self.desc_edit.setPlainText(self.category.get('description', ''))
        self.active_check.setChecked(self.category['is_active'])

    def get_data(self):
        return {
            'name': self.name_edit.text().strip(),
            'description': self.desc_edit.toPlainText().strip(),
            'is_active': self.active_check.isChecked()
        }

class AdminCategoriesWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.category_controller = AdminCategoryController()
        self.admin_controller = AdminController()
        self.setup_ui()
        self.load_categories()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        header = QHBoxLayout()
        header.addWidget(QLabel("<h2>📂 Quản lý danh mục</h2>"))
        header.addStretch()
        
        add_btn = QPushButton("➕ Thêm danh mục")
        add_btn.clicked.connect(self.handle_add)
        header.addWidget(add_btn)
        
        refresh_btn = QPushButton("🔄 Làm mới")
        refresh_btn.clicked.connect(self.load_categories)
        header.addWidget(refresh_btn)
        layout.addLayout(header)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID", "Tên", "Số sản phẩm", "Trạng thái", "Thao tác"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        
        # Fix row height issue
        self.table.verticalHeader().setDefaultSectionSize(50)
        self.table.verticalHeader().setMinimumSectionSize(50)
        
        layout.addWidget(self.table)

    def load_categories(self):
        categories = self.category_controller.get_all_categories()
        self.display_categories(categories)

    def display_categories(self, categories):
        self.table.setRowCount(len(categories))
        for row, cat in enumerate(categories):
            self.table.setItem(row, 0, QTableWidgetItem(str(cat['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(cat['name']))
            self.table.setItem(row, 2, QTableWidgetItem(str(cat.get('product_count', 0))))
            
            status = "✅ Hiển thị" if cat['is_active'] else "❌ Ẩn"
            self.table.setItem(row, 3, QTableWidgetItem(status))

            action_widget = QWidget()
            action_widget.setMinimumWidth(200)
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 2, 5, 2)
            action_layout.setSpacing(5)

            edit_btn = QPushButton("Sửa")
            edit_btn.setToolTip("Sửa danh mục")
            edit_btn.setStyleSheet("background-color: #2196F3; color: white; border: none; padding: 6px 12px; border-radius: 3px; font-size: 12px;")
            edit_btn.clicked.connect(lambda checked, c=cat: self.handle_edit(c))
            action_layout.addWidget(edit_btn)

            toggle_btn = QPushButton("Ẩn" if cat['is_active'] else "Hiện")
            toggle_btn.setToolTip("Ẩn/Hiện danh mục")
            toggle_btn.setStyleSheet("background-color: #FF9800; color: white; border: none; padding: 6px 12px; border-radius: 3px; font-size: 12px;")
            toggle_btn.clicked.connect(lambda checked, c=cat: self.handle_toggle(c))
            action_layout.addWidget(toggle_btn)

            delete_btn = QPushButton("Xóa")
            delete_btn.setToolTip("Xóa danh mục")
            delete_btn.setStyleSheet("background-color: #F44336; color: white; border: none; padding: 6px 12px; border-radius: 3px; font-size: 12px;")
            delete_btn.clicked.connect(lambda checked, c=cat: self.handle_delete(c))
            action_layout.addWidget(delete_btn)

            self.table.setCellWidget(row, 4, action_widget)

            # Set row height to accommodate buttons
            self.table.setRowHeight(row, 50)

        QTimer.singleShot(100, self.adjust_columns)

    def adjust_columns(self):
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        
        for i in [0, 2, 3]:
            self.table.resizeColumnToContents(i)
            
        self.table.setColumnWidth(4, 220)

    def handle_add(self):
        dialog = CategoryDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            admin_id = self.admin_controller.get_current_admin_id()
            success, msg = self.category_controller.create_category(dialog.get_data(), admin_id)
            if success:
                QMessageBox.information(self, "Thành công", msg)
                self.load_categories()
            else:
                QMessageBox.warning(self, "Lỗi", msg)

    def handle_edit(self, cat):
        dialog = CategoryDialog(cat, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            admin_id = self.admin_controller.get_current_admin_id()
            success, msg = self.category_controller.update_category(cat['id'], dialog.get_data(), admin_id)
            if success:
                QMessageBox.information(self, "Thành công", msg)
                self.load_categories()
            else:
                QMessageBox.warning(self, "Lỗi", msg)

    def handle_toggle(self, cat):
        admin_id = self.admin_controller.get_current_admin_id()
        success, msg = self.category_controller.toggle_category_status(cat['id'], admin_id)
        if success:
            self.load_categories()
        else:
            QMessageBox.warning(self, "Lỗi", msg)

    def handle_delete(self, cat):
        reply = QMessageBox.question(self, "Xác nhận", f"Xóa danh mục '{cat['name']}'?")
        if reply == QMessageBox.StandardButton.Yes:
            admin_id = self.admin_controller.get_current_admin_id()
            success, msg = self.category_controller.delete_category(cat['id'], admin_id)
            if success:
                QMessageBox.information(self, "Thành công", msg)
                self.load_categories()
            else:
                QMessageBox.warning(self, "Lỗi", msg)

    def refresh(self):
        self.load_categories()
