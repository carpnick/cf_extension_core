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
        identifier = self.validate_identifier(self.request.desiredResourceState.GeneratedId)
        with self.read_resource(primary_identifier=identifier) as DB:
            # No guarantee of parameters from input request - AWS Contract -
            # need to get them from our data tier instead.
            s: ResourceModel = DB.read_model(ResourceModel)
            assert s.AppName is not None
            assert s.GroupId is not None

            # Need to this here since DB tier is the only guaranteed thing to have it.
            api_client = Common.generate_api_client(s)

            # From DB tier ONLY with verification
            # Need group id for API call - NM Not true
            # primary_identifier = self.validate_identifier(s.GeneratedId)
            # assignment_identifier = CustomResourceHelpers.get_naked_resource_identifier_from_string(
            #     primary_identifier=primary_identifier
            # )

            # Get assignment info?
            # Get App and then the sp ID
            # Then ask the question - is the group assigned to the app
            aws_app_json = api_client.applications.get_by_application_name(app_name=s.AppName)
            aws_sp_json = api_client.applications.get_service_principal_by_app_id(aws_app_json["appId"])
            aws_sp_id = aws_sp_json["id"]

            # If its not assigned to the app, something changed and the Assignment ID is no longer valid....
            # Technically it would be nice to use a get method on the assignment id
            # However we are using this API -
            # https://learn.microsoft.com/en-us/graph/api/serviceprincipal-post-approleassignedto?view=graph-rest-1.0&tabs=http
            # It has no Getter.  There is a list - but that isnt much better than this implementation....
            # TODO: Determine if this should be refactored.
            val = api_client.groups.is_group_assigned_to_app(app_service_principal_id=aws_sp_id, group_id=s.GroupId)
            if not val:
                s.AssignmentId = None

            DB.update_model(s)

            model = ResourceModel(
                AssignmentId=s.AssignmentId,
                AppName=s.AppName,
                AppRoleName=s.AppRoleName,
                GroupId=s.GroupId,
                GeneratedId=s.GeneratedId,
                # All of this is hard coded or None for WriteOnlyProperties
                CredentialAppClientId=None,
                CredentialAppAPIToken=None,
                CredentialTenantId=None,
            )

            return self.return_success_event(resource_model=model)
