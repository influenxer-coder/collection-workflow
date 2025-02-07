# Define weights for each metric (adjust based on your priorities)
import json
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

TOP_X = int(os.getenv("TOP_X", 100))

weights = {
    "digg_count": 0.2,  # Likes
    "comment_count": 0.4,  # Comments
    "share_count": 0.3,  # Shares
    "play_count": 0.1  # Views
}


def calculate_impact_score(post):
    # Calculate the score
    score = (
            int(post.get("digg_count", 0)) * weights["digg_count"]
            + int(post.get("comment_count", 0)) * weights["comment_count"]
            + int(post.get("share_count", 0)) * weights["share_count"]
            + int(post.get("play_count", 0)) * weights["play_count"]
    )
    return score


def lambda_handler(event, context):
    logger.info("Received event: %s", json.dumps(event))
    data = event.get('records', [])
    for post in data:
        post["impact_score"] = calculate_impact_score(post)

    # Sort posts by impact score in descending order
    sorted_posts = sorted(data, key=lambda x: x["impact_score"], reverse=True)

    # Select the top x most impactful posts
    top_x_posts = sorted_posts[:TOP_X]

    return {
        "posts": top_x_posts,
        "message": "Sorted posts successfully"
    }
