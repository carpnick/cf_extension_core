#!/bin/zsh
set -e

echo "Installing files"
poetry install --no-interaction

echo "Generate files"
find src/ -type f -name '*.pyi' -exec rm {} +
stubgen src/ -o src/  --include-private  #Only add include private for local dev work?  Not in Github actions?

echo "Running mypy"
mypy src/ --strict
mypy tests/ --strict

echo "\nRunning Unit Tests"
pytest  --cov-branch --cov=src/ tests/ --log-cli-level=DEBUG --junit-xml=junit.xml --cov-report=xml --cov-report=html:ci_coverage/

#Moved this later for dev since I care less about formatting and more about functionality
echo "\nRunning flake8"
flake8 --max-line-length 120 src/
flake8 --max-line-length 120 tests/

echo "\nRunning black"
black src/ -l 120 --check
black tests/ -l 120 --check


echo "\n\nBuild completed successfully"