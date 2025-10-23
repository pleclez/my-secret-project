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

