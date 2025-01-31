import json
import logging
import re

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def download_webpage(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/58.0.3029.110 Safari/537.3'
    }
    try:
        response = requests.get(url, headers=headers, timeout=120)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred while fetching the webpage: {e}")
        raise e


def scrape_product_page(url):
    response = download_webpage(url)
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

    # TODO: if url is not provided throw an error

    body_content, image_urls, reviews = scrape_product_page(url)

    logger.info('Time remaining: %d second(s)', (context.get_remaining_time_in_millis() / 1000))
    return {
        "body_content": body_content,
        "image_urls": image_urls,
        "reviews": reviews,
        "message": "Processed input successfully"
    }
