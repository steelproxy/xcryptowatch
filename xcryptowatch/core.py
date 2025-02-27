import asyncio
import tweepy
from truthbrush import Api as TruthClient
import postalsend
import openai
from xcryptowatch.config_json import create_config, _save_config, load_config, add_new_account, add_new_recipient, twitter_enabled, truth_enabled, postal_enabled, bluesky_enabled
from xcryptowatch.social.twitter import watch_tweets
from xcryptowatch.social.truth import watch_truths
from xcryptowatch.social.bluesky import watch_bluesky
from xcryptowatch.log import main_logger as logger
from xcryptowatch import __version__

async def main():
    logger.info(f"xcryptowatch version: {__version__}")
    logger.info(f"For more information, visit https://github.com/steelproxy/xcryptowatch")
    logger.info(f"Starting xcryptowatch...")

    config = _setup_config()
    twitter_client, truth_client, bluesky_client = _setup_api(config)
    logger.info("Initialized successfully!")

    twitter_task = None
    truth_task = None
    bluesky_task = None
    
    while True:
        print("Hint: CTRL+C to exit.\n" +
              "1: Start watching tweets\n" +
              "2: Stop watching tweets\n" +
              "3: Start watching truths\n" +
              "4: Stop watching truths\n" +
              "5: Start watching bluesky\n" +
              "6: Stop watching bluesky\n" +
              "7: Add a new account to watch\n" +
              "8: Add a new recipient to notify\n" +
              "9: Configure XCryptoWatch")
        try:
            # Allow tasks to run while waiting for input
            choice = await asyncio.get_event_loop().run_in_executor(None, input, "Please select an option: ")
            
            match choice:
                case "1":
                    if twitter_task and not twitter_task.done():
                        print("Twitter watch is already running!")
                    else:
                        twitter_task = asyncio.create_task(watch_tweets(twitter_client, config))
                        print("Started watching tweets")
                case "2":
                    if twitter_task and not twitter_task.done():
                        twitter_task.cancel()
                        print("Stopped watching tweets")
                    else:
                        print("Twitter watch is not running!")
                case "3":
                    if truth_task and not truth_task.done():
                        print("Truth watch is already running!")
                    else:
                        truth_task = asyncio.create_task(watch_truths(truth_client, config))
                        print("Started watching truths")
                case "4":
                    if truth_task and not truth_task.done():
                        truth_task.cancel()
                        print("Stopped watching truths")
                    else:
                        print("Truth watch is not running!")
                case "5":
                    if bluesky_task and not bluesky_task.done():
                        print("Bluesky watch is already running!")
                    else:
                        bluesky_task = asyncio.create_task(watch_bluesky(bluesky_client, config))
                        print("Started watching bluesky")
                case "6":
                    if bluesky_task and not bluesky_task.done():
                        bluesky_task.cancel()
                        print("Stopped watching bluesky")
                    else:
                        print("Bluesky watch is not running!")
                case "7":
                    await asyncio.get_event_loop().run_in_executor(None, add_new_account, config)
                case "8":
                    await asyncio.get_event_loop().run_in_executor(None, add_new_recipient, config)
                case "9":
                    await asyncio.get_event_loop().run_in_executor(None, _configure, config)
        except KeyboardInterrupt:
            logger.info(f"Quitting due to CTRL+C...")
            if twitter_task and not twitter_task.done():
                twitter_task.cancel()
            if truth_task and not truth_task.done():
                truth_task.cancel()
            if bluesky_task and not bluesky_task.done():
                bluesky_task.cancel()
            await asyncio.sleep(0)  # Let the tasks cancel
            exit(0)

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
        print(f"10: Bluesky Username: {config['bluesky']['username']}")
        print(f"11: Bluesky Password: {config['bluesky']['password']}")
        print(f"12: Bluesky Check Interval: {config['bluesky'].get('check_interval', 15)} minutes")
        print(f"13: OpenAI API Key: {config['openai']['api_key']}")
        print(f"14: From Email: {config['email']['from_email']}")
        print(f"15: To Email: {', '.join(config['email']['to_email'])}")
        print(f"16: Email Subject: {config['email'].get('subject', '')}")
        print(f"17: Postal Enabled: {config['email']['postal'].get('enabled', False)}")
        print(f"18: Postal Server: {config['email']['postal'].get('server', '')}")
        print(f"19: Postal API Key: {config['email']['postal'].get('api_key', '')}")
        print(f"20: SMTP Enabled: {config['email']['smtp'].get('enabled', False)}")
        print(f"21: SMTP Host: {config['email']['smtp'].get('host', '')}")
        print(f"22: SMTP Port: {config['email']['smtp'].get('port', 587)}")
        print(f"23: SMTP Username: {config['email']['smtp'].get('username', '')}")
        print(f"24: SMTP Password: {config['email']['smtp'].get('password', '')}")
        print(f"25: SMTP Use TLS: {config['email']['smtp'].get('use_tls', True)}")
        print(f"26: Exit")
        
        choice = input("Select a number to update a value (or 26 to exit): ")
        
        if choice == "26":
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
            "10": ("bluesky", "username"),
            "11": ("bluesky", "password"),
            "12": ("bluesky", "check_interval"),
            "13": ("openai", "api_key"),
            "14": ("email", "from_email"),
            "15": ("email", "to_email"),
            "16": ("email", "subject"),
            "17": ("email.postal", "enabled"),
            "18": ("email.postal", "server"),
            "19": ("email.postal", "api_key"),
            "20": ("email.smtp", "enabled"),
            "21": ("email.smtp", "host"),
            "22": ("email.smtp", "port"),
            "23": ("email.smtp", "username"),
            "24": ("email.smtp", "password"),
            "25": ("email.smtp", "use_tls"),
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

    # Bluesky
    if bluesky_enabled(config):
        logger.info("Initializing Bluesky client...")
        bluesky_client = _setup_bluesky(config)
    else:
        logger.warning("Bluesky is disabled! Skipping Bluesky client initialization.")
        bluesky_client = None

    return twitter_client, truth_client, bluesky_client

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

def _setup_bluesky(config):
    logger.debug(f"Username: {config['bluesky']['username']}")
    logger.debug(f"Password: {config['bluesky']['password']}")
    try:
        from atproto import Client
        bluesky_client = Client()
        bluesky_client.login(config['bluesky']['username'], config['bluesky']['password'])
    except Exception as e:
        logger.error(f"Failed to initialize Bluesky API client: {e}! Quitting...")
        exit(1)
    return bluesky_client

def _run_main():
        asyncio.run(main())

if __name__ == "__main__":
    _run_main()
