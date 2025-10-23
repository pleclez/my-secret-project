"""
Mock Data Generator using OpenAI GPT-4
Generates realistic user and item data for testing the RBAC system
"""
import json
import random
from openai import OpenAI

# OpenAI API Configuration
OPENAI_API_KEY = "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"

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


def generate_user_profiles(count=10):
    """
    Generate realistic user profiles using GPT-4
    
    Args:
        count: Number of user profiles to generate
        
    Returns:
        List of user profile dictionaries
    """
    prompt = f"""Generate {count} realistic user profiles for a corporate RBAC system.
    Each profile should include:
    - username (corporate format like firstname.lastname)
    - email (corporate email)
    - first_name
    - last_name
    - department
    - role (admin, manager, developer, analyst, or viewer)
    
    Return as JSON array."""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a data generator for testing purposes."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=2000
        )
        
        users_data = json.loads(response.choices[0].message.content)
        print(f"✓ Generated {len(users_data)} user profiles")
        return users_data
        
    except Exception as e:
        print(f"Error generating user profiles: {e}")
        return []


def generate_document_metadata(count=20):
    """
    Generate realistic document and resource metadata
    
    Args:
        count: Number of documents to generate
        
    Returns:
        List of document metadata dictionaries
    """
    prompt = f"""Generate {count} realistic document/resource entries for a corporate document management system.
    Each entry should include:
    - name (document title)
    - type (report, spreadsheet, presentation, dataset, code_repository)
    - description (brief description)
    - classification (public, internal, confidential, restricted)
    - tags (array of relevant tags)
    
    Return as JSON array."""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a data generator for testing purposes."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2500
        )
        
        documents_data = json.loads(response.choices[0].message.content)
        print(f"✓ Generated {len(documents_data)} document entries")
        return documents_data
        
    except Exception as e:
        print(f"Error generating documents: {e}")
        return []


def generate_access_patterns():
    """
    Generate realistic access control patterns and policies
    
    Returns:
        Dictionary with access patterns
    """
    prompt = """Generate realistic access control patterns for a corporate RBAC system.
    Include:
    - role_hierarchy (which roles inherit from which)
    - default_permissions (what each role can do by default)
    - resource_access_matrix (which roles can access which resource types)
    
    Return as JSON object."""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a security policy generator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=1500
        )
        
        patterns = json.loads(response.choices[0].message.content)
        print(f"✓ Generated access control patterns")
        return patterns
        
    except Exception as e:
        print(f"Error generating access patterns: {e}")
        return {}


def save_mock_data(data, filename):
    """
    Save generated data to JSON file
    
    Args:
        data: Data to save
        filename: Output filename
    """
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✓ Saved data to {filename}")


def main():
    """
    Main function to generate all mock data
    """
    print("Starting mock data generation using OpenAI GPT-4...\n")
    
    # Generate user profiles
    print("Generating user profiles...")
    users = generate_user_profiles(count=15)
    if users:
        save_mock_data(users, 'mock_users.json')
    
    # Generate documents
    print("\nGenerating document metadata...")
    documents = generate_document_metadata(count=25)
    if documents:
        save_mock_data(documents, 'mock_documents.json')
    
    # Generate access patterns
    print("\nGenerating access control patterns...")
    patterns = generate_access_patterns()
    if patterns:
        save_mock_data(patterns, 'mock_access_patterns.json')
    
    print("\n✅ Mock data generation complete!")
    print(f"   - {len(users)} users generated")
    print(f"   - {len(documents)} documents generated")
    print(f"   - Access patterns configured")


if __name__ == '__main__':
    main()

