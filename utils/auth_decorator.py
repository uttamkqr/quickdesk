# utils/auth_decorator.py

from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user, login_required as flask_login_required

# ✅ Decorator to ensure user is logged in
def login_required(f):
    @wraps(f)
    @flask_login_required
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function

# ✅ Decorator to enforce role-based access
def role_required(required_role):
    def decorator(f):
        @wraps(f)
        @flask_login_required
        def decorated_function(*args, **kwargs):
            if current_user.role != required_role:
                flash("❌ Unauthorized access.", "danger")
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
