# migrate_database.py
"""
Database Migration Script for QuickDesk v2.0
Adds new features to existing database
"""

from app import app, db
from models import User, Ticket, Category, Comment, Attachment, ActivityLog, Notification, EmailTemplate
from datetime import datetime


def backup_reminder():
    """Remind user to backup database"""
    print("\n" + "=" * 60)
    print("⚠️  IMPORTANT: BACKUP YOUR DATABASE BEFORE PROCEEDING!")
    print("=" * 60)
    print("\nRun this command to backup:")
    print("mysqldump -u root -p quickdesk > quickdesk_backup_$(date +%Y%m%d).sql")
    print("\n")

    response = input("Have you backed up your database? (yes/no): ").lower()
    if response != 'yes':
        print("\n❌ Migration cancelled. Please backup your database first!")
        return False
    return True


def migrate_database():
    """Run database migration"""

    if not backup_reminder():
        return

    print("\n" + "=" * 60)
    print("Starting Database Migration...")
    print("=" * 60)

    with app.app_context():
        try:
            # Create all tables (will add new columns to existing tables)
            print("\n📦 Creating/updating database tables...")
            db.create_all()
            print("✅ Database tables updated successfully!")

            # Update existing tickets with default priority
            print("\n📝 Updating existing tickets...")
            tickets_updated = 0
            for ticket in Ticket.query.all():
                if not hasattr(ticket, 'priority') or ticket.priority is None:
                    ticket.priority = 'Medium'
                    if ticket.due_date is None:
                        ticket.calculate_due_date()
                    tickets_updated += 1

            if tickets_updated > 0:
                db.session.commit()
                print(f"✅ Updated {tickets_updated} tickets with default priority!")

            # Update existing categories
            print("\n🏷️  Updating existing categories...")
            categories_updated = 0
            for category in Category.query.all():
                if not hasattr(category, 'is_active') or category.is_active is None:
                    category.is_active = True
                    category.color = '#007bff'
                    categories_updated += 1

            if categories_updated > 0:
                db.session.commit()
                print(f"✅ Updated {categories_updated} categories!")

            # Update existing users
            print("\n👤 Updating existing users...")
            users_updated = 0
            for user in User.query.all():
                if not hasattr(user, 'is_active') or user.is_active is None:
                    user.is_active = True
                    users_updated += 1

            if users_updated > 0:
                db.session.commit()
                print(f"✅ Updated {users_updated} users!")

            # Create default email templates
            print("\n📧 Creating default email templates...")
            create_default_templates()

            print("\n" + "=" * 60)
            print("✅ Migration completed successfully!")
            print("=" * 60)
            print("\nNew Features Added:")
            print("  ✓ Password Reset System")
            print("  ✓ Ticket Priority & SLA")
            print("  ✓ Ticket Assignment")
            print("  ✓ Enhanced File Management")
            print("  ✓ Activity Logging")
            print("  ✓ Notification System")
            print("  ✓ Rating & Feedback")
            print("  ✓ Internal Notes")
            print("  ✓ Email Templates")
            print("\nNext Steps:")
            print("  1. Test the application: python app.py")
            print("  2. Review FEATURES_GUIDE.md for usage instructions")
            print("  3. Update your routes to use new features")
            print("\n")

        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            print("Please restore from backup and check the error.")
            db.session.rollback()


def create_default_templates():
    """Create default email templates"""

    templates = [
        {
            'name': 'Ticket Created',
            'subject': '🎫 Ticket #{ticket_id} Created - {subject}',
            'body': '''Hello {username},

Your ticket has been created successfully!

Ticket ID: #{ticket_id}
Subject: {subject}
Priority: {priority}
Status: {status}

We will respond to your ticket according to our SLA based on priority.

You can track your ticket status at any time by logging into QuickDesk.

Regards,
QuickDesk Support Team''',
            'template_type': 'ticket_created',
            'variables': '["username", "ticket_id", "subject", "priority", "status"]'
        },
        {
            'name': 'Status Update',
            'subject': '📢 Ticket #{ticket_id} Status Updated',
            'body': '''Hello {username},

Your ticket status has been updated.

Ticket ID: #{ticket_id}
Subject: {subject}
New Status: {status}

{additional_message}

Regards,
QuickDesk Support Team''',
            'template_type': 'status_update',
            'variables': '["username", "ticket_id", "subject", "status", "additional_message"]'
        },
        {
            'name': 'Ticket Assigned',
            'subject': '👤 Ticket #{ticket_id} Assigned to You',
            'body': '''Hello {agent_name},

A new ticket has been assigned to you.

Ticket ID: #{ticket_id}
Subject: {subject}
Priority: {priority}
Created by: {creator_name}

Please review and respond according to the SLA.

Regards,
QuickDesk System''',
            'template_type': 'assignment',
            'variables': '["agent_name", "ticket_id", "subject", "priority", "creator_name"]'
        },
        {
            'name': 'Ticket Resolved',
            'subject': '✅ Ticket #{ticket_id} Resolved',
            'body': '''Hello {username},

Your ticket has been resolved!

Ticket ID: #{ticket_id}
Subject: {subject}
Resolution: {resolution}

If you're satisfied with the resolution, please rate your experience.
If you need further assistance, please reply to this ticket.

Regards,
QuickDesk Support Team''',
            'template_type': 'ticket_resolved',
            'variables': '["username", "ticket_id", "subject", "resolution"]'
        }
    ]

    created = 0
    for template_data in templates:
        existing = EmailTemplate.query.filter_by(name=template_data['name']).first()
        if not existing:
            template = EmailTemplate(**template_data)
            db.session.add(template)
            created += 1

    if created > 0:
        db.session.commit()
        print(f"✅ Created {created} default email templates!")
    else:
        print("✅ Email templates already exist!")


def rollback_migration():
    """Rollback migration (use with caution!)"""
    print("\n⚠️  WARNING: This will remove all new tables!")
    response = input("Are you sure you want to rollback? (yes/no): ").lower()

    if response != 'yes':
        print("Rollback cancelled.")
        return

    with app.app_context():
        try:
            # Drop new tables
            print("Dropping new tables...")
            Notification.__table__.drop(db.engine, checkfirst=True)
            ActivityLog.__table__.drop(db.engine, checkfirst=True)
            Attachment.__table__.drop(db.engine, checkfirst=True)
            EmailTemplate.__table__.drop(db.engine, checkfirst=True)

            print("✅ Rollback completed!")
            print("⚠️  Note: Modified columns in existing tables were not removed.")
            print("    Restore from backup for complete rollback.")

        except Exception as e:
            print(f"❌ Rollback failed: {e}")


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--rollback':
        rollback_migration()
    else:
        migrate_database()
