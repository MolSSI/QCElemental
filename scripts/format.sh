#!/bin/sh -e

set -x

poetry run autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place . --exclude=__init__.py
poetry run black .
poetry run isort .
