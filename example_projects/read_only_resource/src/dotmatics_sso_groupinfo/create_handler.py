import logging
from typing import Optional, MutableMapping, Any, TYPE_CHECKING

from cloudformation_cli_python_lib.interface import ProgressEvent
from cloudformation_cli_python_lib.boto3_proxy import SessionProxy
from cf_extension_core import CustomResourceHelpers, BaseHandler

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource
else:
    DynamoDBServiceResource = object


# Locals
from .models import ResourceModel, ResourceHandlerRequest
from .common import Common
from .read_handler import ReadHandler


LOG = logging.getLogger(__name__)


class CreateHandler(BaseHandler[ResourceModel, ResourceHandlerRequest]):
    def __init__(
        self,
        session: Optional[SessionProxy],
        request: ResourceHandlerRequest,
        callback_context: MutableMapping[str, Any],
        type_name: str,
        db_resource: DynamoDBServiceResource,
        total_timeout_in_minutes: int,
    ):

        LOG.info("CreateHandler Constructor")
        assert session is not None

        super().__init__(
            session=session,
            request=request,
            callback_context=callback_context,
            type_name=type_name,
            db_resource=db_resource,
            total_timeout_in_minutes=total_timeout_in_minutes,
            cf_core_log_level=logging.DEBUG,
        )

    def execute(self) -> ProgressEvent:

        # Creation of resource
        with self.create_resource() as DB:

            # Create resource - RO - No if statement required
            self._create_action1()

            # Get model from callback context
            saved_model = self.get_model_from_callback()

            # Update DB tier
            assert saved_model.GeneratedId is not None
            DB.set_resource_created(
                primary_identifier=saved_model.GeneratedId,
                current_model=self.get_model_from_callback(),
            )

            # Since we are not doing a callback - update request with new model for ReadHandler below
            self.request.desiredResourceState = saved_model

        # Creation code complete
        # Run read handler and return
        return ReadHandler(
            session=self.session,
            request=self.request,
            callback_context=self.callback_context,
            type_name=self.type_name,
            db_resource=self.db_resource,
            total_timeout_in_minutes=self.total_timeout_in_minutes,
        ).execute()

    def _create_action1(self) -> None:

        # In ANY resource - these lines should be right next to each other.
        # Where-ever the primaryIdentifier is created/read is set, it should be set both in the
        # MODEL and the callback at the same time.

        generated_ro_id = CustomResourceHelpers.generate_id_read_only_resource(
            stack_id=self.request.stackId,
            logical_resource_id=self.request.logicalResourceIdentifier,
        )

        model = self.request.desiredResourceState
        assert model is not None
        assert model.GroupName is not None
        assert model.IdentityStoreId is not None

        new_model = ResourceModel(
            GroupName=model.GroupName,
            IdentityStoreId=model.IdentityStoreId,
            GroupId=Common.find_group_id(session=self.session, model=model, type_name=self.type_name),
            GeneratedId=generated_ro_id,
        )

        self.save_model_to_callback(new_model)
