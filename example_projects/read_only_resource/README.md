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

# Build and CI

## Local Build
  - To simulate a local build.  After cloning out source code:
    - PRE-Req - Install [CFN CLI](https://docs.aws.amazon.com/cloudformation-cli/latest/userguide/what-is-cloudformation-cli.html), [AWS CLI](https://aws.amazon.com/cli/) and [SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html)
    - Create a virtual environment
    - Install Requirements - `pip3 install -r requirements_dev.txt`
    - Run local Build: `sh _build/local_build.sh**`
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
    
      # Run effectively the local build
      sh _build/local_build.sh
    
      #Deploy/Archive artifact plan
        # For each active region in Dotmatics (hard coded in jenkins lib)
          # Upload to S3 regional builds bucket in the aws master account
          # Modify template_deploy_regional_extension.yaml with new S3 Key ("Default Value") and upload to same folder as build artifact.
          # Upload for the branch, to the latest folder the modified template_deploy_regional_extension.yaml file
          (We are explicitly making a decision here that this one file creates everything needed to register the custom extension, even if that means duplicating IAM roles in a single account in multi-region scenario)
        
        # BELOW NOT PART OF BUILD
          # Global deploy plan from Framework
          # Stack 1
            # Custom Extension Stack
            # Points at master/latest/template_deploy_regional_extension.yaml file for each custom resource using substacks
            # (All regions will look at master regional builds bucket to pull artifacts from.  So no worrying about anything else other than looking at a specific key - the key will be the same in all regions)
      ```

# Contract Tests

## Local laptop contract test execution
- Because of [this](https://github.com/aws-cloudformation/cloudformation-cli-python-plugin/issues/247) issue, change template.yaml to look at `src/` instead of `build/`.
- Also if on a MAC M1
  - Add this section to each Function definition in the template file:
    ```
     Architectures:
       - arm64
    ```
- SAM CLI default region is `us-east-1`, so if contract tests need to run in different region, you pass the `sam local start-lambda` call a `--region xxxxxx` parameter.  
- Contract Test Inputs
  - I chose to go with `overrides.json` so I could control just a couple properties.  If you choose to use input directory - dont know ramifications.  **Here be dragons potentially**.
- Contract tests do weird things 
  - In `contract_update_read` - It creates a resource, updates it with new parameters, reads with new parameters and then deletes with old parameters.
  - So what this means is we might not be able to trust resourceProperties as being the up to date resource properties.  So if our update properly updates the model, we should use the DB model as source of truth for resource properties if required.

### Example execution
- Build sam output
  - `sam build -u -m requirements.txt`
  - This assumes you modified template file to point at `src/` instead of `build/` already
- In a terminal run something like this to run lambda locally
  - `sam local start-lambda -l log.log  --region eu-west-2`
- In another terminal run `cfn test`.  Right now `cfn` command doesnt support a `--profile` option.  As an alternative, grab environment values from the SSO portal.
  - To run a specific contract test example: `cfn test  -- -k contract_create_delete --log-cli-level=DEBUG`
- Wait for tests to finish running, contract tests should succeed.  These should work on either X86/AMD64 or ARM architectures.
    
## Contract Test Execution in AWS
- If you want to run contract tests in AWS to debug an issue, this is supported.
- ALERT - THIS REQUIRES an `X86/AMD64` output.  No using Mac M1 or ARM architectures
- How to do it:
  - Run `test_deploy/1pre_reqs` in your AWS account.
  - Deploy helper role with `test_deploy/2extension/aws_contract_tests/contract_test_dependencies.yaml`
  - Build the extension locally (until CI is setup)
    - This must be done on an X86/AMD64 system.  NOT supported by ARM today.
    - Option 1 - If you want to run with `cfn submit`:
      - `cfn submit --role-arn arn:aws:iam::xxxxxxxxxx:role/NickTest-ExecutionRole-RYGSUI7UI0RS --region eu-west-2 --set-default`
      - Replace this `role-arn` parameter with the role deployed in the second bullet above.
      - This will automatically create another stack called: `CloudFormationManagedUploadInfrastructure` - this will need to be deleted after you are happy with the contract tests.
    - Option 2 - If you want to deploy with Cloudformation:
      - Run `cfn submit --dry-run` - it will generate a package locally in your source repository
      - Upload it to a manually created S3 bucket.  Preferably the build bucket in the master account
      - Run the template `test_deploy/2extension/aws_contract_tests/deploy_extension.yaml` to deploy the resource
      - Create an S3 bucket manually for contract test results or just use the same bucket that you manually uploaded the artifact to.
  - Run the Contract Tests
    - Example Command `aws cloudformation test-type --arn arn:aws:cloudformation:eu-west-2:xxxxxxxxxxx:type/resource/Dotmatics-SSO-GroupInfo --type RESOURCE  --log-delivery-bucket xxxxxxx-artifactbucket-1ht2bc69x9z9j --region eu-west-2`
    - Will run the contract tests in an ASYNC way.  Check S3 bucket for results.  First a `README` file will show up in the bucket and tell you the location of the results. (Default path: `CloudFormation/ContractTestResults`)
    - `--arn` parameter is the ARN of your registered extension
    - `--log-delivery-bucket` is either from `CloudFormationManagedUploadInfrastructure` infrastructure stack if deployed with `cfn submit` or the manually created/used log bucket if created with cloudformation
  - After complete - Delete all resources.  Cloudwatch Log groups, S3 buckets, KMS keys, CF Stacks, etc etc.

# End to End Testing
  - Assuming `cfn submit --dry-run` was run and/or the build was uploaded to an S3 bucket somewhere you have access to. (X86/AMD64 only for now)
  - Run `test_deploy/1pre_reqs` in your AWS account if required.
  - Run `test_deploy/2extension/end_to_end/1deploy_extension.yaml`.  Will deploy all needed items to do an End to End test.  If there are issues, look for the cloudwatch log group
  - Run test usage of custom extension -  `test_deploy/2extension/end_to_end/2use_extension.yaml`

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
