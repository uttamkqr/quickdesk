from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
from extensions import db
from models import Ticket, User, Category, Comment
from utils.auth_decorator import login_required, role_required
from utils.send_email import send_email
from flask_login import current_user

enduser_bp = Blueprint('enduser', __name__, url_prefix='/enduser')

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# =======================
# 📄 Enduser Dashboard
# =======================
@enduser_bp.route('/dashboard')
@login_required
@role_required('enduser')
def dashboard():
    tickets = Ticket.query.filter_by(user_id=current_user.id).order_by(Ticket.created_at.desc()).all()
    return render_template('enduser_dashboard.html', tickets=tickets, current_user=current_user)

# =======================
# 📝 Create Ticket
# =======================
@enduser_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required('enduser')
def create_ticket():
    if request.method == 'POST':
        subject = request.form['subject']
        description = request.form['description']
        category_name = request.form['category']

        # ✅ Create or fetch category
        category = Category.query.filter_by(name=category_name).first()
        if not category:
            category = Category(name=category_name)
            db.session.add(category)
            db.session.commit()

        # ✅ Handle attachment
        attachment = None
        file = request.files.get('attachment')
        if file and allowed_file(file.filename):
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            attachment = filepath

        # ✅ Save ticket
        ticket = Ticket(
            subject=subject,
            description=description,
            category=category,
            attachment=attachment,
            user_id=current_user.id
        )
        db.session.add(ticket)
        db.session.commit()

        # ✅ Notify user
        send_email(
            subject="🆕 Ticket Submitted",
            recipient=current_user.email,
            body=f"Hi {current_user.username},\n\nYour ticket titled '{subject}' has been submitted successfully.\n\nThanks,\nQuickDesk Team"
        )

        flash("✅ Ticket submitted successfully!", "success")
        return redirect(url_for("enduser.dashboard"))

    categories = [c.name for c in Category.query.all()] or ['Technical', 'Billing', 'Account', 'General']
    return render_template("create_ticket.html", categories=categories, current_user=current_user)

# =======================
# 📄 View Ticket + Comments
# =======================
@enduser_bp.route('/ticket/<int:ticket_id>', methods=['GET', 'POST'])
@login_required
@role_required('enduser')
def ticket_detail(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    comments = Comment.query.filter_by(ticket_id=ticket_id).order_by(Comment.created_at.asc()).all()

    if ticket.user_id != current_user.id:
        flash("❌ You are not authorized to view this ticket.", "danger")
        return redirect(url_for('enduser.dashboard'))

    if request.method == 'POST':
        message = request.form['message'].strip()
        if message:
            new_comment = Comment(ticket_id=ticket.id, user_id=current_user.id, message=message)
            db.session.add(new_comment)
            db.session.commit()
            flash("✅ Comment added.", "success")
            return redirect(url_for('enduser.ticket_detail', ticket_id=ticket.id))

    return render_template("ticket_detail.html", ticket=ticket, comments=comments, current_user=current_user)
