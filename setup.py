"""
QuickDesk Setup Script
Automates the initial setup of the QuickDesk application
"""

import os
import sys
from getpass import getpass


def create_env_file():
    """Create .env file with user input"""
    print("\n" + "=" * 50)
    print("QuickDesk Environment Configuration")
    print("=" * 50)

    if os.path.exists('.env'):
        overwrite = input("\n.env file already exists. Overwrite? (y/n): ").lower()
        if overwrite != 'y':
            print("Skipping .env creation.")
            return

    print("\n📦 Database Configuration")
    db_user = input("MySQL Username (default: root): ").strip() or "root"
    db_password = getpass("MySQL Password: ")
    db_host = input("MySQL Host (default: localhost): ").strip() or "localhost"
    db_name = input("Database Name (default: quickdesk): ").strip() or "quickdesk"

    print("\n📧 Email Configuration (Gmail)")
    email_user = input("Gmail Address: ").strip()
    email_pass = getpass("Gmail App Password: ")

    print("\n🔐 Application Configuration")
    secret_key = input("Secret Key (press Enter for default): ").strip() or "supersecretkey-change-in-production"

    env_content = f"""# Database Configuration
DB_USER={db_user}
DB_PASSWORD={db_password}
DB_HOST={db_host}
DB_NAME={db_name}

# Email Configuration
EMAIL_USER={email_user}
EMAIL_PASS={email_pass}

# Application Secret Key
SECRET_KEY={secret_key}
"""

    with open('.env', 'w') as f:
        f.write(env_content)

    print("\n✅ .env file created successfully!")


def check_dependencies():
    """Check if required Python packages are installed"""
    print("\n" + "=" * 50)
    print("Checking Dependencies")
    print("=" * 50)

    try:
        import flask
        import flask_sqlalchemy
        import flask_login
        import flask_mail
        import pandas
        import openpyxl
        import dotenv
        import pymysql
        print("✅ All required packages are installed!")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e.name}")
        print("\n⚠️ Please install dependencies using:")
        print("   pip install -r requirements.txt")
        return False


def check_mysql_connection():
    """Check MySQL connection"""
    print("\n" + "=" * 50)
    print("Checking MySQL Connection")
    print("=" * 50)

    try:
        import pymysql
        from dotenv import load_dotenv
        load_dotenv()

        connection = pymysql.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '')
        )

        print("✅ MySQL connection successful!")

        # Check if database exists
        cursor = connection.cursor()
        db_name = os.getenv('DB_NAME', 'quickdesk')
        cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")
        result = cursor.fetchone()

        if not result:
            print(f"\n⚠️ Database '{db_name}' does not exist.")
            create_db = input(f"Create database '{db_name}'? (y/n): ").lower()
            if create_db == 'y':
                cursor.execute(f"CREATE DATABASE {db_name}")
                print(f"✅ Database '{db_name}' created successfully!")
        else:
            print(f"✅ Database '{db_name}' exists!")

        connection.close()
        return True

    except Exception as e:
        print(f"❌ MySQL connection failed: {e}")
        return False


def initialize_database():
    """Initialize database tables"""
    print("\n" + "=" * 50)
    print("Initializing Database Tables")
    print("=" * 50)

    try:
        from app import app, db
        with app.app_context():
            db.create_all()
            print("✅ Database tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False


def create_admin_user():
    """Create an admin user"""
    print("\n" + "=" * 50)
    print("Create Admin User")
    print("=" * 50)

    create = input("\nCreate an admin user? (y/n): ").lower()
    if create != 'y':
        return

    try:
        from app import app, db
        from models import User
        from werkzeug.security import generate_password_hash

        username = input("Admin Username: ").strip()
        email = input("Admin Email: ").strip()
        password = getpass("Admin Password: ")

        with app.app_context():
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                print("⚠️ User with this email already exists!")
                return

            hashed_pw = generate_password_hash(password)
            admin = User(username=username, email=email, password=hashed_pw, role='admin')
            db.session.add(admin)
            db.session.commit()

            print("✅ Admin user created successfully!")
            print(f"   Username: {username}")
            print(f"   Email: {email}")

    except Exception as e:
        print(f"❌ Failed to create admin user: {e}")


def main():
    """Main setup function"""
    print("\n" + "=" * 60)
    print("  QuickDesk - Ticket Management System Setup")
    print("=" * 60)

    # Step 1: Create .env file
    create_env_file()

    # Step 2: Check dependencies
    if not check_dependencies():
        print("\n⚠️ Please install dependencies first and run this script again.")
        sys.exit(1)

    # Step 3: Check MySQL connection
    if not check_mysql_connection():
        print("\n⚠️ Please fix MySQL connection issues and run this script again.")
        sys.exit(1)

    # Step 4: Initialize database
    if not initialize_database():
        print("\n⚠️ Database initialization failed.")
        sys.exit(1)

    # Step 5: Create admin user
    create_admin_user()

    print("\n" + "=" * 60)
    print("  Setup Complete! 🎉")
    print("=" * 60)
    print("\n📝 Next Steps:")
    print("   1. Run: python app.py")
    print("   2. Open: http://localhost:5000")
    print("   3. Login with your credentials")
    print("\n⚠️ Remember to:")
    print("   - Never commit the .env file")
    print("   - Change SECRET_KEY in production")
    print("   - Use strong passwords")
    print("\n")


if __name__ == '__main__':
    main()
