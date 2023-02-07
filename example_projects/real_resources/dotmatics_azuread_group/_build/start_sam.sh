set -e

echo "Starting SAM for Contract Tests"
sam local start-lambda -l log.log --region eu-west-2