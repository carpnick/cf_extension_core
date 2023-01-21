import cf_extension_core.resource_create as _resource_create
import cf_extension_core.resource_delete as _resource_delete
import cf_extension_core.resource_list as _resource_list
import cf_extension_core.resource_read as _resource_read
import cf_extension_core.resource_update as _resource_update
from _typeshed import Incomplete
from cf_extension_core.constants import DynamoDBValues as DynamoDBValues
from cf_extension_core.custom_resource_helpers import CustomResourceHelpers as CustomResourceHelpers
from cf_extension_core.dynamo_table_creator import DynamoTableCreator as DynamoTableCreator
from cloudformation_cli_python_lib.boto3_proxy import SessionProxy as _SessionProxy
from cloudformation_cli_python_lib.interface import BaseResourceHandlerRequest as _BaseResourceHandlerRequest
from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource as _DynamoDBServiceResource
from typing import Any, MutableMapping, Optional, TYPE_CHECKING

LOG: Incomplete

def generate_dynamodb_resource(session_proxy: Optional[_SessionProxy]) -> _DynamoDBServiceResource: ...
def create_resource(
    request: _BaseResourceHandlerRequest, type_name: str, db_resource: _DynamoDBServiceResource
) -> _resource_create.ResourceCreate: ...
def update_resource(
    primary_identifier: str, type_name: str, request: _BaseResourceHandlerRequest, db_resource: _DynamoDBServiceResource
) -> _resource_update.ResourceUpdate: ...
def delete_resource(
    primary_identifier: str, type_name: str, request: _BaseResourceHandlerRequest, db_resource: _DynamoDBServiceResource
) -> _resource_delete.ResourceDelete: ...
def read_resource(
    primary_identifier: str, type_name: str, request: _BaseResourceHandlerRequest, db_resource: _DynamoDBServiceResource
) -> _resource_read.ResourceRead: ...
def list_resource(
    type_name: str, request: _BaseResourceHandlerRequest, db_resource: _DynamoDBServiceResource
) -> _resource_list.ResourceList: ...
def initialize_handler(callback_context: MutableMapping[str, Any], total_allowed_time_in_minutes: int) -> None: ...
def package_logging_config(logging_level: int) -> None: ...
