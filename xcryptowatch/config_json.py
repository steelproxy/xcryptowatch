import json
import jsonschema
import sys
import os
from xcryptowatch.log import main_logger as logger

__version__ = "0.1.1"
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
                "check_interval": {"type": "integer", "minimum": 1}
            },
            "required": ["bearer_token", "consumer_key", "consumer_secret", "access_token", "access_token_secret", "check_interval"],
        },
        "truth": {
            "type": "object",
            "properties": {
                "username": {"type": "string"},
                "password": {"type": "string"},
                "check_interval": {"type": "integer", "minimum": 1}
            },
            "required": ["username", "password", "check_interval"],
        },
        "bluesky": {
            "type": "object",
            "properties": {
                "username": {"type": "string"},
                "password": {"type": "string"},
                "check_interval": {"type": "integer", "minimum": 1}
            },
            "required": ["username", "password", "check_interval"],
        },
        "openai": {
            "type": "object",
            "properties": {
                "api_key": {"type": "string"},
            },
            "required": ["api_key"],
        },
        "email": {
            "type": "object",
            "properties": {
                "from_email": {"type": "string"},
                "to_email": {"type": "array", "items": {"type": "string"}},
                "subject": {"type": "string"},
                "postal": {
                    "type": "object",
                    "properties": {
                        "enabled": {"type": "boolean"},
                        "server": {"type": "string"},
                        "api_key": {"type": "string"},
                    },
                    "required": ["enabled"],
                },
                "smtp": {
                    "type": "object",
                    "properties": {
                        "enabled": {"type": "boolean"},
                        "host": {"type": "string"},
                        "port": {"type": "integer"},
                        "username": {"type": "string"},
                        "password": {"type": "string"},
                        "use_tls": {"type": "boolean"}
                    },
                    "required": ["enabled"],
                }
            },
            "required": ["from_email", "to_email"],
        },
        "watch_accounts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "username": {"type": "string"},
                    "platform": {"type": "string", "enum": ["twitter", "truth", "bluesky"]}
                },
                "required": ["username", "platform"],
            },
        },
    },
    "required": ["version", "twitter", "truth", "bluesky", "openai", "watch_accounts"],
}

def twitter_enabled(config):
    return all([
        config['twitter']['bearer_token'],
        config['twitter']['consumer_key'], 
        config['twitter']['consumer_secret'],
        config['twitter']['access_token'],
        config['twitter']['access_token_secret']
    ])

def truth_enabled(config):
    return all([
        config['truth']['username'],
        config['truth']['password']
    ])

def bluesky_enabled(config):
    return all([
        config['bluesky']['username'],
        config['bluesky']['password']
    ])

def postal_enabled(config):
    return (
        config['email']['postal'].get('enabled', False) and
        config['email']['postal'].get('server') and
        config['email']['postal'].get('api_key') and
        config['email']['from_email'] and
        config['email']['to_email']
    )

def smtp_enabled(config):
    return (
        config['email']['smtp'].get('enabled', False) and
        config['email']['smtp'].get('host') and
        config['email']['smtp'].get('username') and
        config['email']['smtp'].get('password') and
        config['email']['from_email'] and
        config['email']['to_email']
    )

def load_config():
    config_path = _get_config_path()
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r") as f:
        config = json.load(f)

    if not _validate_config(config):
        return None

    return config

def create_config():
    twitter_config = {key: input(f"Enter your Twitter {key.replace('_', ' ')} (or leave blank for disabled): ")
                      for key in ['bearer_token', 'consumer_key', 'consumer_secret', 'access_token', 'access_token_secret']}
    twitter_config['check_interval'] = int(input("Enter check interval in minutes for Twitter (default 15): ") or 15)

    truth_config = {
        'username': input("Enter your Truth username (leave blank for disabled): "),
        'password': input("Enter your Truth password (leave blank for disabled): "),
        'check_interval': int(input("Enter check interval in minutes for Truth (default 15): ") or 15)
    }

    bluesky_config = {
        'username': input("Enter your Bluesky username (leave blank for disabled): "),
        'password': input("Enter your Bluesky password (leave blank for disabled): "),
        'check_interval': int(input("Enter check interval in minutes for Bluesky (default 15): ") or 15)
    }

    openai_config = {'api_key': input("Enter your OpenAI API key: ")}

    # Email configuration
    from_email = input("Enter your from email for notifications (e.g. 'XCryptoWatch <xcryptowatch@mailserver.com>'): ")
    to_emails = input("Enter email addresses to send reports to (comma-separated, e.g. 'test@example.com, email2@example.com'): ")
    to_email_list = [email.strip() for email in to_emails.split(",") if email.strip()]
    subject = input("Enter your subject for notifications (can leave blank): ")

    # Postal configuration
    use_postal = input("Do you want to configure Postal email? (y/n, default: n): ").lower() == 'y'
    postal_config = {
        'enabled': use_postal
    }
    if use_postal:
        postal_config.update({
            'server': input("Enter your Postal server: "),
            'api_key': input("Enter your Postal API key: "),
        })

    # SMTP configuration
    use_smtp = input("Do you want to configure SMTP email? (y/n, default: n): ").lower() == 'y'
    smtp_config = {
        'enabled': use_smtp
    }
    if use_smtp:
        smtp_config.update({
            'host': input("Enter your SMTP host: "),
            'port': int(input("Enter your SMTP port (default: 587): ") or 587),
            'username': input("Enter your SMTP username: "),
            'password': input("Enter your SMTP password: "),
            'use_tls': input("Use TLS? (y/n, default: y): ").lower() != 'n'
        })

    email_config = {
        'from_email': from_email,
        'to_email': to_email_list,
        'subject': subject,
        'postal': postal_config,
        'smtp': smtp_config
    }

    config = {
        'version': __version__,
        'twitter': twitter_config,
        'truth': truth_config,
        'bluesky': bluesky_config,
        'openai': openai_config,
        'email': email_config,
        'watch_accounts': []
    }

    logger.info("New configuration created.")
    return config

def add_new_account(config):
    new_account = input("Enter the account to watch (without @): ")
    valid_platforms = ['twitter', 'truth', 'bluesky']
    platform = input(f"Enter the platform to watch ({' or '.join(valid_platforms)}): ").lower()
    
    if platform not in valid_platforms:
        logger.error(f"Invalid platform '{platform}'. Must be one of: {', '.join(valid_platforms)}")
        return
        
    if any(account_info['username'] == new_account and account_info['platform'] == platform for account_info in config['watch_accounts']):
        logger.error(f"Unable to add user {new_account}! Account already exists in config.")
        return

    _add_account(config, new_account, platform)

def add_new_recipient(config):
    new_recipient = input("Enter an email address to send push notifications to (e.g. 'Test <test@example.com>'): ")
    if any(address == new_recipient for address in config['email']['to_email']):
        logger.error(f"Unable to add user {new_recipient}! Account already exists in config.")
        return

    _add_recipient(config, new_recipient)

def _add_account(config, username, platform):
    config['watch_accounts'].append({
        'username': username,
        'platform': platform
    })

    _save_config(config)
    logger.info(f"Added {username} to watch accounts.")

def _add_recipient(config, new_recipient):
    config['email']['to_email'].append(new_recipient)
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
        return os.path.join(application_path, __config_file__)
    elif __file__:
        return __config_file__

def _validate_config(config):
    try:
        jsonschema.validate(instance=config, schema=config_schema)
    except jsonschema.ValidationError as e:
        logger.error(f"Configuration file is invalid: {e.message}")
        return False

    return True