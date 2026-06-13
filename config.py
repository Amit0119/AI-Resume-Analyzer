import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Database
DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'analyzer.db')
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# API
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', '8000'))
API_RELOAD = os.getenv('API_RELOAD', 'True').lower() == 'true'

# Security
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# AI/ML
GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
MODEL_NAME = "all-MiniLM-L6-v2"
DEFAULT_SENSITIVITY = 0.5

# File upload
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'pdf'}

# Analysis
MAX_SKILLS_EXTRACT = 20
MIN_SKILL_LENGTH = 2

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Environment
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
DEBUG = ENVIRONMENT == 'development'