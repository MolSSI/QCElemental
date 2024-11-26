set -xe
# Run tests
pytest --cov-report html:htmlcov --cov
