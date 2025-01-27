import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info('Received event: %s', json.dumps(event))
    
    url = event.get("url", "https://www.example.com")
    return {
        "url": url,
        "message": "Processed input successfully"
    }