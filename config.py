import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY = 'supersecretkey'
    
    # ✅ Replace this:
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///quickdesk.db'
    
    # ✅ With your MySQL connection URI:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:Agrawal%40%403170@localhost/quickdesk'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ✉️ Email config
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('EMAIL_USER')
    MAIL_PASSWORD = os.getenv('EMAIL_PASS')
