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
                model="gpt-4o",  # Or 'gpt-4' if you have access to it
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
            return ""


# Function to summarize the product
def summarize_product(text):
    prompt = (f"Summarize the following text into 2-3 lines, including who the product is for, the promise or impact "
              f"of the product on the end user:\n\n{text}\n\nSummary:")
    return get_openai_completion(prompt)


# Function to summarize the product reviews
def summarize_reviews(reviews):
    if not reviews:
        return "No reviews found."

    # Limit to top 3 reviews or summarize all
    num_reviews_to_summarize = min(len(reviews), 3)
    reviews_to_summarize = reviews[:num_reviews_to_summarize]

    # Concatenate reviews for summarization
    reviews_text = "\n".join(reviews_to_summarize)
    prompt = f"Summarize the top {num_reviews_to_summarize} reviews:\n\n{reviews_text}\n\nSummary:"
    return get_openai_completion(prompt)


def lambda_handler(event, context):
    logger.info('Received event: %s', json.dumps(event))

    body_content = event.get("body_content", "")
    image_urls = event.get("image_urls", [])
    reviews = event.get("reviews", [])

    # Summarize the product
    summary = summarize_product(body_content)

    # Summarize the reviews
    reviews_summary = summarize_reviews(reviews)

    logger.info('Time remaining: %d second(s)', (context.get_remaining_time_in_millis() / 1000))
    return {
        "product_summary": summary,
        "image_urls": image_urls,
        "reviews_summary": reviews_summary,
        "message": "Summarized products successfully"
    }
