import json
import logging
from collections import Counter
from datetime import datetime

import pandas as pd

logger = logging.getLogger()
logger.setLevel(logging.INFO)

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

    df = df.fillna('')
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


def filter_commercial_posts(df):
    return df[df["commerce_info"] == "Paid partnership"]


def filter_data(df):
    df = filter_region(df, 'US')
    # df = filter_commercial_posts(df)
    return df


def get_popular_posts(df):
    # df = df[df['digg_count'] > 200]
    df = df[df['play_count'] > 10000]
    return df


def re_rank_posts(posts):
    df = pd.DataFrame(posts)

    df = filter_data(df)
    df = drop_duplicates(df)
    df = clean_dataframe(df)
    df = get_popular_posts(df)

    df = calculate_impact_scores(df)
    df = normalize_impact_scores(df)

    ranked_posts = df.to_dict("records")

    return sorted(ranked_posts, key=lambda x: x["normalized_score"], reverse=True)


def rank_hashtags(posts):
    all_hashtags = [hashtag for post in posts for hashtag in post.get("hashtags", [])]
    hashtag_counts = Counter(all_hashtags)

    return dict(sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:20])


def lambda_handler(event, context):
    logger.info("Received event: %s", json.dumps(event))
    posts = event.get('records', [])
    posts = [post for post in posts if 'error' not in post]

    ranked_posts = re_rank_posts(posts)

    top_hashtags = rank_hashtags(ranked_posts)

    return {
        "count": len(ranked_posts),
        "posts": ranked_posts,
        "popular_hashtags": top_hashtags,
        "message": "Sorted posts successfully"
    }
