set -e

echo "Starting CFN Contract Tests"
#Currently requires environment variables - Will support --profile in releases above 0.2.28 - https://github.com/aws-cloudformation/cloudformation-cli/issues/965
if [[ -z "${AWS_ACCESS_KEY_ID}" ]]; then
  echo "Failed to find AWS_ACCESS_KEY_ID env variable"
  exit 1
fi

if [[ -z "${AWS_SECRET_ACCESS_KEY}" ]]; then
  echo "Failed to find AWS_SECRET_ACCESS_KEY env variable"
  exit 1
fi

if [[ -z "${AWS_SESSION_TOKEN}" ]]; then
  echo "Failed to find AWS_SESSION_TOKEN env variable"
  exit 1
fi

cfn test
