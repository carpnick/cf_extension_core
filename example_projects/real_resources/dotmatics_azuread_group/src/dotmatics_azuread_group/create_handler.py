import logging
from typing import Optional, MutableMapping, Any, TYPE_CHECKING

from ms_graph_client import Generator
from ms_graph_client.services.groups import Groups
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

        self.api_client = Common.generate_api_client(self.request.desiredResourceState)

    def execute(self) -> ProgressEvent:
        # Creation of resource
        with self.create_resource() as DB:
            # Create Group - if so return immediately
            if self._create_action1():
                # Get model from callback context and save to DB and return to make sure CF knows we created a group
                saved_model = self.get_model_from_callback()
                DB.set_resource_created(
                    primary_identifier=self.validate_identifier(saved_model.GeneratedId),
                    current_model=saved_model,
                )
                return self.return_in_progress_event(message="Group created, stabilizing", call_back_delay_seconds=4)

            # Stabilize
            # Run continuously until we can do a read
            LOG.info("Stabilizing group")

            pe = self.run_call_chain_with_stabilization(
                func_list=[
                    lambda: self._stabilize_group_creation(),
                ],
                in_progress_model=self.get_model_from_callback(),
                func_retries_sleep_time=3,
            )
            if pe is not None:
                return pe

            LOG.info("Group Stabilization completed")

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

    def _create_action1(self) -> bool:
        if "_create_action1" not in self.callback_context:
            # Create the group

            desired_state = self.request.desiredResourceState
            assert desired_state is not None
            assert desired_state.Owners is not None
            assert desired_state.GroupName is not None
            assert desired_state.GroupType is not None
            assert desired_state.GroupDescription is not None

            owners_array = []
            gen = Generator(self.api_client.groups.config)

            for item in desired_state.Owners:
                assert item.Name is not None
                assert item.OwnerType is not None

                if item.OwnerType == "USER":
                    LOG.info("Finding User: " + item.Name)
                    user_id = self.api_client.users.get_user(upn=item.Name)["id"]
                    owners_array.append(gen.user_url(user_obj_id=user_id))
                else:
                    raise NotImplementedError("Cannot support Owner type: " + str(item.OwnerType))

            group_type = Groups.GroupType(desired_state.GroupType)

            LOG.info("Creating Group")
            group_id = self.api_client.groups.create(
                group_name=desired_state.GroupName,
                group_type=group_type,
                owners=owners_array,
                with_stabilization=False,
                group_description=desired_state.GroupDescription,
            )
            LOG.info("Group created Successfully")

            generated_id = CustomResourceHelpers.generate_id_resource(
                stack_id=self.request.stackId,
                logical_resource_id=self.request.logicalResourceIdentifier,
                resource_identifier=group_id,
            )

            desired_state.GeneratedId = generated_id
            desired_state.GroupId = group_id

            self.save_model_to_callback(desired_state)
            self.callback_context["_create_action1"] = True
            return True
        else:
            return False

    def _stabilize_group_creation(self) -> bool:
        if "_stabilize_group_creation_found_times" not in self.callback_context:
            LOG.info("Initializing _stabilize_group_creation_found_times to 0")
            self.callback_context["_stabilize_group_creation_found_times"] = 0

        if "_stabilize_group_creation_done" not in self.callback_context:
            assert self.request.desiredResourceState is not None
            assert self.request.desiredResourceState.GroupName is not None

            if self.api_client.groups.exists_by_name(group_name=self.request.desiredResourceState.GroupName):
                LOG.info("Incrementing create_found_times")
                self.callback_context["_stabilize_group_creation_found_times"] = (
                    self.callback_context["_stabilize_group_creation_found_times"] + 1
                )
            else:
                self.callback_context["_stabilize_group_creation_found_times"] = 0
                LOG.info("Resetting to create_found_times to 0")
                return False

            # Find the group more than 4 times before we say move on.
            if self.callback_context["_stabilize_group_creation_found_times"] > 4:
                LOG.info("_stabilize_group_creation_done - DONE = TRUE")
                self.callback_context["_stabilize_group_creation_done"] = True
                return True
            else:
                LOG.info("_stabilize_group_creation -NOT DONE STABILIZING")
                return False
        else:
            # If more stabilization is needed by another method in call chain
            return True
