import json
import requests
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", None)

def lambda_handler(event, context):
    """
    Lambda handler that sends notifications to Slack.
    
    Args:
        event: Event data from Step Functions containing message details
        context: Lambda context
        
    Returns:
        Response dictionary with status code and message
    """
    logger.info(f"Event received: {json.dumps(event)}")
    
    if not SLACK_WEBHOOK_URL:
        error_msg = "SLACK_WEBHOOK_URL is missing"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    slack_message = generate_slack_message(event, context)
    
    try:
        response = post_to_slack(SLACK_WEBHOOK_URL, slack_message)
        logger.info(f"Message sent to Slack successfully: {str(response)}")
        return {
            "statusCode": 200,
            "body": {
                "message": "Notification sent to Slack successfully"
            }
        }
    except Exception as error:
        error_message = f"Failed to send notification to Slack: {str(error)}"
        logger.error(error_message)
        raise Exception(error_message)


def generate_slack_message(event, context):
    """
    Creates a slack message to be sent to Slack
    
    Args:
        event: Event data from Step Functions containing message details
        context: Lambda context
        
    Returns:
        The slack message object
    """
    message = event.get('message', 'No message provided')
    status = event.get('status', 'unknown')
    details = event.get('details', {})
    execution_id = event.get('executionId', 'Unknown')
    
    emoji = '✅' if status == 'success' else '❌'
    
    error_section = ""
    if details and isinstance(details, dict) and details.get('error'):
        error_obj = details['error']
        if isinstance(error_obj, str):
            error_obj = {"message": error_obj}
            
        error_section = f"*Error Details*:\n```{json.dumps(error_obj, indent=2)}```"


    display_execution_id = execution_id.split(':')[-1] if execution_id and ':' in execution_id else execution_id
    aws_region = context.invoked_function_arn.split(':')[3]
    console_link = f"https://{aws_region}.console.aws.amazon.com/states/home?region={aws_region}#/executions/details/{execution_id}"

    slack_message = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{emoji} {message}"
                }
            }, {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Details* \n\nExecution ID: {display_execution_id}\nConsole Link: <{console_link}|here>"
                }
            }
        ]
    }
    
    if error_section:
        slack_message["blocks"].append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": error_section
            }
        })
    
    return slack_message


def post_to_slack(webhook_url, message):
    """
    Posts a message to a Slack webhook URL.
    
    Args:
        webhook_url: The Slack webhook URL
        message: The message payload to send
        
    Returns:
        The response body from Slack
        
    Raises:
        Exception: If the request fails
    """
    
    headers={'Content-Type': 'application/json'}
    try:
        response = requests.request("POST", webhook_url, json=message, headers=headers)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logger.error(f"Error sending request to Slack: {str(e)}")
        raise e