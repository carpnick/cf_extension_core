import logging
import typing
from typing import TypeVar, Generic, Optional, MutableMapping, Any, TYPE_CHECKING
from cloudformation_cli_python_lib.boto3_proxy import SessionProxy
from cloudformation_cli_python_lib.interface import (
    BaseModel,
    BaseResourceHandlerRequest,
    ProgressEvent,
    OperationStatus,
)

from cf_extension_core.resource_create import ResourceCreate
from cf_extension_core.resource_delete import ResourceDelete
from cf_extension_core.resource_list import ResourceList
from cf_extension_core.resource_read import ResourceRead
from cf_extension_core.resource_update import ResourceUpdate

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import (
        DynamoDBServiceResource as DynamoDBServiceResource,
    )
else:
    DynamoDBServiceResource = object

# Locals
from cf_extension_core.interface import (  # noqa: F401
    create_resource,
    update_resource,
    delete_resource,
    read_resource,
    list_resource,
    CustomResourceHelpers,
    generate_dynamodb_resource,
    initialize_handler,
    package_logging_config,
)

T = TypeVar("T")
K = TypeVar("K")

LOG = logging.getLogger(__name__)


class BaseHandler(Generic[T, K]):
    def __init__(
        self,
        session: Optional[SessionProxy],
        request: K,
        callback_context: MutableMapping[str, Any],
        type_name: str,
        db_resource: DynamoDBServiceResource,
        total_timeout_in_minutes: int,
        cf_core_log_level: int = logging.INFO,
    ):
        self.session = session
        self.request: K = request
        self.callback_context = callback_context
        self.db_resource = db_resource
        self.type_name = type_name

        initialize_handler(
            callback_context=self.callback_context, total_allowed_time_in_minutes=total_timeout_in_minutes
        )

        package_logging_config(logging_level=cf_core_log_level)

        # Validation call on construction
        self._class_type_t()

    def save_model_to_callback(self, data: T) -> None:
        # https://github.com/aws-cloudformation/cloudformation-cli-python-plugin/issues/249
        self.callback_context["working_model"] = data.__dict__

    def get_model_from_callback(self, cls: typing.Type[T] = T) -> T:
        return typing.cast(T, self._class_type_t()._deserialize(self.callback_context["working_model"]))

    # Total hack - but works to use generics like I am trying to use them in the get_model_from_callback method
    def _class_type_t(self, cls: typing.Type[T] = T) -> T:
        orig_bases = self.__class__.__orig_bases__
        assert len(orig_bases) == 1
        real_base = orig_bases[0]

        real_args = real_base.__args__
        assert len(real_args) == 2
        myclass1 = real_args[0]
        assert issubclass(myclass1, BaseModel)

        myclass2 = real_args[1]
        assert issubclass(myclass2, BaseResourceHandlerRequest)

        # Return the model type
        return myclass1

    def handler_is_timing_out(self) -> bool:
        return CustomResourceHelpers.should_return_in_progress_due_to_handler_timeout()

    def create_resource(self) -> ResourceCreate:
        return create_resource(request=self.request, type_name=self.type_name, db_resource=self.db_resource)

    def update_resource(self, primary_identifier: str) -> ResourceUpdate:
        return update_resource(
            request=self.request,
            type_name=self.type_name,
            db_resource=self.db_resource,
            primary_identifier=primary_identifier,
        )

    def list_resource(self) -> ResourceList:
        return list_resource(request=self.request, type_name=self.type_name, db_resource=self.db_resource)

    def read_resource(self, primary_identifier: str) -> ResourceRead:
        return read_resource(
            request=self.request,
            type_name=self.type_name,
            db_resource=self.db_resource,
            primary_identifier=primary_identifier,
        )

    def delete_resource(self, primary_identifier: str) -> ResourceDelete:
        return delete_resource(
            request=self.request,
            type_name=self.type_name,
            db_resource=self.db_resource,
            primary_identifier=primary_identifier,
        )

    def return_in_progress_event(self, message: str = "", call_back_delay_seconds: int = 1) -> ProgressEvent:
        return ProgressEvent(
            status=OperationStatus.IN_PROGRESS,
            callbackContext=self.callback_context,
            callbackDelaySeconds=call_back_delay_seconds,
            resourceModel=self.get_model_from_callback(),
            message=message,
        )

    def return_success_event(self, resource_model: T, message: str = "") -> ProgressEvent:
        return ProgressEvent(
            status=OperationStatus.SUCCESS,
            callbackContext=None,
            callbackDelaySeconds=0,
            resourceModel=resource_model,
            message=message,
        )

    def return_success_delete_event(self, message: str = "") -> ProgressEvent:
        return ProgressEvent(
            status=OperationStatus.SUCCESS,
            callbackContext=None,
            callbackDelaySeconds=0,
            resourceModel=None,
            message=message,
        )
