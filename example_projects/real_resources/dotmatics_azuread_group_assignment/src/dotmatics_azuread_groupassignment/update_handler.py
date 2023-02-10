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

    def execute(self) -> ProgressEvent:
        desired_state = self.request.desiredResourceState
        assert desired_state is not None

        # get the primary identifier
        primary_identifier = self.validate_identifier(desired_state.GeneratedId)

        # Update of resource
        with self.update_resource(primary_identifier=primary_identifier) as DB:
            s: ResourceModel = DB.read_model(ResourceModel)

            self._set_variables(desired_state=desired_state, db_model=s)

            # This leaves just the following parameters that are allowed to be updated according to contract.
            # CredentialAppClientId
            # CredentialAppAPIToken

            # Validate new creds are good.
            api_client = Common.generate_api_client(desired_state)
            api_client.groups.validate_credentials()

            DB.update_model(updated_model=desired_state)

        # Run read handler and return
        return ReadHandler(
            session=self.session,
            request=self.request,
            callback_context=self.callback_context,
            type_name=self.type_name,
            db_resource=self.db_resource,
            total_timeout_in_minutes=self.total_timeout_in_minutes,
        ).execute()

    def _set_variables(self, desired_state: ResourceModel, db_model: ResourceModel) -> None:
        # CreateOnly Properties MUST be the same in an UPDATE
        # Lets guarantee that by pulling from DB tier and setting them.
        # This also solves if AWS framework has any inconsistencies with the Contract tests.
        # It also forces honoring of contract - no matter what end user puts in.
        # This might yield unexpected results but it guarantees following the contract the developer intended.
        # We could make this better user facing by doing a comparison and outputting an error, but since
        # contract test randomly break this - it is hard to do a one size fits all implementation.
        desired_state.GroupId = db_model.GroupId
        desired_state.AppName = db_model.AppName
        desired_state.AppRoleName = db_model.AppRoleName
        desired_state.CredentialTenantId = db_model.CredentialTenantId

        # Apparently non-create-only properties are not guaranteed if they dont change?
        # So if we need the RO property set - we should do it here.  Just not the Primary Identifier, that is provided
        desired_state.AssignmentId = db_model.AssignmentId  # Because CF doesnt send it through sometimes... - CONFIRMED
