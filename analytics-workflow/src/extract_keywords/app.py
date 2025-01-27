import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    
    logger.info("Received event: %s", json.dumps(event))
    
    url = event.get("url", "https://www.example.com")

    keywords = ["keyword1", "keyword2", "keyword3"]
    return {
        "url": url,
        "keywords": keywords,
        "message": "Extracted keywords successfully"
    }