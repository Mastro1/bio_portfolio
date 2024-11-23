import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

class Config:
    """Base configuration with common default settings."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')  # Ensure a strong key in production
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Disable tracking to save resources
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'data/uploads')  # Default upload folder
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')  # Load OpenAI API Key
    FLASK_DEBUG = False
    TESTING = False
    OAUTH_CLIENT_ID = os.getenv("OAUTH_CLIENT_ID")
    OAUTH_CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET")
    OAUTH_REDIRECT_URI = os.getenv("OAUTH_REDIRECT_URI")


class DevelopmentConfig(Config):
    """Development-specific configuration."""
    FLASK_ENV = 'development'
    FLASK_DEBUG = True  # Enable Flask debugging for development
    SQLALCHEMY_DATABASE_URI = os.getenv('DEV_DATABASE_URL', 'sqlite:///data/dev_app.db')  # SQLite for local dev


class TestingConfig(Config):
    """Testing-specific configuration."""
    FLASK_ENV = 'testing'
    TESTING = True  # Enable testing mode
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URL', 'sqlite:///data/test_app.db')  # SQLite for testing


class ProductionConfig(Config):
    """Production-specific configuration."""
    FLASK_ENV = 'production'
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/prod_db')  # PostgreSQL for production
    FLASK_DEBUG = False  # Disable debugging in production


# A dictionary to map environment names to configurations
config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


# Function to retrieve configuration by name
def get_config(config_name=None):
    """
    Retrieve the configuration object by name.

    Args:
        config_name (str): Name of the configuration (e.g., 'development', 'testing', 'production').

    Returns:
        Config: The corresponding configuration object.
    """
    config_name = config_name or os.getenv('FLASK_ENV', 'development')  # Default to development
    return config_by_name.get(config_name, DevelopmentConfig)
