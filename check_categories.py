from app import app
from models import Category

with app.app_context():
    categories = Category.query.all()

    print("\n" + "=" * 60)
    print(f"  Categories in Database")
    print("=" * 60)

    if categories:
        print(f"\n✅ Total Categories: {len(categories)}\n")
        for i, cat in enumerate(categories, 1):
            print(f"  {i}. {cat.name} (ID: {cat.id}, Active: {cat.is_active})")
    else:
        print("\n❌ No categories found!")
        print("Run: python add_default_categories.py\n")

    print("\n" + "=" * 60 + "\n")
