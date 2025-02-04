import openai
from log import gpt_logger as logger

__chatgpt_role__ = ("You are a helpful assistant that analyzes tweets to determine if they mention cryptocurrency "
          "and assess their sentiment. "

          "1. If a tweet **does not** mention cryptocurrency, respond with the string \"nothing\". Make sure it does not include ANY punctuation or extra characters. Simply just that string and nothing else."
          
          "2. If a tweet **does** mention cryptocurrency: "
          "- Determine whether the mention is **positive** or **negative**. "
          "- Summarize the sentiment in 1-2 sentences. "
          "- Compare the sentiment to **current cryptocurrency market trends** "
          "(e.g., price movement, major news, investor sentiment).")

def analyze_tweet(tweet):
    try:
        response = openai.chat.completions.create(
                model="gpt-4o",
                messages=_create_gpt_message(tweet),
                temperature=0.7
            )
    except Exception as e:
        _handle_openai_error(e)
        pass

    if not hasattr(response, 'choices') or not response.choices:
        logger.error("API response does not contain 'choices'")
        raise ValueError("API response does not contain 'choices'")
    if not hasattr(response.choices[0], 'message') or not hasattr(response.choices[0].message, 'content'):
        logger.error("API response does not contain expected content")
        raise ValueError("API response does not contain expected content")
    
    response_message = response.choices[0].message.content.strip()
    if response_message == "nothing":
        logger.info(f"Nothing of value was found in this tweet: {tweet}")
        return None
    else:
        logger.info(f"Crypto mention found in tweet: {tweet}")
        return response_message

def _create_gpt_message(tweet):
    """Create the message structure for the GPT API request."""
    return [
        {"role": "system", "content": __chatgpt_role__},
        {"role": "user", "content": f"{tweet}"}
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
    return