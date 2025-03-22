import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.error("Received event: %s", json.dumps(event))

    return {
        "statusCode": 500,
        "body": json.dumps({
            "message": "Internal Server Error"
        })
    }
