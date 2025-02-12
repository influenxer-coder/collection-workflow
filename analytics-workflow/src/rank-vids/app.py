import json
import logging
import os
from datetime import datetime

import pandas as pd

logger = logging.getLogger()
logger.setLevel(logging.INFO)

TOP_X = int(os.getenv("TOP_X", 100))

weights = {
    "digg_count": 0.2,  # Likes
    "comment_count": 0.3,  # Comments
    "share_count": 0.2,  # Shares
    "play_count": 0.2,  # Views
    "recentness": 0.1  # Recentness
}


def calculate_recentness_score(create_time):
    creation_date = datetime.fromisoformat(create_time.replace("Z", "+00:00"))
    today = datetime.now(creation_date.tzinfo)

    diff = (today - creation_date).days

    # Handle division by zero
    if diff == 0:
        return 365  # Max score

    recentness_score = 365 / diff
    return recentness_score


def filter_region(df, region):
    return df[df['region'] == 'US']


def convert_to_int(value):
    if pd.isna(value) or value == "":
        return 0
    return int(float(value))


def clean_dataframe(df):
    # Handle no hashtags
    if "hashtags" not in df.columns:
        df["hashtags"] = [[] for _ in range(len(df))]
    else:
        df["hashtags"] = df["hashtags"].apply(lambda x: x if isinstance(x, list) else [])

    # Handle no profile_biography
    if "profile_biography" not in df.columns:
        df["profile_biography"] = ""  # Add empty strings for all rows
    else:
        df["profile_biography"] = df["profile_biography"].fillna("")

    # Convert to integer
    count_columns = ["digg_count", "comment_count", "share_count", "play_count"]
    for col in count_columns:
        df[col] = df[col].apply(convert_to_int)

    return df


def calculate_impact_scores(df):
    df["recentness_score"] = df["create_time"].apply(calculate_recentness_score)
    df["raw_score"] = (
            df["digg_count"] * weights["digg_count"]
            + df["comment_count"] * weights["comment_count"]
            + df["share_count"] * weights["share_count"]
            + df["play_count"] * weights["play_count"]
            + df["recentness_score"] * weights["recentness"]
    )
    return df


def normalize_impact_scores(df):
    # Normalize the raw scores to a range of [0, 1]
    min_score = df["raw_score"].min()
    max_score = df["raw_score"].max()
    if min_score == max_score:
        df["normalized_score"] = 0.5  # Neutral score if all scores are the same
    else:
        df["normalized_score"] = (df["raw_score"] - min_score) / (max_score - min_score)

    return df


def drop_duplicates(df):
    return df.drop_duplicates(subset=['url'], keep='last')

def re_rank_posts(posts):
    df = pd.DataFrame(posts)

    df = filter_region(df, 'US')
    df = drop_duplicates(df)
    df = clean_dataframe(df)
    df = calculate_impact_scores(df)
    df = normalize_impact_scores(df)

    ranked_posts = df.to_dict("records")

    return sorted(ranked_posts, key=lambda x: x["normalized_score"], reverse=True)


def lambda_handler(event, context):
    logger.info("Received event: %s", json.dumps(event))
    posts = event.get('records', [])

    ranked_posts = re_rank_posts(posts)

    # Select the top x most impactful posts
    top_x_posts = ranked_posts[:TOP_X]

    return {
        "count": len(top_x_posts),
        "posts": top_x_posts,
        "message": "Sorted posts successfully"
    }
