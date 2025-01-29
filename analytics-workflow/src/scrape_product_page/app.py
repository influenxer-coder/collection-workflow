import json
import logging
import re

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def scrape_product_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract all body text content
    body_content = soup.body.get_text(separator=' ', strip=True)

    # Extract all image URLs
    image_urls = [img['src'] for img in soup.find_all('img') if 'src' in img.attrs]

    # Extract reviews based on identifiable patterns in the text
    reviews = [sentence.strip() for text in soup.find_all(string=True)
               for sentence in re.split('[?.!:]', text)
               if any(word in sentence.lower() for word in ['great', 'good', 'excellent'])]

    return body_content, image_urls, reviews


def lambda_handler(event, context):
    logger.info('Received event: %s', json.dumps(event))

    url = event.get("url", "https://www.example.com")

    # TODO: handle edge case - url might not talk about any product

    body_content, image_urls, reviews = scrape_product_page(url)

    logger.info('Time remaining: %d second(s)', (context.get_remaining_time_in_millis() / 1000))
    return {
        "body_content": body_content,
        "image_urls": image_urls,
        "reviews": reviews,
        "message": "Processed input successfully"
    }
