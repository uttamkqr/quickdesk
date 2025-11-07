# QuickDesk - Quick Start Guide

Get QuickDesk up and running in 5 minutes!

## Prerequisites

✅ Python 3.8+ installed  
✅ MySQL Server running  
✅ Gmail account with App Password (for email notifications)

## Installation (Choose One)

### Option A: Automated Setup (Recommended) ⚡

**Windows:**

```bash
# 1. Run installation script
install.bat

# 2. Activate virtual environment
venv\Scripts\activate

# 3. Run setup wizard
python setup.py
```

**Linux/Mac:**

```bash
# 1. Make script executable
chmod +x install.sh

# 2. Run installation script
./install.sh

# 3. Activate virtual environment
source venv/bin/activate

# 4. Run setup wizard
python setup.py
```

The setup wizard will:

- Help you configure the `.env` file
- Check dependencies
- Test MySQL connection
- Create database
- Initialize tables
- Create admin user

### Option B: Manual Setup 🔧

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment (Windows)
venv\Scripts\activate
# OR (Linux/Mac)
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy and edit environment file
cp .env.example .env
# Edit .env with your credentials

# 5. Create MySQL database
mysql -u root -p
CREATE DATABASE quickdesk;
EXIT;

# 6. Initialize database tables
python init_db.py

# 7. Create admin user
python create_admin.py

# 8. Run the application
python app.py
```

## Configuration

Edit the `.env` file with your credentials:

```env
# Database
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_NAME=quickdesk

# Email (Gmail)
EMAIL_USER=your_email@gmail.com
EMAIL_PASS=your_app_password

# Secret Key
SECRET_KEY=random-secret-key-here
```

### Getting Gmail App Password

1. Go to Google Account Settings
2. Security → 2-Step Verification (enable if not enabled)
3. App Passwords → Select "Mail" and "Windows Computer"
4. Copy the generated 16-character password
5. Use this in `EMAIL_PASS`

## Running the Application

```bash
# Make sure virtual environment is activated
python app.py
```

Open browser: `http://localhost:5000`

## Default Admin Login

If you used `create_admin.py` without changes:

- **Email:** admin@example.com
- **Password:** admin123

⚠️ **Change these credentials immediately after first login!**

## User Roles

### End User

- Create support tickets
- Track ticket status
- Add comments
- Upload attachments

### Agent

- View all tickets
- Update ticket status
- Add comments and updates
- Filter by status

### Admin

- All agent permissions
- Manage users and roles
- Manage categories
- Export tickets to Excel
- View analytics dashboard

## Common Issues & Solutions

### "Access Denied" Database Error

```bash
# Check MySQL credentials in .env
# Ensure MySQL server is running
```

### "Module not found" Error

```bash
# Install dependencies
pip install -r requirements.txt
```

### Email Not Sending

```bash
# Verify EMAIL_USER and EMAIL_PASS in .env
# Use Gmail App Password, not regular password
# Check internet connection
```

### Port Already in Use

```bash
# Change port in app.py
app.run(debug=True, port=5001)
```

## Next Steps

1. **Login** with admin credentials
2. **Create categories** (Technical, Billing, etc.)
3. **Add users** or let them register
4. **Assign roles** (Admin → Users page)
5. **Start creating tickets!**

## File Structure Quick Reference

```
quickdesk/
├── app.py              # Main application
├── config.py           # Configuration
├── models.py           # Database models
├── routes/             # Application routes
├── templates/          # HTML templates
├── static/             # CSS, JS
└── .env               # Your credentials (don't commit!)
```

## Useful Commands

```bash
# Start application
python app.py

# Initialize database
python init_db.py

# Create admin user
python create_admin.py

# Access MySQL console
mysql -u root -p quickdesk

# Deactivate virtual environment
deactivate
```

## Testing the Application

1. **Register** a new end user
2. **Create** a test ticket
3. **Login as agent** and update status
4. **Check email** for notifications
5. **Login as admin** and view dashboard

## Production Deployment Tips

- Change `SECRET_KEY` to a strong random value
- Set `debug=False` in `app.py`
- Use environment-specific `.env` files
- Set up proper web server (nginx/Apache)
- Use WSGI server (gunicorn/uwsgi)
- Enable HTTPS
- Regular database backups

## Getting Help

- Check `README.md` for detailed documentation
- See `FIXES.md` for recent changes
- Review error messages in terminal
- Check MySQL and Python logs

## Security Reminders

🔒 Never commit `.env` to version control  
🔒 Use strong passwords for all accounts  
🔒 Change default admin credentials  
🔒 Keep dependencies updated  
🔒 Use HTTPS in production

---

**Ready to start?** Run the installation script and follow the prompts! 🚀
