import json
import jsonschema
import sys
import os
from log import main_logger as logger

__version__ = "0.1.0"
__config_file__ = "config.json"

# Define the JSON schema
config_schema = {
    "type": "object",
    "properties": {
        "version": {
            "type": "string"
        },
        "twitter": {
            "type": "object",
            "properties": {
                "bearer_token": {"type": "string"},
                "consumer_key": {"type": "string"},
                "consumer_secret": {"type": "string"},
                "access_token": {"type": "string"},
                "access_token_secret": {"type": "string"},
            },
            "required": ["bearer_token", "consumer_key", "consumer_secret", "access_token", "access_token_secret"],
        },
        "openai": {
            "type": "object",
            "properties": {
                "api_key": {"type": "string"},
            },
            "required": ["api_key"],
        },
        "postal":{
            "type": "object",
            "properties": {
                "server": {"type": "string"},
                "api_key": {"type": "string"},
                "from_email": {"type": "string"},
                "to_email": {"type": "array", "items": {"type": "string"}},
                "subject": {"type": "string"}
            },
            "required": ["server", "api_key", "from_email", "to_email"],
        },
        "watch_accounts": {
            "type": "array",

            "items": {
                "type": "object",
                "properties": {
                    "username": {"type": "string"},
                },
                "required": ["username"],
            },
        },
    },
    "required": ["version", "twitter", "openai", "watch_accounts"],
}

def load_config():
    if not os.path.exists(__config_file__):
        raise FileNotFoundError(f"Config file not found: {__config_file__}")

    with open(__config_file__, "r") as f:
        config = json.load(f)

    if not _validate_config(config):
        return None

    return config

def create_config():
    twitter_config = {key: input(f"Enter your Twitter {key.replace('_', ' ')}: ")
                      for key in ['bearer_token', 'consumer_key', 'consumer_secret', 'access_token', 'access_token_secret']}

    openai_config = {'api_key': input("Enter your OpenAI API key: ")}

    postal_config = {
        'server': input("Enter your Postal server: "),
        'api_key': input("Enter your Postal API key: "),
        'from_email': input("Enter your from email for push notifications: "),
        'to_email': [email.strip() for email in input("Enter at least one email address to send the report to, will accept comma-separated values "
                                                      "(e.g. 'Test <test@example.com>, email2 <email2@example.com>, etc.'): ").split(",") if email.strip()],
       'subject': input("Enter your subject for push notifications (can leave blank): ")
    }

    config = {
        'version': __version__,
        'twitter': twitter_config,
        'openai': openai_config,
        'postal': postal_config,
        'watch_accounts': []
    }


    logger.info("New configuration created.")
    return config

def add_new_account(config):
    new_account = input("Enter the Twitter account to watch (without @): ")
    if any(account_info['username'] == new_account for account_info in config['watch_accounts']):
        logger.error(f"Unable to add user {new_account}! Account already exists in config.")
        return

    _add_account(config, new_account)

def add_new_recipient(config):
    new_recipient = input("Enter an email address to send push notifications to (e.g. 'Test <test@example.com>'): ")
    if any(address == new_recipient for address in config['postal']['to_email']):
        logger.error(f"Unable to add user {new_recipient}! Account already exists in config.")
        return

    _add_recipient(config, new_recipient)

def _add_account(config, username):
    config['watch_accounts'].append({
        'username': username,
    })

    _save_config(config)
    logger.info(f"Added {username} to watch accounts.")

def _add_recipient(config, new_recipient):
    config['postal']['to_email'].append(new_recipient)
    _save_config(config)
    logger.info(f"Added {new_recipient} to push notifications.")

def _save_config(config):
    config_path = _get_config_path()

    logger.info(f"Saving configuration to {config_path}")
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)

def _get_config_path():
    # determine if application is a script file or frozen exe
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.dirname(__file__)

    return os.path.join(application_path, __config_file__)


def _validate_config(config):
    try:
        jsonschema.validate(instance=config, schema=config_schema)
    except jsonschema.ValidationError as e:
        logger.error(f"Configuration file is invalid: {e.message}")
        return False

    return True