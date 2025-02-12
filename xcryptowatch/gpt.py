import openai
import asyncio
from xcryptowatch.log import gpt_logger as logger

__chatgpt_role__ = ("You are a helpful assistant that analyzes social media posts to determine if they mention cryptocurrency "
                    "and assess their sentiment. "

                    "1. If a post **does not** mention cryptocurrency, respond with the string \"nothing\". Make sure it does not include ANY punctuation or extra characters. Simply just that string and nothing else."
                    
                    "2. If a post **does** mention cryptocurrency: "
                    "- Be aware that 'DOGE' might refer to either the Dogecoin cryptocurrency OR the 'Department Of Government Efficiency'. Carefully analyze the context to determine which one is being referenced. "
                    "- Determine whether the mention is **positive** or **negative**. "
                    "- Summarize the sentiment in 1-2 sentences. "
                    "- Compare the sentiment to **current cryptocurrency market trends** "
                    "(e.g., price movement, major news, investor sentiment).")

async def analyze_post(post):
    """Analyzes a single post asynchronously."""
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=_create_gpt_message(post),
            temperature=0.7
        )
    except Exception as e:
        return _handle_openai_error(e)

    # Validate API response
    if not hasattr(response, 'choices') or not response.choices:
        logger.error("API response does not contain 'choices'")
        return None
    if not hasattr(response.choices[0], 'message') or not hasattr(response.choices[0].message, 'content'):
        logger.error("API response does not contain expected content")
        return None
    
    response_message = response.choices[0].message.content.strip()
    return f"This post was analyzed and believed to contain relevant information: [{post}]. Thoughts: {response_message}"

async def analyze_posts_concurrently(posts):
    """Analyzes multiple posts concurrently using asyncio.gather."""
    tasks = [analyze_post(post) for post in posts]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results

def _create_gpt_message(post):
    """Create the message structure for the GPT API request."""
    return [
        {"role": "system", "content": __chatgpt_role__},
        {"role": "user", "content": f"{post}"}
    ]

def _handle_openai_error(e):
    """Handle OpenAI API errors."""
    if isinstance(e, openai.RateLimitError):
        logger.error(f"Rate limit reached. Please wait before trying again.")
    elif isinstance(e, openai.AuthenticationError):
        logger.error(f"Authentication error. Please check your API key.")
    elif isinstance(e, openai.PermissionDeniedError):
        logger.error(f"Permission error. Your API key may not have access to this resource.")
    elif isinstance(e, openai.BadRequestError):
        logger.error(f"Invalid request: {str(e)}")
    elif isinstance(e, (openai.APIError, openai.Timeout, openai.APIConnectionError)):
        logger.error(f"API error occurred: {str(e)}. Please try again.")
    elif isinstance(e, openai.APIStatusError):
        logger.error(f"OpenAI service is currently unavailable. Please try again later.")
    else:
        logger.error(f"An unexpected error occurred: {str(e)}")
    return None
