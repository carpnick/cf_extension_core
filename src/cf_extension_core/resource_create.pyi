import types
from _typeshed import Incomplete
from cf_extension_core.resource_base import ResourceBase as _ResourceBase
from cloudformation_cli_python_lib.interface import BaseModel, BaseResourceHandlerRequest as BaseResourceHandlerRequest
from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource
from typing import Literal, Optional, Type, TYPE_CHECKING

logger: Incomplete

class ResourceCreate(_ResourceBase):
    _set_resource_created_called: bool
    _current_model: Incomplete
    def __init__(
        self, request: BaseResourceHandlerRequest, type_name: str, db_resource: DynamoDBServiceResource
    ) -> None: ...
    _primary_identifier: Incomplete
    def set_resource_created(self, primary_identifier: str, current_model: BaseModel) -> None: ...
    def _duplicate_primary_identifier(self) -> None: ...
    def __enter__(self) -> ResourceCreate: ...
    def __exit__(
        self,
        exception_type: Optional[Type[BaseException]],
        exception_value: Optional[BaseException],
        traceback: Optional[types.TracebackType],
    ) -> Literal[False]: ...
