from flask import Flask, redirect, url_for
from config import Config
from extensions import db, mail, login_manager
from models import User
from routes.auth_routes import bp as auth_bp
from routes.user_routes import bp as user_bp
from routes.agent_routes import bp as agent_bp
from routes.admin_routes import bp as admin_bp
from routes.enduser import enduser_bp
from routes.password_reset_routes import bp as password_reset_bp

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.config.from_object("config.Config")

# ✅ Initialize extensions
db.init_app(app)
mail.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# ✅ User loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ✅ Context processor for notifications
@app.context_processor
def inject_notifications():
    from flask_login import current_user
    from utils.notification_helper import get_unread_notifications

    notifications = []
    unread_count = 0

    if current_user.is_authenticated:
        notifications = get_unread_notifications(current_user.id)
        unread_count = len(notifications)

    return dict(
        notifications=notifications,
        unread_count=unread_count
    )


# ✅ Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(agent_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(enduser_bp)
app.register_blueprint(password_reset_bp)

@app.route('/')
def index():
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(debug=True)
