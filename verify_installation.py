#!/usr/bin/env python
"""
QuickDesk Installation Verification Script
Checks all dependencies, configurations, and potential issues
"""

import sys
import os


def check_section(title):
    """Print section header"""
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print('=' * 60)


def check_python_version():
    """Check Python version"""
    check_section("Python Version")
    version = sys.version_info
    print(f"Python Version: {version.major}.{version.minor}.{version.micro}")

    if version.major >= 3 and version.minor >= 8:
        print("✅ Python version is compatible (3.8+)")
        return True
    else:
        print("❌ Python version is too old. Requires 3.8+")
        return False


def check_dependencies():
    """Check if all required packages are installed"""
    check_section("Checking Dependencies")

    required_packages = {
        'flask': 'Flask',
        'flask_sqlalchemy': 'Flask-SQLAlchemy',
        'flask_login': 'Flask-Login',
        'flask_mail': 'Flask-Mail',
        'werkzeug': 'Werkzeug',
        'pandas': 'Pandas',
        'openpyxl': 'OpenPyXL',
        'dotenv': 'python-dotenv',
        'pymysql': 'PyMySQL'
    }

    all_installed = True
    for package, name in required_packages.items():
        try:
            __import__(package)
            print(f"✅ {name} - Installed")
        except ImportError:
            print(f"❌ {name} - NOT INSTALLED")
            all_installed = False

    return all_installed


def check_env_file():
    """Check if .env file exists and has required variables"""
    check_section("Environment Configuration")

    if not os.path.exists('.env'):
        print("⚠️  .env file not found!")
        print("   Create it from .env.example:")
        print("   cp .env.example .env")
        return False

    print("✅ .env file exists")

    required_vars = [
        'DB_USER',
        'DB_PASSWORD',
        'DB_HOST',
        'DB_NAME',
        'EMAIL_USER',
        'EMAIL_PASS',
        'SECRET_KEY'
    ]

    from dotenv import load_dotenv
    load_dotenv()

    missing_vars = []
    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var} - Set")
        else:
            print(f"⚠️  {var} - Not set")
            missing_vars.append(var)

    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing_vars)}")
        return False

    return True


def check_app_imports():
    """Check if application files can be imported"""
    check_section("Application Files")

    try:
        from app import app
        print("✅ app.py - OK")
    except Exception as e:
        print(f"❌ app.py - Error: {e}")
        return False

    try:
        from config import Config
        print("✅ config.py - OK")
    except Exception as e:
        print(f"❌ config.py - Error: {e}")
        return False

    try:
        from models import User, Ticket, Category, Comment
        print("✅ models.py - OK (basic models)")
    except Exception as e:
        print(f"❌ models.py - Error: {e}")
        return False

    try:
        from models import Attachment, ActivityLog, Notification, EmailTemplate
        print("✅ models.py - OK (new models)")
    except Exception as e:
        print(f"⚠️  models.py - New models error: {e}")

    try:
        from extensions import db, mail, login_manager
        print("✅ extensions.py - OK")
    except Exception as e:
        print(f"❌ extensions.py - Error: {e}")
        return False

    return True


def check_routes():
    """Check if route files can be imported"""
    check_section("Route Files")

    routes = [
        'routes.auth_routes',
        'routes.user_routes',
        'routes.agent_routes',
        'routes.admin_routes',
        'routes.enduser',
        'routes.password_reset_routes'
    ]

    all_ok = True
    for route in routes:
        try:
            __import__(route)
            print(f"✅ {route} - OK")
        except Exception as e:
            print(f"⚠️  {route} - Error: {e}")
            all_ok = False

    return all_ok


def check_utilities():
    """Check if utility files can be imported"""
    check_section("Utility Files")

    utilities = [
        'utils.send_email',
        'utils.auth_decorator',
        'utils.notification_helper',
        'utils.activity_logger',
        'utils.file_handler'
    ]

    all_ok = True
    for util in utilities:
        try:
            __import__(util)
            print(f"✅ {util} - OK")
        except Exception as e:
            print(f"⚠️  {util} - Error: {e}")
            all_ok = False

    return all_ok


def check_directories():
    """Check if required directories exist"""
    check_section("Required Directories")

    directories = ['templates', 'static', 'routes', 'utils', 'uploads']

    all_exist = True
    for directory in directories:
        if os.path.exists(directory):
            print(f"✅ {directory}/ - Exists")
        else:
            print(f"⚠️  {directory}/ - Missing")
            all_exist = False

    return all_exist


def check_database_connection():
    """Check if database connection can be established"""
    check_section("Database Connection")

    try:
        import pymysql
        from dotenv import load_dotenv
        load_dotenv()

        connection = pymysql.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '')
        )
        print("✅ MySQL connection successful")

        cursor = connection.cursor()
        db_name = os.getenv('DB_NAME', 'quickdesk')
        cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")
        result = cursor.fetchone()

        if result:
            print(f"✅ Database '{db_name}' exists")
        else:
            print(f"⚠️  Database '{db_name}' does not exist")
            print(f"   Create it with: CREATE DATABASE {db_name};")

        connection.close()
        return True

    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("   Check your .env file settings")
        return False


def print_summary(results):
    """Print summary of checks"""
    check_section("Summary")

    passed = sum(results.values())
    total = len(results)

    print(f"\nChecks Passed: {passed}/{total}")

    if passed == total:
        print("\n✅ ALL CHECKS PASSED! Your QuickDesk installation is ready!")
        print("\nNext steps:")
        print("  1. Initialize database: python init_db.py")
        print("  2. Create admin user: python create_admin.py")
        print("  3. Start application: python app.py")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  - Install dependencies: pip install -r requirements.txt")
        print("  - Create .env file: cp .env.example .env")
        print("  - Configure .env with your settings")
        print("  - Ensure MySQL is running")


def main():
    """Run all verification checks"""
    print("\n" + "=" * 60)
    print("  QuickDesk v2.0 - Installation Verification")
    print("=" * 60)

    results = {
        'Python Version': check_python_version(),
        'Dependencies': check_dependencies(),
        'Environment': check_env_file(),
        'Application': check_app_imports(),
        'Routes': check_routes(),
        'Utilities': check_utilities(),
        'Directories': check_directories(),
        'Database': check_database_connection()
    }

    print_summary(results)

    return all(results.values())


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
