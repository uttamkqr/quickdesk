from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from models import db, Ticket, Comment, User
from utils.send_email import send_email
from utils.notification_helper import notify_ticket_updated
from utils.activity_logger import log_status_change, log_comment_added
import os

bp = Blueprint('agent', __name__)


# Agent Dashboard with optional status filter
@bp.route('/agent/dashboard')
@login_required
def agent_dashboard():
    if current_user.role != 'agent':
        return "Access Denied", 403

    status_filter = request.args.get('status')
    tickets = Ticket.query.filter_by(status=status_filter).all() if status_filter else Ticket.query.all()

    return render_template('agent_dashboard.html', tickets=tickets)


# View Ticket Details - Handle both GET and POST
@bp.route('/agent/ticket/<int:ticket_id>', methods=['GET', 'POST'])
@login_required
def view_ticket(ticket_id):
    if current_user.role != 'agent':
        return "Access Denied", 403

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
            return redirect(url_for('agent.view_ticket', ticket_id=ticket_id))

        comment = Comment(
            ticket_id=ticket_id,
            user_id=current_user.id,
            message=message,
            is_internal=is_internal
        )
        db.session.add(comment)
        db.session.commit()

        # Log activity
        log_comment_added(current_user.id, ticket, comment.id)

        flash("💬 Comment added successfully!", "success")
        return redirect(url_for('agent.view_ticket', ticket_id=ticket_id))

    return render_template('ticket_detail.html', ticket=ticket, comments=comments, current_user=current_user,
                           agents=agents)


# Assign/Forward Ticket to Another Agent
@bp.route('/agent/assign/<int:ticket_id>', methods=['POST'])
@login_required
def assign_ticket(ticket_id):
    if current_user.role != 'agent':
        return "Access Denied", 403

    ticket = Ticket.query.get_or_404(ticket_id)
    assigned_to = request.form.get('assigned_to')
    forward_note = request.form.get('forward_note', '').strip()

    # Validation: Cannot forward tickets that are "In Progress"
    if ticket.status == 'In Progress':
        flash("⚠️ Cannot forward tickets that are already 'In Progress'. Please complete or update status first.",
              "warning")
        return redirect(url_for('agent.view_ticket', ticket_id=ticket_id))

    # Validation: Cannot forward Resolved or Closed tickets
    if ticket.status in ['Resolved', 'Closed']:
        flash("⚠️ Cannot forward tickets that are already Resolved or Closed.", "warning")
        return redirect(url_for('agent.view_ticket', ticket_id=ticket_id))

    if not assigned_to:
        flash("⚠️ Please select an agent to assign.", "warning")
        return redirect(url_for('agent.view_ticket', ticket_id=ticket_id))

    # Update assignment
    old_agent_id = ticket.assigned_to
    ticket.assigned_to = int(assigned_to)
    db.session.commit()

    # Get assigned agent
    assigned_agent = User.query.get(assigned_to)

    # Add internal note about assignment
    if forward_note:
        assignment_comment = Comment(
            ticket_id=ticket_id,
            user_id=current_user.id,
            message=f"🔄 **Ticket Forwarded to {assigned_agent.username}**\n\nNote: {forward_note}",
            is_internal=True
        )
        db.session.add(assignment_comment)
        db.session.commit()

    # Send email notification to assigned agent
    if assigned_agent.email:
        send_email(
            subject=f"📋 New Ticket Assigned: #{ticket.id}",
            recipients=[assigned_agent.email],
            body=f"""
Hello {assigned_agent.username},

A ticket has been assigned to you by {current_user.username}.

Ticket Details:
- ID: #{ticket.id}
- Subject: {ticket.subject}
- Priority: {ticket.priority}
- Status: {ticket.status}

{f'Note from {current_user.username}: {forward_note}' if forward_note else ''}

Please login to view and handle this ticket.

Best regards,
QuickDesk Team
""".strip()
        )

    flash(f"✅ Ticket successfully assigned to {assigned_agent.username}!", "success")
    return redirect(url_for('agent.view_ticket', ticket_id=ticket_id))


# Download Attachment
@bp.route('/agent/download/<int:ticket_id>')
@login_required
def download_attachment(ticket_id):
    if current_user.role not in ['agent', 'admin']:
        return "Access Denied", 403

    ticket = Ticket.query.get_or_404(ticket_id)
    if ticket.attachment and os.path.exists(ticket.attachment):
        return send_file(ticket.attachment, as_attachment=True)
    else:
        flash("❌ Attachment not found.", "danger")
        return redirect(url_for('agent.view_ticket', ticket_id=ticket_id))


# Update Ticket Status
@bp.route('/agent/update_status/<int:ticket_id>', methods=['POST'])
@login_required
def update_status(ticket_id):
    if current_user.role != 'agent':
        return "Access Denied", 403

    ticket = Ticket.query.get_or_404(ticket_id)
    old_status = ticket.status
    new_status = request.form['status'].strip()
    ticket.status = new_status
    db.session.commit()

    # Log activity
    log_status_change(current_user.id, ticket, old_status, new_status)
    notify_ticket_updated(ticket)

    # Notify the ticket creator
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


# Add Comment (Legacy route - redirects to view_ticket POST)
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
