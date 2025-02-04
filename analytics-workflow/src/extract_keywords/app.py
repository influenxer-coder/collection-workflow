import ast
import json
import logging
import os
import time

import openai
from openai import OpenAI

logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = OpenAI(
    api_key=os.environ.get("API_KEY"),
)


# Function to get OpenAI completion with retry logic
def get_openai_completion(prompt):
    while True:
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=200,
                n=1,
                stop=None,
                temperature=0.7,
            )
            return response.choices[0].message.content
        except openai.RateLimitError as e:
            logger.warning("Rate limit exceeded. Retrying in 5 seconds...", e)
            time.sleep(5)
        except openai.OpenAIError as e:
            logger.error("Error in fetching response: %s", str(e), exc_info=True)
            raise e


# Util function to convert string literal to a python object
def get_dict(input_string: str) -> str:
    if "```json" in input_string:
        clean_str = input_string.strip("```json\n").strip("```").strip()
        try:
            data_dict = json.loads(clean_str)
            return data_dict
        except (TypeError, ValueError) as e:
            logger.error(f"Unable to convert to Python Dict: {clean_str}")
            raise e

    clean_str = input_string.strip("```python\n").strip("```").strip() if "```python" in input_string else input_string
    try:
        data_dict = ast.literal_eval(clean_str)
        return data_dict
    except (ValueError, SyntaxError) as e:
        logger.error(f"Unable to convert to Python Dict: {clean_str}")
        raise e


# Function to suggest keywords based on product summary and benefits
def suggest_keywords(summary, benefits):
    prompt = (f"Given a product's description and reviews, give me a json object with the following structure:"
              f"\n 1. 'descriptor': a search term can be used to lookup similar products on TikTok, Instagram reels"
              f" or Youtube shorts. The search term should be as brief as possible (2-3 words)."
              f"\n 2. 'features': an array of ingredients or features present in the product. Each item in the array "
              f"should not be more than 2 words. Order the 'features' array from the most relevant to the least "
              f"relevant. The feature should improve the search when appended to the 'descriptor'.\n\n"
              f"You should only reply with a json object, no extra characters.\n\n"
              f"Product Summary: {summary}\n\n"
              f"Product Reviews: {benefits}")

    response = get_openai_completion(prompt)
    return get_dict(response)


def lambda_handler(event, context):
    logger.info("Received event: %s", json.dumps(event))

    product_summary = event.get("product_summary", "")
    image_urls = event.get("image_urls", [])
    reviews_summary = event.get("reviews_summary", [])

    keywords = suggest_keywords(product_summary, reviews_summary)

    logger.info('Time remaining: %d second(s)', (context.get_remaining_time_in_millis() / 1000))
    return {
        "product_summary": product_summary,
        "reviews_summary": reviews_summary,
        "image_urls": image_urls,
        "keywords": keywords,
        "message": "Extracted keywords successfully"
    }
