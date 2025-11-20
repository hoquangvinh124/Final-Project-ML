"""
Configuration file for Coffee Shop Application
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Database Configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', '1234'),
    'database': os.getenv('DB_NAME', 'coffee_shop'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'charset': 'utf8mb4',
    'autocommit': True
}

# Application Settings
APP_NAME = "Coffee Shop"
APP_VERSION = "1.0.0"

# UI Paths
UI_DIR = BASE_DIR / 'ui'
UI_GENERATED_DIR = BASE_DIR / 'ui_generated'
RESOURCES_DIR = BASE_DIR / 'resources'
STYLES_DIR = RESOURCES_DIR / 'styles'
IMAGES_DIR = RESOURCES_DIR / 'images'
ICONS_DIR = RESOURCES_DIR / 'icons'

# Session Settings
SESSION_TIMEOUT = 3600  # 1 hour in seconds
REMEMBER_ME_DURATION = 2592000  # 30 days in seconds

# OTP Settings
OTP_EXPIRY_MINUTES = 5
OTP_LENGTH = 6

# Loyalty Points Settings
POINTS_PER_VND = 0.01  # 1 point per 100 VND
BRONZE_THRESHOLD = 0
SILVER_THRESHOLD = 1000
GOLD_THRESHOLD = 5000

# Order Settings
DEFAULT_DELIVERY_FEE = 20000  # VND
FREE_SHIPPING_THRESHOLD = 200000  # VND
ORDER_TIMEOUT_MINUTES = 30

# Payment Gateway Settings (Placeholder for future integration)
MOMO_CONFIG = {
    'partner_code': 'YOUR_MOMO_PARTNER_CODE',
    'access_key': 'YOUR_MOMO_ACCESS_KEY',
    'secret_key': 'YOUR_MOMO_SECRET_KEY',
    'endpoint': 'https://test-payment.momo.vn/v2/gateway/api/create'
}

ZALOPAY_CONFIG = {
    'app_id': 'YOUR_ZALOPAY_APP_ID',
    'key1': 'YOUR_ZALOPAY_KEY1',
    'key2': 'YOUR_ZALOPAY_KEY2',
    'endpoint': 'https://sb-openapi.zalopay.vn/v2/create'
}

# API Settings (for future mobile integration)
API_TIMEOUT = 30  # seconds

# Image Upload Settings
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif']

# Pagination
ITEMS_PER_PAGE = 12
REVIEWS_PER_PAGE = 10

# Cache Settings
ENABLE_CACHE = True
CACHE_DURATION = 300  # 5 minutes

USE_MODERN_THEME = True   # Set to False for classic theme
MODERN_STYLESHEET = STYLES_DIR / 'modern_style.qss'
CLASSIC_STYLESHEET = STYLES_DIR / 'style.qss'

# AI Agent Settings
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')  # Set your OpenAI API key here or in .env
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')  # or 'gpt-3.5-turbo' for faster/cheaper
AI_AGENT_TEMPERATURE = 0.1  # Low temperature for more deterministic SQL generation
AI_AGENT_MAX_TOKENS = 2000