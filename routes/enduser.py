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
        category_id = request.form.get('category')
        priority = request.form.get('priority', 'Medium')

        # ✅ Get category
        category = Category.query.get(category_id)
        if not category:
            flash("❌ Invalid category selected.", "danger")
            return redirect(url_for("enduser.create_ticket"))

        # ✅ Handle attachment
        attachment = None
        file = request.files.get('attachment')
        if file and allowed_file(file.filename):
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            attachment = filepath

        # ✅ Save ticket with priority (NOT assigned yet - admin will assign)
        ticket = Ticket(
            subject=subject,
            description=description,
            category_id=category.id,
            priority=priority,
            attachment=attachment,
            user_id=current_user.id,
            assigned_to=None  # Initially not assigned - admin will assign
        )
        db.session.add(ticket)
        db.session.commit()

        # ✅ Notify user that ticket is created
        send_email(
            subject="🆕 Ticket Submitted Successfully",
            recipient=current_user.email,
            body=f"""Hi {current_user.username},

Your ticket has been submitted successfully!

Ticket Details:
- Ticket ID: #{ticket.id}
- Subject: {subject}
- Priority: {priority}
- Category: {category.name}

Your ticket is pending assignment. An admin will review and assign it to an agent shortly.

Thanks,
QuickDesk Team"""
        )

        # 🆕 Notify ALL ADMINS about new ticket for assignment
        admins = User.query.filter_by(role='admin').all()
        for admin in admins:
            if admin.email:
                send_email(
                    subject=f"🆕 New Ticket #{ticket.id} - Needs Assignment",
                    recipient=admin.email,
                    body=f"""Hello {admin.username},

A new ticket has been created and needs to be assigned to an agent.

Ticket Details:
- Ticket ID: #{ticket.id}
- Subject: {subject}
- Priority: {priority} {'🔴' if priority == 'Critical' else '🟠' if priority == 'High' else '🟡' if priority == 'Medium' else '🟢'}
- Category: {category.name}
- Created by: {current_user.username} ({current_user.email})
- Description: {description[:100]}{'...' if len(description) > 100 else ''}

Status: ⏳ UNASSIGNED - Waiting for Admin Assignment

Please login to the admin dashboard to review and assign this ticket to an appropriate agent.

Login URL: http://localhost:5000/login

Best regards,
QuickDesk System"""
                )

        flash("✅ Ticket submitted successfully! Admin will assign it to an agent soon.", "success")
        return redirect(url_for("enduser.dashboard"))

    # GET request - show form with categories
    categories = Category.query.all()
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


# View Ticket Details for End User
@enduser_bp.route('/view/<int:ticket_id>', methods=['GET', 'POST'])
@login_required
@role_required('enduser')
def view_ticket(ticket_id):
    if current_user.role != 'enduser':
        return "Access Denied", 403

    ticket = Ticket.query.get_or_404(ticket_id)

    # Ensure user can only view their own tickets
    if ticket.user_id != current_user.id:
        flash("⛔ You can only view your own tickets.", "danger")
        return redirect(url_for('enduser.dashboard'))

    comments = Comment.query.filter_by(ticket_id=ticket_id, is_internal=False).order_by(Comment.created_at.asc()).all()

    # Handle POST request for adding comment
    if request.method == 'POST':
        message = request.form.get('message', '').strip()

        if not message:
            flash("⚠️ Comment cannot be empty.", "warning")
            return redirect(url_for('enduser.view_ticket', ticket_id=ticket_id))

        comment = Comment(
            ticket_id=ticket_id,
            user_id=current_user.id,
            message=message,
            is_internal=False  # End user comments are never internal
        )
        db.session.add(comment)
        db.session.commit()

        flash("💬 Comment added successfully!", "success")
        return redirect(url_for('enduser.view_ticket', ticket_id=ticket_id))

    return render_template('ticket_detail.html', ticket=ticket, comments=comments, current_user=current_user, agents=[])
