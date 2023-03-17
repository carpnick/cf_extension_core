import logging
import boto3
import cloudformation_cli_python_lib.exceptions as exceptions
from cloudformation_cli_python_lib.boto3_proxy import SessionProxy
from tests.integration.gen_models import ResourceModel, ResourceHandlerRequest

from typing import TYPE_CHECKING, Optional
import typing

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource
else:
    DynamoDBServiceResource = object


# Internal
import cf_extension_core.interface as dynamo


def ret_dynamodb_resource() -> DynamoDBServiceResource:
    session = boto3._get_default_session()
    return dynamo.generate_dynamodb_resource(SessionProxy(session))


def return_handler_request(
    model: ResourceModel,
    resource_identifier: str = "myresourceidentifier",
    stack_id: str = "arn:aws:cloudformation:us-west-2:123456789012:"
    "stack/teststack/51af3dc0-da77-11e4-872e-1234567db123",
) -> ResourceHandlerRequest:
    return ResourceHandlerRequest(
        clientRequestToken="-",
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
        stackId=stack_id,
    )


def return_model(group_name: str = "Test", identity_store_id: str = "identity") -> ResourceModel:
    sample_model_to_save = {
        "GroupName": group_name,
        "IdentityStoreId": identity_store_id,
    }
    mymodel = ResourceModel._deserialize(sample_model_to_save)
    return typing.cast(ResourceModel, mymodel)


def return_type_name() -> str:
    return "ExampleTypeName"


def separator(test_name: str) -> None:
    logging.info("---------------------------------------------------------")
    logging.info("---------------------------------------------------------")
    logging.info("   " + test_name)
    logging.info("---------------------------------------------------------")


# Contract tests from https://docs.aws.amazon.com/cloudformation-cli/latest/userguide/contract-tests.html
# only done at the dynamo db level - no validation on inputs/outputs.  Honoring the contract tests only.
def test_create_read_delete_ro() -> None:
    # Contract tests
    # contract_create_read
    # contract_create_delete

    separator("test_create_read_delete_ro")
    test_input_model = return_model()
    handler_request = return_handler_request(model=test_input_model)

    with dynamo.create_resource(
        request=handler_request, type_name=return_type_name(), db_resource=ret_dynamodb_resource()
    ) as DB:
        model: Optional[ResourceModel] = handler_request.desiredResourceState
        assert model is not None

        # Fake create code
        model.GroupId = "123"
        model.GeneratedReadOnlyId = dynamo.CustomResourceHelpers.generate_id_read_only_resource(
            handler_request.stackId, handler_request.logicalResourceIdentifier
        )

        DB.set_resource_created(primary_identifier=model.GeneratedReadOnlyId, current_model=model)

    with dynamo.read_resource(
        request=handler_request,
        type_name=return_type_name(),
        db_resource=ret_dynamodb_resource(),
        primary_identifier=model.GeneratedReadOnlyId,
    ) as DB:

        # Fake read code
        newmodel = DB.read_model(ResourceModel)
        assert newmodel.GeneratedReadOnlyId == model.GeneratedReadOnlyId

        real_identifier = dynamo.CustomResourceHelpers.get_naked_resource_identifier_from_string(
            newmodel.GeneratedReadOnlyId
        )
        # Go read real_identifier - RO resource nothing to do - could re/read data I suppose -
        # why would I do that though?
        # If you want to detect drift - only way to do it.
        assert real_identifier is not None

    with dynamo.delete_resource(
        request=handler_request,
        type_name=return_type_name(),
        db_resource=ret_dynamodb_resource(),
        primary_identifier=model.GeneratedReadOnlyId,
    ) as DB:
        DB.set_resource_deleted()
        # You are supposed to be able to delete the resource with just the primary identifier
        # RO resource
        pass

        # RW resource - use model.GeneratedReadOnlyId


def test_create_create_same_identifier() -> None:
    # Contract Tests
    # contract_create_create
    separator("test_create_create_same_identifier")
    test_input_model = return_model()
    handler_request = return_handler_request(model=test_input_model)

    with dynamo.create_resource(
        request=handler_request,
        type_name=return_type_name(),
        db_resource=ret_dynamodb_resource(),
    ) as DB:
        model: Optional[ResourceModel] = handler_request.desiredResourceState
        assert model is not None

        # Fake create code
        model.GroupId = "123"
        model.GeneratedReadOnlyId = dynamo.CustomResourceHelpers.generate_id_read_only_resource(
            handler_request.stackId, handler_request.logicalResourceIdentifier
        )

        DB.set_resource_created(primary_identifier=model.GeneratedReadOnlyId, current_model=model)

    try:
        with dynamo.create_resource(
            request=handler_request,
            type_name=return_type_name(),
            db_resource=ret_dynamodb_resource(),
        ) as DB:

            # Use same identifier
            DB.set_resource_created(primary_identifier=model.GeneratedReadOnlyId, current_model=model)

        assert False

    except exceptions.AlreadyExists:
        assert True


def test_create_list() -> None:
    # Contract Tests
    # contract_create_list
    separator("test_contract_create_list")
    test_input_model = return_model()
    handler_request = return_handler_request(model=test_input_model)

    with dynamo.create_resource(
        request=handler_request, type_name=return_type_name(), db_resource=ret_dynamodb_resource()
    ) as DB:
        model: Optional[ResourceModel] = handler_request.desiredResourceState
        assert model is not None

        # Fake create code
        model.GroupId = "123"
        model.GeneratedReadOnlyId = dynamo.CustomResourceHelpers.generate_id_read_only_resource(
            handler_request.stackId, handler_request.logicalResourceIdentifier
        )

        DB.set_resource_created(primary_identifier=model.GeneratedReadOnlyId, current_model=model)

    with dynamo.list_resource(
        request=handler_request, type_name=return_type_name(), db_resource=ret_dynamodb_resource()
    ) as DB:

        identifiers = DB.list_identifiers()
        assert len(identifiers) == 1
        assert identifiers[0] == model.GeneratedReadOnlyId


def test_create_update_list() -> None:
    # Contract Tests
    # contract_update_list
    separator("test_create_update_list")
    test_input_model = return_model()
    handler_request = return_handler_request(model=test_input_model)

    with dynamo.create_resource(
        request=handler_request, type_name=return_type_name(), db_resource=ret_dynamodb_resource()
    ) as DB:
        model: Optional[ResourceModel] = handler_request.desiredResourceState
        assert model is not None

        # Fake create code
        model.GroupId = "123"
        model.GeneratedReadOnlyId = dynamo.CustomResourceHelpers.generate_id_read_only_resource(
            handler_request.stackId, handler_request.logicalResourceIdentifier
        )

        DB.set_resource_created(primary_identifier=model.GeneratedReadOnlyId, current_model=model)

    with dynamo.update_resource(
        request=handler_request,
        type_name=return_type_name(),
        db_resource=ret_dynamodb_resource(),
        primary_identifier=model.GeneratedReadOnlyId,
    ) as DB:
        pass
        DB.update_model(updated_model=model)

    with dynamo.list_resource(
        request=handler_request, type_name=return_type_name(), db_resource=ret_dynamodb_resource()
    ) as DB:

        identifiers = DB.list_identifiers()
        assert len(identifiers) == 1
        assert identifiers[0] == model.GeneratedReadOnlyId


def test_create_update_read() -> None:
    # Contract Tests
    # contract_update_read
    separator("test_create_update_read")
    test_input_model = return_model()
    handler_request = return_handler_request(model=test_input_model)

    with dynamo.create_resource(
        request=handler_request, type_name=return_type_name(), db_resource=ret_dynamodb_resource()
    ) as DB:
        model: Optional[ResourceModel] = handler_request.desiredResourceState
        assert model is not None

        # Fake create code
        model.GroupId = "123"
        model.GeneratedReadOnlyId = dynamo.CustomResourceHelpers.generate_id_read_only_resource(
            handler_request.stackId, handler_request.logicalResourceIdentifier
        )

        DB.set_resource_created(primary_identifier=model.GeneratedReadOnlyId, current_model=model)

    with dynamo.update_resource(
        request=handler_request,
        type_name=return_type_name(),
        db_resource=ret_dynamodb_resource(),
        primary_identifier=model.GeneratedReadOnlyId,
    ) as DB:
        pass
        DB.update_model(updated_model=model)

    with dynamo.read_resource(
        primary_identifier=model.GeneratedReadOnlyId,
        request=handler_request,
        db_resource=ret_dynamodb_resource(),
        type_name=return_type_name(),
    ) as DB:

        mymodel = DB.read_model(model_type=ResourceModel)
        assert mymodel.GeneratedReadOnlyId == model.GeneratedReadOnlyId


def test_update_without_create() -> None:
    # Contract Tests
    # contract_update_without_create
    separator("test_update_without_create")
    test_input_model = return_model()
    handler_request = return_handler_request(model=test_input_model)

    model: Optional[ResourceModel] = handler_request.desiredResourceState
    assert model is not None

    model.GroupId = "123"
    model.GeneratedReadOnlyId = dynamo.CustomResourceHelpers.generate_id_read_only_resource(
        handler_request.stackId, handler_request.logicalResourceIdentifier
    )

    try:
        with dynamo.update_resource(
            request=handler_request,
            type_name=return_type_name(),
            db_resource=ret_dynamodb_resource(),
            primary_identifier=model.GeneratedReadOnlyId,
        ):
            pass

        assert False

    except exceptions.NotFound:
        assert True


def test_delete_create() -> None:
    # Contract Test
    # contract_delete_create

    separator("test_delete_create")
    test_input_model = return_model()
    handler_request = return_handler_request(model=test_input_model)

    stablie_identifier = dynamo.CustomResourceHelpers.generate_id_read_only_resource(
        handler_request.stackId, handler_request.logicalResourceIdentifier
    )

    with dynamo.create_resource(
        request=handler_request,
        type_name=return_type_name(),
        db_resource=ret_dynamodb_resource(),
    ) as DB:
        model: Optional[ResourceModel] = handler_request.desiredResourceState
        assert model is not None

        # Fake create code
        model.GroupId = "123"
        model.GeneratedReadOnlyId = stablie_identifier

        DB.set_resource_created(primary_identifier=model.GeneratedReadOnlyId, current_model=model)

    with dynamo.delete_resource(
        primary_identifier=model.GeneratedReadOnlyId,
        request=handler_request,
        type_name=return_type_name(),
        db_resource=ret_dynamodb_resource(),
    ) as DB:
        DB.set_resource_deleted()

    with dynamo.create_resource(
        request=handler_request,
        type_name=return_type_name(),
        db_resource=ret_dynamodb_resource(),
    ) as DB:
        model2: Optional[ResourceModel] = handler_request.desiredResourceState
        assert model2 is not None

        # Fake create code
        model2.GroupId = "123"
        model2.GeneratedReadOnlyId = stablie_identifier

        DB.set_resource_created(primary_identifier=model2.GeneratedReadOnlyId, current_model=model2)


def test_delete_update() -> None:
    # Contract Test
    # contract_delete_update

    separator("test_delete_create")
    test_input_model = return_model()
    handler_request = return_handler_request(model=test_input_model)

    stablie_identifier = dynamo.CustomResourceHelpers.generate_id_read_only_resource(
        handler_request.stackId, handler_request.logicalResourceIdentifier
    )

    with dynamo.create_resource(
        request=handler_request,
        type_name=return_type_name(),
        db_resource=ret_dynamodb_resource(),
    ) as DB:
        model: Optional[ResourceModel] = handler_request.desiredResourceState
        assert model is not None

        # Fake create code
        model.GroupId = "123"
        model.GeneratedReadOnlyId = stablie_identifier

        DB.set_resource_created(primary_identifier=model.GeneratedReadOnlyId, current_model=model)

    with dynamo.delete_resource(
        primary_identifier=model.GeneratedReadOnlyId,
        request=handler_request,
        type_name=return_type_name(),
        db_resource=ret_dynamodb_resource(),
    ) as DB:
        DB.set_resource_deleted()

    try:
        with dynamo.update_resource(
            primary_identifier=model.GeneratedReadOnlyId,
            request=handler_request,
            type_name=return_type_name(),
            db_resource=ret_dynamodb_resource(),
        ) as DB:
            model2: Optional[ResourceModel] = handler_request.desiredResourceState
            assert model2 is not None

            # Fake update code
            model2.GroupId = "1235"
            DB.update_model(updated_model=model2)

        assert False
    except exceptions.NotFound:
        assert True


def test_create_delete_read() -> None:
    # Contract tests
    # contract_delete_read

    separator("test_create_delete_read")
    test_input_model = return_model()
    handler_request = return_handler_request(model=test_input_model)

    with dynamo.create_resource(
        request=handler_request,
        type_name=return_type_name(),
        db_resource=ret_dynamodb_resource(),
    ) as DB:
        model: Optional[ResourceModel] = handler_request.desiredResourceState
        assert model is not None

        # Fake create code
        model.GroupId = "123"
        model.GeneratedReadOnlyId = dynamo.CustomResourceHelpers.generate_id_read_only_resource(
            handler_request.stackId, handler_request.logicalResourceIdentifier
        )

        DB.set_resource_created(primary_identifier=model.GeneratedReadOnlyId, current_model=model)

    with dynamo.delete_resource(
        primary_identifier=model.GeneratedReadOnlyId,
        request=handler_request,
        type_name=return_type_name(),
        db_resource=ret_dynamodb_resource(),
    ) as DB:
        DB.set_resource_deleted()

    try:
        with dynamo.read_resource(
            request=handler_request,
            type_name=return_type_name(),
            db_resource=ret_dynamodb_resource(),
            primary_identifier=model.GeneratedReadOnlyId,
        ) as DB:

            # Fake read code
            newmodel = DB.read_model(ResourceModel)
            assert newmodel.GeneratedReadOnlyId == model.GeneratedReadOnlyId

            real_identifier = dynamo.CustomResourceHelpers.get_naked_resource_identifier_from_string(
                newmodel.GeneratedReadOnlyId
            )
            # Go read real_identifier - RO resource nothing to do - could re/read data I suppose -
            # why would I do that though?
            # If you want to detect drift - only way to do it.
            assert real_identifier is not None

        assert False
    except exceptions.NotFound:
        assert True


def test_create_delete_list() -> None:
    # Contract tests
    # contract_delete_list

    separator("test_create_delete_list")
    test_input_model = return_model()
    handler_request = return_handler_request(model=test_input_model)

    with dynamo.create_resource(
        request=handler_request,
        type_name=return_type_name(),
        db_resource=ret_dynamodb_resource(),
    ) as DB:
        model: Optional[ResourceModel] = handler_request.desiredResourceState
        assert model is not None

        # Fake create code
        model.GroupId = "123"
        model.GeneratedReadOnlyId = dynamo.CustomResourceHelpers.generate_id_read_only_resource(
            handler_request.stackId, handler_request.logicalResourceIdentifier
        )

        DB.set_resource_created(primary_identifier=model.GeneratedReadOnlyId, current_model=model)

    with dynamo.delete_resource(
        primary_identifier=model.GeneratedReadOnlyId,
        request=handler_request,
        type_name=return_type_name(),
        db_resource=ret_dynamodb_resource(),
    ) as DB:
        DB.set_resource_deleted()

    with dynamo.list_resource(
        request=handler_request,
        type_name=return_type_name(),
        db_resource=ret_dynamodb_resource(),
    ) as DB:

        ids = DB.list_identifiers()

        assert len(ids) == 0


def test_create_delete_delete() -> None:
    # Contract tests
    # contract_delete_delete

    separator("test_delete_delete_list")
    test_input_model = return_model()
    handler_request = return_handler_request(model=test_input_model)

    with dynamo.create_resource(
        request=handler_request,
        type_name=return_type_name(),
        db_resource=ret_dynamodb_resource(),
    ) as DB:
        model: Optional[ResourceModel] = handler_request.desiredResourceState
        assert model is not None

        # Fake create code
        model.GroupId = "123"
        model.GeneratedReadOnlyId = dynamo.CustomResourceHelpers.generate_id_read_only_resource(
            handler_request.stackId, handler_request.logicalResourceIdentifier
        )

        DB.set_resource_created(primary_identifier=model.GeneratedReadOnlyId, current_model=model)

    with dynamo.delete_resource(
        primary_identifier=model.GeneratedReadOnlyId,
        request=handler_request,
        type_name=return_type_name(),
        db_resource=ret_dynamodb_resource(),
    ) as DB:
        DB.set_resource_deleted()

    try:
        with dynamo.delete_resource(
            primary_identifier=model.GeneratedReadOnlyId,
            request=handler_request,
            type_name=return_type_name(),
            db_resource=ret_dynamodb_resource(),
        ):
            DB.set_resource_deleted()

        assert False
    except exceptions.NotFound:
        assert True


# Other use cases


def test_create_create_ro_resource() -> None:
    # Use case - replacement of a readonly resource to re-read data...
    # Use case - re-reading same data in different stacks or logical resource ids (or same resource ids)

    separator("test_create_create_ro_resource")
    test_input_model = return_model()
    handler_request = return_handler_request(model=test_input_model)

    with dynamo.create_resource(
        request=handler_request,
        type_name=return_type_name(),
        db_resource=ret_dynamodb_resource(),
    ) as DB:
        model: Optional[ResourceModel] = handler_request.desiredResourceState
        assert model is not None

        # Fake create code
        model.GroupId = "123"
        model.GeneratedReadOnlyId = dynamo.CustomResourceHelpers.generate_id_read_only_resource(
            handler_request.stackId, handler_request.logicalResourceIdentifier
        )

        DB.set_resource_created(primary_identifier=model.GeneratedReadOnlyId, current_model=model)

    with dynamo.create_resource(
        request=handler_request,
        type_name=return_type_name(),
        db_resource=ret_dynamodb_resource(),
    ) as DB:

        # Fake create code
        model.GroupId = "123"
        model.GeneratedReadOnlyId = dynamo.CustomResourceHelpers.generate_id_read_only_resource(
            handler_request.stackId, handler_request.logicalResourceIdentifier
        )

        DB.set_resource_created(primary_identifier=model.GeneratedReadOnlyId, current_model=model)


def test_create_create_same_identifier_known_ahead_of_time() -> None:

    separator("test_create_create_same_identifier_known_ahead_of_time")
    test_input_model = return_model()
    handler_request = return_handler_request(model=test_input_model)

    stable_identifier = dynamo.CustomResourceHelpers.generate_id_read_only_resource(
        handler_request.stackId, handler_request.logicalResourceIdentifier
    )

    with dynamo.create_resource(
        request=handler_request,
        type_name=return_type_name(),
        db_resource=ret_dynamodb_resource(),
    ) as DB:
        model: Optional[ResourceModel] = handler_request.desiredResourceState
        assert model is not None

        # Fake create code
        model.GroupId = "123"
        model.GeneratedReadOnlyId = stable_identifier

        DB.set_resource_created(primary_identifier=model.GeneratedReadOnlyId, current_model=model)

    try:
        with dynamo.create_resource(
            request=handler_request, type_name=return_type_name(), db_resource=ret_dynamodb_resource()
        ) as DB:
            logging.info("Got here")
            assert True
        assert True
    except Exception:
        assert False, "This needs to be allowed due to reinvoke use case"


def test_create_with_random_exception() -> None:

    separator("test_create_with_random_exception")
    test_input_model = return_model()
    handler_request = return_handler_request(model=test_input_model)

    try:
        with dynamo.create_resource(
            request=handler_request,
            type_name=return_type_name(),
            db_resource=ret_dynamodb_resource(),
        ):
            raise Exception("Random Exception")

        assert False
    except exceptions.HandlerInternalFailure as e:
        logging.info(e.to_progress_event())
        assert True


def test_create_read_with_random_exception() -> None:

    separator("test_create_read_with_random_exception")
    test_input_model = return_model()
    handler_request = return_handler_request(model=test_input_model)
    stable_identifier = dynamo.CustomResourceHelpers.generate_id_read_only_resource(
        handler_request.stackId, handler_request.logicalResourceIdentifier
    )

    with dynamo.create_resource(
        request=handler_request,
        type_name=return_type_name(),
        db_resource=ret_dynamodb_resource(),
    ) as DB:

        model: Optional[ResourceModel] = handler_request.desiredResourceState
        assert model is not None
        model.GeneratedReadOnlyId = stable_identifier
        DB.set_resource_created(primary_identifier=stable_identifier, current_model=model)

    try:
        with dynamo.read_resource(
            request=handler_request,
            type_name=return_type_name(),
            db_resource=ret_dynamodb_resource(),
            primary_identifier=stable_identifier,
        ):
            raise Exception("Random Exception")

        assert False
    except exceptions.HandlerInternalFailure:
        assert True
    except Exception:
        assert False


def test_create_update_with_random_exception() -> None:

    separator("test_create_update_with_random_exception")
    test_input_model = return_model()
    handler_request = return_handler_request(model=test_input_model)
    stable_identifier = dynamo.CustomResourceHelpers.generate_id_read_only_resource(
        handler_request.stackId, handler_request.logicalResourceIdentifier
    )

    with dynamo.create_resource(
        request=handler_request,
        type_name=return_type_name(),
        db_resource=ret_dynamodb_resource(),
    ) as DB:

        model: Optional[ResourceModel] = handler_request.desiredResourceState
        assert model is not None
        model.GeneratedReadOnlyId = stable_identifier
        DB.set_resource_created(primary_identifier=stable_identifier, current_model=model)

    try:
        with dynamo.update_resource(
            request=handler_request,
            type_name=return_type_name(),
            db_resource=ret_dynamodb_resource(),
            primary_identifier=stable_identifier,
        ):
            raise Exception("Random Exception")

        assert False
    except exceptions.HandlerInternalFailure:
        assert True
    except Exception:
        assert False


def test_create_delete_with_random_exception() -> None:

    separator("test_create_delete_with_random_exception")
    test_input_model = return_model()
    handler_request = return_handler_request(model=test_input_model)
    stable_identifier = dynamo.CustomResourceHelpers.generate_id_read_only_resource(
        handler_request.stackId, handler_request.logicalResourceIdentifier
    )

    with dynamo.create_resource(
        request=handler_request,
        type_name=return_type_name(),
        db_resource=ret_dynamodb_resource(),
    ) as DB:

        model: Optional[ResourceModel] = handler_request.desiredResourceState
        assert model is not None
        model.GeneratedReadOnlyId = stable_identifier
        DB.set_resource_created(primary_identifier=stable_identifier, current_model=model)

    try:
        with dynamo.delete_resource(
            request=handler_request,
            type_name=return_type_name(),
            db_resource=ret_dynamodb_resource(),
            primary_identifier=stable_identifier,
        ):
            raise Exception("Random Exception")

        assert False
    except exceptions.HandlerInternalFailure:
        assert True
    except Exception:
        assert False


def test_list_with_random_exception() -> None:

    separator("test_list_with_random_exception")
    test_input_model = return_model()
    handler_request = return_handler_request(model=test_input_model)
    try:
        with dynamo.list_resource(
            request=handler_request, type_name=return_type_name(), db_resource=ret_dynamodb_resource()
        ):
            raise Exception("Random Exception")

        assert False
    except exceptions.HandlerInternalFailure:
        assert True
    except Exception:
        assert False


if __name__ == "__main__":

    from cf_extension_core.constants import DynamoDBValues
    from cf_extension_core.dynamo_table_creator import DynamoTableCreator

    format_string = "%(asctime)s - %(process)d - %(levelname)s - %(filename)s - %(message)s"
    logging.basicConfig(format=format_string, level=logging.INFO)

    dynamo.package_logging_config(logging_level=logging.DEBUG)

    # Use a special TABLE? - HACK alert
    DynamoDBValues.TABLE_NAME = "aut-TEST"

    boto3.setup_default_session(profile_name="SDLC", region_name="us-east-2")

    tests: typing.List[typing.Callable[[], None]] = [
        lambda: test_create_read_delete_ro(),
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
        lambda: test_create_create_same_identifier_known_ahead_of_time(),
        lambda: test_create_with_random_exception(),
        lambda: test_create_read_with_random_exception(),
        lambda: test_create_update_with_random_exception(),
        lambda: test_create_delete_with_random_exception(),
        lambda: test_list_with_random_exception(),
    ]

    for test in tests:
        import random
        if random.randint(1, 10) <= 5:
            DynamoTableCreator(ret_dynamodb_resource()).create_standard_table()

        test()
        DynamoTableCreator(ret_dynamodb_resource()).delete_table()
