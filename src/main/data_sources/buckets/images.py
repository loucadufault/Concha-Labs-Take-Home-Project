from flask import current_app, g
from src.main.helpers.storage_utils import get_new_client_bucket


def get_image_bucket():
    """Connect to the application's configured image Storage bucket.
    The client is unique for each request and is reused throughout the same request."""
    bucket_name = current_app.config["IMAGE_BUCKET"]

    if "buckets" not in g:
        g.buckets = {}

    if bucket_name not in g.buckets:
        g.buckets[bucket_name] = get_new_client_bucket(bucket_name)

    return g.buckets[bucket_name]
