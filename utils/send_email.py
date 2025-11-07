# utils/send_email.py

from flask_mail import Message
from extensions import mail
from flask import current_app


def send_email(subject, recipients=None, recipient=None, body=""):
    """
    Send email to recipient(s).
    
    Args:
        subject: Email subject
        recipients: List of recipient emails (or single email as list)
        recipient: Single recipient email (alternative to recipients)
        body: Email body text
    """
    try:
        # Handle both recipient and recipients parameters
        if recipient and not recipients:
            recipients = [recipient]
        elif recipients and isinstance(recipients, str):
            recipients = [recipients]
        elif not recipients:
            raise ValueError("No recipients provided")

        msg = Message(subject=subject,
                      recipients=recipients,
                      body=body,
                      sender=current_app.config['MAIL_USERNAME'])
        mail.send(msg)
        print(f"📧 Email sent to {', '.join(recipients)}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
