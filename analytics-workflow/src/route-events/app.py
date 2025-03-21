import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    logger.info('Received event: %s', json.dumps(event))

    event_details = event.get('detail', {})
    url = event_details.get('url', None)
    search_terms = event_details.get('search_terms', None)

    logger.info('Time remaining: %d second(s)', (context.get_remaining_time_in_millis() / 1000))
    
    if url:
        return {
            'url': url,
            'type': 'scrape'
            'message': 'Processed events successfully'
        }
    
    if search_terms:
        return {
            'url': search_terms,
            'type': 'collect'
            'message': 'Processed events successfully'
        }
    
    logger.error(f'Failed to fetch details from event: {str(event)}')
    raise Exception('Failed to fetch details from event', event)