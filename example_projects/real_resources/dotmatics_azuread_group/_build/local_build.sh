#Uncomment this when ready to test a build
set -e

echo "Running cfn validate: cfn validate"
cfn validate

echo "Running cfn-lint: cfn-lint -t test_deploy/**/*.yaml -i E3001 E1010"
cfn-lint -t test_deploy/**/*.yaml -i E3001 E1010

echo "Running cfn-lint: cfn-lint -t template_deploy_regional_extension.yaml"
cfn-lint -t template_deploy_regional_extension.yaml

echo "Running cfn generate: cfn generate.  Also determining if files are out of date in git"
cfn generate
set +e
git diff --compact-summary --exit-code
if [ $? -ne 0  ]; then
  echo "---"
  echo "'cfn generate' generated some changes. Run it locally and commit changes."
  exit 1
fi
set -e



echo "Running mypy: mypy src/ tests/  --exclude '.*models.*' --ignore-missing-imports --strict --follow-imports silent"
mypy src/ tests/  --exclude '.*models.*' --ignore-missing-imports --strict --follow-imports silent

echo "\nRunning Unit Tests: pytest --cov --cov-report html --cov-report xml --log-cli-level=DEBUG --junit-xml=junit.xml tests/unit"
pytest --cov --cov-report html --cov-report xml --log-cli-level=DEBUG --junit-xml=junit.xml tests/unit

echo "Running black:  black -l 120 --check --extend-exclude \".*models\.py\" src/ tests/"
black -l 120 --check --extend-exclude ".*models\.py" src/ tests/


echo "\nRunning flake8: flake8 --max-line-length 120 --per-file-ignores='src/**/models.py:F401,W391' src/ tests/"
flake8 --max-line-length 120 --per-file-ignores='src/**/models.py:F401,W391' src/ tests/

echo "\n Running cfn submit for build verification: cfn submit --dry-run"
cfn submit --dry-run

#For local contract testing
sam build -u -m requirements.txt

echo "Build is completed"