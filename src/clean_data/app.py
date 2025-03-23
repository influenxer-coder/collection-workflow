import json
import logging
import os
import requests

from typing import List
import pandas as pd

logger = logging.getLogger()
logger.setLevel(logging.INFO)

BEARER_TOKEN = os.getenv("BEARER_TOKEN", "")

filters = {
    "region": "US",
    "create_time": "2024-06-01"
}

string_columns = [
    'url',
    'post_id',
    'description',
    'create_time',
    'region',
    'commerce_info',
    'profile_url',
    'preview_image'
]

numeric_columns = [
    'digg_count',
    'share_count',
    'collect_count',
    'comment_count',
    'profile_followers',
    'video_duration'
]

array_columns = [
    'hashtags'
]

object_columns = [
    'music',
]

new_columns = [
    'play_count',
    'plays',
    'influencer_type',
    'profile_biography',
    'search_term',
    'product_promo'
]


def restructure(df):
    """
    Restructure the dataframe
    Args:
        df: A Pandas dataframe

    Returns:
        df: A Pandas dataframe
    """
    df[string_columns] = df[string_columns].astype('string')
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce').fillna(0).astype(int)
    df = add_new_columns(df)
    # TODO: Remove these two line once we figure out automated pertinent video selection
    df = restructure_records(df, array_columns, replace_with=list)
    df = restructure_records(df, object_columns, replace_with=dict)
    
    df = df[string_columns + numeric_columns + array_columns + object_columns + new_columns]
    return df


def restructure_records(df: pd.DataFrame, cols: List[str], replace_with) -> pd.DataFrame:
    replacement = replace_with()
        
    for col in cols:
        if col not in df.columns:
            # Add the column if it doesn't exist
            df[col] = [replacement for _ in range(len(df))]
        else:
            # Replace missing or non-list values with empty lists
            df[col] = df[col].apply(lambda x: str(x) if isinstance(x, replace_with) else str(replacement)).astype('string')

    return df

def add_new_columns(df):
    """
    Add new columns to the dataframe
    Args:
        df: A Pandas dataframe

    Returns:
        df: A Pandas dataframe
    """
    df['play_count'] = pd.to_numeric(df['play_count'].str.replace(',', ''), errors='coerce').fillna(0).astype(int)
    df['plays'] = df['play_count'].map(get_play_level).astype('string')
    df['influencer_type'] = df['profile_followers'].map(get_influencer_type).astype('string')
    df['profile_biography'] = df['profile_biography'].map(fix_biography).astype('string')
    df['search_term'] = df['discovery_input'].map(get_search_term).astype('string')
    df['product_promo'] = False
    return df


def get_play_level(play_count):
    """
    Get the play level
    Args:
        play_count: An integer

    Returns:
        play_level: A string
    """
    if play_count < 10_000:
        return "low"
    elif play_count < 50_000:
        return "medium"
    else:
        return "high"


def get_influencer_type(profile_followers):
    """
    Get the influencer type
    Args:
        profile_followers: An integer

    Returns:
        influencer_type: A string
    """
    if profile_followers > 1_000_000:
        return "celebrity"
    elif profile_followers > 100_000:
        return "major"
    elif profile_followers > 10_000:
        return "micro"
    else:
        return "nano"


def get_search_term(discovery: dict):
    """
    Get the search term
    Args:
        discovery: A dict

    Returns:
        search_term: A string
    """
    return discovery.get("search_keyword", "")


def fix_biography(biography):
    """
    Fix the biography
    Args:
        biography: A string

    Returns:
        biography: A string
    """
    if pd.isna(biography):
        return ""
    return biography.replace("\n", " ").replace("\r", " ")


def fix_create_time(df):
    """
    Fix the create_time column
    Args:
        df: A Pandas dataframe

    Returns:
        df: A Pandas dataframe
    """
    df["create_time"] = pd.to_datetime(df["create_time"], format="mixed", utc=True, errors="raise")
    df["create_time"] = df["create_time"].dt.tz_convert("UTC")
    return df


def apply_filters(df):
    """
    Apply filters to the dataframe
    Args:
        df: A Pandas dataframe

    Returns:
        df: A Pandas dataframe
    """
    df = df[df["region"] == filters["region"]]
    cutoff_date = pd.to_datetime(filters["create_time"], utc=True)
    df = df[df["create_time"] > cutoff_date]
    return df


def get_response(snapshot_id: str) -> List[dict]:
    brightdata_url = f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}"
    querystring = {"format":"json"}
    headers = {"Authorization": f"Bearer {BEARER_TOKEN}"}
    
    try:
        response = requests.request("GET", brightdata_url, headers=headers, params=querystring)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to fetch response from Brightdata - {str(e)}")
        raise e


def clean_data(snapshot_id: str) -> pd.DataFrame:
    """
    Download data from Brightdata and process it
    Args:
        snapshot_id: Submitted to the Brightdata call
    
    Returns:
        df: A Pandas dataframe
    """
    data = get_response(snapshot_id)
    df = pd.DataFrame(data)
    df = df.astype({'post_id': 'string', 'profile_id': 'string', 'create_time': 'string', 'play_count': 'string'})
    
    logger.info(f"Received {len(df)} records from Brightdata")
    df = fix_create_time(df)
    df = apply_filters(df)
    df = restructure(df)
    logger.info(f"Cleaned data has {len(df)} records")
    return df

def lambda_handler(event, context):
    logger.info("Received event: %s", json.dumps(event))
    
    snapshot_id = event.get('snapshot_id', None)
    status = event.get('status', 'fail')
    
    if status == 'fail':
        err_message = "Failed status received"
        logger.error(err_message)
        raise Exception(err_message)
    
    if snapshot_id is None:
        err_message = "Snapshot ID is missing"
        logger.error(err_message)
        raise Exception(err_message)
    
    try:
        df = clean_data(snapshot_id)
        posts = df.to_dict(orient='records')
        return posts
    except Exception as e:
        logger.error(f"Failed to clean data: {str(e)}")
        raise e
