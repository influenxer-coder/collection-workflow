import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info('Received event: %s', json.dumps(event))

    url = event.get("detail", {}).get("url", "https://www.example.com")

    logger.info('Time remaining: %d second(s)', (context.get_remaining_time_in_millis() / 1000))
    return {
        "url": url,
        "message": "Processed events successfully"
    }
