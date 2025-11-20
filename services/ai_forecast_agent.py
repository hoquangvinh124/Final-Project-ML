"""
AI Forecast Agent - Smart revenue forecasting assistant
Uses Prophet ML models + OpenAI GPT for insights and recommendations
NO database queries - all predictions from ML models directly
"""
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from openai import OpenAI
from utils.config import OPENAI_API_KEY, OPENAI_MODEL

logger = logging.getLogger(__name__)


class AIForecastAgent:
    """
    AI Agent that:
    1. Gets predictions from Prophet ML models directly
    2. Sends forecast data to OpenAI for analysis
    3. Provides insights and recommendations in Vietnamese
    4. No database interaction - pure ML model inference
    """

    def __init__(self, api_key: str = None):
        """Initialize AI Forecast Agent"""
        self.api_key = api_key or OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY in config or .env")

        self.client = OpenAI(api_key=self.api_key)
        self.model = OPENAI_MODEL or "gpt-4o-mini"

        # Load Prophet predictor
        try:
            from revenue_forecasting.predictor import get_predictor
            self.predictor = get_predictor()
            logger.info("✓ Prophet ML Predictor loaded successfully")
        except Exception as e:
            logger.error(f"✗ Failed to load Prophet predictor: {e}")
            raise RuntimeError(f"Cannot initialize AI Agent without ML models: {e}")

        # Conversation history per session
        self.sessions = {}

    def process_query(self, question: str, session_id: str = "default") -> Dict[str, Any]:
        """
        Process natural language question about revenue forecasting
        
        Args:
            question: User's question in Vietnamese
            session_id: Session ID for conversation tracking
            
        Returns:
            Dict with success, ai_response, forecast_data, etc.
        """
        start_time = datetime.now()

        try:
            # Initialize session if needed
            if session_id not in self.sessions:
                self.sessions[session_id] = []

            # Step 1: Check if question is about revenue forecasting
            if not self._is_forecast_question(question):
                # Just chat, no forecast needed
                ai_response = self._chat_with_openai(question, session_id)
                
                exec_time = int((datetime.now() - start_time).total_seconds() * 1000)
                
                self.sessions[session_id].append({
                    'question': question,
                    'response': ai_response,
                    'timestamp': datetime.now().isoformat()
                })
                
                return {
                    'success': True,
                    'ai_response': ai_response,
                    'forecast_data': None,
                    'forecast_type': 'chat',
                    'execution_time': exec_time
                }

            # Step 2: Understand question and determine what forecast to get
            forecast_request = self._parse_question(question)

            # Step 3: Get forecast data from Prophet models
            forecast_data = self._get_forecast_data(forecast_request)

            # Step 4: Send to OpenAI for analysis
            ai_response = self._analyze_with_openai(question, forecast_data, session_id)

            # Calculate execution time
            exec_time = int((datetime.now() - start_time).total_seconds() * 1000)

            # Store in session history
            self.sessions[session_id].append({
                'question': question,
                'response': ai_response,
                'forecast_data': forecast_data,
                'timestamp': datetime.now().isoformat()
            })

            return {
                'success': True,
                'ai_response': ai_response,
                'forecast_data': forecast_data,
                'forecast_type': forecast_request['type'],
                'execution_time': exec_time
            }

        except Exception as e:
            logger.error(f"Error processing query: {e}")
            import traceback
            traceback.print_exc()

            return {
                'success': False,
                'error': f"Lỗi khi xử lý câu hỏi: {str(e)}",
                'execution_time': int((datetime.now() - start_time).total_seconds() * 1000)
            }

    def _is_forecast_question(self, question: str) -> bool:
        """Check if question is about revenue forecasting"""
        question_lower = question.lower()
        
        # Keywords indicating forecast/revenue questions
        forecast_keywords = [
            'doanh thu', 'donh thu', 'revenue', 'sales', 'bán hàng',
            'dự đoán', 'dự báo', 'forecast', 'predict',
            'tuần sau', 'tháng sau', 'ngày mai', 'năm sau', 'next week', 'next month',
            'cửa hàng', 'store', 'shop',
            'top', 'cao nhất', 'thấp nhất', 'tốt nhất', 'kém nhất',
            'tăng', 'giảm', 'tăng trưởng', 'growth',
            'bao nhiêu', 'how much', 'mức nào',
            'tồn tại', 'còn lại', 'tương lai', 'future',
            'tới', 'đến', 'đến năm', 'tới năm'
        ]
        
        # Check for year numbers (2024-2099)
        import re
        year_pattern = re.search(r'\b(20[2-9]\d)\b', question_lower)
        if year_pattern:
            return True
        
        return any(keyword in question_lower for keyword in forecast_keywords)

    def _chat_with_openai(self, question: str, session_id: str) -> str:
        """Simple chat without forecast - for general questions"""
        history = self.sessions.get(session_id, [])[-5:]
        
        messages = [
            {
                "role": "system",
                "content": """Bạn là AI Assistant vui tính và hài hước, hỗ trợ phân tích doanh thu cho chuỗi cửa hàng cà phê.

TÍNH CÁCH:
- Trả lời vui vẻ, hài hước nhưng không quá lố
- Thỉnh thoảng dùng emoji phù hợp 
- Có thể "cà khịa" nhẹ nhàng người dùng
- Vẫn chuyên nghiệp khi nói về công việc

Nếu người dùng hỏi về dự đoán doanh thu, nhắc họ hỏi cụ thể hơn theo kiểu thân mật.
Với câu hỏi nhảm nhí/vui vui, trả lời hài hước nhưng ngắn gọn (1-2 câu).

Ví dụ:
- "Tôi đẹp chai không?" → "Đẹp thì đẹp đấy, nhưng doanh thu tuần sau quan trọng hơn nha 😄"
- "Hôm nay ăn gì?" → "Ăn cà phê với bánh, rồi xem doanh thu cửa hàng đi! ☕"

Luôn dùng tiếng Việt thân mật."""
            }
        ]
        
        # Add history
        for msg in history:
            messages.append({"role": "user", "content": msg['question']})
            messages.append({"role": "assistant", "content": msg['response']})
        
        # Add current question
        messages.append({"role": "user", "content": question})
        
        # Call OpenAI
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                service_tier="priority"
            )
            
            result = response.choices[0].message.content
            if result:
                return result.strip()
            else:
                logger.warning("OpenAI returned empty response for chat")
                return "Xin lỗi, tôi không thể trả lời câu hỏi này. Hãy thử lại nhé! 😊"
                
        except Exception as e:
            logger.error(f"OpenAI chat error: {e}")
            return f"Lỗi khi xử lý câu hỏi: {str(e)}"

    def _parse_question(self, question: str) -> Dict[str, Any]:
        """
        Parse question to determine what type of forecast to get
        Uses simple keyword matching (fast, no OpenAI call needed)
        """
        question_lower = question.lower()
        import re

        # Default values
        forecast_type = "overall"  # overall, store, top_stores, bottom_stores
        days = 30
        store_nbr = None
        top_n = 10

        # Check for specific year (e.g., "2035", "2030")
        year_match = re.search(r'\b(20[2-9]\d)\b', question)
        if year_match:
            target_year = int(year_match.group(1))
            current_year = datetime.now().year
            years_ahead = target_year - current_year
            if years_ahead > 0:
                days = min(years_ahead * 365, 3650)  # Cap at 10 years (3650 days)

        # Detect time period
        if any(word in question_lower for word in ['tuần', 'week', '7 ngày']):
            days = 7
        elif any(word in question_lower for word in ['tháng', 'month', '30 ngày']):
            days = 30
        elif any(word in question_lower for word in ['quý', 'quarter', '90 ngày']):
            days = 90
        elif any(word in question_lower for word in ['năm', 'year', '365 ngày']) and not year_match:
            days = 365

        # Detect forecast type
        if any(word in question_lower for word in ['cửa hàng cao nhất', 'top cửa hàng', 'tốt nhất', 'cao nhất']):
            forecast_type = "top_stores"
        elif any(word in question_lower for word in ['cửa hàng thấp nhất', 'kém nhất', 'thấp nhất', 'yếu nhất']):
            forecast_type = "bottom_stores"
        elif any(word in question_lower for word in ['cửa hàng', 'store', 'shop']):
            # Try to extract store number (exclude year numbers)
            numbers = re.findall(r'\b(\d{1,2})\b', question)  # 1-2 digit numbers only
            if numbers:
                store_nbr = int(numbers[0])
                forecast_type = "store"
            else:
                forecast_type = "store_list"
        else:
            forecast_type = "overall"

        # Detect top N
        top_matches = re.findall(r'top\s*(\d+)|(\d+)\s*cửa hàng', question_lower)
        if top_matches:
            for match in top_matches:
                n = int(match[0] or match[1])
                if 1 <= n <= 50:
                    top_n = n

        return {
            'type': forecast_type,
            'days': days,
            'store_nbr': store_nbr,
            'top_n': top_n
        }

    def _get_forecast_data(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Get forecast data from Prophet models"""
        forecast_type = request['type']
        days = request['days']

        if forecast_type == "overall":
            # Overall system forecast
            result = self.predictor.predict_overall(days=days)
            return {
                'type': 'overall',
                'days': days,
                'summary': result['summary'],
                'forecasts': result['forecasts'][:7],  # First 7 days for context
                'total_days': len(result['forecasts'])
            }

        elif forecast_type == "store":
            # Specific store forecast
            store_nbr = request['store_nbr']
            result = self.predictor.predict_store(store_nbr=store_nbr, days=days)
            return {
                'type': 'store',
                'store_nbr': store_nbr,
                'store_info': {
                    'city': result['city'],
                    'type': result['type']
                },
                'days': days,
                'forecast_avg_daily': result['forecast_avg_daily'],
                'total_forecast': result['total_forecast'],
                'growth_percent': result['growth_percent'],
                'forecasts': result['forecasts'][:7]
            }

        elif forecast_type == "top_stores":
            # Top performing stores
            result = self.predictor.get_top_stores(n=request['top_n'])
            return {
                'type': 'top_stores',
                'n': request['top_n'],
                'stores': result['stores'][:10]  # Max 10 for context
            }

        elif forecast_type == "bottom_stores":
            # Bottom performing stores
            result = self.predictor.get_bottom_stores(n=request['top_n'])
            return {
                'type': 'bottom_stores',
                'n': request['top_n'],
                'stores': result['stores'][:10]
            }

        elif forecast_type == "store_list":
            # All stores overview
            stores = self.predictor.get_all_stores()
            return {
                'type': 'store_list',
                'total_stores': len(stores),
                'stores': stores[:20]  # First 20 for context
            }

        else:
            raise ValueError(f"Unknown forecast type: {forecast_type}")

    def _analyze_with_openai(self, question: str, forecast_data: Dict[str, Any], session_id: str) -> str:
        """Send forecast data to OpenAI for analysis and insights"""

        # Build context from forecast data
        data_context = self._format_forecast_context(forecast_data)

        # Get conversation history
        history = self.sessions.get(session_id, [])[-5:]  # Last 5 exchanges

        # Build messages
        messages = [
            {
                "role": "system",
                "content": """Bạn là AI Assistant chuyên phân tích dự đoán doanh thu cho chuỗi cửa hàng cà phê.

NHIỆM VỤ:
- Phân tích dữ liệu dự đoán từ ML models (Prophet)
- Đưa ra insights và recommendations bằng tiếng Việt
- Trả lời ngắn gọn, súc tích (2-4 câu)
- Tập trung vào con số cụ thể và hành động khuyến nghị

CÁCH TRẢ LỜI:
1. Nêu con số dự đoán chính (tổng doanh thu, trung bình/ngày)
2. So sánh với mức trung bình (cao/thấp hơn bao nhiêu)
3. Đưa 3-4 khuyến nghị cụ thể. Ngoài ra phải bổ sung thêm bối cảnh liên quan như:
- Xu hướng hiện tại trong ngành
- Best practices
- Hành vi người dùng hoặc benchmark phổ biến
- Các yếu tố môi trường ảnh hưởng (nếu có)

Đơn vị tiền tệ: $ (USD)
Luôn format số với dấu chấm phân cách hàng nghìn (VD: 1.234.567 $)"""
            }
        ]

        # Add history
        for item in history:
            messages.append({"role": "user", "content": item['question']})
            messages.append({"role": "assistant", "content": item['response']})

        # Add current question with data
        user_message = f"""Câu hỏi: {question}

Dữ liệu dự đoán:
{data_context}

Hãy phân tích và trả lời câu hỏi."""

        messages.append({"role": "user", "content": user_message})

        # Call OpenAI
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                service_tier="priority"
            )
            result = response.choices[0].message.content
            if result:
                return result.strip()
            else:
                logger.warning("OpenAI returned empty response for forecast analysis")
                return "Dữ liệu dự báo đã được tạo nhưng không thể phân tích. Vui lòng thử lại."

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return f"Lỗi khi phân tích dữ liệu: {str(e)}"

    def _format_forecast_context(self, data: Dict[str, Any]) -> str:
        """Format forecast data for OpenAI context"""
        if data['type'] == 'overall':
            summary = data['summary']
            return f"""Loại: Dự đoán tổng thể hệ thống
Thời gian: {data['days']} ngày tới
Tổng doanh thu dự đoán: ${summary['total_forecast']:,.2f}
Trung bình/ngày: ${summary['avg_daily_forecast']:,.2f}
Doanh thu thấp nhất: ${summary['min_forecast']:,.2f}
Doanh thu cao nhất: ${summary['max_forecast']:,.2f}
Độ lệch chuẩn: ${summary['std_forecast']:,.2f}

7 ngày đầu tiên:
{self._format_forecasts(data['forecasts'])}"""

        elif data['type'] == 'store':
            return f"""Loại: Dự đoán cửa hàng #{data['store_nbr']}
Thành phố: {data['store_info']['city']}
Loại cửa hàng: {data['store_info']['type']}
Thời gian: {data['days']} ngày tới
Tổng doanh thu dự đoán: ${data['total_forecast']:,.2f}
Trung bình/ngày: ${data['forecast_avg_daily']:,.2f}
Tăng trưởng so với lịch sử: {data['growth_percent']:+.1f}%

7 ngày đầu tiên:
{self._format_forecasts(data['forecasts'])}"""

        elif data['type'] == 'top_stores':
            stores_text = "\n".join([
                f"  #{s['store_nbr']} ({s['city']}): ${s['forecast_avg_daily']:,.2f}/ngày, {s['growth_percent']:+.1f}%"
                for s in data['stores']
            ])
            return f"""Loại: Top {data['n']} cửa hàng tốt nhất
{stores_text}"""

        elif data['type'] == 'bottom_stores':
            stores_text = "\n".join([
                f"  #{s['store_nbr']} ({s['city']}): ${s['forecast_avg_daily']:,.2f}/ngày, {s['growth_percent']:+.1f}%"
                for s in data['stores']
            ])
            return f"""Loại: Top {data['n']} cửa hàng yếu nhất
{stores_text}"""

        elif data['type'] == 'store_list':
            stores_text = "\n".join([
                f"  #{s['store_nbr']} ({s['city']}): ${s['forecast_avg_daily']:,.2f}/ngày"
                for s in data['stores']
            ])
            return f"""Loại: Danh sách cửa hàng
Tổng số: {data['total_stores']} cửa hàng
20 cửa hàng đầu tiên:
{stores_text}"""

        return str(data)

    def _format_forecasts(self, forecasts: list) -> str:
        """Format forecast list for display"""
        lines = []
        for f in forecasts:
            lines.append(f"  {f['date']}: ${f['forecast']:,.2f}")
        return "\n".join(lines)

    def get_suggested_questions(self) -> list:
        """Get suggested questions for user"""
        return [
            "Doanh thu tuần tới dự đoán bao nhiêu?",
            "Cửa hàng nào có doanh thu cao nhất?",
            "Top 5 cửa hàng tốt nhất",
            "Dự đoán doanh thu tháng tới",
            "Cửa hàng nào cần cải thiện?",
            "Tổng doanh thu 30 ngày tới"
        ]

    def clear_session(self, session_id: str):
        """Clear conversation history for session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
