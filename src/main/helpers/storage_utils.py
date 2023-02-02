import os
from google.cloud import storage
from google.oauth2 import service_account
from flask import current_app


def get_new_client_bucket(bucket_name):
    credentials = service_account.Credentials.from_service_account_file(
        os.path.join(current_app.instance_path, "google_application_credentials.json"))
    # Instantiates a client
    storage_client = storage.Client(credentials=credentials)
    # Sets the bucket on client
    return storage_client.bucket(bucket_name)
