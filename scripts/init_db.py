"""
Database initialization script
Creates all tables and inserts seed data
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from src.database.connection import DatabaseConnection
from src.database.models import SCHEMA_SQL

load_dotenv()


def init_database():
    """Initialize database schema"""
    print("Initializing database...")
    
    db = DatabaseConnection()
    db.initialize()
    
    # Execute schema creation
    with db.get_cursor(commit=True) as cursor:
        cursor.execute(SCHEMA_SQL)
        print("✓ Database schema created")
    
    # Insert default roles
    default_roles = [
        ('admin', 'Full system access', None),
        ('editor', 'Can edit and manage items', None),
        ('viewer', 'Read-only access', None),
        ('contributor', 'Can create and edit own items', None),
    ]
    
    with db.get_cursor(commit=True) as cursor:
        for name, description, parent_id in default_roles:
            cursor.execute(
                "INSERT INTO roles (name, description, parent_role_id) VALUES (%s, %s, %s) ON CONFLICT (name) DO NOTHING",
                (name, description, parent_id)
            )
        print("✓ Default roles created")
    
    # Insert default permissions
    default_permissions = [
        ('read_item', 'items', 'read', 'Read item data'),
        ('write_item', 'items', 'write', 'Modify item data'),
        ('delete_item', 'items', 'delete', 'Delete items'),
        ('create_item', 'items', 'create', 'Create new items'),
        ('manage_users', 'users', 'manage', 'Manage user accounts'),
        ('manage_roles', 'roles', 'manage', 'Manage roles and permissions'),
    ]
    
    with db.get_cursor(commit=True) as cursor:
        for name, resource, action, description in default_permissions:
            cursor.execute(
                "INSERT INTO permissions (name, resource, action, description) VALUES (%s, %s, %s, %s) ON CONFLICT (resource, action) DO NOTHING",
                (name, resource, action, description)
            )
        print("✓ Default permissions created")
    
    print("\n✅ Database initialization complete!")
    
    db.close()


if __name__ == '__main__':
    init_database()

