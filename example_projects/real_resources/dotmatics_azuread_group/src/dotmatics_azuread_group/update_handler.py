import logging
from typing import Optional, MutableMapping, Any, TYPE_CHECKING

from cloudformation_cli_python_lib.interface import ProgressEvent
from cloudformation_cli_python_lib.boto3_proxy import SessionProxy
from cf_extension_core import BaseHandler, CustomResourceHelpers

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

        # For an update - the only thing we should need to do is test whether or not we can authorize to the tenant
        # and list out the group by group id
        # Everything else should require a replacement and not hit this code.
        # We are explicitly doing this in an update sense we are designing it for the assumption of API key rotation.
        with self.update_resource(primary_identifier=primary_identifier) as DB:
            group_identifier = CustomResourceHelpers.get_naked_resource_identifier_from_string(
                primary_identifier=primary_identifier
            )

            # CreateOnly Properties MUST be the same in an UPDATE
            # Lets guarantee that by pulling from DB tier and setting them.
            # This also solves if AWS framework has any inconsistencies with the Contract tests.
            # It also forces honoring of contract - no matter what end user puts in.
            # This might yield unexpected results but it guarantees following the contract the developer intended.
            # We could make this better user facing by doing a comparison and outputting an error, but since
            # contract test randomly break this - it is hard to do a one size fits all implementation.

            s: ResourceModel = DB.read_model(ResourceModel)
            desired_state.CredentialTenantId = s.CredentialTenantId
            desired_state.GroupName = s.GroupName
            desired_state.GroupType = s.GroupType
            desired_state.GroupOwnerAppName = s.GroupOwnerAppName
            # desired_state.GeneratedId # read only
            # desired_state.GroupId  # read only

            # This leaves just the following parameters that are allowed to be updated according to contract.
            # CredentialAppClientId
            # CredentialAppAPIToken

            # Validate new creds are good.
            api_client = Common.generate_api_client(desired_state)
            api_client.groups.validate_credentials()

            # Validate group is still valid and exists, basic validation only
            resp = api_client.groups.get_by_object_id(group_id=group_identifier)
            if resp["displayName"] != desired_state.GroupName:
                raise EnvironmentError(
                    "Group found by Group ID: " + group_identifier + " has an incorrect display name"
                )

            # Updating model based on request since we need all of it to do a deletion of the resource
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
