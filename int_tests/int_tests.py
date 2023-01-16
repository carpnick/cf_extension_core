import logging
import boto3
from cloudformation_cli_python_lib import BaseResourceHandlerRequest
from cloudformation_cli_python_lib.exceptions import *
from gen_models import ResourceModel

# Internal
import cf_extension_core as dynamo




def return_handler_request(model, resource_identifier="myresourceidentifier",stack_id="arn:aws:cloudformation:us-west-2:123456789012:stack/teststack/51af3dc0-da77-11e4-872e-1234567db123"):
    return BaseResourceHandlerRequest(clientRequestToken='-',
                                      desiredResourceState=model,
                                      previousResourceState=None,
                                      desiredResourceTags=None,
                                      previousResourceTags=None,
                                      systemTags=None,
                                      previousSystemTags=None,
                                      awsAccountId="11111111",
                                      logicalResourceIdentifier=resource_identifier,
                                      typeConfiguration=None,
                                      nextToken=None,
                                      region="eu-west-2",
                                      awsPartition="aws",
                                      stackId=stack_id
                                      )

def return_model(group_name="Test", identity_store_id="identity"):
    sample_model_to_save = {
        "GroupName": group_name,
        "IdentityStoreId": identity_store_id,
    }
    mymodel = ResourceModel._deserialize(sample_model_to_save)
    return mymodel

def return_read_only_resource_identifier(handler_request):
    return dynamo.CustomResourceHelpers.\
        generate_primary_identifier_for_resource_tracking_read_only_resource(
            handler_request.stackId,
            handler_request.logicalResourceIdentifier
    )

def return_regular_resource_identifier(handler_request, real_identifier):
    return dynamo.CustomResourceHelpers.\
        generate_primary_identifier_for_resource_tracking(
            handler_request.stackId,
            handler_request.logicalResourceIdentifier,
            resource_identifier=real_identifier
    )

def return_type_name():
    return "ExampleTypeName"

def separator(test_name):
    logging.info("---------------------------------------------------------")
    logging.info("---------------------------------------------------------")
    logging.info("   "+ test_name)
    logging.info("---------------------------------------------------------")



#Contract tests from https://docs.aws.amazon.com/cloudformation-cli/latest/userguide/contract-tests.html
# only done at the dynamo db level - no validation on inputs/outputs.  Honoring the contract tests only.
def test_create_read_delete_ro():
    #Contract tests
        #contract_create_read
        #contract_create_delete

    separator("test_create_read_delete_ro")
    test_input_model = return_model()
    handler_request = return_handler_request(model=test_input_model)

    with dynamo.create_resource(request=handler_request,
                                type_name=return_type_name(),
                                db_resource=dynamo.generate_dynamo_resource()) as DB:
        model: ResourceModel = handler_request.desiredResourceState

        # Fake create code
        model.GroupId = "123"
        model.GeneratedReadOnlyId = dynamo.CustomResourceHelpers.generate_primary_identifier_for_resource_tracking_read_only_resource(handler_request.stackId, handler_request.logicalResourceIdentifier)

        DB.set_resource_created(primary_identifier=model.GeneratedReadOnlyId, current_model=model)

    with dynamo.read_resource(request=handler_request,
                              type_name=return_type_name(),
                              db_resource=dynamo.generate_dynamo_resource(),
                              primary_identifier=model.GeneratedReadOnlyId) as DB:

        #Fake read code
        newmodel = DB.read_model(ResourceModel)
        assert newmodel.GeneratedReadOnlyId == model.GeneratedReadOnlyId

        real_identifier = dynamo.CustomResourceHelpers.get_naked_resource_identifier_from_string(newmodel.GeneratedReadOnlyId)
        #Go read real_identifier - RO resource nothing to do - could re/read data I suppose - why would I do that though?
        #If you want to detect drift - only way to do it.
        assert real_identifier != None


    with dynamo.delete_resource(request=handler_request,
                                type_name=return_type_name(),
                                db_resource=dynamo.generate_dynamo_resource(),
                                primary_identifier=model.GeneratedReadOnlyId) as DB:

        #You are supposed to be able to delete the resource with just the primary identifier
        # RO resource
        pass

        #RW resource - use model.GeneratedReadOnlyId
def test_create_create_same_identifier():
    #Contract Tests
        #contract_create_create
    separator("test_create_create_same_identifier")
    test_input_model = return_model()
    handler_request = return_handler_request(model=test_input_model)

    with dynamo.create_resource(request=handler_request,
                                type_name=return_type_name(),
                                db_resource=dynamo.generate_dynamo_resource(),) as DB:
        model: ResourceModel = handler_request.desiredResourceState

        # Fake create code
        model.GroupId = "123"
        model.GeneratedReadOnlyId = dynamo.CustomResourceHelpers.generate_primary_identifier_for_resource_tracking_read_only_resource(handler_request.stackId, handler_request.logicalResourceIdentifier)

        DB.set_resource_created(primary_identifier=model.GeneratedReadOnlyId, current_model=model)

    try:
        with dynamo.create_resource(request=handler_request,
                                    type_name=return_type_name(),
                                    db_resource=dynamo.generate_dynamo_resource(),) as DB:

           #Use same identifier
            DB.set_resource_created(primary_identifier=model.GeneratedReadOnlyId, current_model=model)

        assert False

    except AlreadyExists:
        assert True
def test_create_list():
    # Contract Tests
        #contract_create_list
    separator("test_contract_create_list")
    test_input_model = return_model()
    handler_request = return_handler_request(model=test_input_model)


    with dynamo.create_resource(request=handler_request,
                                type_name=return_type_name(),
                                db_resource=dynamo.generate_dynamo_resource()) as DB:
        model: ResourceModel = handler_request.desiredResourceState

        # Fake create code
        model.GroupId = "123"
        model.GeneratedReadOnlyId = dynamo.CustomResourceHelpers.generate_primary_identifier_for_resource_tracking_read_only_resource(handler_request.stackId, handler_request.logicalResourceIdentifier)

        DB.set_resource_created(primary_identifier=model.GeneratedReadOnlyId, current_model=model)

    with dynamo.list_resource(request=handler_request,
                              type_name=return_type_name(),
                              db_resource=dynamo.generate_dynamo_resource()
                              ) as DB:

        identifiers = DB.list_identifiers()
        assert len(identifiers)==1
        assert identifiers[0] == model.GeneratedReadOnlyId
def test_create_update_list():
    # Contract Tests
        #contract_update_list
    separator("test_create_update_list")
    test_input_model = return_model()
    handler_request = return_handler_request(model=test_input_model)


    with dynamo.create_resource(request=handler_request,
                                type_name=return_type_name(),
                                db_resource=dynamo.generate_dynamo_resource()) as DB:
        model: ResourceModel = handler_request.desiredResourceState

        # Fake create code
        model.GroupId = "123"
        model.GeneratedReadOnlyId = dynamo.CustomResourceHelpers.generate_primary_identifier_for_resource_tracking_read_only_resource(handler_request.stackId, handler_request.logicalResourceIdentifier)

        DB.set_resource_created(primary_identifier=model.GeneratedReadOnlyId, current_model=model)

    with dynamo.update_resource(request=handler_request,
                                type_name=return_type_name(),
                                db_resource=dynamo.generate_dynamo_resource(),
                                primary_identifier=model.GeneratedReadOnlyId) as DB:
        pass
        DB.update_model(updated_model=model)


    with dynamo.list_resource(request=handler_request,
                              type_name=return_type_name(),
                              db_resource=dynamo.generate_dynamo_resource()
                              ) as DB:

        identifiers = DB.list_identifiers()
        assert len(identifiers)==1
        assert identifiers[0] == model.GeneratedReadOnlyId
def test_create_update_read():
    # Contract Tests
        #contract_update_read
    separator("test_create_update_read")
    test_input_model = return_model()
    handler_request = return_handler_request(model=test_input_model)


    with dynamo.create_resource(request=handler_request,
                                type_name=return_type_name(),
                                db_resource=dynamo.generate_dynamo_resource()) as DB:
        model: ResourceModel = handler_request.desiredResourceState

        # Fake create code
        model.GroupId = "123"
        model.GeneratedReadOnlyId = dynamo.CustomResourceHelpers.generate_primary_identifier_for_resource_tracking_read_only_resource(handler_request.stackId, handler_request.logicalResourceIdentifier)

        DB.set_resource_created(primary_identifier=model.GeneratedReadOnlyId, current_model=model)

    with dynamo.update_resource(request=handler_request,
                                type_name=return_type_name(),
                                db_resource=dynamo.generate_dynamo_resource(),
                                primary_identifier=model.GeneratedReadOnlyId) as DB:
        pass
        DB.update_model(updated_model=model)

    with dynamo.read_resource(primary_identifier=model.GeneratedReadOnlyId,
                              request=handler_request,
                              db_resource=dynamo.generate_dynamo_resource(),
                              type_name=return_type_name()) as DB:

        mymodel = DB.read_model(model_type=ResourceModel)
        assert mymodel.GeneratedReadOnlyId == model.GeneratedReadOnlyId
def test_update_without_create():
    # Contract Tests
        #contract_update_without_create
    separator("test_update_without_create")
    test_input_model = return_model()
    handler_request = return_handler_request(model=test_input_model)

    model: ResourceModel = handler_request.desiredResourceState
    model.GroupId = "123"
    model.GeneratedReadOnlyId = dynamo.CustomResourceHelpers.generate_primary_identifier_for_resource_tracking_read_only_resource(
        handler_request.stackId, handler_request.logicalResourceIdentifier)

    try:
        with dynamo.update_resource(request=handler_request,
                                    type_name=return_type_name(),
                                    db_resource=dynamo.generate_dynamo_resource(),
                                    primary_identifier=model.GeneratedReadOnlyId) as DB:
            pass

        assert False

    except NotFound:
        assert True
def test_delete_create():
    #Contract Test
        #contract_delete_create

    separator("test_delete_create")
    test_input_model = return_model()
    handler_request = return_handler_request(model=test_input_model)

    stablie_identifier = dynamo.CustomResourceHelpers.generate_primary_identifier_for_resource_tracking_read_only_resource(handler_request.stackId,
                                                                                                                    handler_request.logicalResourceIdentifier)

    with dynamo.create_resource(request=handler_request,
                                type_name=return_type_name(),
                                db_resource=dynamo.generate_dynamo_resource(),) as DB:
        model: ResourceModel = handler_request.desiredResourceState

        # Fake create code
        model.GroupId = "123"
        model.GeneratedReadOnlyId = stablie_identifier

        DB.set_resource_created(primary_identifier=model.GeneratedReadOnlyId, current_model=model)


    with dynamo.delete_resource(primary_identifier=model.GeneratedReadOnlyId,
                                request=handler_request,
                                type_name=return_type_name(),
                                db_resource=dynamo.generate_dynamo_resource(),) as DB:
        pass

    with dynamo.create_resource(request=handler_request,
                                type_name=return_type_name(),
                                db_resource=dynamo.generate_dynamo_resource(),) as DB:
        model: ResourceModel = handler_request.desiredResourceState

        # Fake create code
        model.GroupId = "123"
        model.GeneratedReadOnlyId = stablie_identifier

        DB.set_resource_created(primary_identifier=model.GeneratedReadOnlyId, current_model=model)
def test_delete_update():
    #Contract Test
        #contract_delete_update

    separator("test_delete_create")
    test_input_model = return_model()
    handler_request = return_handler_request(model=test_input_model)

    stablie_identifier = dynamo.CustomResourceHelpers.generate_primary_identifier_for_resource_tracking_read_only_resource(handler_request.stackId,
                                                                                                                    handler_request.logicalResourceIdentifier)

    with dynamo.create_resource(request=handler_request,
                                type_name=return_type_name(),
                                db_resource=dynamo.generate_dynamo_resource(),) as DB:
        model: ResourceModel = handler_request.desiredResourceState

        # Fake create code
        model.GroupId = "123"
        model.GeneratedReadOnlyId = stablie_identifier

        DB.set_resource_created(primary_identifier=model.GeneratedReadOnlyId, current_model=model)


    with dynamo.delete_resource(primary_identifier=model.GeneratedReadOnlyId,
                                request=handler_request,
                                type_name=return_type_name(),
                                db_resource=dynamo.generate_dynamo_resource(),) as DB:
        pass

    try:
        with dynamo.update_resource(primary_identifier= model.GeneratedReadOnlyId,
                                    request=handler_request,
                                    type_name=return_type_name(),
                                    db_resource=dynamo.generate_dynamo_resource(),) as DB:
            model: ResourceModel = handler_request.desiredResourceState

            # Fake update code
            model.GroupId = "1235"
            DB.update_model(updated_model=model)

        assert False
    except NotFound:
        assert True
def test_create_delete_read():
    #Contract tests
        #contract_delete_read

    separator("test_create_delete_read")
    test_input_model = return_model()
    handler_request = return_handler_request(model=test_input_model)

    with dynamo.create_resource(request=handler_request,
                                type_name=return_type_name(),
                                db_resource=dynamo.generate_dynamo_resource(),) as DB:
        model: ResourceModel = handler_request.desiredResourceState

        # Fake create code
        model.GroupId = "123"
        model.GeneratedReadOnlyId = dynamo.CustomResourceHelpers.generate_primary_identifier_for_resource_tracking_read_only_resource(handler_request.stackId, handler_request.logicalResourceIdentifier)

        DB.set_resource_created(primary_identifier=model.GeneratedReadOnlyId, current_model=model)

    with dynamo.delete_resource(primary_identifier=model.GeneratedReadOnlyId,
                                request=handler_request,
                                type_name=return_type_name(),
                                db_resource=dynamo.generate_dynamo_resource(),) as DB:
        pass


    try:
        with dynamo.read_resource(request=handler_request,
                                  type_name=return_type_name(),
                                  db_resource=dynamo.generate_dynamo_resource(),
                                  primary_identifier=model.GeneratedReadOnlyId) as DB:

            #Fake read code
            newmodel = DB.read_model(ResourceModel)
            assert newmodel.GeneratedReadOnlyId == model.GeneratedReadOnlyId

            real_identifier = dynamo.CustomResourceHelpers.get_naked_resource_identifier_from_string(newmodel.GeneratedReadOnlyId)
            #Go read real_identifier - RO resource nothing to do - could re/read data I suppose - why would I do that though?
            #If you want to detect drift - only way to do it.
            assert real_identifier != None

        assert False
    except NotFound:
        assert True
def test_create_delete_list():
    #Contract tests
        #contract_delete_list

    separator("test_create_delete_list")
    test_input_model = return_model()
    handler_request = return_handler_request(model=test_input_model)

    with dynamo.create_resource(request=handler_request,
                                type_name=return_type_name(),
                                db_resource=dynamo.generate_dynamo_resource(),) as DB:
        model: ResourceModel = handler_request.desiredResourceState

        # Fake create code
        model.GroupId = "123"
        model.GeneratedReadOnlyId = dynamo.CustomResourceHelpers.generate_primary_identifier_for_resource_tracking_read_only_resource(handler_request.stackId, handler_request.logicalResourceIdentifier)

        DB.set_resource_created(primary_identifier=model.GeneratedReadOnlyId, current_model=model)

    with dynamo.delete_resource(primary_identifier=model.GeneratedReadOnlyId,
                                request=handler_request,
                                type_name=return_type_name(),
                                db_resource=dynamo.generate_dynamo_resource(),) as DB:
        pass

    with dynamo.list_resource(request=handler_request,
                              type_name=return_type_name(),
                              db_resource=dynamo.generate_dynamo_resource(),) as DB:

        ids = DB.list_identifiers()

        assert len(ids) == 0
def test_create_delete_delete():
    #Contract tests
        #contract_delete_delete

    separator("test_delete_delete_list")
    test_input_model = return_model()
    handler_request = return_handler_request(model=test_input_model)

    with dynamo.create_resource(request=handler_request,
                                type_name=return_type_name(),
                                db_resource=dynamo.generate_dynamo_resource(),) as DB:
        model: ResourceModel = handler_request.desiredResourceState

        # Fake create code
        model.GroupId = "123"
        model.GeneratedReadOnlyId = dynamo.CustomResourceHelpers.generate_primary_identifier_for_resource_tracking_read_only_resource(handler_request.stackId, handler_request.logicalResourceIdentifier)

        DB.set_resource_created(primary_identifier=model.GeneratedReadOnlyId, current_model=model)

    with dynamo.delete_resource(primary_identifier=model.GeneratedReadOnlyId,
                                request=handler_request,
                                type_name=return_type_name(),
                                db_resource=dynamo.generate_dynamo_resource(),) as DB:
        pass

    try:
        with dynamo.delete_resource(primary_identifier=model.GeneratedReadOnlyId,
                                    request=handler_request,
                                    type_name=return_type_name(),
                                    db_resource=dynamo.generate_dynamo_resource(),) as DB:
            pass

        assert False
    except NotFound:
        assert True


#Other use cases
def test_create_create_ro_resource():
    #Use case - replacement of a readonly resource to re-read data...
    #Use case - re-reading same data in different stacks or logical resource ids (or same resource ids)

    separator("test_create_create_ro_resource")
    test_input_model = return_model()
    handler_request = return_handler_request(model=test_input_model)

    with dynamo.create_resource(request=handler_request,
                                type_name=return_type_name(),
                                db_resource=dynamo.generate_dynamo_resource(),) as DB:
        model: ResourceModel = handler_request.desiredResourceState

        # Fake create code
        model.GroupId = "123"
        model.GeneratedReadOnlyId = dynamo.CustomResourceHelpers.generate_primary_identifier_for_resource_tracking_read_only_resource(handler_request.stackId, handler_request.logicalResourceIdentifier)

        DB.set_resource_created(primary_identifier=model.GeneratedReadOnlyId, current_model=model)

    with dynamo.create_resource(request=handler_request,
                                type_name=return_type_name(),
                                db_resource=dynamo.generate_dynamo_resource(),) as DB:

        # Fake create code
        model.GroupId = "123"
        model.GeneratedReadOnlyId = dynamo.CustomResourceHelpers.generate_primary_identifier_for_resource_tracking_read_only_resource(
            handler_request.stackId, handler_request.logicalResourceIdentifier)

        DB.set_resource_created(primary_identifier=model.GeneratedReadOnlyId, current_model=model)
def test_create_create_same_identifier_known_ahead_of_time():

    separator("test_create_create_same_identifier_known_ahead_of_time")
    test_input_model = return_model()
    handler_request = return_handler_request(model=test_input_model)

    stable_identifier = dynamo.CustomResourceHelpers.generate_primary_identifier_for_resource_tracking_read_only_resource(handler_request.stackId, handler_request.logicalResourceIdentifier)

    with dynamo.create_resource(request=handler_request,
                                type_name=return_type_name(),
                                db_resource=dynamo.generate_dynamo_resource(),) as DB:
        model: ResourceModel = handler_request.desiredResourceState

        # Fake create code
        model.GroupId = "123"
        model.GeneratedReadOnlyId = stable_identifier

        DB.set_resource_created(primary_identifier=model.GeneratedReadOnlyId, current_model=model)

    try:
        with dynamo.create_resource(request=handler_request,
                                    type_name=return_type_name(),
                                    db_resource=dynamo.generate_dynamo_resource()) as DB:
            logging.info("Got here")
            assert True

    except Exception:
        assert False, "This needs to be allowed due to reinvoke use case"

if __name__ == "__main__":

    from cf_extension_core.constants import DynamoDBValues
    from cf_extension_core.dynamo_table_creator import DynamoTableCreator

    format_string = "%(asctime)s - %(process)d - %(levelname)s - %(filename)s - %(message)s"
    logging.basicConfig(
        format=format_string,
        level=logging.INFO)

    dynamo._default_package_logging_config()

    # Use a special TABLE? - HACK alert
    DynamoDBValues.TABLE_NAME = "aut-TEST"

    boto3.setup_default_session(profile_name="CT", region_name="eu-west-2")

    tests = [
        lambda: test_create_read_delete_ro() ,
        lambda: test_create_create_same_identifier(),
        lambda: test_create_create_ro_resource(),
        lambda: test_create_list(),
        lambda: test_create_update_list(),
        lambda: test_create_update_read(),
        lambda: test_update_without_create(),
        lambda: test_delete_create(),
        lambda: test_delete_update(),
        lambda: test_create_delete_read(),
        lambda: test_create_delete_list(),
        lambda: test_create_delete_delete(),
        lambda: test_create_create_same_identifier_known_ahead_of_time()
    ]

    for test in tests:
        DynamoTableCreator(dynamo.interface.generate_dynamo_resource()).delete_table()
        test()



