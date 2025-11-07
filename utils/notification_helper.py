# utils/notification_helper.py

from models import Notification, User, db
from flask import current_app


def create_notification(user_id, title, message, notification_type, ticket_id=None):
    """
    Create a notification for a user
    
    Args:
        user_id: ID of the user to notify
        title: Notification title
        message: Notification message
        notification_type: Type of notification
        ticket_id: Related ticket ID (optional)
    """
    try:
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            ticket_id=ticket_id
        )
        db.session.add(notification)
        db.session.commit()
        return notification
    except Exception as e:
        print(f"❌ Failed to create notification: {e}")
        db.session.rollback()
        return None


def notify_ticket_created(ticket):
    """Notify relevant users when a ticket is created"""
    # Notify all agents
    agents = User.query.filter_by(role='agent', is_active=True).all()
    for agent in agents:
        create_notification(
            user_id=agent.id,
            title="New Ticket Created",
            message=f"Ticket #{ticket.id}: {ticket.subject}",
            notification_type='ticket_created',
            ticket_id=ticket.id
        )


def notify_ticket_assigned(ticket, agent):
    """Notify agent when a ticket is assigned to them"""
    create_notification(
        user_id=agent.id,
        title="Ticket Assigned to You",
        message=f"You have been assigned ticket #{ticket.id}: {ticket.subject}",
        notification_type='assignment',
        ticket_id=ticket.id
    )


def notify_ticket_updated(ticket):
    """Notify ticket creator when ticket is updated"""
    create_notification(
        user_id=ticket.user_id,
        title="Ticket Updated",
        message=f"Your ticket #{ticket.id} has been updated. Status: {ticket.status}",
        notification_type='ticket_update',
        ticket_id=ticket.id
    )


def notify_new_comment(ticket, comment, commenter):
    """Notify relevant users about new comment"""
    # Notify ticket creator if comment is from someone else
    if commenter.id != ticket.user_id and not comment.is_internal:
        create_notification(
            user_id=ticket.user_id,
            title="New Comment on Your Ticket",
            message=f"{commenter.username} commented on ticket #{ticket.id}",
            notification_type='comment',
            ticket_id=ticket.id
        )

    # Notify assigned agent if exists and not the commenter
    if ticket.assigned_to and ticket.assigned_to != commenter.id:
        create_notification(
            user_id=ticket.assigned_to,
            title="New Comment on Assigned Ticket",
            message=f"{commenter.username} commented on ticket #{ticket.id}",
            notification_type='comment',
            ticket_id=ticket.id
        )


def get_unread_notifications(user_id):
    """Get unread notifications for a user"""
    return Notification.query.filter_by(
        user_id=user_id,
        is_read=False
    ).order_by(Notification.created_at.desc()).all()


def mark_notification_read(notification_id):
    """Mark a notification as read"""
    try:
        notification = Notification.query.get(notification_id)
        if notification:
            notification.is_read = True
            db.session.commit()
            return True
        return False
    except Exception as e:
        print(f"❌ Failed to mark notification as read: {e}")
        db.session.rollback()
        return False


def mark_all_notifications_read(user_id):
    """Mark all notifications as read for a user"""
    try:
        Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).update({'is_read': True})
        db.session.commit()
        return True
    except Exception as e:
        print(f"❌ Failed to mark all notifications as read: {e}")
        db.session.rollback()
        return False
