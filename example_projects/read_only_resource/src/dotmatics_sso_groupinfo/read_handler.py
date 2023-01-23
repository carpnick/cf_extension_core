import logging
from typing import Optional, MutableMapping, Any, TYPE_CHECKING

from cloudformation_cli_python_lib.interface import ProgressEvent
from cloudformation_cli_python_lib.boto3_proxy import SessionProxy
from cf_extension_core import BaseHandler

# Locals
from .models import ResourceModel, ResourceHandlerRequest
from .common import Common


if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource
else:
    DynamoDBServiceResource = object

LOG = logging.getLogger(__name__)


class ReadHandler(BaseHandler[ResourceModel, ResourceHandlerRequest]):
    def __init__(
        self,
        session: Optional[SessionProxy],
        request: ResourceHandlerRequest,
        callback_context: MutableMapping[str, Any],
        type_name: str,
        db_resource: DynamoDBServiceResource,
        total_timeout_in_minutes: int,
    ):

        LOG.info("ReadHandler Constructor")
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

        # Validates a row exists - otherwise fail out with a NotFound
        assert self.request.desiredResourceState is not None
        identifier = self.validate_identifier(self.request.desiredResourceState.GeneratedReadOnlyId)
        with self.read_resource(primary_identifier=identifier) as DB:

            # No guarantee of parameters from input request - AWS Contract -
            # need to get them from our data tier instead.
            s = DB.read_model(ResourceModel)

            # Re-read group info based on parameters in data model from data tier (Thanks AWS)
            new_model = ResourceModel(
                GroupName=s.GroupName,
                IdentityStoreId=s.IdentityStoreId,
                GroupId=Common.find_group_id(session=self.session, model=s, type_name=self.type_name),
                GeneratedReadOnlyId=identifier,
            )

            # Update data tier (in case it has changed)
            DB.update_model(new_model)

            return self.return_success_event(resource_model=new_model)
