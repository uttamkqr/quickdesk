from app import app
from models import db, Category

# Default categories for ticket system
default_categories = [
    {
        'name': 'Technical Support',
        'description': 'Hardware, Software, and Technical Issues',
        'color': '#dc3545'  # Red
    },
    {
        'name': 'Billing',
        'description': 'Payment and Billing Related Queries',
        'color': '#28a745'  # Green
    },
    {
        'name': 'Account',
        'description': 'Account Access and Settings',
        'color': '#007bff'  # Blue
    },
    {
        'name': 'General Inquiry',
        'description': 'General Questions and Information',
        'color': '#6c757d'  # Gray
    },
    {
        'name': 'Bug Report',
        'description': 'Report Software Bugs and Issues',
        'color': '#ffc107'  # Yellow
    },
    {
        'name': 'Feature Request',
        'description': 'Request New Features',
        'color': '#17a2b8'  # Cyan
    }
]

with app.app_context():
    print("\n" + "=" * 60)
    print("Adding Default Categories to QuickDesk")
    print("=" * 60 + "\n")

    added = 0
    skipped = 0

    for cat_data in default_categories:
        # Check if category already exists
        existing = Category.query.filter_by(name=cat_data['name']).first()

        if existing:
            print(f"⚠️  {cat_data['name']} - Already exists")
            skipped += 1
        else:
            # Add new category
            category = Category(
                name=cat_data['name'],
                description=cat_data['description'],
                color=cat_data['color'],
                is_active=True
            )
            db.session.add(category)
            print(f"✅ {cat_data['name']} - Added")
            added += 1

    # Commit all changes
    if added > 0:
        db.session.commit()

    print("\n" + "=" * 60)
    print(f"Summary: {added} categories added, {skipped} skipped")
    print("=" * 60 + "\n")

    # Display all categories
    all_categories = Category.query.all()
    print("Current Categories in Database:")
    print("-" * 60)
    for cat in all_categories:
        status = "Active" if cat.is_active else "Inactive"
        print(f"  • {cat.name} ({status}) - {cat.description}")
    print("-" * 60)
    print(f"\n✅ Total Categories: {len(all_categories)}\n")
