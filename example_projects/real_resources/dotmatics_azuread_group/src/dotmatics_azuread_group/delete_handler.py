import logging
from typing import Optional, MutableMapping, Any, TYPE_CHECKING

from cloudformation_cli_python_lib.interface import ProgressEvent
from cloudformation_cli_python_lib.boto3_proxy import SessionProxy
from cf_extension_core import BaseHandler

# Locals
from .common import Common
from .models import ResourceModel, ResourceHandlerRequest

LOG = logging.getLogger(__name__)

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource
else:
    DynamoDBServiceResource = object


class DeleteHandler(BaseHandler[ResourceModel, ResourceHandlerRequest]):
    def __init__(
        self,
        session: Optional[SessionProxy],
        request: ResourceHandlerRequest,
        callback_context: MutableMapping[str, Any],
        type_name: str,
        db_resource: DynamoDBServiceResource,
        total_timeout_in_minutes: int,
    ):
        LOG.info("DeleteHandler Constructor")
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

        with self.delete_resource(primary_identifier=identifier) as DB:
            # Need to do this late since we can only count on the primary identifier in a delete event
            self.db_model: ResourceModel = DB.read_model(model_type=ResourceModel)
            self.api_client = Common.generate_api_client(self.db_model)

            if self._delete_group():
                # Need to save model to callback for returning in progress event
                self.save_model_to_callback(self.db_model)
                return self.return_in_progress_event(message="Group deleted, stabilizing", call_back_delay_seconds=1)

            LOG.info("Stabilizing group deletion")
            pe = self.run_call_chain_with_stabilization(
                func_list=[
                    lambda: self._stabilize_group_deletion(),
                ],
                in_progress_model=self.db_model,
                func_retries_sleep_time=3,
            )
            if pe is not None:
                return pe
            LOG.info("Group Stabilization completed")

            # Now we can mark deletion since it is stabilized
            DB.set_resource_deleted()

            return self.return_success_delete_event()

    def _delete_group(self) -> bool:
        if "_delete_group" not in self.callback_context:
            ds = self.db_model
            assert ds is not None
            assert ds.GroupName is not None
            assert ds.GroupId is not None

            LOG.info("Deleting group: " + ds.GroupName)
            self.api_client.groups.delete(group_id=ds.GroupId, group_name=ds.GroupName, with_stabilization=False)
            LOG.info("Group Deleted successfully")
            self.callback_context["_delete_group"] = True

            return True
        else:
            return False

    def _stabilize_group_deletion(self) -> bool:
        if "_stabilize_group_deletion_not_found_times" not in self.callback_context:
            LOG.info("Initializing _stabilize_group_deletion_not_found_times to 0")
            self.callback_context["_stabilize_group_deletion_not_found_times"] = 0

        if "_stabilize_group_deletion_done" not in self.callback_context:
            assert self.db_model.GroupName is not None

            if self.api_client.groups.exists_by_name(group_name=self.db_model.GroupName):
                self.callback_context["_stabilize_group_deletion_not_found_times"] = 0
                LOG.info("Resetting to not_found_times to 0")
                return False
            else:
                LOG.info("Incrementing _stabilize_group_deletion_not_found_times")
                self.callback_context["_stabilize_group_deletion_not_found_times"] = (
                    self.callback_context["_stabilize_group_deletion_not_found_times"] + 1
                )

            # Find the group more than 4 times before we say move on.
            if self.callback_context["_stabilize_group_deletion_not_found_times"] > 4:
                LOG.info("_stabilize_group_deletion_done - DONE = TRUE")
                self.callback_context["_stabilize_group_deletion_done"] = True
                return True
            else:
                LOG.info("_stabilize_group_deletion -NOT DONE STABILIZING")
                return False
        else:
            # If more stabilization is needed by another method in call chain
            return True
