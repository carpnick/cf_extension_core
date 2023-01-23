# Dotmatics::SSO::GroupInfo

# Development Tips
- We are using type checking from mypy.  So to get boto3 stubs we pulled them in via [boto3-stubs](https://pypi.org/project/boto3-stubs/).  See `reqs_dev.txt`
  - To make it so stubs are only a development dependency, used syntax like the following at top of python files (for example dynamodb resource):
    - ```
      if TYPE_CHECKING:
          from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource
      else:
          DynamoDBServiceResource = object
      ```
- Work on JSON modeling contract first
  - Delete the `update_handler` json section in json schema if your resource doesnt support mutable properties
- Do not count on AWS to give you the needed data. Use our data tier or callback instead.  
  - Contract is too wishy-washy what you can expect from AWS
- Assume in the Read/Delete handler the only data given is a primary identifier.  All other parameters should come from OUR DB Model or read dynamically from resource
- Only save/restore callback state using basehandler methods - `save_model_to_callback` and `get_model_from_callback`.  AWS doesnt store state properly in callback - these handle it for you.  See [this](https://github.com/aws-cloudformation/cloudformation-cli-python-plugin/issues/249)

# Local Build  and CI Use Cases

## CI System Execution
  - ```
    #Assuming latest cfn and python lib are installed, NOT in virtual env
    pip3 install cloudformation-cli --upgrade
    pip3 install cloudformation-cli-python-plugin --upgrade
    
    #Activate/Create virutal env
    python3 -m venv venv
    source venv/bin/activate
    
    #Install requirements
    pip3 install -r requirements_dev.txt
    
    echo "Running cfn validate: cfn validate"
    cfn validate
    
    echo "Running cfn generate: cfn generate"
    cfn generate
    
    echo "Running mypy: mypy src/"
    mypy src/
    
    echo "Running black:  black -l 120 --check --extend-exclude ".*models\.py" src/"
    black -l 120 --check --extend-exclude ".*models\.py" src/
    
    echo "\nRunning flake8: flake8 --max-line-length 120 --per-file-ignores='src/**/models.py:F401,W391' src/"
    flake8 --max-line-length 120 --per-file-ignores='src/**/models.py:F401,W391' src/
    
    echo "\nRunning pytest: "
    #TODO
    
    echo "\n Running cfn submit for build verification: cfn submit --dry-run"
    cfn submit --dry-run
    ```
## Local contract test execution
- Because of [this](https://github.com/aws-cloudformation/cloudformation-cli-python-plugin/issues/247) issue, change template.yaml to look at `src/` instead of `build/`.
- SAM CLI default region is `us-east-1`, so if contract tests need to run in different region, you pass the `sam local start-lambda` call a `--region xxxxxx` parameter.  
- Contract Test Inputs
  - I chose to go with `overrides.json` so I could control just a couple properties.  If you choose to use input directory - dont know ramifications.  Here be dragons potentially.
- Contract tests do weird things 
  - In `contract_update_read` - It creates a resource, updates it with new parameters, reads with new parameters and then deletes with old parameters.
  - So what this means is we might not be able to trust resourceProperties as being the up to date resource properties.  So if our update properly updates the model, we should use the DB model as source of truth for resource properties if required.

### Example execution
- Build sam output
  - `sam build -u -m requirements.txt`
  - This assumes you modified template file to point at `src/` instead of `build/` already
- In a terminal run something like this to run lambda locally
  - `sam local start-lambda -l log.log  --region eu-west-2`
- In another terminal run `cfn test`
  - To run a specific contract test example: `cfn test  -- -k contract_create_delete --log-cli-level=DEBUG`
- Wait for tests to finish running, contract tests should succeed.
    


# Other Dev Resources
- mypy - [https://mypy.readthedocs.io/en/stable/getting_started.html](https://mypy.readthedocs.io/en/stable/getting_started.html) 
- What if I am dealing with failing imports before my function runs?  Run docker container like Lambda locally, and simulate python3 code:
  - ```
    docker run -it  -v "/Users/nicholascarpenter/Downloads/code/temp/.aws-sam/build/TypeFunction:/var/task"  --entrypoint /bin/bash public.ecr.aws/sam/emulation-python3.9:rapid-1.70.0-arm64
  
    #In the new shell
    python3
    import os, sys
    sys.path.append(os.getcwd())
    #Try to import the function
    import dotmatics_sso_groupinfo.handlers


# Default README from CFN Init below.

Congratulations on starting development! Next steps:

1. Write the JSON schema describing your resource, `dotmatics-sso-groupinfo.json`
2. Implement your resource handlers in `dotmatics_sso_groupinfo/handlers.py`

> Don't modify `models.py` by hand, any modifications will be overwritten when the `generate` or `package` commands are run.

Implement CloudFormation resource here. Each function must always return a ProgressEvent.

```python
ProgressEvent(
    # Required
    # Must be one of OperationStatus.IN_PROGRESS, OperationStatus.FAILED, OperationStatus.SUCCESS
    status=OperationStatus.IN_PROGRESS,
    # Required on SUCCESS (except for LIST where resourceModels is required)
    # The current resource model after the operation; instance of ResourceModel class
    resourceModel=model,
    resourceModels=None,
    # Required on FAILED
    # Customer-facing message, displayed in e.g. CloudFormation stack events
    message="",
    # Required on FAILED: a HandlerErrorCode
    errorCode=HandlerErrorCode.InternalFailure,
    # Optional
    # Use to store any state between re-invocation via IN_PROGRESS
    callbackContext={},
    # Required on IN_PROGRESS
    # The number of seconds to delay before re-invocation
    callbackDelaySeconds=0,
)
```

Failures can be passed back to CloudFormation by either raising an exception from `cloudformation_cli_python_lib.exceptions`, or setting the ProgressEvent's `status` to `OperationStatus.FAILED` and `errorCode` to one of `cloudformation_cli_python_lib.HandlerErrorCode`. There is a static helper function, `ProgressEvent.failed`, for this common case.

## What's with the type hints?

We hope they'll be useful for getting started quicker with an IDE that support type hints. Type hints are optional - if your code doesn't use them, it will still work.