import json
import logging
import os

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.client("stepfunctions")

def lambda_handler(event, context):
    try:
        logger.info("Received request: %s", json.dumps(event))
        
        body = json.loads(event.get("body", "{}"))
        
        input = {}
        if "url" in body:
            input['url'] = body.get('url')
            input['type'] = 'scrape'
        elif "search_terms" in body:
            input['search_terms'] = body.get('search_terms', [])
            input['type'] = 'collect'
        else:
            raise ValueError("Failed to process request body")

        response = client.start_execution(
            stateMachineArn=os.environ['STATE_MACHINE_ARN'],
            input=json.dumps(input)
        )
        logger.info("Event sent successfully: %s", str(response))
        logger.info('Time remaining: %d second(s)', (context.get_remaining_time_in_millis() / 1000))
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Collection triggered successfully",
                "response": response['ResponseMetadata']
            })
        }
    except Exception as e:
        logger.error("Failed to trigger collection: %s", str(e), exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": "Failed to trigger collection",
                "error": str(e)
            })
        }
