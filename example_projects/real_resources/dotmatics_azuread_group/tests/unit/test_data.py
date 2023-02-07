from dotmatics_azuread_group.models import ResourceModel, ResourceHandlerRequest

GROUP_NAME = "Test Group"
GROUP_OWNER_NAME = "APP 123"
APP_CLIENT_ID = "123"
APP_CLIENT_API_TOKEN = "token"
TENANT_ID = "123432432"


def standard_create_resource_model() -> ResourceModel:
    return ResourceModel(
        GroupName=GROUP_NAME,
        GroupOwnerAppName=GROUP_OWNER_NAME,
        GroupType="",
        CredentialAppClientId=APP_CLIENT_ID,
        CredentialAppAPIToken=APP_CLIENT_API_TOKEN,
        CredentialTenantId=TENANT_ID,
        GeneratedId=None,
        GroupId=None,
    )


def standard_update_request() -> ResourceHandlerRequest:
    gen_id = "1232134534423"

    desired = standard_create_resource_model()
    previous = standard_create_resource_model()
    previous.GroupName = "Previous Group"

    desired.GeneratedId = gen_id
    previous.GeneratedId = gen_id

    return ResourceHandlerRequest(
        clientRequestToken="sss",
        desiredResourceState=desired,
        previousResourceState=previous,
        desiredResourceTags=None,
        previousResourceTags=None,
        systemTags=None,
        previousSystemTags=None,
        awsAccountId="11111",
        logicalResourceIdentifier="test",
        typeConfiguration=None,
        nextToken=None,
        region="us-east-1",
        awsPartition="aws",
        stackId="stack_name",
    )


def standard_create_request() -> ResourceHandlerRequest:
    return ResourceHandlerRequest(
        clientRequestToken="sss",
        desiredResourceState=standard_create_resource_model(),
        previousResourceState=None,
        desiredResourceTags=None,
        previousResourceTags=None,
        systemTags=None,
        previousSystemTags=None,
        awsAccountId="11111",
        logicalResourceIdentifier="test",
        typeConfiguration=None,
        nextToken=None,
        region="us-east-1",
        awsPartition="aws",
        stackId="stack_name",
    )