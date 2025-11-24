#!/usr/bin/env python3
"""
VPS Database Migration Script
Adds new columns for Masala system to existing production database
Run this on VPS after deploying new code
"""

from app import app, db
from sqlalchemy import inspect, text

def check_column_exists(table_name, column_name):
    """Check if a column exists in a table"""
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def migrate_database():
    """Add missing columns to production database"""
    
    with app.app_context():
        print("=" * 60)
        print("VPS DATABASE MIGRATION")
        print("=" * 60)
        
        # Check if masala table exists
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'masala' not in tables:
            print("\n✅ Creating masala table...")
            db.create_all()
            print("   Masala table created successfully")
        else:
            print("\n✓ Masala table already exists")
        
        # Check and add missing columns to user table
        print("\n📋 Checking user table columns...")
        
        user_columns_to_add = []
        
        # Check sms_count column
        if not check_column_exists('user', 'sms_count'):
            user_columns_to_add.append({
                'name': 'sms_count',
                'sql': 'ALTER TABLE user ADD COLUMN sms_count INTEGER DEFAULT 0'
            })
        
        if user_columns_to_add:
            for col in user_columns_to_add:
                print(f"\n✅ Adding column: {col['name']}")
                try:
                    db.session.execute(text(col['sql']))
                    db.session.commit()
                    print(f"   ✓ Successfully added {col['name']}")
                except Exception as e:
                    print(f"   ⚠ Error adding {col['name']}: {e}")
                    db.session.rollback()
        else:
            print("   ✓ All user columns exist")
        
        # Check sms_log table
        if 'sms_log' not in tables:
            print("\n✅ Creating sms_log table...")
            db.create_all()
            print("   SMS log table created successfully")
        else:
            print("\n✓ SMS log table already exists")
        
        print("\n" + "=" * 60)
        print("MIGRATION COMPLETED")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Restart the application: sudo systemctl restart madrasha")
        print("2. Check application status: sudo systemctl status madrasha")
        print("3. Test login with all user roles")
        print("=" * 60)

if __name__ == '__main__':
    migrate_database()
