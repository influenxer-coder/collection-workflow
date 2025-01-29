import json
import logging
import os

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

eventbridge = boto3.client('events')


def put_event(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
        detail = {
            "url": body.get("url", "https://example.com")
        }

        logger.info("Received request: %s", json.dumps(detail))

        response = eventbridge.put_events(
            Entries=[
                {
                    "Source": os.getenv("EVENT_SOURCE", "tapestry"),
                    "DetailType": os.getenv("EVENT_DETAIL_TYPE", "api-request"),
                    "Detail": json.dumps(detail),
                    "EventBusName": os.getenv("EVENT_BUS_NAME", "default")
                }
            ]
        )
        logger.info("Event sent successfully: %s", json.dumps(response))

        logger.info('Time remaining: %d second(s)', (context.get_remaining_time_in_millis() / 1000))
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Event sent to Tapestry event bus",
                "response": response
            })
        }

    except Exception as e:
        logger.error("Error sending event: %s", str(e), exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Failed to send event to Tapestry event bus",
                "error": str(e)
            })
        }
