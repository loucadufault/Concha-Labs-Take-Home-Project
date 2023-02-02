install:
	pip install -r requirements/prod.txt

run:
	gunicorn -w 1 'main:create_app()'

clean:
	rm -rf instance && rm -rf venv

test-unit:
	pytest -m "not uses_server"

provision-buckets:
	python3 scripts/provision_bucket.py --key image_bucket --name user_info_images && python3 scripts/provision_bucket.py --key audio_bucket --name audio_files
