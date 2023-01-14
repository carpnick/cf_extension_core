# Summary
- Helper to enable all types of resource types for create/update/read/list operations
- Heavily inspired to use dynamodb for resource management.  Supports all native create/read/update/list/delete operations for any resource.
- Dynamic identifier generation to support any resource identifier use case.  Read Only resources or real resource creation.

# Required extra permissions in each handlers permissions:
- Due to us using dynamodb as a backend, we need extra permissions to store/retrieve state information from dynamo.  These permissions should be added in addition to any other required permissions by each handler.

  - dynamodb:CreateTable
  - dynamodb:PutItem
  - dynamodb:DeleteItem
  - dynamodb:GetItem
  - dynamodb:UpdateItem
  - dynamodb:UpdateTable
  - dynamodb:DescribeTable
  - dynamodb:Scan


# Development
- Use of poetry
- ```commandline
curl -sSL https://install.python-poetry.org | python3 -
export PATH="/Users/nicholascarpenter/.local/bin:$PATH"
poetry --version
poetry add boto3

poetry add --group dev  pytest

poetry install --no-root
poetry build
poetry config pypi-token.pypi ""
poetry publish
```