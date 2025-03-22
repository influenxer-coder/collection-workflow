import json
import logging
import re

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def download_webpage(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/132.0.0.0 Safari/537.36',
        'Accept-Language': 'da, en-gb, en',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Referer': 'https://www.google.com/'
    }
    try:
        response = requests.get(url, headers=headers, timeout=120)
        response.raise_for_status()
        if len(response.content) < 100:
            raise Exception(f"Page redirected: {response.content}")
        return response
    except Exception as e:
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

    if "url" not in event:
        logger.error(f"URL not provided: {json.dumps(event)}")
        raise Exception("URL not provided")

    url = event.get("url")
    body_content, image_urls, reviews = scrape_product_page(url)
    # TODO: save the product details to the Database

    logger.info('Time remaining: %d second(s)', (context.get_remaining_time_in_millis() / 1000))
    return {
        "body_content": body_content,
        "reviews": reviews,
        "message": "Processed input successfully"
    }
