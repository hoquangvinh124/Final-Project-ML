"""Admin Vouchers Management"""
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QDate, QTimer
from controllers.admin_voucher_controller import AdminVoucherController
from controllers.admin_controller import AdminController
from utils.validators import format_currency

class VoucherDialog(QDialog):
    def __init__(self, voucher=None, parent=None):
        super().__init__(parent)
        self.voucher = voucher
        self.setWindowTitle("Sửa voucher" if voucher else "Thêm voucher")
        self.resize(500, 600)
        self.setup_ui()
        if voucher:
            self.load_data()

    def setup_ui(self):
        layout = QFormLayout(self)
        
        self.code_edit = QLineEdit()
        self.code_edit.setPlaceholderText("VD: SUMMER2024")
        layout.addRow("Mã voucher:", self.code_edit)
        
        self.name_edit = QLineEdit()
        layout.addRow("Tên voucher:", self.name_edit)
        
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
        
        self.type_combo = QComboBox()
        self.type_combo.addItem("Phần trăm (%)", "percentage")
        self.type_combo.addItem("Số tiền cố định (đ)", "fixed")
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        layout.addRow("Loại giảm giá:", self.type_combo)
        
        self.value_spin = QDoubleSpinBox()
        self.value_spin.setRange(0, 1000000)
        self.value_spin.setDecimals(0)
        layout.addRow("Giá trị:", self.value_spin)
        
        self.min_order_spin = QDoubleSpinBox()
        self.min_order_spin.setRange(0, 10000000)
        self.min_order_spin.setDecimals(0)
        self.min_order_spin.setSuffix(" đ")
        layout.addRow("Đơn tối thiểu:", self.min_order_spin)
        
        self.max_discount_spin = QDoubleSpinBox()
        self.max_discount_spin.setRange(0, 1000000)
        self.max_discount_spin.setDecimals(0)
        self.max_discount_spin.setSuffix(" đ")
        layout.addRow("Giảm tối đa:", self.max_discount_spin)
        
        self.usage_limit_spin = QSpinBox()
        self.usage_limit_spin.setRange(0, 100000)
        self.usage_limit_spin.setSpecialValueText("Không giới hạn")
        layout.addRow("Số lần sử dụng:", self.usage_limit_spin)
        
        self.from_date = QDateEdit()
        self.from_date.setDate(QDate.currentDate())
        self.from_date.setCalendarPopup(True)
        layout.addRow("Từ ngày:", self.from_date)
        
        self.to_date = QDateEdit()
        self.to_date.setDate(QDate.currentDate().addDays(30))
        self.to_date.setCalendarPopup(True)
        layout.addRow("Đến ngày:", self.to_date)
        
        self.active_check = QCheckBox("Kích hoạt")
        self.active_check.setChecked(True)
        layout.addRow("Trạng thái:", self.active_check)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def on_type_changed(self):
        is_percentage = self.type_combo.currentData() == "percentage"
        self.value_spin.setSuffix("%" if is_percentage else " đ")
        self.value_spin.setMaximum(100 if is_percentage else 1000000)

    def load_data(self):
        from datetime import datetime
        try:
            print(f"Loading voucher data: {self.voucher}")  # Debug

            self.code_edit.setText(self.voucher['code'])
            self.name_edit.setText(self.voucher['name'])
            self.desc_edit.setPlainText(self.voucher.get('description', ''))

            idx = self.type_combo.findData(self.voucher['discount_type'])
            if idx >= 0:
                self.type_combo.setCurrentIndex(idx)

            self.value_spin.setValue(float(self.voucher['discount_value']))
            self.min_order_spin.setValue(float(self.voucher.get('min_order_amount', 0)))
            self.max_discount_spin.setValue(float(self.voucher.get('max_discount_amount', 0) or 0))
            self.usage_limit_spin.setValue(self.voucher.get('usage_limit', 0) or 0)

            # Handle start_date
            start_date = self.voucher.get('start_date')
            if start_date:
                if isinstance(start_date, datetime):
                    self.from_date.setDate(QDate(start_date.year, start_date.month, start_date.day))
                else:
                    # Try to parse string date
                    from datetime import datetime as dt
                    date_obj = dt.strptime(str(start_date)[:10], '%Y-%m-%d')
                    self.from_date.setDate(QDate(date_obj.year, date_obj.month, date_obj.day))

            # Handle end_date
            end_date = self.voucher.get('end_date')
            if end_date:
                if isinstance(end_date, datetime):
                    self.to_date.setDate(QDate(end_date.year, end_date.month, end_date.day))
                else:
                    # Try to parse string date
                    from datetime import datetime as dt
                    date_obj = dt.strptime(str(end_date)[:10], '%Y-%m-%d')
                    self.to_date.setDate(QDate(date_obj.year, date_obj.month, date_obj.day))

            self.active_check.setChecked(bool(self.voucher.get('is_active', True)))
        except Exception as e:
            print(f"Error loading voucher data: {e}")
            import traceback
            traceback.print_exc()

    def get_data(self):
        return {
            'code': self.code_edit.text().strip(),
            'name': self.name_edit.text().strip(),
            'description': self.desc_edit.toPlainText().strip(),
            'discount_type': self.type_combo.currentData(),
            'discount_value': self.value_spin.value(),
            'min_order_amount': self.min_order_spin.value(),
            'max_discount_amount': self.max_discount_spin.value() if self.max_discount_spin.value() > 0 else None,
            'usage_limit': self.usage_limit_spin.value() if self.usage_limit_spin.value() > 0 else None,
            'start_date': self.from_date.date().toString("yyyy-MM-dd"),
            'end_date': self.to_date.date().toString("yyyy-MM-dd"),
            'is_active': self.active_check.isChecked()
        }

class AdminVouchersWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.voucher_controller = AdminVoucherController()
        self.admin_controller = AdminController()
        self.setup_ui()
        self.load_vouchers()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        header = QHBoxLayout()
        header.addWidget(QLabel("<h2>🎫 Quản lý voucher</h2>"))
        header.addStretch()
        
        add_btn = QPushButton("➕ Thêm voucher")
        add_btn.clicked.connect(self.handle_add)
        header.addWidget(add_btn)
        
        refresh_btn = QPushButton("🔄 Làm mới")
        refresh_btn.clicked.connect(self.load_vouchers)
        header.addWidget(refresh_btn)
        layout.addLayout(header)

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Tìm kiếm:"))
        self.search_edit = QLineEdit()
        self.search_edit.textChanged.connect(self.load_vouchers)
        filter_layout.addWidget(self.search_edit)
        
        filter_layout.addWidget(QLabel("Trạng thái:"))
        self.status_combo = QComboBox()
        self.status_combo.addItem("Tất cả", None)
        self.status_combo.addItem("Đang hoạt động", "active")
        self.status_combo.addItem("Đã hết hạn", "expired")
        self.status_combo.addItem("Không hoạt động", "inactive")
        self.status_combo.currentIndexChanged.connect(self.load_vouchers)
        filter_layout.addWidget(self.status_combo)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Mã", "Tên", "Loại", "Giá trị", "Sử dụng", "Từ ngày", "Đến ngày", "Thao tác"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        
        # Fix row height issue
        self.table.verticalHeader().setDefaultSectionSize(50)
        self.table.verticalHeader().setMinimumSectionSize(50)
        
        layout.addWidget(self.table)

    def load_vouchers(self):
        search = self.search_edit.text().strip()
        status = self.status_combo.currentData()
        vouchers = self.voucher_controller.get_all_vouchers(
            status=status,
            search=search if search else None
        )
        self.display_vouchers(vouchers)

    def display_vouchers(self, vouchers):
        from datetime import datetime
        self.table.setRowCount(len(vouchers))
        for row, v in enumerate(vouchers):
            self.table.setItem(row, 0, QTableWidgetItem(v['code']))
            self.table.setItem(row, 1, QTableWidgetItem(v['name']))
            
            type_text = "%" if v['discount_type'] == 'percentage' else "đ"
            self.table.setItem(row, 2, QTableWidgetItem(type_text))
            
            value = f"{v['discount_value']}{type_text}"
            self.table.setItem(row, 3, QTableWidgetItem(value))
            
            usage = f"{v.get('usage_count', 0)}"
            if v.get('usage_limit'):
                usage += f"/{v['usage_limit']}"
            self.table.setItem(row, 4, QTableWidgetItem(usage))
            
            from_date = v.get('start_date')
            if isinstance(from_date, datetime):
                from_str = from_date.strftime("%d/%m/%Y")
            else:
                from_str = str(from_date) if from_date else ""
            self.table.setItem(row, 5, QTableWidgetItem(from_str))

            to_date = v.get('end_date')
            if isinstance(to_date, datetime):
                to_str = to_date.strftime("%d/%m/%Y")
            else:
                to_str = str(to_date) if to_date else ""
            self.table.setItem(row, 6, QTableWidgetItem(to_str))

            action_widget = QWidget()
            action_widget.setMinimumWidth(200)
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(5, 2, 5, 2)
            action_layout.setSpacing(5)

            edit_btn = QPushButton("Sửa")
            edit_btn.setToolTip("Sửa voucher")
            edit_btn.setStyleSheet("background-color: #2196F3; color: white; border: none; padding: 6px 12px; border-radius: 3px; font-size: 12px;")
            edit_btn.clicked.connect(lambda checked, voucher=v: self.handle_edit(voucher))
            action_layout.addWidget(edit_btn)

            toggle_btn = QPushButton("Tắt" if v['is_active'] else "Bật")
            toggle_btn.setToolTip("Bật/Tắt voucher")
            toggle_btn.setStyleSheet("background-color: #FF9800; color: white; border: none; padding: 6px 12px; border-radius: 3px; font-size: 12px;")
            toggle_btn.clicked.connect(lambda checked, voucher=v: self.handle_toggle(voucher))
            action_layout.addWidget(toggle_btn)

            delete_btn = QPushButton("Xóa")
            delete_btn.setToolTip("Xóa voucher")
            delete_btn.setStyleSheet("background-color: #F44336; color: white; border: none; padding: 6px 12px; border-radius: 3px; font-size: 12px;")
            delete_btn.clicked.connect(lambda checked, voucher=v: self.handle_delete(voucher))
            action_layout.addWidget(delete_btn)

            self.table.setCellWidget(row, 7, action_widget)

            # Set row height to accommodate buttons
            self.table.setRowHeight(row, 50)

        QTimer.singleShot(100, self.adjust_columns)

    def adjust_columns(self):
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Fixed)
        
        for i in [0, 2, 3, 4, 5, 6]:
            self.table.resizeColumnToContents(i)
            
        self.table.setColumnWidth(7, 220)

    def handle_add(self):
        dialog = VoucherDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            admin_id = self.admin_controller.get_current_admin_id()
            success, msg = self.voucher_controller.create_voucher(dialog.get_data(), admin_id)
            if success:
                QMessageBox.information(self, "Thành công", msg)
                self.load_vouchers()
            else:
                QMessageBox.warning(self, "Lỗi", msg)

    def handle_edit(self, v):
        try:
            dialog = VoucherDialog(v, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                admin_id = self.admin_controller.get_current_admin_id()
                data = dialog.get_data()
                success, msg = self.voucher_controller.update_voucher(v['id'], data, admin_id)
                if success:
                    QMessageBox.information(self, "Thành công", msg)
                    self.load_vouchers()
                else:
                    QMessageBox.warning(self, "Lỗi", msg)
        except Exception as e:
            print(f"Error in handle_edit: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi sửa voucher: {str(e)}")

    def handle_toggle(self, v):
        try:
            admin_id = self.admin_controller.get_current_admin_id()
            success, msg = self.voucher_controller.toggle_voucher_status(v['id'], admin_id)
            if success:
                self.load_vouchers()
            else:
                QMessageBox.warning(self, "Lỗi", msg)
        except Exception as e:
            print(f"Error in handle_toggle: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi bật/tắt voucher: {str(e)}")

    def handle_delete(self, v):
        try:
            reply = QMessageBox.question(self, "Xác nhận", f"Xóa voucher '{v['code']}'?")
            if reply == QMessageBox.StandardButton.Yes:
                admin_id = self.admin_controller.get_current_admin_id()
                success, msg = self.voucher_controller.delete_voucher(v['id'], admin_id)
                if success:
                    QMessageBox.information(self, "Thành công", msg)
                    self.load_vouchers()
                else:
                    QMessageBox.warning(self, "Lỗi", msg)
        except Exception as e:
            print(f"Error in handle_delete: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi xóa voucher: {str(e)}")

    def refresh(self):
        self.load_vouchers()
