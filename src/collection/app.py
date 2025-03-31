import json
import logging
import os

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.client("stepfunctions")


def lambda_handler(event, context):
    try:
        logger.info("Event received: %s", json.dumps(event))

        body = json.loads(event.get("body", "{}"))

        input = {}
        if "url" in body:
            input['url'] = body.get('url')
            input['type'] = 'scrape'
        elif "search_terms" in body:
            input['search_terms'] = body.get('search_terms', [])
            input['type'] = 'collect'
        else:
            input['type'] = 'undefined'
            input['body'] = body

        response = client.start_execution(
            stateMachineArn=os.environ['STATE_MACHINE_ARN'],
            input=json.dumps(input)
        )
        success_message = "Collection triggered successfully"
        logger.info("{success_message}: %s", str(response))
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": success_message,
                "response": response['ResponseMetadata']
            })
        }
    except Exception as e:
        err_message = "Failed to trigger collection"
        logger.error(f"{err_message}", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({
                "message": err_message,
                "error": str(e)
            })
        }
