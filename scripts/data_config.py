"""
Configuration file for data generation scripts
"""

# OpenAI Configuration
OPENAI_CONFIG = {
    'api_key': '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',
    'model': 'gpt-4',
    'temperature': 0.7,
    'max_tokens': 2000
}

# Data Generation Settings
GENERATION_SETTINGS = {
    'num_users': 50,
    'num_documents': 100,
    'num_roles': 8,
    'enable_ai_generation': True
}

# API Endpoints
API_BASE_URL = 'https://api.openai.com/v1'

