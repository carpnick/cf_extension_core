#!/bin/zsh
set -e

echo "Installing files"
poetry install --no-interaction

echo "Generate files"
find src/ -type f -name '*.pyi' -exec rm {} +
stubgen src/ -o src/  --include-private  #Only add include private for local dev work?  Not in Github actions?


echo "Running mypy: mypy src/ tests/ --strict"
mypy src/ tests/ --strict

echo "\nRunning Unit Tests: pytest  --cov-branch --cov=src/ tests/unit --log-cli-level=DEBUG --junit-xml=junit.xml --cov-report=xml --cov-report=html:ci_coverage/"
pytest  --cov-branch --cov=src/ tests/unit --log-cli-level=DEBUG --junit-xml=junit.xml --cov-report=xml --cov-report=html:ci_coverage/

#Moved this later for dev since I care less about formatting and more about functionality
echo "\nRunning flake8: flake8 --max-line-length 120 src/ tests/"
flake8 --max-line-length 120 src/ tests/

echo "\nRunning black: black src/ tests/ -l 120 --check"
black src/ tests/ -l 120 --check


echo "\n Running poetry build: poetry build"
poetry build

echo "\n\nBuild completed successfully"