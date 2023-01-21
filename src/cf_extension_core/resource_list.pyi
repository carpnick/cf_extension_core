import types
from _typeshed import Incomplete
from cf_extension_core.resource_base import ResourceBase as ResourceBase
from cloudformation_cli_python_lib.interface import BaseResourceHandlerRequest as BaseResourceHandlerRequest
from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource
from typing import Literal, Optional, Type, TYPE_CHECKING

logger: Incomplete

class ResourceList(ResourceBase):
    def __init__(
        self, request: BaseResourceHandlerRequest, db_resource: DynamoDBServiceResource, type_name: str
    ) -> None: ...
    def list_identifiers(self) -> list[str]: ...
    def __enter__(self) -> ResourceList: ...
    def __exit__(
        self,
        exception_type: Optional[Type[BaseException]],
        exception_value: Optional[BaseException],
        traceback: Optional[types.TracebackType],
    ) -> Literal[False]: ...
