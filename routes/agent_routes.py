from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Ticket, Comment, User
from utils.send_email import send_email


bp = Blueprint('agent', __name__)

# ✅ Agent Dashboard with optional status filter
@bp.route('/agent/dashboard')
@login_required
def agent_dashboard():
    if current_user.role != 'agent':
        return "Access Denied", 403

    status_filter = request.args.get('status')
    tickets = Ticket.query.filter_by(status=status_filter).all() if status_filter else Ticket.query.all()

    return render_template('agent_dashboard.html', tickets=tickets)

# ✅ View Ticket Details
@bp.route('/agent/ticket/<int:ticket_id>', methods=['GET'])
@login_required
def view_ticket(ticket_id):
    if current_user.role != 'agent':
        return "Access Denied", 403
    ticket = Ticket.query.get_or_404(ticket_id)
    return render_template('ticket_detail.html', ticket=ticket)

# ✅ Update Ticket Status
@bp.route('/agent/update_status/<int:ticket_id>', methods=['POST'])
@login_required
def update_status(ticket_id):
    if current_user.role != 'agent':
        return "Access Denied", 403

    ticket = Ticket.query.get_or_404(ticket_id)
    new_status = request.form['status'].strip()
    ticket.status = new_status
    db.session.commit()

    # ✅ Notify the ticket creator
    if ticket.creator and ticket.creator.email:
        send_email(
            subject=f"📢 Ticket #{ticket.id} Status Updated",
            recipients=[ticket.creator.email],
            body=f"""
Hello {ticket.creator.username},

Your ticket titled: "{ticket.subject}" has been updated to the status: {ticket.status}.

Regards,  
QuickDesk Support Team
""".strip()
        )

    flash("✅ Ticket status updated and email sent to user.", "success")
    return redirect(url_for('agent.view_ticket', ticket_id=ticket.id))

# ✅ Add Comment
@bp.route('/agent/comment/<int:ticket_id>', methods=['POST'])
@login_required
def add_comment(ticket_id):
    if current_user.role != 'agent':
        return "Access Denied", 403

    message = request.form['message'].strip()
    if not message:
        flash("⚠️ Comment cannot be empty.", "warning")
        return redirect(url_for('agent.view_ticket', ticket_id=ticket_id))

    comment = Comment(ticket_id=ticket_id, user_id=current_user.id, message=message)
    db.session.add(comment)
    db.session.commit()

    flash("💬 Comment added.", "info")
    return redirect(url_for('agent.view_ticket', ticket_id=ticket_id))
