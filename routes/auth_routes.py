from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from models import User

bp = Blueprint('auth', __name__)

# ✅ Register Route
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        role = request.form['role'].strip()

        # ✅ Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("⚠️ Email already registered. Please log in.", "warning")
            return redirect(url_for('auth.login'))

        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_pw, role=role)
        db.session.add(new_user)
        db.session.commit()

        flash("✅ Registration successful! Please log in.", "success")
        return redirect(url_for('auth.login'))

    return render_template('register.html')


# ✅ Login Route
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("✅ Login successful!", "success")

            # ✅ Redirect based on role
            if user.role == 'admin':
                return redirect(url_for('admin.admin_dashboard'))
            elif user.role == 'agent':
                return redirect(url_for('agent.agent_dashboard'))
            elif user.role == 'enduser':
                return redirect(url_for('enduser.dashboard'))
            else:
                flash("❌ Unknown role. Contact admin.", "danger")
                return redirect(url_for('auth.login'))
        else:
            flash("❌ Invalid email or password.", "danger")

    return render_template('login.html')


# ✅ Logout Route
@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("👋 You have been logged out.", "info")
    return redirect(url_for('auth.login'))
