# QuickDesk - Ticket Management System v2.0

A comprehensive, enterprise-grade helpdesk ticket management system built with Flask, supporting multiple user roles (
End Users, Agents, and Admins).

## 🌟 What's New in v2.0

- 🔐 **Password Reset System** - Secure email-based password recovery
- 📊 **Priority System** - Critical, High, Medium, Low priorities with SLA tracking
- 👥 **Ticket Assignment** - Assign tickets to specific agents
- 📁 **Enhanced File Management** - Multiple file uploads with validation
- 📝 **Activity Logging** - Complete audit trail for all actions
- 🔔 **Notification System** - Real-time in-app notifications
- ⏰ **SLA Tracking** - Automatic due dates based on priority
- ⭐ **Rating & Feedback** - Collect user feedback on resolved tickets
- 🔒 **Internal Notes** - Private agent-only comments
- 📧 **Email Templates** - Customizable email notifications

## 📚 Documentation

- **[Quick Start Guide](QUICKSTART.md)** - Get up and running in 5 minutes
- **[Features Guide](FEATURES_GUIDE.md)** - Detailed documentation of all features
- **[Update Guide](UPDATE_GUIDE.md)** - Upgrade from v1.0 to v2.0
- **[Quick Reference](QUICK_REFERENCE.md)** - Handy reference card for daily use
- **[Summary](SUMMARY.md)** - Complete overview of changes
- **[Fixes](FIXES.md)** - List of all bug fixes and improvements

## Features

### 🎯 Core Functionality

- **Multi-role Support**: End Users, Agents, and Admins with role-based access control
- **Ticket Management**: Create, view, update, and track support tickets
- **Category System**: Organize tickets by categories
- **Comment System**: Add comments and updates to tickets
- **File Attachments**: Upload and attach files to tickets (15+ file types supported)
- **Email Notifications**: Automated email notifications for ticket updates
- **Excel Export**: Export tickets data to Excel format (Admin only)
- **Status Tracking**: Track ticket status (Open, In Progress, Resolved, Closed)
- **Priority System**: Critical, High, Medium, Low priority levels
- **SLA Tracking**: Automatic due dates and overdue detection
- **Activity Logging**: Complete audit trail of all actions
- **Notifications**: In-app notifications for important events
- **Password Reset**: Secure token-based password recovery

### 👥 User Roles

- **End User**: Create and track their own tickets, upload files, rate support
- **Agent**: View all tickets, update status, add comments, add internal notes, assign tickets
- **Admin**: Full system access, manage users, categories, export data, view activity logs

## Installation

### Quick Installation (Recommended) ⚡

**Windows:**

```bash
install.bat
venv\Scripts\activate
python setup.py
```

**Linux/Mac:**

```bash
chmod +x install.sh
./install.sh
source venv/bin/activate
python setup.py
```

The setup wizard will guide you through configuration!

### Manual Installation

#### Prerequisites

- Python 3.8 or higher
- MySQL Server
- pip (Python package manager)

#### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd quickdesk
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Create a `.env` file in the root directory:
   ```env
   # Database Configuration
   DB_USER=your_mysql_username
   DB_PASSWORD=your_mysql_password
   DB_HOST=localhost
   DB_NAME=quickdesk
   
   # Email Configuration
   EMAIL_USER=your_email@gmail.com
   EMAIL_PASS=your_app_password
   
   # Application Secret Key
   SECRET_KEY=your-secret-key-here
   ```

5. **Create MySQL Database**
   ```sql
   CREATE DATABASE quickdesk;
   ```

6. **Initialize the database**
   ```bash
   python init_db.py
   ```

7. **Create an admin user (optional)**
   ```bash
   python create_admin.py
   ```

8. **Run the application**
   ```bash
   python app.py
   ```

9. **Access the application**

   Open your browser and navigate to: `http://localhost:5000`

## Upgrading from v1.0

If you have an existing QuickDesk v1.0 installation:

```bash
# 1. Backup your database
mysqldump -u root -p quickdesk > backup.sql

# 2. Pull latest code
git pull origin main

# 3. Install new dependencies
pip install -r requirements.txt --upgrade

# 4. Run migration
python migrate_database.py

# 5. Start application
python app.py
```

**See [UPDATE_GUIDE.md](UPDATE_GUIDE.md) for detailed upgrade instructions.**

## Project Structure

```
quickdesk/
├── routes/                    # Application routes
│   ├── auth_routes.py         # Authentication (login, register, logout)
│   ├── user_routes.py         # User dashboard and ticket creation
│   ├── agent_routes.py        # Agent dashboard and ticket management
│   ├── admin_routes.py        # Admin dashboard and system management
│   ├── enduser.py             # End user specific routes
│   └── password_reset_routes.py # Password reset functionality
├── templates/                 # HTML templates
│   ├── forgot_password.html   # Password reset request
│   └── reset_password.html    # Password reset form
├── static/                    # CSS, JS, and static assets
│   ├── css/
│   └── js/
├── utils/                     # Utility functions
│   ├── auth_decorator.py      # Authentication decorators
│   ├── send_email.py          # Email sending functionality
│   ├── notification_helper.py # Notification management
│   ├── activity_logger.py     # Activity logging
│   └── file_handler.py        # File upload handling
├── uploads/                   # User uploaded files
├── app.py                     # Application entry point
├── config.py                  # Application configuration
├── models.py                  # Database models
├── extensions.py              # Flask extensions initialization
├── requirements.txt           # Python dependencies
├── setup.py                   # Interactive setup wizard
├── migrate_database.py        # Database migration script
└── .env                       # Environment variables (not in git)
```

## Database Models

- **User**: Stores user information, authentication, and password reset tokens
- **Ticket**: Stores support tickets with priority, SLA, and assignment
- **Category**: Ticket categories with colors and descriptions
- **Comment**: Ticket comments and updates (including internal notes)
- **Attachment**: File attachments with metadata
- **ActivityLog**: Audit trail of all user actions
- **Notification**: In-app notifications for users
- **EmailTemplate**: Customizable email templates

## Email Configuration

For Gmail, you need to:

1. Enable 2-Factor Authentication
2. Generate an App Password
3. Use the App Password in the `EMAIL_PASS` variable

**Detailed instructions:** See [QUICKSTART.md](QUICKSTART.md#getting-gmail-app-password)

## Security Notes

- ✅ Never commit the `.env` file to version control
- ✅ Change the `SECRET_KEY` in production
- ✅ Use strong passwords for database and email
- ✅ Keep dependencies updated
- ✅ Regular database backups
- ✅ Enable HTTPS in production

## Troubleshooting

### Database Connection Issues

- Ensure MySQL server is running
- Verify database credentials in `.env`
- Check if the database exists

### Email Not Sending

- Verify email credentials
- Check if 2FA and App Password are configured for Gmail
- Ensure firewall allows SMTP connections

### Import Errors

- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Activate the virtual environment

### Linter Errors

The linter errors you see are IDE-related and will resolve once dependencies are installed:

```bash
pip install python-dotenv pymysql flask flask-sqlalchemy flask-login flask-mail
```

**More troubleshooting:** See [UPDATE_GUIDE.md](UPDATE_GUIDE.md#common-issues--solutions)

## Usage Examples

### Creating a Ticket with Priority

```python
from utils.notification_helper import notify_ticket_created
from utils.activity_logger import log_ticket_created

ticket = Ticket(
    subject="Server Down",
    description="Production server is not responding",
    priority="Critical",
    category_id=1,
    user_id=current_user.id
)
ticket.calculate_due_date()  # Auto-calculates based on priority
db.session.add(ticket)
db.session.commit()

log_ticket_created(current_user.id, ticket)
notify_ticket_created(ticket)
```

### Assigning a Ticket

```python
from utils.notification_helper import notify_ticket_assigned

ticket.assigned_to = agent_id
db.session.commit()

agent = User.query.get(agent_id)
notify_ticket_assigned(ticket, agent)
```

**More examples:** See [FEATURES_GUIDE.md](FEATURES_GUIDE.md)

## Testing

```bash
# Run the application in debug mode
python app.py

# Access at http://localhost:5000

# Default admin credentials (if using create_admin.py):
# Email: admin@example.com
# Password: admin123
```

**⚠️ Change default credentials immediately after first login!**

## Performance Tips

1. **Add database indexes** for large datasets (see [UPDATE_GUIDE.md](UPDATE_GUIDE.md#performance-considerations))
2. **Clean up old notifications** regularly
3. **Monitor database size** and implement archiving
4. **Use connection pooling** in production
5. **Enable caching** for frequently accessed data

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Create a Pull Request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:

- Check the [documentation](FEATURES_GUIDE.md)
- Review [troubleshooting guide](UPDATE_GUIDE.md#troubleshooting)
- Create an issue in the repository
- Contact the development team

## Credits

**Version:** 2.0  
**Release Date:** 2025  
**Status:** Production Ready

Built with ❤️ using Flask, SQLAlchemy, and Bootstrap.

---

## Quick Links

- 📖 [Quick Start Guide](QUICKSTART.md)
- 🚀 [Features Guide](FEATURES_GUIDE.md)
- 🔄 [Update Guide](UPDATE_GUIDE.md)
- 📋 [Quick Reference](QUICK_REFERENCE.md)
- 📊 [Summary](SUMMARY.md)
- 🔧 [Fixes](FIXES.md)

**Happy Ticketing! 🎫**
