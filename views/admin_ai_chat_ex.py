"""
Admin AI Chat Widget - Extended Logic
AI-powered chat interface for querying predictions and getting insights
Uses Prophet ML models directly (no database queries)
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QLineEdit, QScrollArea, QFrame, QMessageBox,
    QListWidget, QListWidgetItem, QSplitter, QProgressDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QTextCursor, QColor
import json
from datetime import datetime
from typing import Optional
import logging

from services.ai_forecast_agent import AIForecastAgent

logger = logging.getLogger(__name__)


class AIQueryThread(QThread):
    """Background thread for AI query processing"""
    result_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, agent: AIForecastAgent, question: str, session_id: str):
        super().__init__()
        self.agent = agent
        self.question = question
        self.session_id = session_id

    def run(self):
        """Run AI query in background"""
        try:
            result = self.agent.process_query(self.question, self.session_id)
            self.result_ready.emit(result)
        except Exception as e:
            logger.error(f"Error in AI query thread: {str(e)}")
            self.error_occurred.emit(str(e))


class ChatMessageWidget(QFrame):
    """Widget to display a single chat message"""

    def __init__(self, message: str, is_user: bool, parent=None):
        super().__init__(parent)
        self.setup_ui(message, is_user)

    def setup_ui(self, message: str, is_user: bool):
        """Setup message UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        # Message container
        message_frame = QFrame()
        message_frame.setFrameShape(QFrame.Shape.StyledPanel)

        if is_user:
            # User message - align right, blue background
            message_frame.setStyleSheet("""
                QFrame {
                    background-color: #c7a17a;
                    color: white;
                    border-radius: 10px;
                    padding: 10px;
                }
            """)
            message_frame.setMaximumWidth(1000)
            layout.addStretch()
        else:
            # AI message - align left, gray background
            message_frame.setStyleSheet("""
                QFrame {
                    background-color: #f0f0f0;
                    color: #2c2c2c;
                    border-radius: 10px;
                    padding: 10px;
                }
            """)
            message_frame.setMaximumWidth(1000)

        message_layout = QVBoxLayout(message_frame)

        # Message text
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setTextFormat(Qt.TextFormat.RichText)
        message_label.setStyleSheet("background-color: transparent; font-size: 17px; font-weight: 500;")
        message_layout.addWidget(message_label)

        layout.addWidget(message_frame)

        if is_user:
            pass  # Already stretched
        else:
            layout.addStretch()


class AdminAIChatWidget(QWidget):
    """AI Chat widget for admin panel"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialize AI Agent
        try:
            self.agent = AIForecastAgent()
            self.agent_ready = True
        except Exception as e:
            logger.error(f"Failed to initialize AI Agent: {str(e)}")
            self.agent = None
            self.agent_ready = False

        # Session ID for tracking conversation
        self.session_id = f"session_{int(datetime.now().timestamp())}"

        # Current query thread
        self.query_thread: Optional[AIQueryThread] = None

        self.setup_ui()

        if not self.agent_ready:
            self.show_error_message("Lỗi: Không thể khởi tạo AI Agent. Vui lòng kiểm tra:\n1. Prophet models đã được train\n2. OpenAI API key đã cấu hình")

    def setup_ui(self):
        """Setup UI components"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header
        header_layout = QHBoxLayout()

        title_label = QLabel("AI Analytics Assistant")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Status indicator
        self.status_label = QLabel("● Sẵn sàng" if self.agent_ready else "● Lỗi")
        self.status_label.setStyleSheet(
            "color: green; font-weight: bold;" if self.agent_ready else "color: red; font-weight: bold;"
        )
        header_layout.addWidget(self.status_label)

        # New session button
        new_session_btn = QPushButton("Phiên mới")
        new_session_btn.clicked.connect(self.start_new_session)
        new_session_btn.setStyleSheet("""
            QPushButton {
                background-color: #c7a17a;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #b08968;
            }
        """)
        header_layout.addWidget(new_session_btn)

        main_layout.addLayout(header_layout)

        # Chat area (full width - no suggestions panel)
        chat_panel_layout = QVBoxLayout()
        chat_panel_layout.setContentsMargins(0, 0, 0, 0)

        # Chat display area
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setMinimumHeight(600)
        self.chat_scroll.setStyleSheet("""
            QScrollArea {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
        """)

        # Chat container
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_layout.setSpacing(10)

        self.chat_scroll.setWidget(self.chat_container)
        chat_panel_layout.addWidget(self.chat_scroll)

        # Input area
        input_layout = QHBoxLayout()

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Nhập câu hỏi của bạn... (ví dụ: Doanh thu tuần tới dự đoán bao nhiêu?)")
        self.input_field.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #c7a17a;
            }
        """)
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field, stretch=1)

        self.send_button = QPushButton("Gửi")
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #c7a17a;
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #b08968;
            }
            QPushButton:pressed {
                background-color: #9a7a5a;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)

        chat_panel_layout.addLayout(input_layout)

        main_layout.addLayout(chat_panel_layout)

        # Welcome message
        self.add_ai_message(
            "Xin chào! Tôi là AI Forecast Assistant. "
            "Tôi sử dụng Prophet ML models để dự đoán doanh thu và đưa ra phân tích. "
            "Hãy hỏi tôi về dự đoán doanh thu, top cửa hàng, hay xu hướng kinh doanh! 😊"
        )

    # Removed suggestions panel - full width chat interface

    def send_message(self):
        """Send message to AI"""
        if not self.agent_ready:
            QMessageBox.warning(self, "Lỗi", "AI Agent chưa sẵn sàng. Vui lòng kiểm tra cấu hình.")
            return

        question = self.input_field.text().strip()
        if not question:
            return

        # Disable input while processing
        self.input_field.setEnabled(False)
        self.send_button.setEnabled(False)
        self.status_label.setText("⏳ Đang xử lý...")
        self.status_label.setStyleSheet("color: orange; font-weight: bold;")

        # Add user message
        self.add_user_message(question)

        # Clear input
        self.input_field.clear()

        # Process query in background thread
        self.query_thread = AIQueryThread(self.agent, question, self.session_id)
        self.query_thread.result_ready.connect(self.on_result_ready)
        self.query_thread.error_occurred.connect(self.on_error_occurred)
        self.query_thread.start()

    def on_result_ready(self, result: dict):
        """Handle AI response"""
        # Re-enable input
        self.input_field.setEnabled(True)
        self.send_button.setEnabled(True)
        self.status_label.setText("● Sẵn sàng")
        self.status_label.setStyleSheet("color: green; font-weight: bold;")

        if result.get('success'):
            # Format response
            response_html = self.format_ai_response(result)
            self.add_ai_message(response_html)
        else:
            error_msg = result.get('error', 'Không thể xử lý câu hỏi này.')
            self.add_ai_message(f"❌ <b>Lỗi:</b> {error_msg}")

    def on_error_occurred(self, error: str):
        """Handle error"""
        self.input_field.setEnabled(True)
        self.send_button.setEnabled(True)
        self.status_label.setText("● Lỗi")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")

        self.add_ai_message(f"❌ <b>Lỗi:</b> {error}")

    def format_ai_response(self, result: dict) -> str:
        """Format AI response with HTML"""
        html = f"<div style='line-height: 1.6;'>"

        # AI Response (main content)
        ai_response = result.get('ai_response', '')
        if ai_response:
            # Replace newlines with <br> for proper formatting
            formatted_response = ai_response.replace('\n', '<br>')
            html += f"<p>{formatted_response}</p>"

        # Forecast type indicator
        forecast_type = result.get('forecast_type', '')
        type_labels = {
            'overall': '🌐 Tổng thể hệ thống',
            'store': '🏪 Cửa hàng cụ thể',
            'top_stores': '🏆 Top cửa hàng tốt nhất',
            'bottom_stores': '⚠️ Top cửa hàng yếu nhất',
            'store_list': '📋 Danh sách cửa hàng'
        }
        if forecast_type in type_labels:
            html += f"<p style='margin-top: 8px; font-size: 11px; color: #666;'>{type_labels[forecast_type]}</p>"

        # Execution time
        exec_time = result.get('execution_time', 0)
        if exec_time:
            html += f"<p style='margin-top: 5px; font-size: 10px; color: #999;'>⏱️ {exec_time}ms</p>"

        html += "</div>"
        return html

    def add_user_message(self, message: str):
        """Add user message to chat"""
        msg_widget = ChatMessageWidget(message, is_user=True)
        self.chat_layout.addWidget(msg_widget)
        self.scroll_to_bottom()

    def add_ai_message(self, message: str):
        """Add AI message to chat"""
        msg_widget = ChatMessageWidget(message, is_user=False)
        self.chat_layout.addWidget(msg_widget)
        self.scroll_to_bottom()

    def scroll_to_bottom(self):
        """Scroll chat to bottom"""
        scrollbar = self.chat_scroll.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def start_new_session(self):
        """Start a new chat session"""
        reply = QMessageBox.question(
            self,
            "Phiên mới",
            "Bạn có muốn bắt đầu phiên chat mới không? Lịch sử chat hiện tại sẽ bị xóa khỏi màn hình.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Clear chat display
            while self.chat_layout.count():
                item = self.chat_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            # Create new session ID
            self.session_id = f"session_{int(datetime.now().timestamp())}"

            # Add welcome message
            self.add_ai_message(
                "Xin chào! Đây là phiên chat mới. "
                "Tôi sẵn sàng giúp bạn phân tích dữ liệu dự đoán doanh thu. "
                "Hãy hỏi tôi bất kỳ điều gì! 😊"
            )

    def show_error_message(self, message: str):
        """Show error message"""
        QMessageBox.critical(self, "Lỗi", message)
