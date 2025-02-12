import asyncio
import tweepy
from truthbrush import Api as TruthClient
import postalsend
import openai
from xcryptowatch.config_json import create_config, _save_config, load_config, add_new_account, add_new_recipient, twitter_enabled, truth_enabled, postal_enabled
from xcryptowatch.social.twitter import watch_tweets
from xcryptowatch.social.truth import watch_truths
from xcryptowatch.log import main_logger as logger

async def main():
    logger.info(f"Starting xcryptowatch...")

    config = _setup_config()
    twitter_client, truth_client = _setup_api(config)
    logger.info("Initialized successfully!")
    
    while True:
        print("Hint: CTRL+C to exit.\n" +
              "1: Watch for tweets.\n" +
              "2: Watch for truths.\n" +
              "3: Add a new account to watch.\n" +
              "4: Add a new recipient to notify.\n" +
              "5: Configure XCryptoWatch")
        try:
            choice = input("Please select an option: ")
            if choice not in ["1", "2", "3", "4", "5"]:
                input("Invalid option! Press enter to try again...")
            match choice:
                case "1":
                    await watch_tweets(twitter_client, config)
                case "2":
                    await watch_truths(truth_client, config)
                case "3":
                    add_new_account(config)
                case "4":
                    add_new_recipient(config)
                case "5":
                    _configure(config)
        except KeyboardInterrupt:
            logger.info(f"Quitting due to CTRL+C...")
            return
                
def _configure(config):
    while True:
        print(f"1: Twitter Bearer Token: {config['twitter']['bearer_token']}")
        print(f"2: Twitter Consumer Key: {config['twitter']['consumer_key']}")
        print(f"3: Twitter Consumer Secret: {config['twitter']['consumer_secret']}")
        print(f"4: Twitter Access Token: {config['twitter']['access_token']}")
        print(f"5: Twitter Access Token Secret: {config['twitter']['access_token_secret']}")
        print(f"6: Twitter Check Interval: {config['twitter'].get('check_interval', 15)} minutes")
        print(f"7: Truth Username: {config['truth']['username']}")
        print(f"8: Truth Password: {config['truth']['password']}")
        print(f"9: Truth Check Interval: {config['truth'].get('check_interval', 15)} minutes")
        print(f"10: OpenAI API Key: {config['openai']['api_key']}")
        print(f"11: From Email: {config['email']['from_email']}")
        print(f"12: To Email: {', '.join(config['email']['to_email'])}")
        print(f"13: Email Subject: {config['email'].get('subject', '')}")
        print(f"14: Postal Enabled: {config['email']['postal'].get('enabled', False)}")
        print(f"15: Postal Server: {config['email']['postal'].get('server', '')}")
        print(f"16: Postal API Key: {config['email']['postal'].get('api_key', '')}")
        print(f"17: SMTP Enabled: {config['email']['smtp'].get('enabled', False)}")
        print(f"18: SMTP Host: {config['email']['smtp'].get('host', '')}")
        print(f"19: SMTP Port: {config['email']['smtp'].get('port', 587)}")
        print(f"20: SMTP Username: {config['email']['smtp'].get('username', '')}")
        print(f"21: SMTP Password: {config['email']['smtp'].get('password', '')}")
        print(f"22: SMTP Use TLS: {config['email']['smtp'].get('use_tls', True)}")
        print(f"23: Exit")
        
        choice = input("Select a number to update a value (or 23 to exit): ")
        
        if choice == "23":
            break
        
        options = {
            "1": ("twitter", "bearer_token"),
            "2": ("twitter", "consumer_key"),
            "3": ("twitter", "consumer_secret"),
            "4": ("twitter", "access_token"),
            "5": ("twitter", "access_token_secret"),
            "6": ("twitter", "check_interval"),
            "7": ("truth", "username"),
            "8": ("truth", "password"),
            "9": ("truth", "check_interval"),
            "10": ("openai", "api_key"),
            "11": ("email", "from_email"),
            "12": ("email", "to_email"),
            "13": ("email", "subject"),
            "14": ("email.postal", "enabled"),
            "15": ("email.postal", "server"),
            "16": ("email.postal", "api_key"),
            "17": ("email.smtp", "enabled"),
            "18": ("email.smtp", "host"),
            "19": ("email.smtp", "port"),
            "20": ("email.smtp", "username"),
            "21": ("email.smtp", "password"),
            "22": ("email.smtp", "use_tls"),
        }
        
        if choice in options:
            section, key = options[choice]
            
            # Handle special cases
            if key == "check_interval":
                try:
                    new_value = int(input(f"Enter new value for {section} check interval (in minutes): "))
                    if new_value < 1:
                        print("Check interval must be at least 1 minute")
                        continue
                except ValueError:
                    print("Please enter a valid number")
                    continue
            elif key == "to_email":
                new_emails = input("Enter email addresses (comma-separated): ")
                new_value = [email.strip() for email in new_emails.split(",") if email.strip()]
            elif key == "enabled":
                new_value = input("Enable? (y/n): ").lower() == 'y'
            elif key == "port":
                try:
                    new_value = int(input("Enter SMTP port: "))
                except ValueError:
                    print("Please enter a valid number")
                    continue
            elif key == "use_tls":
                new_value = input("Use TLS? (y/n): ").lower() == 'y'
            else:
                new_value = input(f"Enter new value for {section} -> {key}: ")
            
            # Handle nested config updates
            if "." in section:
                parent, child = section.split(".")
                if parent not in config:
                    config[parent] = {}
                if child not in config[parent]:
                    config[parent][child] = {}
                config[parent][child][key] = new_value
            else:
                config[section][key] = new_value
                
            logger.info(f"Updated {section} -> {key} successfully.")
            _save_config(config)
        else:
            print("Invalid choice, please try again.")

def _setup_config():
    logger.info(f"Loading configuration...")
    try:     
        config = load_config()
    except Exception as e:
        logger.error(f"Unable to load configuration file! May not exist: {e}")
        config = None
    if not config:
        config = create_config()
        _save_config(config)
    return config

def _setup_api(config):
    # Twitter
    if twitter_enabled(config):
        logger.info("Initializing Twitter client...")
        twitter_client = _setup_twitter(config)
    else:
        logger.warning("Twitter is disabled! Skipping Twitter client initialization.")
        twitter_client = None

    # Truth
    if truth_enabled(config):
        logger.info("Initializing Truth client...")
        truth_client = _setup_truth(config)
    else:
        logger.warning("Truth is disabled! Skipping Truth client initialization.")
        truth_client = None

    # OpenAI
    logger.info("Initializing OpenAI client...")
    _setup_openai(config)

    # Postal
    if postal_enabled(config):
        logger.info("Initializing Postal client...")
        _setup_postal(config)
    else:
        logger.warning("Postal is disabled! Skipping Postal client initialization.")
    return twitter_client, truth_client

def _setup_twitter(config):
    logger.debug(f"Bearer Token: {config['twitter']['bearer_token']}")
    logger.debug(f"Consumer Key: {config['twitter']['consumer_key']}")
    logger.debug(f"Consumer Secret: {config['twitter']['consumer_secret']}")
    logger.debug(f"Access Token: {config['twitter']['access_token']}")
    logger.debug(f"Access Token Secret: {config['twitter']['access_token_secret']}")
    try:
        twitter_client = tweepy.Client(
            bearer_token=config['twitter']['bearer_token'],
            consumer_key=config['twitter']['consumer_key'],
            consumer_secret=config['twitter']['consumer_secret'],
            access_token=config['twitter']['access_token'],
            access_token_secret=config['twitter']['access_token_secret']
        )
    except Exception as e:
        logger.error(f"Failed to initialize Twitter API client: {e}! Quitting...")
        exit(1)
    return twitter_client

def _setup_truth(config):
    logger.debug(f"Username: {config['truth']['username']}")
    logger.debug(f"Password: {config['truth']['password']}")
    try:
        truth_client = TruthClient(
            username=config['truth']['username'],
            password=config['truth']['password']
        )
        truth_client.trending()  # Test the client with a simple API call
    except Exception as e:
        logger.error(f"Failed to initialize Truth API client: {e}! Quitting...")
        exit(1)
    return truth_client

def _setup_openai(config):
    logger.debug(f"API Key: {config['openai']['api_key']}")
    try:
        openai.api_key = config['openai']['api_key']
        openai.models.list()    # Test the client with a simple API call
    except Exception as e:
        logger.error(f"Error initializing OpenAI client: {str(e)}!")
        exit(1)

def _setup_postal(config):
    logger.debug(f"Server: {config['email']['postal'].get('server')}")
    logger.debug(f"Key: {config['email']['postal'].get('api_key')}")
    logger.debug(f"To: {config['email']['to_email']}")
    logger.debug(f"From: {config['email']['from_email']}")
    try:
        postalsend.login(config['email']['postal']['server'], config['email']['postal']['api_key'])
        postalsend.push_setup(config['email']['to_email'], config['email']['from_email'])
    except Exception as e:
        logger.error(f"Error initializing Postal client: {str(e)}!")

if __name__ == "__main__":  
    asyncio.run(main())
