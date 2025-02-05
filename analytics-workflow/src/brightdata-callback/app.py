import json
import logging
import os
import urllib.parse

import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

BEARER_TOKEN = os.getenv("BEARER_TOKEN", "")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
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
        "endpoint": f"{WEBHOOK_URL}?taskToken={safe_token}",
        "format": "json"
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
        logger.error(f"Error from Brightdata API call: {e}")
        raise e


def get_payload(keywords):
    descriptor = keywords.get("descriptor", "")
    features = keywords.get("features", [])
    search_terms = [descriptor]
    search_terms.extend([f"{descriptor} {feature}" for feature in features])

    return [dict(search_keyword=term) for term in search_terms]


def lambda_handler(event, context):
    logger.info("Received event: %s", json.dumps(event))

    event_input = event.get("input", {})
    task_token = event.get("taskToken", {})

    payload = get_payload(event_input.get("keywords", {}))

    response = trigger_api_request(task_token, payload)

    logger.info('Time remaining: %d second(s)', (context.get_remaining_time_in_millis() / 1000))

    return {
        "payload": payload,
        "taskToken": task_token,
        "brightdata_response": response,
        "message": "Called brightdata API successfully"
    }
