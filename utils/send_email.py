# utils/send_email.py

from flask_mail import Message
from extensions import mail
from flask import current_app

def send_email(subject, recipient, body):
    try:
        msg = Message(subject=subject,
                      recipients=[recipient],
                      body=body,
                      sender=current_app.config['MAIL_USERNAME'])
        mail.send(msg)
        print(f"📧 Email sent to {recipient}")
    except Exception as e:
        print(f"❌ Failed to send email to {recipient}: {e}")
