"""
Seed database with sample data for testing
"""
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from faker import Faker
from src.database.connection import DatabaseConnection
from src.services.auth_service import AuthService

load_dotenv()
fake = Faker()


def seed_users(auth_service, count=10):
    """Create sample users"""
    print(f"Creating {count} sample users...")
    
    user_ids = []
    for i in range(count):
        username = f"user{i+1}"
        email = f"user{i+1}@example.com"
        
        user_id = auth_service.create_user(
            username=username,
            email=email,
            password="password123",
            first_name=fake.first_name(),
            last_name=fake.last_name()
        )
        
        if user_id:
            user_ids.append(user_id)
    
    print(f"✓ Created {len(user_ids)} users")
    return user_ids


def seed_items(db, user_ids, count=50):
    """Create sample items"""
    print(f"Creating {count} sample items...")
    
    item_types = ['document', 'file', 'resource', 'dataset', 'report']
    
    query = """
    INSERT INTO items (name, item_type, owner_id, metadata, is_public)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING id
    """
    
    item_ids = []
    for i in range(count):
        name = f"{fake.catch_phrase()} {i+1}"
        item_type = fake.random_element(item_types)
        owner_id = fake.random_element(user_ids)
        is_public = fake.boolean(chance_of_getting_true=30)
        
        result = db.execute_query(
            query,
            (name, item_type, owner_id, None, is_public),
            fetch_one=True
        )
        
        if result:
            item_ids.append(result['id'])
    
    print(f"✓ Created {len(item_ids)} items")
    return item_ids


def assign_roles(db, user_ids):
    """Assign roles to users"""
    print("Assigning roles to users...")
    
    # Get role IDs
    roles = db.execute_query("SELECT id, name FROM roles")
    role_map = {r['name']: r['id'] for r in roles}
    
    query = """
    INSERT INTO user_roles (user_id, role_id, granted_by)
    VALUES (%s, %s, %s)
    ON CONFLICT (user_id, role_id) DO NOTHING
    """
    
    # Assign roles to users
    for user_id in user_ids:
        role_name = fake.random_element(['admin', 'editor', 'viewer', 'contributor'])
        role_id = role_map.get(role_name)
        
        if role_id:
            db.execute_update(query, (user_id, role_id, 1))
    
    print("✓ Roles assigned")


def seed_database():
    """Main seeding function"""
    print("Seeding database with sample data...\n")
    
    db = DatabaseConnection()
    db.initialize()
    
    auth_service = AuthService(db)
    
    # Create users
    user_ids = seed_users(auth_service, count=10)
    
    # Create items
    item_ids = seed_items(db, user_ids, count=50)
    
    # Assign roles
    assign_roles(db, user_ids)
    
    print("\n✅ Database seeding complete!")
    print(f"   - {len(user_ids)} users created")
    print(f"   - {len(item_ids)} items created")
    print(f"   - Roles assigned to users")
    
    db.close()


if __name__ == '__main__':
    seed_database()

