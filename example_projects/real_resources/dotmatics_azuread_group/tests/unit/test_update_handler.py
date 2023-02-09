from typing import MutableMapping, Any

from cf_extension_core import CustomResourceHelpers
from pytest_mock import MockFixture

from dotmatics_azuread_group.handlers import TYPE_NAME
from dotmatics_azuread_group.update_handler import UpdateHandler
from tests.unit.test_data import standard_create_request, GROUP_OWNER_NAME


def test_update_success(mocker: MockFixture) -> None:
    # Mock sessionproxy
    session_proxy = mocker.MagicMock()

    # Get rid of sleeps
    mocker.patch("time.sleep")

    # We are calling ReadHandler - so disable that
    read_handler_mock_class = mocker.MagicMock()
    mocker.patch(target="dotmatics_azuread_group.update_handler.ReadHandler", new=read_handler_mock_class)

    # API Client Mocking
    api_client = mocker.MagicMock()
    groups_client = mocker.MagicMock()
    groups_client.validate_credentials = mocker.MagicMock()

    api_client.groups = groups_client

    # Disable Common class

    common_class = mocker.MagicMock()
    common_class.generate_api_client = mocker.MagicMock(return_value=api_client)
    mocker.patch(target="dotmatics_azuread_group.update_handler.Common", new=common_class)

    # Hide DynamoDB stuff
    db_context = mocker.MagicMock()
    db_ops = mocker.MagicMock()
    db_context.__enter__ = mocker.MagicMock(return_value=db_ops)

    # Parameters
    r = standard_create_request()
    assert r.desiredResourceState is not None
    r.desiredResourceState.GroupId = "1"
    r.desiredResourceState.GeneratedId = CustomResourceHelpers.generate_id_resource("-", "-", "123")

    callback_context: MutableMapping[str, Any] = {}
    callback_context.update({"_create_action1": True})
    type_name = TYPE_NAME
    dbresource = mocker.MagicMock()

    # Final mocking
    db_ops.read_model = mocker.MagicMock(return_value=r.desiredResourceState)
    groups_client.get_by_object_id = mocker.MagicMock(
        return_value={
            "displayName": r.desiredResourceState.GroupName,
            "description": r.desiredResourceState.GroupDescription,
        }
    )
    groups_client.list_owners = mocker.MagicMock(return_value=[{"id": "1123", "userPrincipalName": GROUP_OWNER_NAME}])

    # Execute
    uh = UpdateHandler(
        session=session_proxy,
        request=r,
        callback_context=callback_context,
        type_name=type_name,
        db_resource=dbresource,
        total_timeout_in_minutes=5,
    )

    with mocker.patch.context_manager(target=uh, attribute="update_resource", return_value=db_context):
        uh.execute()

        # Assertion
        assert db_ops.read_model.called
        assert db_ops.update_model.called
        assert groups_client.validate_credentials.called
        assert groups_client.get_by_object_id.called


# def test_update_fail_with_different_group_name(mocker: MockFixture) -> None:
#     # Mock sessionproxy
#     session_proxy = mocker.MagicMock()
#
#     # API Client Mocking
#     api_client = mocker.MagicMock()
#     groups_client = mocker.MagicMock()
#     groups_client.validate_credentials = mocker.MagicMock()
#
#     api_client.groups = groups_client
#
#     # Disable Common class
#
#     common_class = mocker.MagicMock()
#     common_class.generate_api_client = mocker.MagicMock(return_value=api_client)
#     mocker.patch(target="dotmatics_azuread_group.update_handler.Common", new=common_class)
#
#     # Hide DynamoDB stuff
#     db_context = mocker.MagicMock()
#     db_ops = mocker.MagicMock()
#     db_context.__enter__ = mocker.MagicMock(return_value=db_ops)
#
#     # Parameters
#     r = standard_create_request()
#     assert r.desiredResourceState is not None
#     r.desiredResourceState.GroupId = "1"
#     r.desiredResourceState.GeneratedId = CustomResourceHelpers.generate_id_resource("-", "-", "123")
#
#     callback_context: MutableMapping[str, Any] = {}
#     callback_context.update({"_create_action1": True})
#     type_name = TYPE_NAME
#     dbresource = mocker.MagicMock()
#
#     # Final mocking
#     db_ops.read_model = mocker.MagicMock(return_value=r.desiredResourceState)
#     groups_client.get_by_object_id = mocker.MagicMock(return_value={"displayName": "SomethingDifferent"})
#
#     # Execute
#     uh = UpdateHandler(
#         session=session_proxy,
#         request=r,
#         callback_context=callback_context,
#         type_name=type_name,
#         db_resource=dbresource,
#         total_timeout_in_minutes=5,
#     )
#
#     try:
#         with mocker.patch.context_manager(target=uh, attribute="update_resource", return_value=db_context):
#             uh.execute()
#             assert False
#     except EnvironmentError:
#         assert True

# Assertion
# assert db_ops.read_model.called
# assert not db_ops.update_model.called
# assert groups_client.validate_credentials.called
# assert groups_client.get_by_object_id.called
