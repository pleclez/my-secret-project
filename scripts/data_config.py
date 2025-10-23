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

