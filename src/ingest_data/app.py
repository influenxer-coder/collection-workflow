import json
import logging
import os

import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info(f"Event received: {json.dumps(event)}")

    api_base_url = os.getenv('API_BASE_URL', None)
    if api_base_url is None:
        raise ValueError("API Base URL is missing")

    ingestion_url = f"{api_base_url}/ingest"
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(
            ingestion_url,
            json=event,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        return {
            "response": response.json()
        }
    except requests.exceptions.JSONDecodeError as e:
        logger.warning(f"Unable to parse response to JSON: {str(e)}")
        return {
            "response": response.text
        }
    except Exception as e:
        logger.error(f"Error while ingesting data")
        raise e
