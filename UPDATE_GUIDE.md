# QuickDesk Update Guide - v1.0 to v2.0

## 🚀 Overview

This guide will help you upgrade your QuickDesk installation from version 1.0 to 2.0 with all the new features.

## ⚡ Quick Summary of Changes

### New Features Added

- ✅ Password Reset via Email
- ✅ Ticket Priority System (Critical/High/Medium/Low)
- ✅ Ticket Assignment to Agents
- ✅ Enhanced File Upload Management
- ✅ Activity Logging & Audit Trail
- ✅ In-app Notification System
- ✅ SLA Tracking & Due Dates
- ✅ Ticket Rating & Feedback
- ✅ Internal Notes for Agents
- ✅ Email Template System

### Database Changes

- 4 new tables added
- Multiple new fields in existing tables
- Enhanced relationships between models

---

## 📋 Pre-Update Checklist

- [ ] Backup your database
- [ ] Backup your code files
- [ ] Note your current .env configuration
- [ ] Stop the running application
- [ ] Have database access credentials ready

---

## 🔧 Step-by-Step Update Process

### Step 1: Backup Everything

**Backup Database:**

```bash
# MySQL backup
mysqldump -u root -p quickdesk > quickdesk_backup_$(date +%Y%m%d).sql

# For Windows (PowerShell)
mysqldump -u root -p quickdesk > quickdesk_backup_$(Get-Date -Format 'yyyyMMdd').sql
```

**Backup Code Files:**

```bash
# Create a backup directory
mkdir quickdesk_backup
cp -r . quickdesk_backup/

# Or compress it
tar -czf quickdesk_backup.tar.gz .
# Windows: Use File Explorer to copy the folder
```

### Step 2: Pull Latest Code

```bash
# If using Git
git pull origin main

# Or download and extract manually
# Then replace files (keep your .env file!)
```

### Step 3: Install New Dependencies

```bash
# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install/update dependencies
pip install -r requirements.txt --upgrade
```

**New packages installed:**

- python-dotenv==1.0.0
- pymysql==1.1.0

### Step 4: Update Configuration

Your `.env` file should now include these variables:

```env
# Database Configuration
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_NAME=quickdesk

# Email Configuration
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_gmail_app_password

# Application Secret Key
SECRET_KEY=your-secret-key-here
```

**Changes in config.py:**

- Database credentials now use environment variables
- More flexible configuration
- No hardcoded passwords

### Step 5: Run Database Migration

```bash
# Run the migration script
python migrate_database.py
```

**What the migration does:**

1. Asks for backup confirmation
2. Creates new tables (Attachment, ActivityLog, Notification, EmailTemplate)
3. Adds new columns to existing tables
4. Sets default values for existing data
5. Creates default email templates

**Expected Output:**

```
⚠️  IMPORTANT: BACKUP YOUR DATABASE BEFORE PROCEEDING!
...
Have you backed up your database? (yes/no): yes

Starting Database Migration...
📦 Creating/updating database tables...
✅ Database tables updated successfully!

📝 Updating existing tickets...
✅ Updated X tickets with default priority!

... (more output)

✅ Migration completed successfully!
```

### Step 6: Test the Application

```bash
# Start the application
python app.py
```

Open browser: `http://localhost:5000`

**Test These Features:**

1. Login with existing account
2. Create a new ticket (check priority field)
3. Check notifications bell icon
4. Try forgot password flow
5. View ticket activities
6. Upload a file to a ticket

### Step 7: Update Your Custom Code (if any)

If you have custom routes or modifications:

#### Update Ticket Creation

**Old Code:**

```python
ticket = Ticket(
    subject=subject,
    description=description,
    category_id=category_id,
    user_id=current_user.id
)
db.session.add(ticket)
db.session.commit()
```

**New Code:**

```python
from utils.notification_helper import notify_ticket_created
from utils.activity_logger import log_ticket_created

ticket = Ticket(
    subject=subject,
    description=description,
    category_id=category_id,
    user_id=current_user.id,
    priority=request.form.get('priority', 'Medium')  # Add priority
)
ticket.calculate_due_date()  # Calculate SLA
db.session.add(ticket)
db.session.commit()

# Log and notify
log_ticket_created(current_user.id, ticket)
notify_ticket_created(ticket)
```

#### Update Status Changes

**Add logging and notifications:**

```python
from utils.activity_logger import log_status_change
from utils.notification_helper import notify_ticket_updated

old_status = ticket.status
ticket.status = new_status
db.session.commit()

log_status_change(current_user.id, ticket, old_status, new_status)
notify_ticket_updated(ticket)
```

---

## 🗄️ Database Schema Changes

### New Tables

#### 1. Attachment

```sql
CREATE TABLE attachment (
    id INT PRIMARY KEY AUTO_INCREMENT,
    filename VARCHAR(255),
    original_filename VARCHAR(255),
    file_path VARCHAR(500),
    file_size INT,
    file_type VARCHAR(50),
    ticket_id INT,
    uploaded_by INT,
    uploaded_at DATETIME,
    FOREIGN KEY (ticket_id) REFERENCES ticket(id),
    FOREIGN KEY (uploaded_by) REFERENCES user(id)
);
```

#### 2. ActivityLog

```sql
CREATE TABLE activity_log (
    id INT PRIMARY KEY AUTO_INCREMENT,
    action VARCHAR(100),
    description TEXT,
    ip_address VARCHAR(45),
    user_id INT,
    ticket_id INT,
    created_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (ticket_id) REFERENCES ticket(id)
);
```

#### 3. Notification

```sql
CREATE TABLE notification (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(100),
    message TEXT,
    notification_type VARCHAR(50),
    is_read BOOLEAN DEFAULT 0,
    user_id INT,
    ticket_id INT,
    created_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (ticket_id) REFERENCES ticket(id)
);
```

#### 4. EmailTemplate

```sql
CREATE TABLE email_template (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) UNIQUE,
    subject VARCHAR(200),
    body TEXT,
    template_type VARCHAR(50),
    variables TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME,
    updated_at DATETIME
);
```

### Modified Tables

#### User Table - New Columns

- `is_active` BOOLEAN
- `phone` VARCHAR(20)
- `department` VARCHAR(50)
- `created_at` DATETIME
- `last_login` DATETIME
- `reset_token` VARCHAR(100)
- `reset_token_expiry` DATETIME

#### Ticket Table - New Columns

- `priority` VARCHAR(20)
- `resolution` TEXT
- `due_date` DATETIME
- `resolved_at` DATETIME
- `closed_at` DATETIME
- `rating` INT
- `feedback` TEXT
- `assigned_to` INT (Foreign Key to user)

#### Category Table - New Columns

- `description` VARCHAR(200)
- `color` VARCHAR(7)
- `is_active` BOOLEAN
- `created_at` DATETIME

#### Comment Table - New Columns

- `is_internal` BOOLEAN
- `updated_at` DATETIME

---

## 🔄 Rollback Procedure

If something goes wrong:

### Option 1: Restore from Backup

```bash
# Stop the application
# Drop the database
mysql -u root -p
DROP DATABASE quickdesk;
CREATE DATABASE quickdesk;
EXIT;

# Restore from backup
mysql -u root -p quickdesk < quickdesk_backup_20250101.sql

# Restore code files
rm -rf * .[^.]*
cp -r ../quickdesk_backup/* .

# Restart application
python app.py
```

### Option 2: Migration Rollback

```bash
# This removes new tables only
python migrate_database.py --rollback

# Note: This won't remove new columns from existing tables
# Use full backup restore for complete rollback
```

---

## 🎯 Verification Tests

Run these tests after migration:

### 1. Authentication Tests

- [ ] Login with existing account
- [ ] Register new account
- [ ] Test forgot password flow
- [ ] Receive password reset email
- [ ] Successfully reset password

### 2. Ticket Tests

- [ ] Create ticket with priority
- [ ] View ticket list
- [ ] Update ticket status
- [ ] Add comment to ticket
- [ ] Upload file attachment
- [ ] View ticket activities

### 3. Notification Tests

- [ ] Create ticket (agents should get notified)
- [ ] Update ticket (creator should get notified)
- [ ] Check notification bell icon
- [ ] Mark notification as read

### 4. Agent Tests

- [ ] Assign ticket to agent
- [ ] Agent receives assignment notification
- [ ] View assigned tickets
- [ ] Add internal note
- [ ] Update ticket status

### 5. Admin Tests

- [ ] View all tickets
- [ ] Manage users
- [ ] Manage categories
- [ ] Export tickets
- [ ] View activity logs

---

## 🐛 Common Issues & Solutions

### Issue 1: Import Errors

```bash
ModuleNotFoundError: No module named 'dotenv'
```

**Solution:**

```bash
pip install python-dotenv pymysql
```

### Issue 2: Database Connection Error

```
sqlalchemy.exc.OperationalError: (pymysql.err.OperationalError) (1045, "Access denied")
```

**Solution:**

- Check .env file for correct credentials
- Ensure MySQL server is running
- Verify database exists

### Issue 3: Column Already Exists Error

```
sqlalchemy.exc.OperationalError: (1060, "Duplicate column name 'priority'")
```

**Solution:**

- Migration already ran
- No action needed
- Or restore from backup and try again

### Issue 4: Notifications Not Showing

**Solution:**

- Check app.py has context_processor registered
- Ensure base.html has notification UI
- Clear browser cache

### Issue 5: File Upload Fails

**Solution:**

```bash
# Create uploads directory
mkdir uploads
chmod 755 uploads
```

---

## 📊 Performance Considerations

### Database Indexes

For better performance with large datasets:

```sql
-- Add indexes for frequently queried fields
CREATE INDEX idx_ticket_status ON ticket(status);
CREATE INDEX idx_ticket_priority ON ticket(priority);
CREATE INDEX idx_ticket_assigned ON ticket(assigned_to);
CREATE INDEX idx_notification_user ON notification(user_id, is_read);
CREATE INDEX idx_activity_ticket ON activity_log(ticket_id);
```

### Cleanup Old Data

```python
# Optional: Clean up old notifications (run periodically)
from datetime import datetime, timedelta
from models import Notification, db

# Delete read notifications older than 30 days
threshold = datetime.utcnow() - timedelta(days=30)
Notification.query.filter(
    Notification.is_read == True,
    Notification.created_at < threshold
).delete()
db.session.commit()
```

---

## 📱 UI Updates Needed

Update your templates to show new features:

### base.html - Add Notification Bell

```html
<!-- Add to navigation -->
<li class="nav-item dropdown">
    <a class="nav-link" href="#" data-bs-toggle="dropdown">
        <i class="fas fa-bell"></i>
        {% if unread_count > 0 %}
        <span class="badge bg-danger">{{ unread_count }}</span>
        {% endif %}
    </a>
    <!-- Dropdown menu -->
</li>
```

### create_ticket.html - Add Priority Field

```html
<div class="mb-3">
    <label for="priority" class="form-label">Priority</label>
    <select class="form-select" id="priority" name="priority" required>
        <option value="Low">Low</option>
        <option value="Medium" selected>Medium</option>
        <option value="High">High</option>
        <option value="Critical">Critical</option>
    </select>
</div>
```

### login.html - Add Forgot Password Link

```html
<div class="text-center mt-3">
    <a href="{{ url_for('password_reset.forgot_password') }}">
        Forgot Password?
    </a>
</div>
```

---

## 📚 Next Steps

1. **Read the Features Guide**
    - Open `FEATURES_GUIDE.md`
    - Learn about each new feature
    - See code examples

2. **Customize Settings**
    - Adjust SLA times in `models.py`
    - Configure file upload limits
    - Customize email templates

3. **Update Routes**
    - Add activity logging
    - Add notifications
    - Use new features

4. **Train Users**
    - Show new features to agents
    - Demonstrate priority system
    - Explain notifications

5. **Monitor Performance**
    - Check database size
    - Monitor notification count
    - Review activity logs

---

## 🆘 Getting Help

If you encounter issues:

1. Check this guide
2. Review `FEATURES_GUIDE.md`
3. Check console error messages
4. Review MySQL error logs
5. Restore from backup if needed

---

## ✅ Update Complete!

Congratulations! Your QuickDesk is now updated to v2.0 with all the new features!

**What's New:**

- 🔐 Better security with password reset
- 📊 Better management with priorities and SLA
- 🔔 Better communication with notifications
- 📁 Better file handling
- 📝 Better audit trail with activity logs
- ⭐ Better feedback with ratings

**Enjoy the enhanced QuickDesk experience!**

---

**Version:** 2.0
**Last Updated:** 2025
