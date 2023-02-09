from typing import Optional
import logging

import ms_graph_client
from ms_graph_client import GraphAPI

from dotmatics_azuread_group.models import ResourceModel

LOG = logging.getLogger(__name__)


class Common:
    @staticmethod
    def group_owners_are_equal(api_client: GraphAPI, group_identifier: str, desired_state: ResourceModel) -> bool:
        owners = api_client.groups.list_owners(group_id=group_identifier)
        owners_are_equal = True

        assert desired_state.Owners is not None

        if len(owners) != len(desired_state.Owners):
            owners_are_equal = False
        else:
            for item in desired_state.Owners:
                found = False
                for real_owner in owners:
                    if "userPrincipalName" in real_owner:
                        if item.Name == real_owner["userPrincipalName"]:
                            found = True
                            break
                if not found:
                    owners_are_equal = False
                    break
        LOG.info("Owners are equal: " + str(owners_are_equal))
        return owners_are_equal

    @staticmethod
    def generate_api_client(rm: Optional[ResourceModel]) -> ms_graph_client.GraphAPI:
        assert rm is not None
        assert rm.CredentialAppAPIToken is not None
        assert rm.CredentialAppClientId is not None
        assert rm.CredentialTenantId is not None

        config = ms_graph_client.GraphAPIConfig(
            client_id=rm.CredentialAppClientId,
            client_secret=rm.CredentialAppAPIToken,
            api_url="https://graph.microsoft.com/v1.0",
            tenant_id=rm.CredentialTenantId,
        )

        return ms_graph_client.GraphAPI(config=config)
