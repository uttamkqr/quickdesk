from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from extensions import db
from models import Category, User, Ticket
import pandas as pd
import io

bp = Blueprint('admin', __name__)

# ✅ Admin-only decorator-style check
def admin_only():
    if current_user.role != 'admin':
        flash("⛔ Access Denied: Admins only!", "danger")
        return True  # means not admin
    return False


# ✅ Admin Dashboard
@bp.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if admin_only(): return redirect(url_for('auth.login'))

    categories = Category.query.all()
    total_tickets = Ticket.query.count()
    resolved_tickets = Ticket.query.filter_by(status='Resolved').count()
    pending_tickets = Ticket.query.filter_by(status='In Progress').count()
    closed_tickets = Ticket.query.filter_by(status='Closed').count()

    # Chart data
    status_counts = db.session.query(Ticket.status, db.func.count(Ticket.id)).group_by(Ticket.status).all()
    labels = [row[0] for row in status_counts]
    values = [row[1] for row in status_counts]

    return render_template("admin_dashboard.html",
        categories=categories,
        total_tickets=total_tickets,
        resolved_tickets=resolved_tickets,
        pending_tickets=pending_tickets,
        closed_tickets=closed_tickets,
        labels=labels,
        values=values
    )


# ✅ Create Category
@bp.route('/admin/category/create', methods=['POST'])
@login_required
def create_category():
    if admin_only(): return redirect(url_for('auth.login'))

    name = request.form['name'].strip()
    if name:
        db.session.add(Category(name=name))
        db.session.commit()
        flash("✅ Category created.", "success")
    else:
        flash("❌ Category name cannot be empty.", "danger")
    return redirect(url_for('admin.admin_dashboard'))


# ✅ Delete Category
@bp.route('/admin/category/delete/<int:id>')
@login_required
def delete_category(id):
    if admin_only(): return redirect(url_for('auth.login'))

    category = Category.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    flash("🗑️ Category deleted.", "info")
    return redirect(url_for('admin.admin_dashboard'))


# ✅ View All Users
@bp.route('/admin/users')
@login_required
def view_users():
    if admin_only(): return redirect(url_for('auth.login'))

    users = User.query.all()
    return render_template('users.html', users=users)


# ✅ Update User Role
@bp.route('/admin/user/role/<int:id>', methods=['POST'])
@login_required
def update_user_role(id):
    if admin_only(): return redirect(url_for('auth.login'))

    user = User.query.get_or_404(id)
    new_role = request.form['role'].strip()
    if new_role in ['enduser', 'agent', 'admin']:
        user.role = new_role
        db.session.commit()
        flash("🛠️ User role updated.", "success")
    else:
        flash("❌ Invalid role selected.", "danger")
    return redirect(url_for('admin.view_users'))


# ✅ Export Tickets to Excel
@bp.route('/admin/export_tickets')
@login_required
def export_tickets():
    if admin_only(): return redirect(url_for('auth.login'))

    tickets = Ticket.query.all()
    data = [{
        "ID": t.id,
        "Subject": t.subject,
        "Description": t.description,
        "Status": t.status,
        "Category": t.category.name if t.category else "N/A",
        "User": t.creator.username if t.creator else "N/A",
        "Created At": t.created_at.strftime("%Y-%m-%d %H:%M"),
        "Updated At": t.updated_at.strftime("%Y-%m-%d %H:%M")
    } for t in tickets]

    df = pd.DataFrame(data)
    output = io.BytesIO()

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Tickets', index=False)

    output.seek(0)

    return send_file(
        output,
        download_name="tickets_export.xlsx",
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
