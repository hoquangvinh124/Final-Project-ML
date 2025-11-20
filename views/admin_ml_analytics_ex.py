"""
Admin ML Analytics Widget - Revenue Forecasting
Each chart has its own controls
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QComboBox, QLabel, QMessageBox, QDateEdit, QGroupBox,
                              QScrollArea, QFrame, QGridLayout, QSizePolicy, QSpinBox)
from PyQt6.QtCore import Qt, QDate, QThread, pyqtSignal
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from revenue_forecasting.predictor import get_predictor


class PredictionWorker(QThread):
    """Worker thread for running predictions"""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, predictor, task, **kwargs):
        super().__init__()
        self.predictor = predictor
        self.task = task
        self.kwargs = kwargs

    def run(self):
        """Run prediction task"""
        try:
            if self.task == 'overall':
                result = self.predictor.predict_overall(**self.kwargs)
            elif self.task == 'store':
                result = self.predictor.predict_store(**self.kwargs)
            elif self.task == 'top_stores':
                result = self.predictor.get_top_stores(**self.kwargs)
            elif self.task == 'bottom_stores':
                result = self.predictor.get_bottom_stores(**self.kwargs)
            else:
                raise ValueError(f"Unknown task: {self.task}")
            self.finished.emit(result)
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error.emit(str(e))


class CompactChart(FigureCanvas):
    """Compact chart widget"""

    def __init__(self, parent=None, width=6, height=3.5):
        self.fig = Figure(figsize=(width, height), dpi=80)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(280)
        self.setMaximumHeight(320)

        self.fig.patch.set_facecolor('#ffffff')
        self.axes.set_facecolor('#ffffff')
        self.axes.grid(True, alpha=0.2, linestyle='--')

        # Disable mouse wheel zoom to allow scrolling
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def wheelEvent(self, event):
        """Override wheel event to pass it to parent (allow scroll)"""
        event.ignore()

    def plot_line_forecast(self, data, title=None):
        """Plot line chart for forecast"""
        self.axes.clear()

        if not data or 'forecasts' not in data:
            self.axes.text(0.5, 0.5, 'Chưa có dữ liệu', ha='center', va='center')
            self.draw()
            return

        forecasts = data['forecasts']
        dates = [f['date'] for f in forecasts]
        values = [f['forecast'] for f in forecasts]

        self.axes.plot(dates, values, 'b-', linewidth=2.5, marker='o', markersize=4, alpha=0.8)

        if title:
            self.axes.set_title(title, fontsize=11, fontweight='bold', pad=10)

        self.axes.set_xlabel('Ngày', fontsize=9)
        self.axes.set_ylabel('Doanh thu ($)', fontsize=9)

        if len(dates) > 10:
            step = max(1, len(dates) // 8)
            self.axes.set_xticks(range(0, len(dates), step))
            self.axes.set_xticklabels([dates[i] for i in range(0, len(dates), step)],
                                     rotation=45, ha='right', fontsize=8)
        else:
            self.axes.set_xticks(range(len(dates)))
            self.axes.set_xticklabels(dates, rotation=45, ha='right', fontsize=8)

        from matplotlib.ticker import FuncFormatter
        def currency_formatter(x, p):
            if x >= 1000000:
                return f'{x/1000000:.1f}M'
            elif x >= 1000:
                return f'{x/1000:.0f}K'
            return f'{int(x)}'
        self.axes.yaxis.set_major_formatter(FuncFormatter(currency_formatter))
        self.axes.tick_params(axis='y', labelsize=8)

        self.fig.tight_layout()
        self.draw()

        # Return statistics for display
        return {
            'values': values,
            'max': max(values),
            'min': min(values),
            'avg': sum(values) / len(values),
            'total': sum(values)
        }

    def plot_bar_comparison(self, stores_data, days, title=""):
        """Plot bar chart for store comparison"""
        self.axes.clear()

        if not stores_data:
            self.axes.text(0.5, 0.5, 'Chưa có dữ liệu', ha='center', va='center')
            self.draw()
            return

        store_names = [f"#{s['store_nbr']}" for s in stores_data]
        revenues = [s['forecast_avg_daily'] * days for s in stores_data]

        colors = ['#4CAF50' if i < len(stores_data)//2 else '#FF9800' for i in range(len(stores_data))]
        bars = self.axes.bar(range(len(store_names)), revenues, color=colors, alpha=0.7)

        for bar in bars:
            height = bar.get_height()
            self.axes.text(bar.get_x() + bar.get_width()/2., height,
                          f'{height/1000:.0f}K',
                          ha='center', va='bottom', fontsize=7)

        self.axes.set_title(title, fontsize=11, fontweight='bold', pad=10)
        self.axes.set_xlabel('Cửa hàng', fontsize=9)
        self.axes.set_ylabel('Doanh thu ($)', fontsize=9)
        self.axes.set_xticks(range(len(store_names)))
        self.axes.set_xticklabels(store_names, fontsize=8)

        from matplotlib.ticker import FuncFormatter
        def currency_formatter(x, p):
            if x >= 1000000:
                return f'{x/1000000:.1f}M'
            elif x >= 1000:
                return f'{x/1000:.0f}K'
            return f'{int(x)}'
        self.axes.yaxis.set_major_formatter(FuncFormatter(currency_formatter))
        self.axes.tick_params(axis='y', labelsize=8)

        self.fig.tight_layout()
        self.draw()

        # Return statistics for display
        return {
            'values': revenues,
            'max': max(revenues),
            'min': min(revenues),
            'avg': sum(revenues) / len(revenues),
            'total': sum(revenues)
        }


class AdminMLAnalyticsWidget(QWidget):
    """Admin ML Analytics widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.predictor = get_predictor()
        self.setup_ui()
        self.load_stores()
        self.load_initial_stats()  # Load stats from dataset on startup

    def setup_ui(self):
        """Setup UI"""
        # Create main layout for this widget
        widget_layout = QVBoxLayout(self)
        widget_layout.setContentsMargins(0, 0, 0, 0)
        widget_layout.setSpacing(0)

        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Create content widget for scroll area
        content_widget = QWidget()
        main_layout = QVBoxLayout(content_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Title
        title_label = QLabel("Dự Báo Doanh Thu")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 12px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #c7a17a, stop:1 #f5f5f5);
                border-radius: 6px;
            }
        """)
        main_layout.addWidget(title_label)

        # STATS FIRST - Thống kê tổng quan
        stats_group = self.create_stats_panel()
        main_layout.addWidget(stats_group)

        # Chart 1: Overall Forecast with own controls
        overall_section = self.create_chart_section(
            "Dự Báo Tổng Thể Hệ Thống",
            has_store_selector=False,
            chart_name='overall'
        )
        main_layout.addWidget(overall_section)

        # Chart 2: Store Forecast with own controls
        store_section = self.create_chart_section(
            "Dự Báo Từng Cửa Hàng",
            has_store_selector=True,
            chart_name='store'
        )
        main_layout.addWidget(store_section)

        # Chart 3 & 4: Comparison charts with shared controls
        comparison_section = self.create_comparison_section()
        main_layout.addWidget(comparison_section)

        # AI Chat Assistant - Integrated
        ai_chat_section = self.create_ai_chat_section()
        main_layout.addWidget(ai_chat_section)

        # Add stretch to push everything up
        main_layout.addStretch()

        # Set content widget to scroll area and add to main widget layout
        scroll_area.setWidget(content_widget)
        widget_layout.addWidget(scroll_area)

    def create_stats_panel(self):
        """Create stats panel"""
        group = QGroupBox("Thống Kê Tổng Quan")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid #2196F3;
                border-radius: 8px;
                margin-top: 10px;
                padding: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        group.setMinimumHeight(150)
        group.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QHBoxLayout(group)
        layout.setContentsMargins(10, 25, 10, 10)
        layout.setSpacing(15)

        self.stat1 = self.create_stat_card("Doanh thu tích lũy", "--", "#2196F3")
        self.stat2 = self.create_stat_card("TB doanh thu cửa hàng", "--", "#4CAF50")
        self.stat3 = self.create_stat_card("TB doanh thu cuối tuần", "--", "#FF9800")
        self.stat4 = self.create_stat_card("Tăng trưởng", "--", "#9C27B0")

        layout.addWidget(self.stat1)
        layout.addWidget(self.stat2)
        layout.addWidget(self.stat3)
        layout.addWidget(self.stat4)

        return group

    def create_stat_card(self, title, value, color):
        """Create stat card"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 6px;
            }}
        """)
        card.setMinimumHeight(110)
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {color}; font-size: 16px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        title_label.setWordWrap(True)
        layout.addWidget(title_label)

        value_label = QLabel(value)
        value_label.setObjectName("value")
        value_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        value_label.setWordWrap(True)
        value_label.setTextFormat(Qt.TextFormat.PlainText)
        layout.addWidget(value_label)

        layout.addStretch()

        return card

    def create_chart_stats_panel(self, chart_name):
        """Create stats panel for chart"""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 2px solid #4a90e2;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        panel.setMinimumHeight(100)
        panel.setMaximumHeight(120)
        panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QGridLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Create labels for stats
        stats_labels = [
            ("Tổng:", f"{chart_name}_total_label"),
            ("Cao nhất:", f"{chart_name}_max_label"),
            ("Thấp nhất:", f"{chart_name}_min_label"),
            ("Trung bình:", f"{chart_name}_avg_label"),
        ]

        for i, (title, label_name) in enumerate(stats_labels):
            # Title
            title_label = QLabel(title)
            title_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #2c5aa0;")
            layout.addWidget(title_label, i // 2, (i % 2) * 2)

            # Value
            value_label = QLabel("--")
            value_label.setObjectName(label_name)
            value_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #1a1a1a;")
            layout.addWidget(value_label, i // 2, (i % 2) * 2 + 1)
            setattr(self, label_name, value_label)

        return panel

    def create_chart_section(self, title, has_store_selector, chart_name):
        """Create section with chart and its own controls"""
        section = QGroupBox(title)
        section.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid #c7a17a;
                border-radius: 8px;
                margin-top: 10px;
                padding: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        layout = QVBoxLayout(section)

        # Controls
        controls_layout = QHBoxLayout()

        if has_store_selector:
            controls_layout.addWidget(QLabel("Cửa hàng:"))
            store_combo = QComboBox()
            store_combo.addItem("Đang tải...")
            store_combo.setMinimumWidth(200)
            controls_layout.addWidget(store_combo)
            setattr(self, f'{chart_name}_store_combo', store_combo)

        controls_layout.addWidget(QLabel("Thời gian:"))
        period_combo = QComboBox()
        period_combo.addItems(["7 Ngày", "1 Tháng (30)", "1 Quý (90)", "1 Năm (365)", "Tùy chỉnh"])
        controls_layout.addWidget(period_combo)
        setattr(self, f'{chart_name}_period_combo', period_combo)

        # Custom dates (hidden by default)
        start_date = QDateEdit()
        start_date.setCalendarPopup(True)
        start_date.setDate(QDate.currentDate())
        start_date.hide()
        controls_layout.addWidget(start_date)
        setattr(self, f'{chart_name}_start_date', start_date)

        end_date = QDateEdit()
        end_date.setCalendarPopup(True)
        end_date.setDate(QDate.currentDate().addDays(30))
        end_date.hide()
        controls_layout.addWidget(end_date)
        setattr(self, f'{chart_name}_end_date', end_date)

        # Connect period change
        period_combo.currentIndexChanged.connect(
            lambda idx, cn=chart_name: self.on_period_changed(idx, cn)
        )

        # Analyze button
        analyze_btn = QPushButton("Phân Tích")
        analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #c7a17a;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #a0826d; }
            QPushButton:disabled { background-color: #ccc; }
        """)
        analyze_btn.clicked.connect(lambda: self.analyze_chart(chart_name))
        controls_layout.addWidget(analyze_btn)
        setattr(self, f'{chart_name}_analyze_btn', analyze_btn)

        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        # Chart
        chart = CompactChart(self)
        layout.addWidget(chart)
        setattr(self, f'{chart_name}_chart', chart)

        # Stats panel (below chart)
        stats_panel = self.create_chart_stats_panel(chart_name)
        layout.addWidget(stats_panel)
        setattr(self, f'{chart_name}_stats_panel', stats_panel)

        return section

    def create_comparison_section(self):
        """Create comparison section with shared controls"""
        section = QGroupBox("So Sánh Cửa Hàng")
        section.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                border: 2px solid #c7a17a;
                border-radius: 8px;
                margin-top: 10px;
                padding: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        layout = QVBoxLayout(section)

        # Shared controls
        controls_layout = QHBoxLayout()

        controls_layout.addWidget(QLabel("Top N:"))
        self.comparison_topn = QSpinBox()
        self.comparison_topn.setRange(3, 20)
        self.comparison_topn.setValue(10)
        controls_layout.addWidget(self.comparison_topn)

        controls_layout.addWidget(QLabel("Thời gian:"))
        self.comparison_period = QComboBox()
        self.comparison_period.addItems(["7 Ngày", "1 Tháng (30)", "1 Quý (90)", "1 Năm (365)"])
        self.comparison_period.setCurrentIndex(1)
        controls_layout.addWidget(self.comparison_period)

        self.comparison_analyze_btn = QPushButton("Phân Tích")
        self.comparison_analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #c7a17a;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover { background-color: #a0826d; }
            QPushButton:disabled { background-color: #ccc; }
        """)
        self.comparison_analyze_btn.clicked.connect(self.analyze_comparison)
        controls_layout.addWidget(self.comparison_analyze_btn)

        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        # Charts side by side
        charts_layout = QHBoxLayout()

        # Top stores
        top_group = QGroupBox("Top Cao Nhất")
        top_layout = QVBoxLayout(top_group)
        self.top_chart = CompactChart(self)
        top_layout.addWidget(self.top_chart)

        # Top stats panel
        self.top_stats_panel = self.create_chart_stats_panel('top')
        top_layout.addWidget(self.top_stats_panel)

        charts_layout.addWidget(top_group)

        # Bottom stores
        bottom_group = QGroupBox("Top Thấp Nhất")
        bottom_layout = QVBoxLayout(bottom_group)
        self.bottom_chart = CompactChart(self)
        bottom_layout.addWidget(self.bottom_chart)

        # Bottom stats panel
        self.bottom_stats_panel = self.create_chart_stats_panel('bottom')
        bottom_layout.addWidget(self.bottom_stats_panel)

        charts_layout.addWidget(bottom_group)

        layout.addLayout(charts_layout)

        return section

    def on_period_changed(self, index, chart_name):
        """Handle period change"""
        start_date = getattr(self, f'{chart_name}_start_date')
        end_date = getattr(self, f'{chart_name}_end_date')

        if index == 4:  # Tùy chỉnh
            start_date.show()
            end_date.show()
        else:
            start_date.hide()
            end_date.hide()

    def update_stat_card(self, card, value):
        """Update stat card"""
        value_label = card.findChild(QLabel, "value")
        if value_label:
            # Clean the value string to ensure proper display
            clean_value = str(value).replace(',', '.')
            value_label.setText(clean_value)
            value_label.update()  # Force update

    def update_chart_stats(self, chart_name, stats):
        """Update chart statistics panel"""
        def format_currency(value):
            if value >= 1000000:
                return f"${value/1000000:.2f}M"
            elif value >= 1000:
                return f"${value/1000:.1f}K"
            else:
                return f"${value:.0f}"

        # Update labels
        total_label = getattr(self, f'{chart_name}_total_label', None)
        max_label = getattr(self, f'{chart_name}_max_label', None)
        min_label = getattr(self, f'{chart_name}_min_label', None)
        avg_label = getattr(self, f'{chart_name}_avg_label', None)

        if total_label:
            total_label.setText(format_currency(stats['total']))
        if max_label:
            max_label.setText(format_currency(stats['max']))
        if min_label:
            min_label.setText(format_currency(stats['min']))
        if avg_label:
            avg_label.setText(format_currency(stats['avg']))

    def load_stores(self):
        """Load stores list"""
        try:
            stores = self.predictor.get_all_stores()

            # Update store combo for store chart
            if hasattr(self, 'store_store_combo'):
                self.store_store_combo.clear()
                for store in stores:
                    self.store_store_combo.addItem(
                        f"Store #{store['store_nbr']} - {store['city']} (Type {store['type']})",
                        store['store_nbr']
                    )
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể load danh sách cửa hàng:\n{str(e)}")

    def get_days(self, chart_name):
        """Get days for chart"""
        period_combo = getattr(self, f'{chart_name}_period_combo')
        index = period_combo.currentIndex()

        if index == 4:  # Custom
            start_date = getattr(self, f'{chart_name}_start_date')
            end_date = getattr(self, f'{chart_name}_end_date')
            start = start_date.date().toPyDate()
            end = end_date.date().toPyDate()
            return (end - start).days
        else:
            days_map = {0: 7, 1: 30, 2: 90, 3: 365}
            return days_map[index]

    def analyze_chart(self, chart_name):
        """Analyze specific chart"""
        analyze_btn = getattr(self, f'{chart_name}_analyze_btn')
        analyze_btn.setEnabled(False)
        analyze_btn.setText("⏳ Đang phân tích...")

        days = self.get_days(chart_name)

        if chart_name == 'overall':
            worker = PredictionWorker(self.predictor, 'overall', days=days)
            worker.finished.connect(lambda data: self.on_overall_loaded(data))
        elif chart_name == 'store':
            store_nbr = self.store_store_combo.currentData()
            if not store_nbr:
                QMessageBox.warning(self, "Lỗi", "Vui lòng chọn cửa hàng!")
                analyze_btn.setEnabled(True)
                analyze_btn.setText("Phân Tích")
                return
            worker = PredictionWorker(self.predictor, 'store', store_nbr=store_nbr, days=days)
            worker.finished.connect(lambda data: self.on_store_loaded(data, chart_name))

        worker.error.connect(lambda e: self.on_error(e, chart_name))
        worker.start()
        setattr(self, f'{chart_name}_worker', worker)

    def on_overall_loaded(self, data):
        """Handle overall loaded"""
        stats = self.overall_chart.plot_line_forecast(data, "Dự Báo Tổng Thể Hệ Thống")

        # Update chart stats panel
        if stats:
            self.update_chart_stats('overall', stats)

        self.overall_analyze_btn.setEnabled(True)
        self.overall_analyze_btn.setText("Phân Tích")

    def on_store_loaded(self, data, chart_name):
        """Handle store loaded"""
        chart = getattr(self, f'{chart_name}_chart')
        store_name = f"Store #{data['store_nbr']} - {data['city']}"
        stats = chart.plot_line_forecast(data, store_name)

        # Update chart stats panel
        if stats:
            self.update_chart_stats(chart_name, stats)

        analyze_btn = getattr(self, f'{chart_name}_analyze_btn')
        analyze_btn.setEnabled(True)
        analyze_btn.setText("Phân Tích")

    def analyze_comparison(self):
        """Analyze comparison"""
        self.comparison_analyze_btn.setEnabled(False)
        self.comparison_analyze_btn.setText("Đang phân tích...")

        n = self.comparison_topn.value()
        period_idx = self.comparison_period.currentIndex()
        days_map = {0: 7, 1: 30, 2: 90, 3: 365}
        days = days_map[period_idx]

        # Top stores
        worker_top = PredictionWorker(self.predictor, 'top_stores', n=n)
        worker_top.finished.connect(lambda data: self.on_top_loaded(data, days))
        worker_top.error.connect(lambda e: self.on_error(e, 'comparison'))
        worker_top.start()
        self.top_worker = worker_top

        # Bottom stores
        worker_bottom = PredictionWorker(self.predictor, 'bottom_stores', n=n)
        worker_bottom.finished.connect(lambda data: self.on_bottom_loaded(data, days))
        worker_bottom.error.connect(lambda e: self.on_error(e, 'comparison'))
        worker_bottom.start()
        self.bottom_worker = worker_bottom

    def on_top_loaded(self, data, days):
        """Handle top stores loaded"""
        stores = data.get('stores', [])
        stats = self.top_chart.plot_bar_comparison(stores, days, f"Top {len(stores)} Cao Nhất ({days} ngày)")

        # Update stats panel
        if stats:
            self.update_chart_stats('top', stats)

    def on_bottom_loaded(self, data, days):
        """Handle bottom stores loaded"""
        stores = data.get('stores', [])
        stats = self.bottom_chart.plot_bar_comparison(stores, days, f"Top {len(stores)} Thấp Nhất ({days} ngày)")

        # Update stats panel
        if stats:
            self.update_chart_stats('bottom', stats)

        self.comparison_analyze_btn.setEnabled(True)
        self.comparison_analyze_btn.setText("Phân Tích")

    def on_error(self, error_msg, chart_name):
        """Handle error"""
        if chart_name == 'comparison':
            self.comparison_analyze_btn.setEnabled(True)
            self.comparison_analyze_btn.setText("Phân Tích")
        else:
            analyze_btn = getattr(self, f'{chart_name}_analyze_btn')
            analyze_btn.setEnabled(True)
            analyze_btn.setText("Phân Tích")

        QMessageBox.critical(self, "Lỗi", f"Không thể thực hiện dự đoán:\n{error_msg}")

    def load_initial_stats(self):
        """Load statistics from dataset on startup"""
        try:
            import pandas as pd
            from pathlib import Path
            
            # Load dataset
            data_path = Path(__file__).parent.parent / 'revenue_forecasting' / 'data' / 'daily_sales_cafe.csv'
            df = pd.read_csv(data_path)
            df['ds'] = pd.to_datetime(df['ds'])
            
            # 1. Doanh thu tích lũy (total cumulative revenue)
            total_revenue = df['y'].sum()
            stat1_text = f"${int(total_revenue):,}".replace(',', '.')
            
            # 2. Trung bình doanh thu cửa hàng (assuming all stores contribute equally)
            # Get number of stores from metadata
            stores = self.predictor.get_all_stores()
            num_stores = len(stores) if stores else 54
            avg_per_store = total_revenue / num_stores if num_stores > 0 else 0
            stat2_text = f"${int(avg_per_store):,}".replace(',', '.')
            
            # 3. Trung bình doanh thu cuối tuần (Sat-Sun)
            df['weekday'] = df['ds'].dt.dayofweek
            weekend_df = df[df['weekday'].isin([5, 6])]  # 5=Saturday, 6=Sunday
            avg_weekend = weekend_df['y'].mean() if len(weekend_df) > 0 else 0
            stat3_text = f"${int(avg_weekend):,}".replace(',', '.')
            
            # 4. Tăng trưởng (compare first 90 days vs last 90 days)
            df_sorted = df.sort_values('ds')
            first_90_avg = df_sorted.head(90)['y'].mean()
            last_90_avg = df_sorted.tail(90)['y'].mean()
            growth_rate = ((last_90_avg - first_90_avg) / first_90_avg * 100) if first_90_avg > 0 else 0
            stat4_text = f"{growth_rate:+.1f}%"
            
            # Update stat cards
            self.update_stat_card(self.stat1, stat1_text)
            self.update_stat_card(self.stat2, stat2_text)
            self.update_stat_card(self.stat3, stat3_text)
            self.update_stat_card(self.stat4, stat4_text)
            
        except Exception as e:
            print(f"Error loading initial stats: {e}")
            import traceback
            traceback.print_exc()

    def create_ai_chat_section(self):
        """Create AI Chat Assistant section"""
        group = QGroupBox("AI Chat Assistant - Hỏi đáp về Dự Báo")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #4CAF50;
                border-radius: 8px;
                margin-top: 10px;
                padding: 15px;
                background-color: #f9f9f9;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #4CAF50;
            }
        """)
        group.setMinimumHeight(500)

        layout = QVBoxLayout(group)
        layout.setContentsMargins(15, 25, 15, 15)
        layout.setSpacing(10)

        # Import AI Chat widget
        try:
            from views.admin_ai_chat_ex import AdminAIChatWidget

            # Create AI chat widget
            ai_chat_widget = AdminAIChatWidget()

            # Add to layout
            layout.addWidget(ai_chat_widget)

        except Exception as e:
            # Show error if AI Chat cannot be loaded
            error_label = QLabel(
                f"⚠️ Không thể tải AI Chat Assistant.\n\n"
                f"Lỗi: {str(e)}\n\n"
                f"Vui lòng kiểm tra:\n"
                f"1. File views/admin_ai_chat_ex.py tồn tại\n"
                f"2. OpenAI API key đã được cấu hình\n"
                f"3. Đã cài đặt: pip install openai"
            )
            error_label.setStyleSheet("color: red; padding: 20px;")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(error_label)

        return group
