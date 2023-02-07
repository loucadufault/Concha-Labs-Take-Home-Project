# Concha-Labs-Backend-Engineer-Take-Home-Project

# Pre-requisites

The app is written in Python3 and uses Flask as a server framework. It requires all the runtime dependencies listed in the `requirements.txt` folder in the project root. It has been tested with Python 3.7.9 on macOS, but should be compatible with older Python3 versions.

This README documents the specific commands to set up, build, run or deploy, and test the server. Several of the commands are present as targets in the `Makefile` which can be convenient. This requires [`make`](https://en.wikipedia.org/wiki/Make_(software)).

The commands may need to be adapted for a Windows environment.

The setup assumes some familiarity with the Google Cloud Platform, as well as a functioning and billable GCP account.

# Compatibility

The latest compatible Python major version is Python 3.7, as the application code uses a package that only supports this version: https://pypi.org/project/dataclasses-json/

The Docker image sets the Python version used in the image to 3.7, so there is no need to change Python versions so long as the server is run in a container. The scripts that are run locally (before building the Docker image) should be compatible with the latest Python release.

# Installation

Clone the repo:

`git clone git@github.com:loucadufault/Concha-Labs-Backend-Engineer-Take-Home-Project.git`

In the root of the project directory, create and activate a virtual environment with the [`venv`](https://docs.python.org/3/library/venv.html#module-venv) module:

`python3 -m venv venv`

`. venv/bin/activate`

Then install the dependencies with `pip`:

`pip install -r requirements.txt`

# Quick setup

This uses already-provisioned GCP resources to speed up the setup process. 

It does not require provisioning CGP Storage buckets, or creating a key and copying credentials to grant programmatic access to the GCP client libraries to access these at runtime. You will still need to setup the GCP CLI and login, in order to be able to deploy the server as a GCP service.

Namely, the required GCP Storage buckets have already been provisioned (in a project of an account I own) and made publicly available. The credentials file for a service account key under this project is included in the source code committed to the VCS (for convenience, this is a bad practice outside a toy project).

To set up this way, follow the [Setup](#setup) process, skipping the [Authenticate GCP client libraries](#authenticate-gcp-client-libraries) and [Provision GCP resources](#provision-gcp-resources) steps.

# Setup

All commands should be run from the project root.

## Setup GCP Project and CLI

1. In the Google Cloud console, on the project selector page, select or [create a Google Cloud project](https://cloud.google.com/resource-manager/docs/creating-managing-projects).

2. Make sure that billing is enabled for your Cloud project. See [how to check if billing is enabled on a project](https://cloud.google.com/billing/docs/how-to/verify-billing-enabled). 

3. Install the Google Cloud CLI https://cloud.google.com/sdk/docs/install

4. To [initialize](https://cloud.google.com/sdk/docs/initializing) the gcloud CLI, run the following command:

`gcloud init`

5. To set the default project for your Cloud Run service: 

`gcloud config set project PROJECT_ID`

Replace `PROJECT_ID` with the name of the project you created.

## Authenticate GCP client libraries

The application must be configured to authenticate the GCP client libraries running on the server with appropriate permissions to access the GCP resources. This is done by creating a key for a service account in the GCP project (usually the "Default compute service account"), and then including the credentials file in the project source so that it can be made available to the application at runtime, to be used to authorize the GCP client libraries to access the provisioned services.

To download a private key, go to [console.cloud.google.com/iam-admin/serviceaccounts](https://console.cloud.google.com/iam-admin/serviceaccounts), select the project, then choose the “KEYS” tab, from the ADD KEY dropdown choose “Create new key”, choose the Key type as JSON, then click “CREATE” to download the credentials file. Copy this file into the project root directory as is, then either:  
a) Rename it to “google_application_credentials.json” or  
b) Create a `.env` file in the project root and set the `GOOGLE_APPLICATION_CREDENTIALS_FILENAME` variable to the filename of the credentials file. The `.env` file might look like (this is the one committed to the VCS for quick setup):

```commandline
GOOGLE_APPLICATION_CREDENTIALS_FILENAME=concha-labs-take-home-project-b91859524e56.json
```

## Provision GCP resources

The server requires two distinct GCP Storage buckets. One bucket is used to store images uploaded as part of basic user info, while the other backs the `audios` endpoint to persist the uploaded audio files.

As such, these two buckets must be provisioned for the server, and read and make changes to the blobs in these buckets.

The image and audios bucket names used to retrieve the bucket contents using the GCP client libraries are looked up using predetermined keys when starting the server. It expects a `config.cfg` file to be in the `instance` directory with two variables set under the `DEFAULT` section, one mapping the `image_bucket` key to its bucket name in GCP, and the other mapping the `audio_bucket` key to its bucket name.
The `scripts/provision_bucket.py` script is provided to provision a bucket against the GCP Storage service using the client libraries project dependencies, saving its generated name under the given key to a `bucket_metadata.cfg` config file in the project root. The script appends a UUID to the given base name to ensure uniqueness in the GCP Storage system namespace.

Note that provisioned buckets are not public by default, so you will not have the permission to view the links to bucket blobs that are returned as part of some resources by the server (namely the `image_hosted_url` returned as part of the user info resource under the `/accounts` endpoint). You can view these blobs by directly opening the buckets under your GCP project in the console, or by granting public access to the buckets.

Run the script with the given key and bucket name base, for both the `image_bucket` and `audio_bucket` keys:

`python3 scripts/provision_bucket.py --key image_bucket --name user_info_images`

`python3 scripts/provision_bucket.py --key audio_bucket --name audio_files`

Alternatively, run the corresponding `make` target: 

`make provision-buckets`

This should create a `bucket_metadata.cfg` file in the project root like (this is the same as the file included in the source code committed to the VCS, containing the names of the already-provisioned publicly-accessible buckets for the [Quick setup](#quick-setup)):

```
[DEFAULT]
image_bucket = user_info_images-d87de10e-a638-4f7b-8bf0-a56dcef2fea3
audio_bucket = audio_files-c9157cbb-4e5b-49ab-9431-0cade0d1db3c
```

# Serve the application

The application can be run as a container with Docker. The `Dockerfile` is included in the source code to build images.

The Dockerfile entrypoint simply runs the root `start.sh` script, which itself runs three Flask commands to setup files in the `instance` directory that are used at runtime, before starting the server with the `gunicorn` WSGI webserver with one worker process and 8 threads. 

The three Flask commands are described below (no need to run these, as it is run automatically as part of Docker build process).

### Configure Flask application to point to GCP Storage buckets (by globally-unique name)

The running Flask application reads these bucket names from a `config.cfg` file it expects in the `instance` directory. The bucket metadata is parsed and copied over from the `bucket_metadata.cfg` file in the project root in the correct format into the `instance` directory, with the Flask command to configure the buckets,

`flask --app src.main configure-buckets` (no need to run this command)

### Configure Flask application to use this credentials file

The running Flask application reads the credentials from a `google_application_credentials.json` file it expects in the `instance` directory. The downloaded credentials file is copied over from the project root directory into the `instance` directory, with the Flask command to configure credentials:

`flask --app src.main configure-gcp-credentials` (no need to run this command)

### Initialize the Database

The application uses SQLite to back the server, which stores data as a database file on the host filesystem. The Flask application is configured to store its database file in the `instance` directory, as a `main.sql` file. 

The database needs to be initialized before starting the server, which will load the `schema.sql` file and execute it to define the tables in the database file. The server will then open a connection to the SQLite database file database upon each request.

This is done with:

`flask --app src.main init-db` (no need to run this command)

## Run the server locally

### Build the Docker image

A Dockerfile is included which contains the instructions for containerizing the Flask application server. Images can be used to run local containers of the server, or deploy to GCP.

Build the Docker image tagged as `server` with:

`docker build -t server .`

### Run the container

Run an instance of the `server` image, setting the environment variable `PORT` to 8080 in the container which will be used in `start.sh` script to bind `gunicorn`, and publishing the container's 8080 port to the 9090 port on the host.

`docker run --rm -p 9090:8080 -e PORT=8080 server`

The server running inside the running container will be listening for requests to the host at the URL http://localhost:9090.

> **Note:** This will run as a long-lived process in the current terminal session. You may want to run the container in a different terminal session to avoid having to repeat the setup process.

## Deploy server to GCP

Deploy to GCP Cloud Run from source. See https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-service#deploy

Namely, run the Google Cloud CLI command:

`gcloud run deploy`

Make note of the `Service URL` printed to the console once the command completes

# Make requests to the server

If the Server is running locally, use the URL http://localhost:9090 to access the server, otherwise use the URL of the deployed GCP service.

You can make sure the server is running by making a GET request to the `/ping` route, for example http://localhost:9090/ping.

It is recommended to use an HTTP GUI client like Postman to facilitate making requests to the server. The server expects requests to the `/accounts` and `/audios` endpoints. For most operations, the server either expects the data to be encoded as URL path or query params, or as a JSON payload in the body. For a few operations, it expects either JSON or image files as form data for file uploads.

See the [Documentation](#documentation) section to explore the functionality provided by the API.

Inspecting the code of the e2e tests under the `tests/e2e` directory can also be useful in understanding the server API.

# Run the tests

Before running the tests, install the main package with:

`pip install -e .`

Otherwise, when running `pytest` you will get errors like:

```commandline
ImportError while loading conftest '.../Concha-Labs-Backend-Engineer-Take-Home-Project/tests/conftest.py'.
tests/conftest.py:6: in <module>
    from src.main import create_app
E   ModuleNotFoundError: No module named 'src'
```

The tests are run with `pytest`, and are found in the `tests` directory under the project root.

There are two test suites:
- unit tests use a test client to emulate requests against the application server, without starting the server and making requests over the network. This means they do not require a running server, nor any provisioned GCP buckets (mocked in the test code). These test the infrastructure code and the service code including request data parsing and validation. 
- end-to-end (e2e) tests run locally, but make real HTTP requests against a server that is listening for requests over the network at some URL. As such, they require a running instance of the application server (either locally such as within a Docker container, or deployed such as a deployed GCP service), and require the URL of the server to be provided as an input. These test the complete behavior of the application server and request handling, including persisting entities to the server persistence and to the buckets provisioned on GCP for the server, and retrieving resources in subsequent requests.

## Run the unit tests

The unit tests can be run with:

`pytest -m "not uses_server"`

This uses `pytest`’s [Marks API](https://docs.pytest.org/en/7.1.x/reference/reference.html#marks-ref) to only run those test functions that do not require a running server (namely filters out the e2e tests).

Alternatively, run the corresponding `make` target:

`make test-unit`

### Coverage 

Coverage can be tracked for the unit tests with:

`coverage run -m pytest -m "not uses_server"`

Here is the coverage report, generated with `coverage report`:

```commandline
Name                                            Stmts   Miss Branch BrPart  Cover
---------------------------------------------------------------------------------
src/main/__init__.py                               84     36      8      1    55%
src/main/controllers/accounts.py                   54     37     14      0    25%
src/main/controllers/audios.py                     56     40     14      0    23%
src/main/controllers/docs.py                        3      0      0      0   100%
src/main/data_sources/buckets/audios.py             9      6      4      0    23%
src/main/data_sources/buckets/images.py             9      6      4      0    23%
src/main/data_sources/db.py                        25      0      8      0   100%
src/main/exceptions/NoSuchInstanceError.py          8      3      0      0    62%
src/main/exceptions/ValidationError.py             11      3      0      0    73%
src/main/exceptions/__init__.py                     2      0      0      0   100%
src/main/helpers/dict_utils.py                      2      1      2      0    25%
src/main/helpers/email_utils.py                    11      2      0      0    82%
src/main/helpers/filename_validation_utils.py       2      1      0      0    50%
src/main/helpers/header_utils.py                    3      1      0      0    67%
src/main/helpers/storage_utils.py                   8      3      0      0    62%
src/main/models/Audio.py                            9      0      2      0   100%
src/main/models/HttpProblem.py                     26     19      8      0    21%
src/main/models/UserInfo.py                         7      0      2      0   100%
src/main/models/__init__.py                         4      0      0      0   100%
src/main/parse_request/__init__.py                 58     11     26      3    81%
src/main/services/audios.py                        40     22     12      0    38%
src/main/services/user_infos.py                    53     12     10      3    73%
---------------------------------------------------------------------------------
TOTAL                                             484    203    114      7    54%
```
## Run the e2e tests

The end-to-end tests are found in the `tests/e2e` directory, and are run with `pytest` against a server that is listening for requests over the network on some url. This can either be the server running locally (or within a Docker container), or the url of the service deployed to GCP. It is specified as an input to the test runner via the `server_url` CLI option, which is used to configure the HTTP session test fixture.

For example, to run the e2e test suite against the server running locally within a Docker container where the server port is published to the 9090 port on the host, you would use:

`pytest tests/e2e --server_url=http://127.0.0.1:9090`

Note that the e2e tests are implemented as complete flows exercising the user infos and audio resources. There is a file for each endpoint, each with a single test function since the order of operations against the server is important. The test functions implement several checks against most operations provided by the API and asserting several post-conditions after each attempted operation to verify proper server state mutations.

Since the tests run against the real server, they access and mutate the data persisted on the server as well as on the various GCP services (namely the two buckets). As such, you will need to wipe this data to reset the server to a known state before beginning the tests. This can be done manually by emptying the buckets provisioned for the server, and making the corresponding HTTP DELETE requests to delete all user info. 

Alternatively, the `scripts/delete_server_resources.py` script is provided to automate the process of deleting the REST resources persisted in the server state. Call it by specifying the URL of the server to make the HTTP DELETE requests against, and the endpoint corresponding to the resources to delete. You would need to run this for both the `accounts` and `audios` endpoints. For example, to delete all user info resources under the `accounts` and all audio files under the `audios` endpoint from the server running locally within a Docker container where the server port is published to the 9090 port on the host, you would use (do not include the leading ‘/’ in the endpoint):

`python3 scripts/delete_server_resources.py --server_url http://127.0.0.1:9090 --endpoint accounts && python3 scripts/delete_server_resources.py --server_url http://127.0.0.1:9090 --endpoint audios`

This would need to be run before each run of the e2e test suite, otherwise the tests will not pass (as they will assume an incorrect initial state of the server).

# Documentation

An OpenAPI spec is included in the source code documenting the API endpoints and functionality, namely the various operations and expected inputs. 

The spec is served from the server itself as a SwaggerUI at the `/docs` endpoint, or as the `.yaml` file itself from the `/docs/openapi.yaml` route. For example:

`http://localhost:9090/docs`

There are a few aspects that are not documented in the spec.

The first is the `/accounts/{user_id}/upload_image` route, which enables uploading an image to the server to be used as the basic user information image. The image file must be attached as form-data under the "image" key. The image file must have a `.jpeg` or `.png` file extension, and the file mimetype must be 'image/jpeg' or 'image/png'. This image is saved as a blob on the image_bucket, and the blob's `media_link` is saved to the user info in the database and returned as the `image_hosted_url` property of the response and all subsequent responses including this user info as a resource. The image can be updated on the user's info by simply calling this operation again with another image (the `image_hosted_url` cannot be directly updated with the `updateUserInfo` PUT operation).

The second is the fact that all operations to the `/audios` endpoint which accept a JSON request body representing the audio data as a JSON string, also accept the JSON file directly as a file. The audio data file must be attached as form-data under the "audio" key. The audio data file must have a `.json` file extension. Regardless of how the audio data is inputted, it is saved as a blob on the audio_bucket (with the `session_id` as the blob name for search and retrieval).

> Note on emails: We normalize emails by lower-casing the domain part. This also applies when searching by email. We perform only basic validation on emails (check that it is a string split by an ‘@’), as advanced validation is out of scope and not all that useful since we are not verifying them.

# Improvements

There are a few main areas of improvement.

## Improvements to the architecture

The audio data files are directly persisted as `.json` files in a GCP Storage bucket with the blob name as the session_id. This was done since the audio file does not necessarily make sense to encode into a SQL table, and also since the requirements specified it only necessary to retrieve audio data by session_id. Rather than directly store the audio files as blobs with the session_id as the blob name, it would have been better to use an indirection to map the audio data to the names of the blobs. This would enable searching the audio data files by properties other than the session_id. Namely, an SQL table would be maintained containing indexed properties of the audio data (such as step_count, selected_tick as well as the session_id) together with the randomly generated blob name. This would allow searching and retrieving audio files by any of these indexed properties. It would also make the bucket resilient to schema changes or duplicate session_ids.

## Improvements to the implementation code

It might have been better to abstract interactions with the data access layer as repositories implementing generic CRUD operations, to expose to the service layers. As it is the service layer is quite business heavy as it includes business logic and SQL query manipulation.

It would have been better to add typings to the source code, to gain confidence that all code paths are type-safe.

## Improvements to the API

Operations that return several resources should be paginated, and trimmed to a maximum number of results. This implies including pagination arguments as query params, to indicate which page of resources to retrieve.

Resources should have an etag in-built, to enable optimistic resource locking (prevent two server clients from updating the same resource concurrently, causing a lost update, by requiring the etag be provided and matched against the existing persisted entity's tag).

Responses could return a response that wraps the resource(s) with some metadata, for example the item count, the resource type.

Problem response could be better formalized, for example by having the problem types be actual URI routes on the API, having instance ids for cross-referencing.

Resources could be returned with timestamps like created_at and updated_at.

## Improvements to the infrastructure

It would be better to house the application persistence as a separate service, probably using a GCP service for this purpose (some SQL or noSQL service). This would present better separation of concerns, as well as eliminating problems related to setting up the Database in order to start the server, filesystem strain and resource contention between the SQL engine and server. It would also enable using the data management practices offered by managed data services, such as logging, auditing, recovery, access control.

In a real-world backend, depending on the scale and availability requirements, it might be appropriate to replicate the server to multiple hosts and front the hosts with some sort of load-balancer or other gateway/ingress to filter out bad requests and re-route good requests based on target load and health, to ensure that the service can withold high uptime.

The server could also be improved to produce and rotate structured logs of the handled requests, application logs, and host logs. It could also report metrics, and publish these for consumption for example by some GCP service that enables visualization.

To facilitate provisioning and coordination if using multiple services as described above, it would make more sense to use some template or CDK to specify the infrastructure as code (IaC). This would ensure service provisioning would be reproducible, autitable and tracked as part of VCS, and services would be properly connected with appropriate (minimal) IAM roles and permissions.

CI jobs could be added to automatically run the unit tests.
