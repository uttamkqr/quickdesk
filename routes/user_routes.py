from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Ticket, Category
import os
from werkzeug.utils import secure_filename
from utils.send_email import send_email


bp = Blueprint('user', __name__)
UPLOAD_FOLDER = 'uploads'

# ✅ Dashboard for logged-in user
@bp.route('/dashboard')
@login_required
def dashboard():
    categories = Category.query.all()
    tickets = Ticket.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', tickets=tickets, categories=categories)

# ✅ Create new ticket (form & handler)
@bp.route('/create_ticket', methods=['GET', 'POST'])
@login_required
def create_ticket():
    if request.method == 'POST':
        subject = request.form['subject'].strip()
        description = request.form['description'].strip()
        category_id = int(request.form['category'])
        file = request.files.get('attachment')

        filename = None
        if file and file.filename != '':
            filename = secure_filename(file.filename)

            # ✅ Create upload folder if not exists
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)

        # ✅ Create ticket object
        ticket = Ticket(
            subject=subject,
            description=description,
            category_id=category_id,
            user_id=current_user.id,
            attachment=filename
        )
        db.session.add(ticket)
        db.session.commit()

        # ✅ Email notification
        send_email(
            subject="🎫 Ticket Submitted",
            recipients=[current_user.email],
            body=f"Dear {current_user.username}, your ticket '{subject}' has been submitted successfully."
        )

        flash("🎫 Ticket created successfully!", "success")
        return redirect(url_for('user.dashboard'))

    categories = Category.query.all()
    return render_template('create_ticket.html', categories=categories)
