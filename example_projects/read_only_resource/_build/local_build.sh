set -e

echo "Running cfn validate: cfn validate"
cfn validate

echo "Running cfn generate: cfn generate"
cfn generate

echo "Running mypy: mypy src/ tests/"
mypy src/ tests/

echo "\nRunning Unit Tests: pytest --cov-branch --cov=src/ tests/unit --log-cli-level=DEBUG --junit-xml=junit.xml --cov-report=xml --cov-report=html:ci_coverage/"
pytest --cov-branch --cov=src/ tests/unit --log-cli-level=DEBUG --junit-xml=junit.xml --cov-report=xml --cov-report=html:ci_coverage/

echo "Running black:  black -l 120 --check --extend-exclude \".*models\.py\" src/ tests/"
black -l 120 --check --extend-exclude ".*models\.py" src/ tests/


echo "\nRunning flake8: flake8 --max-line-length 120 --per-file-ignores='src/**/models.py:F401,W391' src/ tests/"
flake8 --max-line-length 120 --per-file-ignores='src/**/models.py:F401,W391' src/ tests/


echo "\n Running cfn submit for build verification: cfn submit --dry-run"
cfn submit --dry-run


echo "Build is completed"