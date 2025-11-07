# QuickDesk v2.0 - Quick Reference Card

## 🚀 Installation Commands

```bash
# New Installation
install.bat              # Windows
./install.sh             # Linux/Mac
python setup.py          # Interactive setup

# Existing Installation Upgrade
python migrate_database.py

# Manual Installation
pip install -r requirements.txt
cp .env.example .env
python init_db.py
python app.py
```

## 📝 Important Files

| File | Purpose |
|------|---------|
| `app.py` | Main application entry point |
| `models.py` | Database models |
| `config.py` | Configuration settings |
| `.env` | **Secret** credentials (never commit!) |
| `requirements.txt` | Python dependencies |
| `migrate_database.py` | Database migration |

## 🗄️ Database Commands

```bash
# Backup database
mysqldump -u root -p quickdesk > backup.sql

# Restore database
mysql -u root -p quickdesk < backup.sql

# Initialize database
python init_db.py

# Create admin user
python create_admin.py

# Run migration
python migrate_database.py
```

## 🔧 Common Tasks

### Start Application

```bash
python app.py
```

Access at: `http://localhost:5000`

### Create Admin User

```bash
python create_admin.py
```

### Reset Database

```bash
mysql -u root -p
DROP DATABASE quickdesk;
CREATE DATABASE quickdesk;
EXIT;
python init_db.py
```

## 📊 New Features Quick Reference

### 1. Priority Levels

- **Critical** - 4 hour SLA
- **High** - 24 hour SLA
- **Medium** - 72 hour SLA (default)
- **Low** - 1 week SLA

### 2. Notification Types

- `ticket_created` - New ticket created
- `assignment` - Ticket assigned to you
- `ticket_update` - Status/priority changed
- `comment` - New comment added

### 3. User Roles

- **enduser** - Create and track tickets
- **agent** - Handle tickets, add notes
- **admin** - Full system access

### 4. Ticket Statuses

- Open
- In Progress
- Resolved
- Closed

## 🔌 Code Snippets

### Create Ticket with Priority

```python
from utils.notification_helper import notify_ticket_created
from utils.activity_logger import log_ticket_created

ticket = Ticket(
    subject=subject,
    description=description,
    priority='High',
    category_id=category_id,
    user_id=current_user.id
)
ticket.calculate_due_date()
db.session.add(ticket)
db.session.commit()

log_ticket_created(current_user.id, ticket)
notify_ticket_created(ticket)
```

### Assign Ticket to Agent

```python
from utils.notification_helper import notify_ticket_assigned
from utils.activity_logger import log_ticket_assigned

ticket.assigned_to = agent_id
db.session.commit()

agent = User.query.get(agent_id)
notify_ticket_assigned(ticket, agent)
log_ticket_assigned(current_user.id, ticket, agent.username)
```

### Upload File

```python
from utils.file_handler import save_file

attachment, error = save_file(file, ticket_id, user_id)
if attachment:
    flash("File uploaded successfully!")
else:
    flash(f"Error: {error}")
```

### Send Notification

```python
from utils.notification_helper import create_notification

create_notification(
    user_id=user_id,
    title="Ticket Updated",
    message="Your ticket status has changed",
    notification_type='ticket_update',
    ticket_id=ticket.id
)
```

### Log Activity

```python
from utils.activity_logger import log_activity

log_activity(
    user_id=current_user.id,
    action='status_changed',
    description=f"Changed status from Open to In Progress",
    ticket_id=ticket.id
)
```

## 📁 Directory Structure

```
quickdesk/
├── app.py                  # Main app
├── config.py               # Configuration
├── models.py               # Database models
├── requirements.txt        # Dependencies
├── .env                    # Secrets (don't commit!)
├── routes/                 # Application routes
│   ├── auth_routes.py
│   ├── user_routes.py
│   ├── agent_routes.py
│   ├── admin_routes.py
│   ├── enduser.py
│   └── password_reset_routes.py
├── templates/              # HTML templates
├── static/                 # CSS, JS
│   ├── css/
│   └── js/
├── utils/                  # Utility functions
│   ├── send_email.py
│   ├── auth_decorator.py
│   ├── notification_helper.py
│   ├── activity_logger.py
│   └── file_handler.py
└── uploads/                # User files
```

## 🔐 Environment Variables

```env
# Database
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_NAME=quickdesk

# Email (Gmail)
EMAIL_USER=your@gmail.com
EMAIL_PASS=app_password

# Secret
SECRET_KEY=random-key
```

## 🐛 Troubleshooting Quick Fixes

### Module Not Found

```bash
pip install -r requirements.txt --upgrade
```

### Database Connection Error

```bash
# Check .env file
# Ensure MySQL is running
mysql -u root -p quickdesk
```

### Port Already in Use

```python
# In app.py
app.run(debug=True, port=5001)
```

### File Upload Fails

```bash
mkdir uploads
chmod 755 uploads
```

### Linter Errors

```bash
# Install missing packages
pip install python-dotenv pymysql
```

## 📚 Documentation Map

| Document | When to Use |
|----------|-------------|
| **README.md** | First time setup, overview |
| **QUICKSTART.md** | Quick 5-minute setup |
| **FEATURES_GUIDE.md** | Learn about features |
| **UPDATE_GUIDE.md** | Upgrading from v1.0 |
| **FIXES.md** | See what was fixed |
| **SUMMARY.md** | Complete project overview |
| **QUICK_REFERENCE.md** | This file - quick lookup |

## ⚡ Keyboard Shortcuts (Browser)

- `Ctrl+/` - Focus search
- `Ctrl+K` - Open notifications
- `Esc` - Close modals
- `Tab` - Navigate forms

## 🔗 Important URLs

| URL | Purpose |
|-----|---------|
| `/` | Home (redirects to login) |
| `/login` | User login |
| `/register` | New user registration |
| `/forgot-password` | Password reset request |
| `/dashboard` | User dashboard |
| `/agent/dashboard` | Agent dashboard |
| `/admin/dashboard` | Admin dashboard |
| `/enduser/dashboard` | End user dashboard |
| `/create_ticket` | Create new ticket |

## 🎨 UI Color Codes

```css
Critical: #dc3545 (red)
High: #ffc107 (yellow)
Medium: #0dcaf0 (cyan)
Low: #6c757d (gray)
Success: #198754 (green)
Info: #0d6efd (blue)
```

## 📊 Database Table Reference

| Table | Purpose |
|-------|---------|
| `user` | User accounts |
| `ticket` | Support tickets |
| `category` | Ticket categories |
| `comment` | Ticket comments |
| `attachment` | File attachments |
| `activity_log` | Audit trail |
| `notification` | In-app notifications |
| `email_template` | Email templates |

## 🔍 Search & Filter

### Filter Tickets by Priority

```python
tickets = Ticket.query.filter_by(priority='Critical').all()
```

### Filter by Status

```python
tickets = Ticket.query.filter_by(status='Open').all()
```

### Filter by Assigned Agent

```python
tickets = Ticket.query.filter_by(assigned_to=agent_id).all()
```

### Get Overdue Tickets

```python
from datetime import datetime
overdue = Ticket.query.filter(
    Ticket.due_date < datetime.utcnow(),
    Ticket.status.in_(['Open', 'In Progress'])
).all()
```

## 💡 Pro Tips

1. **Always backup before migration**
   ```bash
   mysqldump -u root -p quickdesk > backup.sql
   ```

2. **Use environment variables**
    - Never commit `.env` file
    - Use `.env.example` as template

3. **Test in development first**
   ```bash
   export FLASK_ENV=development
   python app.py
   ```

4. **Monitor logs**
   ```bash
   tail -f /var/log/mysql/error.log
   ```

5. **Regular cleanup**
   ```python
   # Delete old notifications
   python cleanup_notifications.py
   ```

## 🚨 Emergency Commands

### Stop Application

```bash
Ctrl+C  # In terminal
```

### Rollback Migration

```bash
python migrate_database.py --rollback
```

### Restore from Backup

```bash
mysql -u root -p quickdesk < backup.sql
```

### Reset Admin Password (via MySQL)

```sql
UPDATE user 
SET password = 'new_hash' 
WHERE email = 'admin@example.com';
```

## 📞 Getting Help

1. Check documentation
2. Review error messages
3. Check MySQL logs
4. Test in development
5. Restore from backup

## ✅ Pre-Production Checklist

- [ ] Change SECRET_KEY
- [ ] Use strong passwords
- [ ] Enable HTTPS
- [ ] Set debug=False
- [ ] Configure firewall
- [ ] Setup backups
- [ ] Test all features
- [ ] Train users

---

**Quick Reference Version:** 2.0  
**Last Updated:** 2025  
**Keep this handy for daily operations!**
