from typing import MutableMapping, Any

from cf_extension_core import CustomResourceHelpers
from cloudformation_cli_python_lib.interface import OperationStatus

from dotmatics_azuread_group.read_handler import ReadHandler
from dotmatics_azuread_group.handlers import TYPE_NAME
from pytest_mock import MockFixture
from .test_data import standard_create_request


def test_read_success(mocker: MockFixture) -> None:
    # Mock sessionproxy
    session_proxy = mocker.MagicMock()

    # API Client Mocking
    api_client = mocker.MagicMock()
    groups_client = mocker.MagicMock()

    api_client.groups = groups_client

    # Disable Common class
    common_class = mocker.MagicMock()
    common_class.generate_api_client = mocker.MagicMock(return_value=api_client)
    mocker.patch(target="dotmatics_azuread_group.read_handler.Common", new=common_class)

    # Hide DynamoDB stuff
    db_context = mocker.MagicMock()
    db_ops = mocker.MagicMock()
    db_context.__enter__ = mocker.MagicMock(return_value=db_ops)

    # Parameters
    r = standard_create_request()
    assert r.desiredResourceState is not None
    r.desiredResourceState.GeneratedId = CustomResourceHelpers.generate_id_resource("-", "-", "gid")
    r.desiredResourceState.GroupId = "gid"
    callback_context: MutableMapping[str, Any] = {}
    type_name = TYPE_NAME
    dbresource = mocker.MagicMock()

    # Final Mocks
    groups_client.get_by_object_id = mocker.MagicMock(
        return_value={
            "displayName": r.desiredResourceState.GroupName,
            "description": r.desiredResourceState.GroupDescription,
            "groupTypes": [],
            "id": "gid",
        }
    )
    db_ops.read_model = mocker.MagicMock(return_value=r.desiredResourceState)

    # Execute
    rh = ReadHandler(
        session=session_proxy,
        request=r,
        callback_context=callback_context,
        type_name=type_name,
        db_resource=dbresource,
        total_timeout_in_minutes=5,
    )

    with mocker.patch.context_manager(target=rh, attribute="read_resource", return_value=db_context):
        pe = rh.execute()

        # What to assert

        # We get to the ReadHandler
        assert pe.status == OperationStatus.SUCCESS
