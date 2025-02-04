import tweepy
import postalsend
import openai
from xcryptowatch.config_json import create_config, _save_config, load_config, add_new_account, add_new_recipient
from xcryptowatch.twitter import watch_tweets
from xcryptowatch.log import main_logger as logger

def main():
    logger.info(f"Starting xcryptowatch...")

    config = _setup_config()
    twitter_client = _setup_api(config)
    logger.info("Initialized successfully!")
    
    while True:
        print("Hint: CTRL+C to exit.\n" +
              "1: Watch for tweets.\n" +
              "2: Add a new account to watch.\n" +
              "3: Add a new recipient to notify.\n" +
              "4: Configure XCryptoWatch")
        try:
            choice = input("Please select an option: ")
            if choice not in ["1", "2", "3", "4"]:
                input("Invalid option! Press enter to try again...")
            match choice:
                case "1":
                    watch_tweets(twitter_client, config)
                case "2":
                    add_new_account(config)
                case "3":
                    add_new_recipient(config)
                case "4":
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
        print(f"6: OpenAI API Key: {config['openai']['api_key']}")
        print(f"7: Postal Server: {postalsend._app._get_server()}")
        print(f"8: Postal Key: {postalsend._app._get_api_key()}")
        print(f"9: Exit")
        choice = input("Select a number to update a value (or 11 to exit): ")
        
        if choice == "9":
            break
        
        options = {
            "1": ("twitter", "bearer_token"),
            "2": ("twitter", "consumer_key"),
            "3": ("twitter", "consumer_secret"),
            "4": ("twitter", "access_token"),
            "5": ("twitter", "access_token_secret"),
            "6": ("openai", "api_key"),
            "7": ("postal", "server"),
            "8": ("postal", "api_key"),
        }
        
        if choice in options:
            section, key = options[choice]
            new_value = input(f"Enter new value for {section} -> {key}: ")
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
        logger.error("Unable to load configuration file! May not exist!")
        config = None
    if not config:
        config = create_config()
        _save_config(config)
    return config

def _setup_api(config):
    logger.info("Initializing Twitter client...")
    try:
        twitter_client = tweepy.Client(
            bearer_token=config['twitter']['bearer_token'],
            consumer_key=config['twitter']['consumer_key'],
            consumer_secret=config['twitter']['consumer_secret'],
            access_token=config['twitter']['access_token'],
            access_token_secret=config['twitter']['access_token_secret']
        )
    except tweepy.errors.TweepyException as e:
        logger.error(f"Failed to initialize Twitter API client: {e}! Quitting...")
        exit(1)
    logger.debug(f"Bearer Token: {config['twitter']['bearer_token']}")
    logger.debug(f"Consumer Key: {config['twitter']['consumer_key']}")
    logger.debug(f"Consumer Secret: {config['twitter']['consumer_secret']}")
    logger.debug(f"Access Token: {config['twitter']['access_token']}")
    logger.debug(f"Access Token Secret: {config['twitter']['access_token_secret']}")

    logger.info("Initializing OpenAI client...")
    try:
        openai.api_key = config['openai']['api_key']
        # Test the client with a simple API call
        openai.models.list()
    except Exception as e:
        logger.error(f"Error initializing OpenAI client: {str(e)}!")
        exit(1)
    logger.debug(f"API Key: {config['openai']['api_key']}")

    logger.info("Initializing Postal client...")
    postalsend.login(config['postal']['server'], config['postal']['api_key'])
    postalsend.push_setup(config['postal']['to_email'], config['postal']['from_email'])
    logger.debug(f"Server: {postalsend._app._get_server()}")
    logger.debug(f"Key: {postalsend._app._get_api_key()}")
    logger.debug(f"To: {postalsend._app._get_to_address()}")
    logger.debug(f"From: {postalsend._app._get_from_address()}")
    return twitter_client
            
if __name__ == "__main__":  
    main()
