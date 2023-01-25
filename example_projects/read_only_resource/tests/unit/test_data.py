from dotmatics_sso_groupinfo.models import ResourceModel, ResourceHandlerRequest

GROUP_IDENTITY_STORE_ID = "d-12345"
GROUP_NAME = "Test Group"


def standard_create_resource_model() -> ResourceModel:
    return ResourceModel(
        GroupName=GROUP_NAME, IdentityStoreId=GROUP_IDENTITY_STORE_ID, GroupId=None, GeneratedReadOnlyId=None
    )


def standard_update_request() -> ResourceHandlerRequest:
    gen_id = "1232134534423"

    desired = standard_create_resource_model()
    previous = standard_create_resource_model()
    previous.GroupName = "Previous Group"

    desired.GeneratedReadOnlyId = gen_id
    previous.GeneratedReadOnlyId = gen_id

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
