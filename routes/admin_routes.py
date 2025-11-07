from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from extensions import db
from models import Category, User, Ticket, Comment
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

    # Recent tickets for admin to view
    recent_tickets = Ticket.query.order_by(Ticket.created_at.desc()).limit(10).all()

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


# ✅ View Ticket Details (for admin)
@bp.route('/admin/ticket/<int:ticket_id>', methods=['GET', 'POST'])
@login_required
def view_ticket(ticket_id):
    if admin_only(): return redirect(url_for('auth.login'))

    ticket = Ticket.query.get_or_404(ticket_id)
    comments = Comment.query.filter_by(ticket_id=ticket_id).order_by(Comment.created_at.asc()).all()

    # Get all agents for assignment dropdown
    agents = User.query.filter_by(role='agent').all()

    # Handle POST request for adding comment
    if request.method == 'POST':
        message = request.form.get('message', '').strip()
        is_internal = request.form.get('is_internal') == 'on'

        if not message:
            flash("⚠️ Comment cannot be empty.", "warning")
            return redirect(url_for('admin.view_ticket', ticket_id=ticket_id))

        comment = Comment(
            ticket_id=ticket_id,
            user_id=current_user.id,
            message=message,
            is_internal=is_internal
        )
        db.session.add(comment)
        db.session.commit()

        # Log activity
        # log_comment_added(current_user.id, ticket, comment.id)

        flash("💬 Comment added successfully!", "success")
        return redirect(url_for('admin.view_ticket', ticket_id=ticket_id))

    return render_template('ticket_detail.html', ticket=ticket, comments=comments, current_user=current_user,
                           agents=agents)


# Assign/Forward Ticket (Admin)
@bp.route('/admin/assign/<int:ticket_id>', methods=['POST'])
@login_required
def assign_ticket(ticket_id):
    if admin_only(): return redirect(url_for('auth.login'))

    ticket = Ticket.query.get_or_404(ticket_id)
    assigned_to = request.form.get('assigned_to')
    forward_note = request.form.get('forward_note', '').strip()

    if not assigned_to:
        flash("⚠️ Please select an agent to assign.", "warning")
        return redirect(url_for('admin.view_ticket', ticket_id=ticket_id))

    # Update assignment
    ticket.assigned_to = int(assigned_to)
    db.session.commit()

    # Get assigned agent
    assigned_agent = User.query.get(assigned_to)

    # Add internal note about assignment
    if forward_note:
        assignment_comment = Comment(
            ticket_id=ticket_id,
            user_id=current_user.id,
            message=f"🔄 **Ticket Assigned to {assigned_agent.username} by Admin**\n\nNote: {forward_note}",
            is_internal=True
        )
        db.session.add(assignment_comment)
        db.session.commit()

    # Send email notification to assigned agent
    from utils.send_email import send_email
    if assigned_agent.email:
        send_email(
            subject=f"📋 New Ticket Assigned by Admin: #{ticket.id}",
            recipients=[assigned_agent.email],
            body=f"""
Hello {assigned_agent.username},

A ticket has been assigned to you by Admin ({current_user.username}).

Ticket Details:
- ID: #{ticket.id}
- Subject: {ticket.subject}
- Priority: {ticket.priority}
- Status: {ticket.status}

{f'Note from Admin: {forward_note}' if forward_note else ''}

Please login to view and handle this ticket.

Best regards,
QuickDesk Team
""".strip()
        )

    flash(f"✅ Ticket successfully assigned to {assigned_agent.username}!", "success")
    return redirect(url_for('admin.view_ticket', ticket_id=ticket_id))


# Export Tickets to Excel
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
