import json
import logging
import os
import urllib.parse

import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

BEARER_TOKEN = os.getenv("BEARER_TOKEN", "")
NOTIFICATION_URL = os.getenv("NOTIFICATION_URL", "")
LIMIT_RECORDS = int(os.getenv("LIMIT_RECORDS", 10))


def trigger_api_request(task_token, payload):
    safe_token = urllib.parse.quote_plus(task_token)

    brightdata_url = "https://api.brightdata.com/datasets/v3/trigger"

    querystring = {
        "dataset_id": "gd_lu702nij2f790tmv9h",
        "type": "discover_new",
        "discover_by": "keyword",
        "include_errors": "true",
        "limit_per_input": f"{LIMIT_RECORDS}",
        "notify": f"{NOTIFICATION_URL}?taskToken={safe_token}"
    }

    headers = {
        "Authorization": f"Bearer {BEARER_TOKEN}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.request("POST", brightdata_url, json=payload, headers=headers, params=querystring)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error from Brightdata API call: {str(e)}")
        raise e


def get_payload(event_input: dict):
    search_terms = event_input.get("search_terms", None)

    if search_terms is not None and not isinstance(search_terms, list):
        raise ValueError(f"search_terms must be a list")

    if search_terms is not None:
        return [dict(search_keyword=term) for term in search_terms]

    keywords = event_input.get("keywords", {})
    descriptor = keywords.get("descriptor", "")
    features = keywords.get("features", [])
    search_terms = [descriptor]
    search_terms.extend([f"{descriptor} {feature}" for feature in features])

    return [dict(search_keyword=term) for term in search_terms]


def lambda_handler(event, context):
    logger.info("Event received: %s", json.dumps(event))

    event_input = event.get("input", {})
    task_token = event.get("taskToken", "")

    try:
        payload = get_payload(event_input)
        response = trigger_api_request(task_token, payload)
        success_message = "Called brightdata API successfully"

        logger.info(f"{success_message}: Task token - {task_token}")
        return {
            "payload": payload,
            "brightdata_response": response,
            "message": success_message
        }
    except Exception as e:
        logger.error(f"Error in Brightdata Callback Lambda Function: {str(e)}")
        raise e
