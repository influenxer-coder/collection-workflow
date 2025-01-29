import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info("Received event: %s", json.dumps(event))

    product_summary = event.get("product_summary", "")
    image_urls = event.get("image_urls", [])
    reviews_summary = event.get("reviews_summary", [])

    keywords = ["keyword1", "keyword2", "keyword3"]

    logger.info('Time remaining: %d second(s)', (context.get_remaining_time_in_millis() / 1000))
    return {
        "product_summary": product_summary,
        "reviews_summary": reviews_summary,
        "image_urls": image_urls,
        "keywords": keywords,
        "message": "Extracted keywords successfully"
    }
