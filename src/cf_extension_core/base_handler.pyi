import typing
from _typeshed import Incomplete
from cf_extension_core.interface import (
    CustomResourceHelpers as CustomResourceHelpers,
    create_resource as create_resource,
    delete_resource as delete_resource,
    generate_dynamodb_resource as generate_dynamodb_resource,
    initialize_handler as initialize_handler,
    list_resource as list_resource,
    package_logging_config as package_logging_config,
    read_resource as read_resource,
    update_resource as update_resource,
)
from cf_extension_core.resource_create import ResourceCreate as ResourceCreate
from cf_extension_core.resource_delete import ResourceDelete as ResourceDelete
from cf_extension_core.resource_list import ResourceList as ResourceList
from cf_extension_core.resource_read import ResourceRead as ResourceRead
from cf_extension_core.resource_update import ResourceUpdate as ResourceUpdate
from cloudformation_cli_python_lib.boto3_proxy import SessionProxy as SessionProxy
from cloudformation_cli_python_lib.interface import ProgressEvent
from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource
from typing import Any, MutableMapping, TypeVar, Generic, TYPE_CHECKING

T = TypeVar("T")
K = TypeVar("K")
LOG: Incomplete

class BaseHandler(Generic[T, K]):
    _session: SessionProxy
    _request: K
    _callback_context: MutableMapping[str, Any]
    _db_resource: DynamoDBServiceResource
    _type_name: str
    _total_timeout_in_minutes: int
    def __init__(
        self,
        session: SessionProxy,
        request: K,
        callback_context: MutableMapping[str, Any],
        type_name: str,
        db_resource: DynamoDBServiceResource,
        total_timeout_in_minutes: int,
        cf_core_log_level: int = ...,
    ) -> None: ...
    @property
    def session(self) -> SessionProxy: ...
    @property
    def request(self) -> K: ...
    @property
    def callback_context(self) -> MutableMapping[str, Any]: ...
    @property
    def db_resource(self) -> DynamoDBServiceResource: ...
    @property
    def type_name(self) -> str: ...
    @property
    def total_timeout_in_minutes(self) -> int: ...
    def save_model_to_callback(self, data: T) -> None: ...
    def get_model_from_callback(self, cls: typing.Type[T] = ...) -> T: ...
    def is_model_saved_in_callback(self) -> bool: ...
    def _class_type_t(self, cls: typing.Type[T] = ...) -> T: ...
    def handler_is_timing_out(self) -> bool: ...
    def create_resource(self) -> ResourceCreate: ...
    def update_resource(self, primary_identifier: str) -> ResourceUpdate: ...
    def list_resource(self) -> ResourceList: ...
    def read_resource(self, primary_identifier: str) -> ResourceRead: ...
    def delete_resource(self, primary_identifier: str) -> ResourceDelete: ...
    def return_in_progress_event(self, message: str = ..., call_back_delay_seconds: int = ...) -> ProgressEvent: ...
    def return_success_event(self, resource_model: T, message: str = ...) -> ProgressEvent: ...
    def return_success_delete_event(self, message: str = ...) -> ProgressEvent: ...
    def validate_identifier(self, identifier: typing.Optional[str]) -> str: ...
    def _stabilize(
        self,
        function: typing.Callable[[], bool],
        sleep_seconds: int = 3,
        callback_delay: int = 1,
        callback_message: str = "",
    ) -> typing.Union[None, ProgressEvent]: ...
    def run_call_chain_with_stabilization(
        self,
        func_list: list[typing.Callable[[], bool]],
        in_progress_model: T,
        func_retries_sleep_time: int = 3,
        callback_delay: int = 1,
        callback_message: str = "",
    ) -> typing.Union[ProgressEvent, None]: ...
