#!/bin/sh -e

set -x

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place qcelemental devtools --exclude=__init__.py
black qcelemental devtools
isort qcelemental devtools
