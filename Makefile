run-backends:
	docker-compose up -d

pretty:
	poetry run ruff check --fix
	poetry run black .

lint:
	poetry run ruff check
	poetry run black --check .
	poetry run mypy .

test: run-backends
	poetry run pytest --cov django_limits

test-ci:
	poetry run pytest --cov django_limits --cov-report=xml

html-cov: test
	poetry run coverage html
	open htmlcov/index.html

cleanup:
	docker-compose down -v
	rm -rf dist
	rm -rf htmlcov
