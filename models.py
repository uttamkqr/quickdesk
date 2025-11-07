# models.py

from flask_login import UserMixin
from extensions import db  # Imported from extensions.py
from datetime import datetime, timedelta
import secrets

# ================================
# 1. User Table
# ================================
class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'enduser', 'agent', 'admin'

    # New fields
    is_active = db.Column(db.Boolean, default=True)
    phone = db.Column(db.String(20), nullable=True)
    department = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    # Password reset
    reset_token = db.Column(db.String(100), nullable=True, unique=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)

    # Relationships
    tickets = db.relationship('Ticket', foreign_keys='Ticket.user_id', backref='creator', lazy=True,
                              cascade="all, delete")
    assigned_tickets = db.relationship('Ticket', foreign_keys='Ticket.assigned_to', backref='assigned_agent', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True, cascade="all, delete")
    activities = db.relationship('ActivityLog', backref='user', lazy=True, cascade="all, delete")
    notifications = db.relationship('Notification', backref='user', lazy=True, cascade="all, delete")

    def generate_reset_token(self):
        """Generate password reset token"""
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
        return self.reset_token

    def verify_reset_token(self, token):
        """Verify if reset token is valid"""
        if self.reset_token == token and self.reset_token_expiry > datetime.utcnow():
            return True
        return False

    def clear_reset_token(self):
        """Clear reset token after use"""
        self.reset_token = None
        self.reset_token_expiry = None

    def __repr__(self):
        return f'<User {self.username}>'


# ================================
# 2. Category Table
# ================================
class Category(db.Model):
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    color = db.Column(db.String(7), default='#007bff')  # Hex color for UI
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    tickets = db.relationship('Ticket', backref='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'


# ================================
# 3. Ticket Table 
# ================================
class Ticket(db.Model):
    __tablename__ = 'ticket'

    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Open', nullable=False)  # Open, In Progress, Resolved, Closed

    # New fields
    priority = db.Column(db.String(20), default='Medium', nullable=False)  # Low, Medium, High, Critical
    attachment = db.Column(db.String(200), nullable=True)
    resolution = db.Column(db.Text, nullable=True)  # Resolution details

    # SLA tracking
    due_date = db.Column(db.DateTime, nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    closed_at = db.Column(db.DateTime, nullable=True)

    # Rating system
    rating = db.Column(db.Integer, nullable=True)  # 1-5 stars
    feedback = db.Column(db.Text, nullable=True)

    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Assigned agent

    # Timestamps
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    # Relationships
    comments = db.relationship('Comment', backref='ticket', lazy=True, cascade="all, delete-orphan")
    attachments = db.relationship('Attachment', backref='ticket', lazy=True, cascade="all, delete-orphan")
    activities = db.relationship('ActivityLog', backref='ticket', lazy=True, cascade="all, delete-orphan")

    def is_overdue(self):
        """Check if ticket is overdue"""
        if self.due_date and self.status not in ['Resolved', 'Closed']:
            return datetime.utcnow() > self.due_date
        return False

    def calculate_due_date(self):
        """Calculate due date based on priority"""
        priority_hours = {
            'Critical': 4,
            'High': 24,
            'Medium': 72,
            'Low': 168
        }
        hours = priority_hours.get(self.priority, 72)
        self.due_date = datetime.utcnow() + timedelta(hours=hours)

    def __repr__(self):
        return f'<Ticket #{self.id} - {self.subject}>'


# ================================
# 4. Comment Table
# ================================
class Comment(db.Model):
    __tablename__ = 'comment'

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    is_internal = db.Column(db.Boolean, default=False)  # Internal notes for agents only

    # Foreign Keys
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<Comment #{self.id} on Ticket #{self.ticket_id}>'


# ================================
# 5. Attachment Table 
# ================================
class Attachment(db.Model):
    __tablename__ = 'attachment'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # in bytes
    file_type = db.Column(db.String(50), nullable=False)

    # Foreign Keys
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    uploader = db.relationship('User', backref='uploaded_files')

    def __repr__(self):
        return f'<Attachment {self.original_filename}>'


# ================================
# 6. Activity Log Table 
# ================================
class ActivityLog(db.Model):
    __tablename__ = 'activity_log'

    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(100), nullable=False)  # 'created', 'updated', 'commented', etc.
    description = db.Column(db.Text, nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)

    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ActivityLog {self.action} by User {self.user_id}>'


# ================================
# 7. Notification Table 
# ================================
class Notification(db.Model):
    __tablename__ = 'notification'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # 'ticket_update', 'assignment', 'comment'
    is_read = db.Column(db.Boolean, default=False)

    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    related_ticket = db.relationship('Ticket', backref='notifications')

    def __repr__(self):
        return f'<Notification {self.title}>'


# ================================
# 8. Email Template Table 
# ================================
class EmailTemplate(db.Model):
    __tablename__ = 'email_template'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    template_type = db.Column(db.String(50), nullable=False)  # 'ticket_created', 'status_update', etc.
    variables = db.Column(db.Text, nullable=True)  # JSON string of available variables
    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<EmailTemplate {self.name}>'
