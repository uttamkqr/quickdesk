# utils/activity_logger.py

from models import ActivityLog, db
from flask import request


def log_activity(user_id, action, description, ticket_id=None):
    """
    Log user activity
    
    Args:
        user_id: ID of the user performing the action
        action: Type of action (created, updated, deleted, etc.)
        description: Description of the activity
        ticket_id: Related ticket ID (optional)
    """
    try:
        # Get IP address
        ip_address = request.remote_addr if request else None

        activity = ActivityLog(
            user_id=user_id,
            action=action,
            description=description,
            ticket_id=ticket_id,
            ip_address=ip_address
        )
        db.session.add(activity)
        db.session.commit()
        return activity
    except Exception as e:
        print(f"❌ Failed to log activity: {e}")
        db.session.rollback()
        return None


def log_ticket_created(user_id, ticket):
    """Log ticket creation"""
    return log_activity(
        user_id=user_id,
        action='ticket_created',
        description=f"Created ticket #{ticket.id}: {ticket.subject}",
        ticket_id=ticket.id
    )


def log_ticket_updated(user_id, ticket, changes):
    """Log ticket update"""
    return log_activity(
        user_id=user_id,
        action='ticket_updated',
        description=f"Updated ticket #{ticket.id}: {changes}",
        ticket_id=ticket.id
    )


def log_ticket_assigned(user_id, ticket, agent_name):
    """Log ticket assignment"""
    return log_activity(
        user_id=user_id,
        action='ticket_assigned',
        description=f"Assigned ticket #{ticket.id} to {agent_name}",
        ticket_id=ticket.id
    )


def log_status_change(user_id, ticket, old_status, new_status):
    """Log status change"""
    return log_activity(
        user_id=user_id,
        action='status_changed',
        description=f"Changed ticket #{ticket.id} status from {old_status} to {new_status}",
        ticket_id=ticket.id
    )


def log_comment_added(user_id, ticket, comment_id):
    """Log comment addition"""
    return log_activity(
        user_id=user_id,
        action='comment_added',
        description=f"Added comment #{comment_id} to ticket #{ticket.id}",
        ticket_id=ticket.id
    )


def log_user_login(user_id, username):
    """Log user login"""
    return log_activity(
        user_id=user_id,
        action='user_login',
        description=f"User {username} logged in"
    )


def log_user_logout(user_id, username):
    """Log user logout"""
    return log_activity(
        user_id=user_id,
        action='user_logout',
        description=f"User {username} logged out"
    )


def get_ticket_activities(ticket_id, limit=50):
    """Get activities for a specific ticket"""
    return ActivityLog.query.filter_by(
        ticket_id=ticket_id
    ).order_by(ActivityLog.created_at.desc()).limit(limit).all()


def get_user_activities(user_id, limit=100):
    """Get activities for a specific user"""
    return ActivityLog.query.filter_by(
        user_id=user_id
    ).order_by(ActivityLog.created_at.desc()).limit(limit).all()


def get_recent_activities(limit=100):
    """Get recent activities across the system"""
    return ActivityLog.query.order_by(
        ActivityLog.created_at.desc()
    ).limit(limit).all()
