import logging
from typing import Optional, MutableMapping, Any, TYPE_CHECKING

from cloudformation_cli_python_lib.interface import ProgressEvent
from cloudformation_cli_python_lib.boto3_proxy import SessionProxy
from cf_extension_core import BaseHandler, CustomResourceHelpers
from ms_graph_client.services.groups import Groups

# Locals
from .models import ResourceModel, ResourceHandlerRequest, Owner
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

            model = self.read_group_info(db_model=s)

            return self.return_success_event(resource_model=model)

    def read_group_info(self, db_model: ResourceModel) -> ResourceModel:
        # Need to this here since DB tier is the only guaranteed thing to have it.
        api_client = Common.generate_api_client(db_model)

        # Need group id for API call
        primary_identifier = self.validate_identifier(db_model.GeneratedId)
        group_identifier = CustomResourceHelpers.get_naked_resource_identifier_from_string(
            primary_identifier=primary_identifier
        )

        # Get Group info
        group_info = api_client.groups.get_by_object_id(group_id=group_identifier)
        # LOG.info("Group Info: "+ str(group_info))
        group_name = group_info["displayName"]
        group_description = group_info["description"]
        group_id = group_info["id"]

        if len(group_info["groupTypes"]) == 0:
            group_type = Groups.GroupType.SECURITY.name
        else:
            group_type = group_info["groupTypes"][0]

        # Due to bug in python plugin from AWS we cant ignore insertion order for Owners in json schema
        # So the best I can do is do a non-order based comparison and return in kind.
        owners: list[Owner] = []
        assert self.request.desiredResourceState is not None
        if Common.group_owners_are_equal(
            api_client=api_client,
            group_identifier=group_identifier,
            desired_state=db_model,
        ):
            assert db_model.Owners is not None
            owners = list(db_model.Owners.__iter__())
        else:
            owners_api = api_client.groups.list_owners(group_id=group_identifier)
            for item in owners_api:
                if item["@odata.type"] == "#microsoft.graph.user":
                    owners.append(Owner(OwnerType="USER", Name=item["userPrincipalName"]))
                else:
                    raise NotImplementedError()

        # What needs to be filled out according to contract?
        model = ResourceModel(
            GroupName=group_name,
            GroupDescription=group_description,
            GroupType=group_type,
            GroupId=group_id,
            Owners=owners,
            # All of this is hard coded or None for WriteOnlyProperties
            CredentialAppClientId=None,
            CredentialAppAPIToken=None,
            CredentialTenantId=None,
            GeneratedId=db_model.GeneratedId,
        )
        return model
