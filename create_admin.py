from app import app        # ✅ import app from the right file
from models import db, User
from werkzeug.security import generate_password_hash

# 🔑 Your desired admin credentials
admin_username = 'admin'
admin_email = 'admin@example.com'
admin_password = 'admin123'

with app.app_context():
    if User.query.filter_by(username=admin_username).first():
        print("❌ Admin user already exists.")
    else:
        hashed_password = generate_password_hash(admin_password)
        admin = User(username=admin_username, email=admin_email, password=hashed_password, role='admin')
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin user created successfully.")
