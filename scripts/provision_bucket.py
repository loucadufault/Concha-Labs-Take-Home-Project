import configparser
import click
import os
from google.cloud import storage
import uuid

BUCKET_METADATA_CONFIG_FILENAME = os.environ.get("BUCKET_METADATA_CONFIG_FILENAME", "bucket_metadata.cfg")


def save_bucket_metadata(bucket_key, bucket_name):
    """Stores the complete bucket name in the bucket metadata config file.
    The config in this file will be included in the Flask app instance config when creating the app,
    to access the bucket real names at runtime."""
    config = configparser.ConfigParser()
    config.read(BUCKET_METADATA_CONFIG_FILENAME)

    if "DEFAULT" not in config:
        config["DEFAULT"] = {}

    config["DEFAULT"][bucket_key] = bucket_name

    with open(BUCKET_METADATA_CONFIG_FILENAME, "w") as config_file:
        config.write(config_file)


def get_new_client_bucket(bucket_name):
    # Instantiates a client
    storage_client = storage.Client()
    # Sets the bucket on client
    return storage_client.bucket(bucket_name)


def create_globally_unique_bucket(base_name):
    """Creates a GCP Storage bucket with a globally unique name, by suffixing with a uuid."""
    # we suffix the bucket name to prevent namespace conflicts
    # as the bucket namespace is shared by all users of the system
    bucket_name = base_name + "-" + str(uuid.uuid4())

    bucket = get_new_client_bucket(bucket_name)

    try:
        bucket.create()
        print(f"Bucket '{bucket_name}' created.")
    except Exception as e:
        print(f"Exception when creating bucket '{bucket_name}':")
        print(e)

    return bucket_name


@click.command()
@click.option("--key", prompt="The key or role of the bucket")
@click.option("--name", prompt="The base name of the bucket.")
def provision_bucket(key, name):
    """Provision a bucket against the GCP Storage service by generating a unique bucket name from the given base name.
    Saves the generated bucket name in the package bucket metadata config file pointed to by the
    BUCKET_METADATA_CONFIG_FILENAME environment variable (defaults to "bucket_metadata.cfg")."""
    bucket_name = create_globally_unique_bucket(name)
    click.echo(f"Created '{key}' bucket with name '{bucket_name}.'")
    save_bucket_metadata(key, bucket_name)
    click.echo(f"Saved '{key}' bucket metadata to package config file '{BUCKET_METADATA_CONFIG_FILENAME}'.")


if __name__ == "__main__":
    provision_bucket()
