from atproto import AsyncClient
import datetime
import asyncio
import xcryptowatch.mail as mail
from xcryptowatch.log import bluesky_logger as logger
from xcryptowatch.gpt import analyze_posts_concurrently

async def watch_bluesky(client, config):
    watched_posts = []
    await mail.status_update(f"Starting new bluesky watch at {datetime.datetime.now(datetime.timezone.utc)}.", config)

    while True:
        start_time = datetime.datetime.now(datetime.timezone.utc)# - datetime.timedelta(days=1)
        to_process = []
        for account in config['watch_accounts']:
            if account.get('platform', '').lower() != 'bluesky':
                continue
            account_username = account['username']
            logger.info(f"Fetching posts for @{account_username}...")
            profile_feed = client.get_author_feed(actor=account_username)
            if profile_feed:
                for feed_view in profile_feed.feed:
                    if feed_view.post.record.createdAt > start_time:
                        if feed_view.post.uri not in watched_posts:
                            watched_posts.append(feed_view.post.uri)
                            to_process.append(feed_view.post.record.text)
                            logger.info(f"Found {len(to_process)} posts to process...")
                    if len(watched_posts) > 100 * len(config['watch_accounts']):
                        watched_posts = watched_posts[-(100 * len(config['watch_accounts'])):]
            else:
                logger.error(f"Fetched user contains no data (posts may be too old)! Account: @{account_username}. Moving to next account...")

        if to_process:
            await _process_posts(to_process, config)
        to_process.clear()

        logger.info(f"Waiting for {config['bluesky']['check_interval']} minutes till next post check...")
        await asyncio.sleep(60*int(config['bluesky']['check_interval']))

# Post processing

async def _process_posts(posts, config):
    results = await analyze_posts_concurrently(posts)
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
