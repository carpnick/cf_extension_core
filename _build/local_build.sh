#!/bin/zsh
set -e

echo "Installing Dependencies"
poetry install --no-interaction --no-root
mypy src/
echo "\nRunning flake8"
flake8 --max-line-length 120 src/
echo "\nRunning black"
black src/ -l 120 --check

echo "\nRunning Unit Tests"
pytest  --cov-branch --cov=src/ tests/ --log-cli-level=DEBUG --junit-xml=junit.xml --cov-report=xml --cov-report=html:ci_coverage/


echo "\n\nBuild completed successfully"