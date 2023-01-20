import logging
from cloudformation_cli_python_lib.interface import BaseResourceHandlerRequest as _BaseResourceHandlerRequest
from cloudformation_cli_python_lib.boto3_proxy import SessionProxy as _SessionProxy
from typing import TYPE_CHECKING, Optional, MutableMapping, Any

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import (
        DynamoDBServiceResource as _DynamoDBServiceResource,
    )
else:
    _DynamoDBServiceResource = object

# Locals
import cf_extension_core.resource_update as _resource_update
import cf_extension_core.resource_create as _resource_create
import cf_extension_core.resource_read as _resource_read
import cf_extension_core.resource_delete as _resource_delete
import cf_extension_core.resource_list as _resource_list
from cf_extension_core.dynamo_table_creator import DynamoTableCreator  # noqa: F401
from cf_extension_core.custom_resource_helpers import CustomResourceHelpers  # noqa: F401
from cf_extension_core.constants import DynamoDBValues  # noqa: F401


LOG = logging.getLogger(__name__)


def generate_dynamodb_resource(session_proxy: Optional[_SessionProxy]) -> _DynamoDBServiceResource:
    return session_proxy.resource(service_name="dynamodb")


def create_resource(
    request: _BaseResourceHandlerRequest,
    type_name: str,
    db_resource: _DynamoDBServiceResource,
) -> _resource_create.ResourceCreate:

    return _resource_create.ResourceCreate(
        db_resource=db_resource,
        type_name=type_name,
        request=request,
    )


def update_resource(
    primary_identifier: str,
    type_name: str,
    request: _BaseResourceHandlerRequest,
    db_resource: _DynamoDBServiceResource,
) -> _resource_update.ResourceUpdate:
    return _resource_update.ResourceUpdate(
        db_resource=db_resource,
        type_name=type_name,
        primary_identifier=primary_identifier,
        request=request,
    )


def delete_resource(
    primary_identifier: str,
    type_name: str,
    request: _BaseResourceHandlerRequest,
    db_resource: _DynamoDBServiceResource,
) -> _resource_delete.ResourceDelete:
    return _resource_delete.ResourceDelete(
        db_resource=db_resource,
        type_name=type_name,
        primary_identifier=primary_identifier,
        request=request,
    )


def read_resource(
    primary_identifier: str,
    type_name: str,
    request: _BaseResourceHandlerRequest,
    db_resource: _DynamoDBServiceResource,
) -> _resource_read.ResourceRead:
    return _resource_read.ResourceRead(
        db_resource=db_resource,
        type_name=type_name,
        primary_identifier=primary_identifier,
        request=request,
    )


def list_resource(
    type_name: str,
    request: _BaseResourceHandlerRequest,
    db_resource: _DynamoDBServiceResource,
) -> _resource_list.ResourceList:

    return _resource_list.ResourceList(db_resource=db_resource, type_name=type_name, request=request)


def initialize_handler(
    callback_context: MutableMapping[str, Any],
    total_allowed_time_in_minutes: int,
) -> None:
    LOG.debug("Start initialize_handler")

    # TODO: Consider overriding the Table name based on Type Name here
    CustomResourceHelpers._callback_add_resource_end_time(
        callback_context=callback_context,
        total_allowed_time_in_minutes=total_allowed_time_in_minutes,
    )
    CustomResourceHelpers._callback_add_handler_entry_time()
    CustomResourceHelpers._return_failure_due_to_timeout(callback_context)

    LOG.debug("End initialize_handler")


def package_logging_config(logging_level: int) -> None:
    """
    Helps setup default logging config for custom resources
    :return:
    """

    logging.getLogger("cf_extension_core").setLevel(logging_level)
    LOG.info("cf_extension_core logging enabled")
