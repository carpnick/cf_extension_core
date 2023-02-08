from typing import Optional
import logging

from dotmatics_azuread_groupassignment.models import ResourceModel
import ms_graph_client

LOG = logging.getLogger(__name__)


class Common:
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
