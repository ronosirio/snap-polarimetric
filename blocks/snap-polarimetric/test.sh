#!/bin/bash
find . -name "__pycache__" -exec rm -rf {} +
find . -name ".mypy_cache" -exec rm -rf {} +
find . -name ".pytest_cache" -exec rm -rf {} +
find . -name ".coverage" -exec rm -f {} +

python -m pytest --pylint --pylint-rcfile=../../pylintrc --mypy --mypy-ignore-missing-imports --cov=src/
