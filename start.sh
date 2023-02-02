#!/bin/bash

flask --app src.main init-db
flask --app src.main configure-gcp-credentials
flask --app src.main configure-buckets
gunicorn --bind :$1 --workers 1 --threads 8 --timeout 0 'src.main:create_app()'
