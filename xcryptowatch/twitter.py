import datetime
import xcryptowatch.gpt as gpt
import time
import tweepy
import tweepy.errors
import xcryptowatch.postal as postal
import datetime
from datetime import timedelta
from xcryptowatch.log import twitter_logger as logger

CHECK_INTERVAL = 15
watched_tweets = []

def watch_tweets(client, config):
    start_time = datetime.datetime.now(datetime.timezone.utc)
    postal.status_update(f"Starting new watch at {datetime.datetime.now(datetime.timezone.utc)}.")
    while True:
        for account in config['watch_accounts']:
            account_username = account['username']
            logger.info(f"Fetching tweets for @{account_username}...")
            try:
                user = client.get_user(username=account_username)
                if user.data:
                    tweets = client.get_users_tweets(user.data.id, max_results=5, tweet_fields=['created_at', 'text'])

                    logger.info("Tweets fetched...")
                    for tweet in tweets.data:
                        _process_tweet(config, tweet, account, start_time)
                else: 
                    logger.error(f"Fetched user contains no data! Account: {account_username}. Moving to next account...")
            except tweepy.errors.TooManyRequests as e:
                logger.error(f"Too many requests! Waiting 15 minutes...")
                time.sleep(15*60)
            except tweepy.errors.TweepyException as e:
                logger.error(f"Tweepy error while fetching tweets for @{account_username}: {str(e).replace('\n', ' ')} Waiting 60 seconds...")
                time.sleep(60)
            except Exception as e:
                logger.error(f"General error while fetching tweets for @{account_username}: {str(e).replace('\n', ' ')} Waiting 60 seconds...")
                time.sleep(60)
        logger.info(f"Waiting for {CHECK_INTERVAL} minutes till next tweet check...")
        time.sleep(60*CHECK_INTERVAL)

# Tweet processing

def _process_tweet(config, tweet, account, start_time):
    username = account['username']
    
    if tweet.created_at > start_time and tweet.id not in watched_tweets:
        try:
            logger.info(f"Tweet analysis started: {tweet.text}")
            watched_tweets.append(tweet.id)
            if len(watched_tweets) > 10 * len(config['watch_accounts']):
                watched_tweets = watched_tweets[-(10 * len(config['watch_accounts'])):]
            analysis = gpt.analyze_tweet(tweet)

            if not analysis:
                logger.info("Nothing relevant here. Moving on.")
                return
            else:
                logger.info("Analysis returned result. Sending to any configured emails...")
                postal.send_analysis(analysis, config)

            logger.info(f"Tweet analysis completed: {tweet.text}")
        except Exception as e:
            logger.error(f"General error while processing tweet: {e}")
    else:
        logger.debug(f"Tweet too old. Start time: {start_time}. Tweet created: {tweet.created_at}.")
