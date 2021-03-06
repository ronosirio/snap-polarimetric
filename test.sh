#!/bin/bash
find . -name "__pycache__" -exec rm -rf {} +
find . -name ".mypy_cache" -exec rm -rf {} +
find . -name ".pytest_cache" -exec rm -rf {} +
find . -name ".coverage" -exec rm -f {} +

# Hrm, if we don't delete the cache the linter skips all if its test cases as it has problems with our conftest
rm -r .pytest_cache
black .
if [[ $* == *--live* ]]
then
  python -m pytest --pylint --pylint-rcfile=../../pylintrc --mypy --mypy-ignore-missing-imports --cov=src/ --runlive
  RET_VALUE=$?
else
  python -m pytest --pylint --pylint-rcfile=../../pylintrc --mypy --mypy-ignore-missing-imports --cov=src/
  RET_VALUE=$?
  coverage-badge -f -o coverage.svg
fi
exit $RET_VALUE
