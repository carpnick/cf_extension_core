import logging
from typing import Optional, MutableMapping, Any, TYPE_CHECKING

from cloudformation_cli_python_lib.interface import ProgressEvent
from cloudformation_cli_python_lib.boto3_proxy import SessionProxy
from cf_extension_core import BaseHandler, CustomResourceHelpers
from ms_graph_client import GraphAPI

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

            # desired_state.GeneratedId # read only
            # desired_state.GroupId  # read only

            # This leaves just the following parameters that are allowed to be updated according to contract.
            # CredentialAppClientId
            # CredentialAppAPIToken
            # Owners
            # GroupDescription

            # Validate new creds are good if there are new ones
            api_client = Common.generate_api_client(desired_state)
            api_client.groups.validate_credentials()

            # Idempotent changes with callback opt outs for Description and owners
            group_info = api_client.groups.get_by_object_id(group_id=group_identifier)
            self._descrption_peform_update(
                group_info=group_info,
                desired_state=desired_state,
                api_client=api_client,
                group_identifier=group_identifier,
            )

            # Modify Owners - Add and Remove if necessary
            self._owners_perform_update(
                api_client=api_client,
                group_identifier=group_identifier,
                desired_state=desired_state,
            )

            # If our code reaches here
            # in theory all API calls should have succeeded and we are just waiting for stabilization
            # Stabilize Description and Owners - credentials are way past stabilization :)
            self.run_call_chain_with_stabilization(
                func_list=[lambda: self._full_stabilization()],
            )

            # Updating model based on request - non-create only properties
            s.CredentialAppClientId = desired_state.CredentialAppClientId
            s.CredentialAppAPIToken = desired_state.CredentialAppAPIToken
            s.Owners = desired_state.Owners
            s.GroupDescription = desired_state.GroupDescription
            DB.update_model(updated_model=s)

        # Run read handler and return
        return ReadHandler(
            session=self.session,
            request=self.request,
            callback_context=self.callback_context,
            type_name=self.type_name,
            db_resource=self.db_resource,
            total_timeout_in_minutes=self.total_timeout_in_minutes,
        ).execute()

    # def _owners_need_updates_state(
    #     self, api_client: GraphAPI, group_identifier: str, desired_state: ResourceModel
    # ) -> bool:
    #     if "_owners_need_updates" in self.callback_context:
    #         return typing.cast(bool, self.callback_context["_owners_need_updates"])
    #     else:
    #         is_equal = Common.group_owners_are_equal(
    #             api_client=api_client, group_identifier=group_identifier, desired_state=desired_state
    #         )
    #         self.callback_context["_owners_need_updates"] = not is_equal
    #         return typing.cast(bool, self.callback_context["_owners_need_updates"])

    def _descrption_peform_update(
        self,
        group_info: Any,
        desired_state: ResourceModel,
        api_client: GraphAPI,
        group_identifier: str,
    ) -> None:
        if group_info["description"] != desired_state.GroupDescription:
            if "description_updated" not in self.callback_context:
                LOG.info("Updating Description")
                api_client.groups.update(group_id=group_identifier, group_description=desired_state.GroupDescription)
                self.callback_context["description_updated"] = True

    def _owners_perform_add(
        self,
        api_client: GraphAPI,
        group_identifier: str,
        desired_state: ResourceModel,
        current_owners: list[str],
    ) -> None:
        assert desired_state.Owners is not None
        for desired in desired_state.Owners:
            if desired.Name not in current_owners:
                if desired.OwnerType == "USER":
                    # Perform add
                    assert desired.Name is not None
                    LOG.info("Adding owner: " + str(desired.Name))
                    user_info = api_client.users.get_user(upn=desired.Name)
                    api_client.groups.add_owner(group_id=group_identifier, user_obj_id=user_info["id"])
                else:
                    raise NotImplementedError()

    def _owners_perform_remove(
        self,
        api_client: GraphAPI,
        group_identifier: str,
        desired_state: ResourceModel,
        current_owners: list[str],
    ) -> None:
        to_remove = []
        assert desired_state.Owners is not None

        for item in current_owners:
            found = False
            for des in desired_state.Owners:
                if des.OwnerType == "USER":
                    if item == des.Name:
                        found = True
                else:
                    raise NotImplementedError()

            if not found:
                to_remove.append(item)

        for removal in to_remove:
            # Perform remove
            LOG.info("Removing owner: " + str(removal))
            user_info = api_client.users.get_user(upn=removal)
            api_client.groups.remove_owner(group_id=group_identifier, user_obj_id=user_info["id"])

    def _owners_perform_update(
        self,
        api_client: GraphAPI,
        group_identifier: str,
        desired_state: ResourceModel,
    ) -> bool:
        if "_owners_perform_update" not in self.callback_context:
            # The ways it can be different
            # Different length local vs remote
            # Different values but same length

            # Get the list
            owners = api_client.groups.list_owners(group_id=group_identifier)
            simpler_owners = []

            for item in owners:
                simpler_owners.append(item["userPrincipalName"])

            # Run special Add and remove
            self._owners_perform_add(
                api_client=api_client,
                group_identifier=group_identifier,
                desired_state=desired_state,
                current_owners=simpler_owners,
            )
            self._owners_perform_remove(
                api_client=api_client,
                group_identifier=group_identifier,
                desired_state=desired_state,
                current_owners=simpler_owners,
            )

            self.callback_context["_owners_perform_update"] = True

            return True
        else:
            return False

    def _full_stabilization(self) -> bool:
        if "_full_stabilization" in self.callback_context:
            return True
        else:
            desired_state = self.request.desiredResourceState
            assert desired_state is not None
            assert desired_state.GroupId is not None

            api_client = Common.generate_api_client(desired_state)

            # Description first
            group_info = api_client.groups.get_by_object_id(group_id=desired_state.GroupId)
            description_good = group_info["description"] == desired_state.GroupDescription

            # Owners
            owners_good = Common.group_owners_are_equal(
                api_client=api_client, group_identifier=desired_state.GroupId, desired_state=desired_state
            )

            # Now stabilization code
            if "_full_stabilization_found_times" not in self.callback_context:
                LOG.info("Initializing _full_stabilization_found_times to 0")
                self.callback_context["_full_stabilization_found_times"] = 0

            LOG.info("Owners correct: " + str(owners_good) + "  Description correct: " + str(description_good))
            if description_good and owners_good:
                LOG.info("Incrementing _full_stabilization_found_times")
                self.callback_context["_full_stabilization_found_times"] = (
                    self.callback_context["_full_stabilization_found_times"] + 1
                )
            else:
                self.callback_context["_full_stabilization_found_times"] = 0
                LOG.info("Resetting to _full_stabilization_found_times to 0")
                return False

            # Find the group more than 4 times before we say move on.
            if self.callback_context["_full_stabilization_found_times"] > 4:
                LOG.info("_full_stabilization_found_times - DONE = TRUE")
                self.callback_context["_full_stabilization"] = True
                return True
            else:
                LOG.info("_full_stabilization_found_times -NOT DONE STABILIZING")
                return False
