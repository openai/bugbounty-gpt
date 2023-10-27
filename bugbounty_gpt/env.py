import os
import yaml
import re
import logging

logger = logging.getLogger(__name__)

def load_config() -> dict:
    """Loads the configuration from the YAML file."""
    config_path = os.path.join(os.path.dirname(__file__), '../config.yaml')
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def sanitize_category(category: str) -> str:
    """Sanitizes a single category name to ensure it is a valid Python identifier."""
    return re.sub(r'\W|^(?=\d)', '_', category).upper().strip()

def sanitize_categories(categories: list) -> list:
    """Sanitizes a list of category names using sanitize_category."""
    return [sanitize_category(category) for category in categories]

def validate_valid_categories(config: dict):
    """Checks that the 'valid' categories are defined in the configuration."""
    if 'valid' not in config['categories']:
        raise ValueError("Missing 'valid' categories in configuration.")

def validate_response_categories_subset(config: dict):
    """Ensures that the response categories are a subset of the valid categories."""
    valid_categories = set(config['categories']['valid'])
    response_categories = {item['name'] for item in config['categories']['response']}
    if not response_categories.issubset(valid_categories):
        raise ValueError('Response categories must be a subset of valid categories.')

def validate_response_pairs(config: dict):
    """Ensures that each response category contains both a 'name' and 'response' key."""
    for item in config['categories']['response']:
        if 'name' not in item or 'response' not in item:
            raise ValueError("Each response category must contain 'name' and 'response' keys.")

def validate_config(config: dict):
    """Validates the entire configuration."""
    validate_valid_categories(config)
    validate_response_categories_subset(config)
    validate_response_pairs(config)

CONFIG = load_config()

# API settings
API_BASE_URL = CONFIG['api']['base_url']
BUGCROWD_API_KEY = os.getenv('BUGCROWD_API_KEY')
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = CONFIG['api']['openai_model']

# Database settings
SQLALCHEMY_URL = os.getenv("SQLALCHEMY_URL")

# Other user-specific settings
USER_ID = CONFIG['user']['user_id']
FILTER_PROGRAM = CONFIG['user']['filter_program']

# OpenAI Prompt
OPENAI_PROMPT = CONFIG['openai_prompt']

# Categories & Responses
VALID_CATEGORIES = sanitize_categories(CONFIG['categories']['valid'])
RESPONSE_CATEGORIES = sanitize_categories([item['name'] for item in CONFIG['categories']['response']])
DEFAULT_CATEGORY = sanitize_category(CONFIG['categories']['default'])
RESPONSES = {sanitize_category(item['name']): item['response'] for item in CONFIG['categories']['response']}

validate_config(CONFIG)
