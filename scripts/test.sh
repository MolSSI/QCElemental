set -xe
# Run tests
poetry run pytest --cov-report html:htmlcov --cov
