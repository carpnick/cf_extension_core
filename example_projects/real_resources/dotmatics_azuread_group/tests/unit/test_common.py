from dotmatics_azuread_group.common import Common
from .test_data import standard_create_request, APP_CLIENT_ID, APP_CLIENT_API_TOKEN, TENANT_ID


def test_generate_api_client() -> None:
    s = standard_create_request()

    api_client = Common.generate_api_client(s.desiredResourceState)
    assert api_client.groups.config.client_id == APP_CLIENT_ID
    assert api_client.groups.config.client_secret == APP_CLIENT_API_TOKEN
    assert api_client.groups.config.tenant_id == TENANT_ID
