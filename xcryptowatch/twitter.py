import datetime
import gpt
import time
import tweepy
import tweepy.errors
import postal
import datetime
from datetime import timedelta
from log import twitter_logger as logger

CHECK_INTERVAL = 15

# Rate limits
APP_RATE_LIMIT = 300  # app limit: 300 requests per 15 min
USER_RATE_LIMIT = 900  # user limit: 900 requests per 15 min
USER_REPLY_LIMIT = 200  # user reply limit: 200 requests per 15 min

# Track request counts and timestamps
request_timestamps = []
user_request_counts = {}

# Track replies and start time
watched_tweets = []

def watch_tweets(client, config):
    start_time = datetime.datetime.now(datetime.timezone.utc)
    #postal.status_update(f"Starting new watch at {datetime.now()}.")
    while True:
        for account in config['watch_accounts']:
            account_username = account['username']
            logger.info(f"Fetching tweets for @{account_username}...")
            try:
                user = client.get_user(username=account_username)
                if user.data:
                    user_id = user.data.id
                    _increment_request_count(user_id) # for client.get_user
                    _is_rate_limited(user_id)
                    
                    tweets = client.get_users_tweets(user_id, max_results=5, tweet_fields=['created_at', 'text'])
                    _increment_request_count(user_id) # for client.get_users_tweets
                    _is_rate_limited(user_id)

                    logger.info("Tweets fetched...")
                    for tweet in tweets.data:
                        _process_tweet(config, tweet, account, start_time)
                else: 
                    logger.error(f"Fetched user contains no data! Account: {account_username}. Moving to next account...")
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
    
    if tweet.id not in watched_tweets:
        try:
            logger.info(f"Tweet analysis started: {tweet.text}")
            if len(watched_tweets) > 10 * len(config['watch_accounts']):
                watched_tweets = watched_tweets[-(10 * len(config['watch_accounts'])):]
            watched_tweets.append(tweet.id)
            analysis = gpt.analyze_tweet(tweet)

            if not analysis:
                logger.info("Nothing relevant here. Moving on.")
                return
            else:
                logger.info("Analysis returned result. Sending to any configured emails...")
                postal.send_analysis(analysis, config)

            logger.info(f"Tweet analysis completed: {tweet.text}")
        except tweepy.errors.TweepyException as e:
            logger.error(f"Tweepy error while replying to @{account}: {e}")
        except Exception as e:
            logger.error(f"General error while replying to @{account}: {e}")
    else:
        logger.debug(f"Tweet too old. Start time: {start_time}. Tweet created: {tweet.created_at}.")

# Rate limiting funcions
def _increment_request_count(user_id):
    if user_id not in user_request_counts:
        user_request_counts[user_id] = {'count': 0, 'first_request_time': datetime.datetime.now(datetime.timezone.utc)}
    user_request_counts[user_id]['count'] += 1
    request_timestamps.append(datetime.datetime.now(datetime.timezone.utc))
    
def _is_app_rate_limited(now):
    if len(request_timestamps) >= APP_RATE_LIMIT:
        logger.warning("App rate limit reached. Waiting until reset...")
        wait_time = 15 * 60 - (now - request_timestamps[0]).total_seconds()
        time.sleep(max(0, wait_time))

def _is_user_rate_limited(user_id, now):
    if user_request_counts[user_id]['count'] >= USER_RATE_LIMIT:
        logger.warning(f"User {user_id} rate limit reached. Waiting until reset...")
        wait_time = 15 * 60 - (now - user_request_counts[user_id]['first_request_time']).total_seconds()
        time.sleep(max(0, wait_time))
        user_request_counts[user_id]['count'] = 0  # Reset after waiting
        user_request_counts[user_id]['first_request_time'] = now
    
def _is_rate_limited(user_id):
    # Remove timestamps older than 15 minutes
    now = datetime.datetime.now(datetime.timezone.utc)
    request_timestamps[:] = [ts for ts in request_timestamps if ts > now - timedelta(minutes=15)]
    
    # Check app request limits
    _is_app_rate_limited(now)
    
    # Check user limits
    if user_id not in user_request_counts:
        user_request_counts[user_id] = {'count': 0, 'first_request_time': now}
    
    # Check if user limit is reached
    _is_user_rate_limited(user_id, now)
    
    return user_request_counts[user_id]

