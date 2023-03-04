import types
from _typeshed import Incomplete
from cf_extension_core.resource_base import ResourceBase as _ResourceBase
from cloudformation_cli_python_lib.interface import (
    BaseModel as BaseModel,
    BaseResourceHandlerRequest as _BaseResourceHandlerRequest,
)
from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource
from typing import Literal, Optional, Type, TYPE_CHECKING

logger: Incomplete

class ResourceUpdate(_ResourceBase):
    _updated_model: Incomplete
    _was_model_updated: bool
    def __init__(
        self,
        request: _BaseResourceHandlerRequest,
        db_resource: DynamoDBServiceResource,
        primary_identifier: str,
        type_name: str,
    ) -> None: ...
    def update_model(self, updated_model: _ResourceBase.T) -> None: ...
    def read_model(self, model_type: Type[_ResourceBase.T]) -> _ResourceBase.T: ...
    def __enter__(self) -> ResourceUpdate: ...
    def __exit__(
        self,
        exception_type: Optional[Type[BaseException]],
        exception_value: Optional[BaseException],
        traceback: Optional[types.TracebackType],
    ) -> Literal[False]: ...
