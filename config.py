import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Load environment variables from .env file
load_dotenv()

class Config:
    # ============================================
    # Application Security
    # ============================================
    SECRET_KEY = os.getenv('SECRET_KEY', 'supersecretkey')

    # ============================================
    # Database Configuration
    # Reads from .env file:
    # - DB_USER = root
    # - DB_PASSWORD = 
    # - DB_HOST = localhost
    # - DB_NAME = quickdesk
    # ============================================
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_NAME = os.getenv('DB_NAME', 'quickdesk')

    # URL encode the password to handle special characters like @, !, etc.
    # Password:  -> 
    DB_PASSWORD_ENCODED = quote_plus(DB_PASSWORD) if DB_PASSWORD else ''

    # Build MySQL connection string with encoded password
    # Format: mysql+pymysql://root:@localhost/quickdesk
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD_ENCODED}@{DB_HOST}/{DB_NAME}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ============================================
    # Email Configuration (Gmail)
    # Reads from .env file:
    # - EMAIL_USER = 
    # - EMAIL_PASS = 
    # ============================================
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('EMAIL_USER')
    MAIL_PASSWORD = os.getenv('EMAIL_PASS')
