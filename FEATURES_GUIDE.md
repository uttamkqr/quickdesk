# QuickDesk - New Features Guide

This document provides a comprehensive guide to all the new features added to QuickDesk.

## 📋 Table of Contents

1. [Password Reset System](#1-password-reset-system)
2. [Priority System](#2-priority-system)
3. [Ticket Assignment](#3-ticket-assignment)
4. [Enhanced File Management](#4-enhanced-file-management)
5. [Activity Logging](#5-activity-logging)
6. [Notification System](#6-notification-system)
7. [SLA Tracking](#7-sla-tracking)
8. [Rating & Feedback](#8-rating--feedback)
9. [Internal Notes](#9-internal-notes)
10. [Email Templates](#10-email-templates)

---

## 1. Password Reset System

### Overview

Users can now reset their password via email verification.

### Features

- Secure token-based password reset
- Token expires after 1 hour
- Email notifications for reset requests and successful changes
- Security best practices (doesn't reveal if email exists)

### How to Use

**For End Users:**

1. Go to login page
2. Click "Forgot Password?"
3. Enter your email address
4. Check your email for reset link
5. Click link and enter new password
6. Log in with new password

**Routes:**

- `/forgot-password` - Request password reset
- `/reset-password/<token>` - Reset password with token

**Database Fields Added:**

```python
User.reset_token          # Unique reset token
User.reset_token_expiry   # Token expiration time
```

---

## 2. Priority System

### Overview

Tickets now have priority levels affecting SLA and visibility.

### Priority Levels

- **Critical** - 4 hour SLA
- **High** - 24 hour SLA
- **Medium** - 72 hour SLA (default)
- **Low** - 168 hour SLA (1 week)

### Features

- Automatic due date calculation based on priority
- Visual indicators for priority
- Filter tickets by priority
- Overdue ticket alerts

### How to Use

**Creating Ticket with Priority:**

```python
ticket = Ticket(
    subject="Server Down",
    priority="Critical",
    # ... other fields
)
ticket.calculate_due_date()  # Auto-calculates due date
```

**Database Fields Added:**

```python
Ticket.priority      # Low, Medium, High, Critical
Ticket.due_date      # Calculated based on priority
```

---

## 3. Ticket Assignment

### Overview

Tickets can be assigned to specific agents for better workflow management.

### Features

- Assign tickets to agents
- View assigned tickets separately
- Notify agents when assigned
- Track assignment history
- Reassign tickets

### How to Use

**For Agents/Admins:**

1. Open ticket details
2. Select agent from dropdown
3. Click "Assign"
4. Agent receives notification

**For Agents:**

- View "My Assigned Tickets" in dashboard
- Filter by assigned tickets
- See assignment notifications

**Database Fields Added:**

```python
Ticket.assigned_to    # Foreign key to User (agent)
```

**Relationships:**

```python
User.assigned_tickets  # All tickets assigned to this agent
```

---

## 4. Enhanced File Management

### Overview

Improved file upload system with better validation and management.

### Features

- Multiple file attachments per ticket
- File type validation
- File size limits (10MB)
- Unique filename generation
- File metadata storage
- Download/delete attachments
- File size formatting

### Supported File Types

- **Images:** png, jpg, jpeg, gif, bmp, webp
- **Documents:** pdf, doc, docx, txt, rtf, odt
- **Spreadsheets:** xls, xlsx, csv, ods
- **Archives:** zip, rar, 7z, tar, gz
- **Other:** xml, json, log

### How to Use

**Uploading Files:**

```python
from utils.file_handler import save_file

attachment, error = save_file(file, ticket_id, user_id)
if attachment:
    flash("File uploaded successfully!")
else:
    flash(f"Error: {error}")
```

**File Utilities:**

```python
from utils.file_handler import (
    allowed_file,           # Check if file type is allowed
    get_ticket_attachments, # Get all files for a ticket
    delete_file,           # Delete a file
    format_file_size       # Format bytes to human-readable
)
```

**Database Model:**

```python
class Attachment:
    filename              # Unique filename
    original_filename     # Original upload name
    file_path            # Path to file
    file_size            # Size in bytes
    file_type            # Category (image, document, etc.)
    ticket_id            # Related ticket
    uploaded_by          # User who uploaded
    uploaded_at          # Upload timestamp
```

---

## 5. Activity Logging

### Overview

Track all user actions for audit trail and security.

### Tracked Actions

- User login/logout
- Ticket created/updated/deleted
- Status changes
- Comments added
- Ticket assignments
- File uploads

### Features

- IP address tracking
- Timestamp for all activities
- Detailed descriptions
- View activity by ticket/user
- Recent activity feed

### How to Use

**Logging Activities:**

```python
from utils.activity_logger import (
    log_ticket_created,
    log_status_change,
    log_user_login,
    log_comment_added
)

# Log ticket creation
log_ticket_created(user_id, ticket)

# Log status change
log_status_change(user_id, ticket, "Open", "In Progress")
```

**Viewing Activities:**

```python
from utils.activity_logger import (
    get_ticket_activities,    # Get activities for a ticket
    get_user_activities,      # Get activities for a user
    get_recent_activities     # Get recent system activities
)
```

**Database Model:**

```python
class ActivityLog:
    action          # Type of action
    description     # Detailed description
    ip_address      # User's IP
    user_id         # User who performed action
    ticket_id       # Related ticket (optional)
    created_at      # Timestamp
```

---

## 6. Notification System

### Overview

Real-time notifications for ticket updates and activities.

### Notification Types

- **ticket_created** - New ticket created
- **assignment** - Ticket assigned to you
- **ticket_update** - Ticket status/priority changed
- **comment** - New comment on your ticket

### Features

- In-app notifications
- Unread notification count
- Mark as read functionality
- Notification history
- Automatic cleanup

### How to Use

**Creating Notifications:**

```python
from utils.notification_helper import (
    notify_ticket_created,
    notify_ticket_assigned,
    notify_ticket_updated,
    notify_new_comment
)

# Notify about new ticket
notify_ticket_created(ticket)

# Notify agent about assignment
notify_ticket_assigned(ticket, agent)
```

**Viewing Notifications:**

```python
from utils.notification_helper import (
    get_unread_notifications,
    mark_notification_read,
    mark_all_notifications_read
)

# Get unread notifications
notifications = get_unread_notifications(user_id)

# Mark single notification as read
mark_notification_read(notification_id)

# Mark all as read
mark_all_notifications_read(user_id)
```

**Database Model:**

```python
class Notification:
    title               # Notification title
    message             # Notification message
    notification_type   # Type of notification
    is_read             # Read status
    user_id             # Recipient
    ticket_id           # Related ticket
    created_at          # Timestamp
```

---

## 7. SLA Tracking

### Overview

Service Level Agreement tracking based on priority.

### Features

- Automatic due date calculation
- Overdue ticket detection
- SLA violation alerts
- Resolution time tracking
- Performance metrics

### SLA Times

| Priority | Response Time |
|----------|--------------|
| Critical | 4 hours      |
| High     | 24 hours     |
| Medium   | 72 hours     |
| Low      | 1 week       |

### How to Use

**Checking SLA Status:**

```python
# Check if ticket is overdue
if ticket.is_overdue():
    flash("⚠️ This ticket is overdue!", "warning")

# Calculate due date
ticket.calculate_due_date()
```

**Database Fields:**

```python
Ticket.due_date       # When ticket should be resolved
Ticket.resolved_at    # When ticket was resolved
Ticket.closed_at      # When ticket was closed
```

---

## 8. Rating & Feedback

### Overview

Allow users to rate resolved tickets and provide feedback.

### Features

- 1-5 star rating system
- Text feedback
- Only available for resolved/closed tickets
- Agent performance metrics
- Feedback history

### How to Use

**For End Users:**

1. Go to resolved/closed ticket
2. Click "Rate This Ticket"
3. Select star rating (1-5)
4. Add optional feedback
5. Submit

**For Agents/Admins:**

- View average ratings
- Read user feedback
- Track performance metrics

**Database Fields:**

```python
Ticket.rating     # 1-5 stars
Ticket.feedback   # User feedback text
```

---

## 9. Internal Notes

### Overview

Agents can add internal notes not visible to end users.

### Features

- Private comments for agents only
- Visible only to agents and admins
- Used for internal communication
- Track agent discussions

### How to Use

**Adding Internal Note:**

```python
comment = Comment(
    ticket_id=ticket.id,
    user_id=agent.id,
    message="Internal note about ticket",
    is_internal=True  # Mark as internal
)
```

**In Templates:**

```html
{% if comment.is_internal %}
    <span class="badge bg-warning">Internal</span>
{% endif %}
```

**Database Field:**

```python
Comment.is_internal   # Boolean flag
```

---

## 10. Email Templates

### Overview

Customizable email templates for system notifications.

### Template Types

- ticket_created
- status_update
- assignment_notification
- ticket_resolved
- password_reset
- welcome_email

### Features

- Variable substitution
- HTML/Plain text support
- Template versioning
- Active/inactive templates
- Preview functionality

### How to Use

**Creating Template:**

```python
template = EmailTemplate(
    name="Ticket Created",
    subject="New Ticket #{ticket_id}: {ticket_subject}",
    body="Hello {username}, your ticket has been created...",
    template_type="ticket_created",
    variables='["username", "ticket_id", "ticket_subject"]'
)
```

**Using Template:**

```python
from utils.email_template_helper import render_template

# Render template with variables
body = render_template('ticket_created', {
    'username': user.username,
    'ticket_id': ticket.id,
    'ticket_subject': ticket.subject
})
```

**Database Model:**

```python
class EmailTemplate:
    name            # Template name
    subject         # Email subject
    body            # Email body
    template_type   # Type identifier
    variables       # Available variables (JSON)
    is_active       # Active status
```

---

## 🚀 Migration Guide

### Step 1: Update Database

```bash
# Backup existing database
mysqldump -u root -p quickdesk > quickdesk_backup.sql

# Drop existing tables (if needed)
python
>>> from app import app, db
>>> with app.app_context():
...     db.drop_all()
...     db.create_all()
>>> exit()
```

### Step 2: Initialize New Features

```bash
# Run database migrations
python init_db.py

# Create default email templates (optional)
python create_email_templates.py
```

### Step 3: Update Existing Routes

Update your route files to use the new features:

```python
# In ticket creation route
from utils.notification_helper import notify_ticket_created
from utils.activity_logger import log_ticket_created

# After creating ticket
ticket.calculate_due_date()  # Calculate SLA
db.session.commit()

log_ticket_created(current_user.id, ticket)
notify_ticket_created(ticket)
```

---

## 📊 API Integration Examples

### Notification API

```python
@app.route('/api/notifications')
@login_required
def get_notifications_api():
    notifications = get_unread_notifications(current_user.id)
    return jsonify([{
        'id': n.id,
        'title': n.title,
        'message': n.message,
        'type': n.notification_type,
        'created_at': n.created_at.isoformat()
    } for n in notifications])
```

### Activity API

```python
@app.route('/api/ticket/<int:ticket_id>/activities')
@login_required
def get_ticket_activities_api(ticket_id):
    activities = get_ticket_activities(ticket_id)
    return jsonify([{
        'action': a.action,
        'description': a.description,
        'user': a.user.username,
        'created_at': a.created_at.isoformat()
    } for a in activities])
```

---

## 🔧 Configuration

### File Upload Settings

Edit `utils/file_handler.py`:

```python
# Change maximum file size (default: 10MB)
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB

# Add allowed extensions
ALLOWED_EXTENSIONS['code'] = {'py', 'js', 'html', 'css'}
```

### SLA Settings

Edit `models.py`:

```python
def calculate_due_date(self):
    priority_hours = {
        'Critical': 2,   # Change to 2 hours
        'High': 12,      # Change to 12 hours
        'Medium': 48,    # Change to 48 hours
        'Low': 120       # Change to 5 days
    }
```

---

## 🎨 UI Enhancements

### Notification Bell

Add to your `base.html`:

```html
<li class="nav-item dropdown">
    <a class="nav-link" href="#" id="notificationDropdown" 
       data-bs-toggle="dropdown">
        <i class="fas fa-bell"></i>
        {% if unread_count > 0 %}
        <span class="badge bg-danger">{{ unread_count }}</span>
        {% endif %}
    </a>
    <div class="dropdown-menu" aria-labelledby="notificationDropdown">
        {% for notification in notifications[:5] %}
        <a class="dropdown-item" href="#">
            <strong>{{ notification.title }}</strong><br>
            <small>{{ notification.message }}</small>
        </a>
        {% endfor %}
    </div>
</li>
```

### Priority Badges

```html
{% if ticket.priority == 'Critical' %}
    <span class="badge bg-danger">Critical</span>
{% elif ticket.priority == 'High' %}
    <span class="badge bg-warning">High</span>
{% elif ticket.priority == 'Medium' %}
    <span class="badge bg-info">Medium</span>
{% else %}
    <span class="badge bg-secondary">Low</span>
{% endif %}
```

---

## 📱 Best Practices

1. **Always log activities** for audit trails
2. **Send notifications** for important events
3. **Set ticket priorities** appropriately
4. **Assign tickets** to agents promptly
5. **Use internal notes** for agent communication
6. **Monitor SLA compliance** regularly
7. **Validate file uploads** before processing
8. **Clean up old notifications** periodically

---

## 🐛 Troubleshooting

### Notifications Not Showing

```python
# Check if context processor is registered
# In app.py, ensure inject_notifications() is defined
```

### File Upload Fails

```bash
# Check upload folder permissions
chmod 755 uploads/

# Check file size limit
# Edit MAX_FILE_SIZE in utils/file_handler.py
```

### Activity Log Not Recording

```python
# Ensure activity logger is imported and called
from utils.activity_logger import log_activity
```

---

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Bootstrap 5](https://getbootstrap.com/docs/5.0/)

---

## 🤝 Contributing

To add new features:

1. Update `models.py` with new database fields
2. Create utility functions in `utils/`
3. Update routes to use new features
4. Create/update templates
5. Update documentation
6. Test thoroughly

---

## 📞 Support

For questions or issues with new features:

- Check the documentation
- Review the code examples
- Test in development first
- Contact the development team

---

**Last Updated:** 2025
**Version:** 2.0
