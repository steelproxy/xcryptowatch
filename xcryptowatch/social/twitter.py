import datetime
#from datetime import timedelta
import tweepy
import tweepy.errors
import xcryptowatch.mail as mail
from xcryptowatch.log import twitter_logger as logger
from xcryptowatch.gpt import analyze_posts_concurrently
import asyncio

async def watch_tweets(client, config):
    watched_tweets = []
    await mail.status_update(f"Starting new watch at {datetime.datetime.now(datetime.timezone.utc)}.")
    
    while True:
        start_time = datetime.datetime.now(datetime.timezone.utc) # - timedelta(days=7)
        to_process = []
        for account in config['watch_accounts']:
            if account.get('platform', '').lower() != 'twitter':
                continue
                
            account_username = account['username']
            logger.info(f"Fetching tweets for @{account_username}...")
            try:
                user = client.get_user(username=account_username)
                if user.data:
                    tweets = client.get_users_tweets(user.data.id, max_results=5, start_time=start_time, tweet_fields=['created_at', 'text'])
                    if tweets.data:
                        for tweet in tweets.data:
                            if tweet.created_at > start_time and tweet.id not in watched_tweets:
                                to_process.append(tweet.text)
                                watched_tweets.append(tweet.id)
                                logger.info(f"Found {len(to_process)} tweets to process...")
                                if len(watched_tweets) > 100 * len(config['watch_accounts']):
                                    watched_tweets = watched_tweets[-(100 * len(config['watch_accounts'])):]
                    else:
                        logger.error(f"Fetched user contains no data (tweets may be too old)! Account: @{account_username}. Moving to next account...")
            except tweepy.errors.TooManyRequests as e:
                logger.error(f"Too many requests! Waiting 15 minutes...")
                await asyncio.sleep(15*60)
            except tweepy.errors.TweepyException as e:
                logger.error(f"Tweepy error while fetching tweets for @{account_username}: {str(e).replace('\n', ' ')} Waiting 60 seconds...")
                #await asyncio.sleep(60)
            except Exception as e:
                logger.error(f"General error while fetching tweets for @{account_username}: {str(e).replace('\n', ' ')} Waiting 60 seconds...")
                #await asyncio.sleep(60)
        
        logger.info("Tweets finished fetching...")
        if to_process:
            await _process_tweets(to_process, config)
        to_process.clear()

        logger.info(f"Waiting for {config['twitter']['check_interval']} minutes till next tweet check...")
        await asyncio.sleep(60*int(config['twitter']['check_interval']))

async def _process_tweets(tweets, config):
    results = await analyze_posts_concurrently(tweets)
    if results:
        for i, result in enumerate(results):
            if not result:
                logger.error(f"Task {i} returned error!")
            elif result == "nothing":
                logger.debug(f"Task {i}: No crypto mention.")
            else:
                logger.info(f"Task {i} returned result: {result}")
                logger.info(f"Task {i} sending result to any configured emails...")
                await mail.send_analysis(result, config)
    else:
        logger.error("No results to process!")

