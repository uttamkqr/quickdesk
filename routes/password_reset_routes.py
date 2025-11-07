# routes/password_reset_routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import User, db
from werkzeug.security import generate_password_hash
from utils.send_email import send_email

bp = Blueprint('password_reset', __name__)


@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Request password reset"""
    if request.method == 'POST':
        email = request.form['email'].strip()
        user = User.query.filter_by(email=email).first()

        if user:
            # Generate reset token
            token = user.generate_reset_token()
            db.session.commit()

            # Create reset link
            reset_link = url_for('password_reset.reset_password',
                                 token=token, _external=True)

            # Send email
            send_email(
                subject="🔐 Password Reset Request - QuickDesk",
                recipient=user.email,
                body=f"""
Hello {user.username},

You requested a password reset for your QuickDesk account.

Click the link below to reset your password:
{reset_link}

This link will expire in 1 hour.

If you didn't request this, please ignore this email.

Regards,
QuickDesk Team
                """.strip()
            )

            flash("📧 Password reset instructions have been sent to your email.", "info")
        else:
            # Don't reveal if email exists or not (security)
            flash("📧 If that email exists, password reset instructions have been sent.", "info")

        return redirect(url_for('auth.login'))

    return render_template('forgot_password.html')


@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password with token"""
    user = User.query.filter_by(reset_token=token).first()

    if not user or not user.verify_reset_token(token):
        flash("❌ Invalid or expired reset link.", "danger")
        return redirect(url_for('password_reset.forgot_password'))

    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("❌ Passwords do not match.", "danger")
            return render_template('reset_password.html', token=token)

        if len(password) < 6:
            flash("❌ Password must be at least 6 characters long.", "danger")
            return render_template('reset_password.html', token=token)

        # Update password
        user.password = generate_password_hash(password)
        user.clear_reset_token()
        db.session.commit()

        # Send confirmation email
        send_email(
            subject="✅ Password Changed Successfully - QuickDesk",
            recipient=user.email,
            body=f"""
Hello {user.username},

Your password has been changed successfully.

If you didn't make this change, please contact support immediately.

Regards,
QuickDesk Team
            """.strip()
        )

        flash("✅ Password reset successful! Please log in with your new password.", "success")
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html', token=token)
