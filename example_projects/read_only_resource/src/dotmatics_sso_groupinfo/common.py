from typing import Optional, TYPE_CHECKING
import logging

from cloudformation_cli_python_lib.boto3_proxy import SessionProxy
import cloudformation_cli_python_lib.exceptions as exceptions
from dotmatics_sso_groupinfo.models import ResourceModel


if TYPE_CHECKING:
    from mypy_boto3_identitystore import Client as IdentityStoreClient
else:
    IdentityStoreClient: object

LOG = logging.getLogger(__name__)


class Common:
    @staticmethod
    def find_group_id(session: Optional[SessionProxy], model: Optional[ResourceModel], type_name: str) -> str:
        assert session is not None
        assert model is not None
        assert model.IdentityStoreId is not None
        assert model.GroupName is not None

        idc_client: IdentityStoreClient = session.client(service_name="identitystore")
        returned_groups = idc_client.list_groups(
            IdentityStoreId=model.IdentityStoreId,
            Filters=[{"AttributePath": "DisplayName", "AttributeValue": model.GroupName}],
        )["Groups"]

        if len(returned_groups) == 0:
            raise exceptions.NotFound(type_name, model.GroupName)
        elif len(returned_groups) >= 2:
            raise exceptions.HandlerInternalFailure("Found more than 1 group for group name: " + model.GroupName)
        else:
            return returned_groups[0]["GroupId"]
