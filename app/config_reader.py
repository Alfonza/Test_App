import configparser
import os

# Define the path to your config file
config_file_path = os.path.join(os.path.dirname(__file__), '..\config\config.properties')

# Initialize the ConfigParser object
config = configparser.ConfigParser()
config.read(config_file_path)

def get_database_url():
    """
    Construct the database URL from the values in the config file.
    """
    db_username = config.get('DEFAULT', 'DATABASE_USERNAME')
    db_password = config.get('DEFAULT', 'DATABASE_PASSWORD')
    db_host = config.get('DEFAULT', 'DATABASE_HOST')
    db_port = config.get('DEFAULT', 'DATABASE_PORT')
    db_name = config.get('DEFAULT', 'DATABASE_NAME')

    # Construct the database URL
    db_url = f"mysql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}"
    return db_url

def get_secret_key():
    return config.get('DEFAULT', 'SECRET_KEY')

def get_algorithm():
    return config.get('DEFAULT', 'ALGORITHM')

def get_token_expiry_minutes():
    return int(config.get('DEFAULT', 'ACCESS_TOKEN_EXPIRE_MINUTES'))
