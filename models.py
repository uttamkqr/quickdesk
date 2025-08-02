# models.py

from flask_login import UserMixin
from extensions import db  # Imported from extensions.py

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

    # Relationships
    tickets = db.relationship('Ticket', backref='creator', lazy=True, cascade="all, delete")
    comments = db.relationship('Comment', backref='author', lazy=True, cascade="all, delete")

    def __repr__(self):
        return f'<User {self.username}>'


# ================================
# 2. Category Table
# ================================
class Category(db.Model):
    __tablename__ = 'category'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

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
    attachment = db.Column(db.String(200), nullable=True)

    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    # Relationships
    comments = db.relationship('Comment', backref='ticket', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Ticket #{self.id} - {self.subject}>'


# ================================
# 4. Comment Table
# ================================
class Comment(db.Model):
    __tablename__ = 'comment'

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)

    # Foreign Keys
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f'<Comment #{self.id} on Ticket #{self.ticket_id}>'
