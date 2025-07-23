setup:
	pipenv install
	pipenv run pre-commit install

train_pipeline:
	pipenv run python train/main.py

local_inference:
	pipenv run python inference/app.py

unit_test:
	pipenv run pytest inference/tests/unit_test/test_all.py

integration_test:
	pipenv run pytest inference/tests/integration_test/test_lambda_api.py

code_format:
	pipenv run isort .
	pipenv run black .
	pipenv run pylint .
