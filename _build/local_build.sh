#!/bin/zsh
set -e

echo "Installing files"
poetry install --no-interaction

echo "Running Stub file checks: stubtest cf_extension_core"
stubtest cf_extension_core



echo "Running mypy: mypy src/ tests/ --strict"
mypy src/ tests/ --strict

echo "\nRunning Unit Tests: pytest  --cov-branch --cov=src/ tests/unit --log-cli-level=DEBUG --junit-xml=junit.xml --cov-report=xml --cov-report=html:ci_coverage/"
pytest  --cov-branch --cov=src/ tests/unit --log-cli-level=DEBUG --junit-xml=junit.xml --cov-report=xml --cov-report=html:ci_coverage/

#Moved this later for dev since I care less about formatting and more about functionality
echo "\nRunning black: black src/ tests/ -l 120 --check"
black src/ tests/ -l 120 --check

echo "\nRunning flake8: flake8 --max-line-length 120 src/ tests/"
flake8 --max-line-length 120 src/ tests/


echo "\n Running poetry build: poetry build"
poetry build

echo "\n\nBuild completed successfully"