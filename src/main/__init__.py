import os
import shutil
import sys
import click
from werkzeug.exceptions import HTTPException
from werkzeug.middleware.proxy_fix import ProxyFix
from flask import Flask, json, make_response, send_from_directory
from .exceptions import ValidationError, NoSuchInstanceError
import configparser
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

DB_FILENAME = "db.sqlite"
SPEC_FILENAME = "openapi.yaml"

BUCKET_METADATA_CONFIG_FILENAME = os.environ.get("BUCKET_METADATA_CONFIG_FILENAME", "bucket_metadata.cfg")

# detect if we are running the app or a click command (hacky, but we only use this to conditionally suppress a warning)
command_line = ' '.join(sys.argv)
is_running_server = ('run' in command_line) or ('gunicorn' in command_line)


def create_app(test_config=None):
    """Create and configure the app."""

    app = Flask(__name__, instance_relative_config=True)

    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
    )

    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, DB_FILENAME)
    )

    def load_bucket_metadata_config(file):
        config = configparser.ConfigParser()
        config.optionxform = lambda option: option.upper()  # Only values in uppercase are actually stored in the config object later on
        config.read(file.name)
        return dict(config["bucket_metadata"])

    if test_config is None:
        try:
            app.config.from_file("config.cfg", load=load_bucket_metadata_config)  # , silent=True)
        except FileNotFoundError as le:
            # we only want to error if this is the case once running the app, otherwise we may be running commands
            if is_running_server:
                print("No instance config file, make sure to configure buckets with 'configure-buckets' command.")
                raise le
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Register error handling middleware

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        """Return JSON instead of HTML for HTTP errors."""
        # start with the correct headers and status code from the error
        response = e.get_response()
        # replace the body with JSON
        response.data = json.dumps({
            "code": e.code,
            "name": e.name,
            "description": e.description,
        })
        response.content_type = "application/json"
        return response

    @app.errorhandler(ValidationError)
    def handle_validation_error(e):
        response = make_response(json.dumps(
            e.to_http_problem().serialize()
        ), 400)
        response.content_type = "application/json"
        return response

    @app.errorhandler(NoSuchInstanceError)
    def handle_no_such_instance_error(e):
        response = make_response(json.dumps(
            e.to_http_problem().serialize()
        ), 404)
        response.content_type = "application/json"
        return response

    # Register CLI commands to provision resources on machine and in GCP

    from .data_sources import db
    db.init_app(app)

    @click.command("configure-buckets")
    def configure_buckets():
        if not os.path.isfile(BUCKET_METADATA_CONFIG_FILENAME):
            click.echo(f"Bucket metadata config file '{BUCKET_METADATA_CONFIG_FILENAME}' was not found.")
            click.echo("Make sure to provision the buckets first with 'provision_bucket.py' script.")
            return

        bucket_metadata_config = configparser.ConfigParser()
        bucket_metadata_config.read(BUCKET_METADATA_CONFIG_FILENAME)

        instance_config_filename = os.path.join(app.instance_path, "config.cfg")
        current_instance_config = configparser.ConfigParser()
        current_instance_config.read(instance_config_filename)

        current_instance_config["bucket_metadata"] = bucket_metadata_config["DEFAULT"]

        with open(instance_config_filename, "w") as instance_config_file:
            current_instance_config.write(instance_config_file)

        click.echo(f"Copied bucket metadata config from package config '{BUCKET_METADATA_CONFIG_FILENAME}' to instance config '{instance_config_filename}'.")

    app.cli.add_command(configure_buckets)

    @click.command("configure-gcp-credentials")
    def configure_gcp_credentials():
        google_application_credentials_filename = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_FILENAME", "google_application_credentials.json")
        ROOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
        src = os.path.join(ROOT_DIR, google_application_credentials_filename)
        dst = os.path.join(app.instance_path, "google_application_credentials.json")
        shutil.copyfile(src, dst)
        click.echo(f"Copied GCP credentials file from package file '{src}' to instance file '{dst}'.")

    app.cli.add_command(configure_gcp_credentials)

    # Register routes

    @app.route("/ping")
    def hello():
        return "running", 200

    @app.route("/docs/openapi.yaml")
    def specs():
        return send_from_directory(app.root_path, SPEC_FILENAME)

    from .controllers import accounts, audios, docs
    app.register_blueprint(accounts.bp)
    app.register_blueprint(audios.bp)
    app.register_blueprint(docs.bp)

    return app
