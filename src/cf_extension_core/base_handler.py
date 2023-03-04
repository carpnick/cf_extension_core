import logging
import typing
import time
from typing import TypeVar, Generic, MutableMapping, Any, TYPE_CHECKING
from cloudformation_cli_python_lib.boto3_proxy import SessionProxy
from cloudformation_cli_python_lib.interface import (
    BaseModel,
    BaseResourceHandlerRequest,
    ProgressEvent,
    OperationStatus,
)
from cloudformation_cli_python_lib.exceptions import NotFound

from cf_extension_core.resource_create import ResourceCreate
from cf_extension_core.resource_delete import ResourceDelete
from cf_extension_core.resource_list import ResourceList
from cf_extension_core.resource_read import ResourceRead
from cf_extension_core.resource_update import ResourceUpdate

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource
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
        session: SessionProxy,
        request: K,
        callback_context: MutableMapping[str, Any],
        type_name: str,
        db_resource: DynamoDBServiceResource,
        total_timeout_in_minutes: int,
        cf_core_log_level: int = logging.INFO,
    ):
        self._session: SessionProxy = session
        self._request: K = request
        self._callback_context: MutableMapping[str, Any] = callback_context
        self._db_resource: object = db_resource
        self._type_name: str = type_name
        self._total_timeout_in_minutes: int = total_timeout_in_minutes

        initialize_handler(
            callback_context=self.callback_context, total_allowed_time_in_minutes=total_timeout_in_minutes
        )

        package_logging_config(logging_level=cf_core_log_level)

        # Validation call on construction
        self._class_type_t()

    @property
    def total_timeout_in_minutes(self) -> int:
        return self._total_timeout_in_minutes

    @property
    def type_name(self) -> str:
        return self._type_name

    @property
    def db_resource(self) -> DynamoDBServiceResource:
        return self._db_resource

    @property
    def callback_context(self) -> MutableMapping[str, Any]:
        return self._callback_context

    @property
    def request(self) -> K:
        return self._request

    @property
    def session(self) -> SessionProxy:
        return self._session

    def save_model_to_callback(self, data: T) -> None:
        """
        Saves the ResourceModel to the callback context in a way we can expect.
        :param data:
        :return:
        """
        # https://github.com/aws-cloudformation/cloudformation-cli-python-plugin/issues/249
        self._callback_context["working_model"] = data._serialize()

    def is_model_saved_in_callback(self) -> bool:
        """
        Loads the ResourceModel data from the callback context and deserializes it into the proper object type
        :param cls:
        :return:
        """
        if "working_model" in self._callback_context:
            return True
        else:
            return False

    def get_model_from_callback(self, cls: typing.Type[T] = typing.Type[T]) -> T:
        """
        Loads the ResourceModel data from the callback context and deserializes it into the proper object type
        :param cls:
        :return:
        """
        return typing.cast(T, self._class_type_t()._deserialize(self._callback_context["working_model"]))

    # Total hack - but works to use generics like I am trying to use them in the get_model_from_callback method
    def _class_type_t(self, cls: typing.Type[T] = typing.Type[T]) -> T:
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
        """
        Determines if the handler is timing out in its current execution environment.
        :return:
        """
        return CustomResourceHelpers.should_return_in_progress_due_to_handler_timeout(
            callback_context=self.callback_context
        )

    def create_resource(self) -> ResourceCreate:
        """
        Use as a context manager in the CreateHandler class.  See example_projects directory
        :return:
        """
        return create_resource(request=self._request, type_name=self._type_name, db_resource=self._db_resource)

    def update_resource(self, primary_identifier: str) -> ResourceUpdate:
        """
        Use as a context manager in the UpdateHandler class and optionally the CreateHandler.
        See example_projects directory
        :param primary_identifier:
        :return:
        """
        return update_resource(
            request=self._request,
            type_name=self._type_name,
            db_resource=self._db_resource,
            primary_identifier=primary_identifier,
        )

    def list_resource(self) -> ResourceList:
        """
        Use as a context manager in the ListHandler class.
        :return:
        """
        return list_resource(
            request=self._request,
            type_name=self._type_name,
            db_resource=self._db_resource,
        )

    def read_resource(self, primary_identifier: str) -> ResourceRead:
        """
        Use as a context manager in the ReadHandler class.
        See example_projects directory
        :param primary_identifier:
        :return:
        """
        return read_resource(
            request=self._request,
            type_name=self._type_name,
            db_resource=self._db_resource,
            primary_identifier=primary_identifier,
        )

    def delete_resource(self, primary_identifier: str) -> ResourceDelete:
        """
        Use as a context manager in the DeleteHandler class.
        See example_projects directory
        :param primary_identifier:
        :return:
        """
        return delete_resource(
            request=self._request,
            type_name=self._type_name,
            db_resource=self._db_resource,
            primary_identifier=primary_identifier,
        )

    def return_in_progress_event(self, message: str = "", call_back_delay_seconds: int = 1) -> ProgressEvent:
        """
        Use this only in the Create/Delete/Update handlers.  The Read/List handlers are now allowed to use "IN_PROGRESS"
        :param message:
        :param call_back_delay_seconds:
        :return:
        """
        return ProgressEvent(
            status=OperationStatus.IN_PROGRESS,
            callbackContext=self._callback_context,
            callbackDelaySeconds=call_back_delay_seconds,
            resourceModel=self.get_model_from_callback(),
            message=message,
        )

    def return_success_event(self, resource_model: T, message: str = "") -> ProgressEvent:
        """
        Use this method for  Create/Update/Read handlers when the model has been partially/completely defined
        :param resource_model:
        :param message:
        :return:
        """
        return ProgressEvent(
            status=OperationStatus.SUCCESS,
            callbackContext=None,
            callbackDelaySeconds=0,
            resourceModel=resource_model,
            message=message,
        )

    def return_success_delete_event(self, message: str = "") -> ProgressEvent:
        """
        Use this method if your DeleteHandler properly deleted the resource
        :param message:
        :return:
        """
        return ProgressEvent(
            status=OperationStatus.SUCCESS,
            callbackContext=None,
            callbackDelaySeconds=0,
            resourceModel=None,
            message=message,
        )

    def validate_identifier(self, identifier: typing.Optional[str]) -> str:
        """
        Validates the identifier as being filled out and a str.

        If identifier is None raises exceiption of `NotFound` from CF Library
        :param identifier: Optional[str] identifier from ResourceModel object.
        :return: identifier as a str
        """
        if identifier is None:
            raise NotFound(self.type_name, str(None))
        else:
            return typing.cast(str, identifier)

    def _stabilize(
        self,
        function: typing.Callable[[], bool],
        sleep_seconds: int = 3,
        callback_delay: int = 1,
        callback_message: str = "",
    ) -> typing.Union[None, ProgressEvent]:
        while True:
            if self.handler_is_timing_out():
                LOG.info("Returning in progress due to handler timing out")
                return self.return_in_progress_event(
                    message=callback_message,
                    call_back_delay_seconds=callback_delay,
                )
            else:
                # Assumption - if callback needs to be updated - happening in the functions being called
                # Functions will skip through if already invoked and return true
                # Note to implementors - make your functions idempotent
                complete = function()
                if complete:
                    return None
                else:
                    time.sleep(sleep_seconds)

    def run_call_chain_with_stabilization(
        self,
        func_list: list[typing.Callable[[], bool]],
        in_progress_model: T,
        func_retries_sleep_time: int = 3,
        callback_delay: int = 1,
        callback_message: str = "",
    ) -> typing.Union[ProgressEvent, None]:
        """
        Runs a list of lambda functions with included stabilization if required.

        The stabilization parameters (func_retries_sleep_time) control how often your method gets called.

        The callback_delay and callback_message are used in case the function needs to timeout before all functions are
        executed.

        :param func_list: List of lambda functions pointing at your implementation methods.
        Each method must return True/False - True if executed to complete or False needs re-execution.
        :param in_progress_model: Current in progress model.  This function requires there to be a current model in the
         callback to allow for timing out and re-executing the handler.

        :param func_retries_sleep_time: Time in between executing the same function again.
        :param callback_delay: Total time in seconds before Cloudformation recalls the function
        :param callback_message: Message to include in callback message IE ProgressEvent Object.
        :return: ProgressEvent if timed out or None which means all functions ran to complete.
        """
        for func in func_list:

            if not self.is_model_saved_in_callback():
                self.save_model_to_callback(data=in_progress_model)

            pe: typing.Union[None, ProgressEvent] = self._stabilize(
                function=func,
                sleep_seconds=func_retries_sleep_time,
                callback_delay=callback_delay,
                callback_message=callback_message,
            )
            if pe is not None:
                return pe

        # We are done
        return None
