import json
import logging

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

sfn_client = boto3.client("stepfunctions")


def lambda_handler(event, context):
    logger.info("Event received: %s", json.dumps(event))

    # Parse the Task Token from the query string
    task_token = event.get("queryStringParameters", {}).get("taskToken")
    if not task_token:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Task Token is missing"})
        }

    # Parse the notification payload from the request body
    try:
        payload = json.loads(event.get("body", "{}"))
    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid JSON payload"})
        }

    # Notify the Step Function of success
    try:
        sfn_client.send_task_success(
            taskToken=task_token,
            output=json.dumps(payload)
        )
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "taskToken": task_token,
                "error": f"Failed to notify Step Function: {str(e)}"
            })
        }

    # Return success response
    success_message = "Successfully received notifcation from Brightdata and send control back to Collection Step Function"
    logger.info(f"{success_message}: Payload - {str(payload)}")
    return {
        "statusCode": 200,
        "body": {
            "status": "SUCCESS",
            "notification": payload
        }
    }
