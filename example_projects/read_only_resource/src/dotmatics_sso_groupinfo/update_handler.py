import logging
from typing import Optional, MutableMapping, Any, TYPE_CHECKING

from cloudformation_cli_python_lib.interface import ProgressEvent
from cloudformation_cli_python_lib.boto3_proxy import SessionProxy
from cf_extension_core import BaseHandler

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource
else:
    DynamoDBServiceResource = object


# Locals
from .models import ResourceModel, ResourceHandlerRequest
from .common import Common
from .read_handler import ReadHandler

LOG = logging.getLogger(__name__)


class UpdateHandler(BaseHandler[ResourceModel, ResourceHandlerRequest]):
    def __init__(
        self,
        session: Optional[SessionProxy],
        request: ResourceHandlerRequest,
        callback_context: MutableMapping[str, Any],
        type_name: str,
        db_resource: DynamoDBServiceResource,
        total_timeout_in_minutes: int,
    ):

        LOG.info("UpdateHandler Constructor")
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

    def get_primary_identifier(self, model: Optional[ResourceModel]) -> str:
        assert model is not None
        return self.validate_identifier(model.GeneratedId)

    def execute(self) -> ProgressEvent:

        # Update of resource
        with self.update_resource(
            primary_identifier=self.get_primary_identifier(self.request.previousResourceState)
        ) as DB:

            self._update_action_1()

            # Where we use the callback info to push data into database tier
            saved_model = self.get_model_from_callback()
            DB.update_model(updated_model=saved_model)

        # Run read handler and return
        return ReadHandler(
            session=self.session,
            request=self.request,
            callback_context=self.callback_context,
            type_name=self.type_name,
            db_resource=self.db_resource,
            total_timeout_in_minutes=self.total_timeout_in_minutes,
        ).execute()

    def _update_action_1(self) -> None:
        model = self.request.desiredResourceState
        assert model is not None
        assert model.GroupName is not None
        assert model.IdentityStoreId is not None

        new_model = ResourceModel(
            GroupName=model.GroupName,
            IdentityStoreId=model.IdentityStoreId,
            GroupId=Common.find_group_id(session=self.session, model=model, type_name=self.type_name),
            GeneratedId=self.get_primary_identifier(self.request.previousResourceState),
        )

        self.save_model_to_callback(new_model)
