from typing import MutableMapping, Any

from cf_extension_core import CustomResourceHelpers
from cloudformation_cli_python_lib.interface import OperationStatus

from dotmatics_azuread_group.delete_handler import DeleteHandler
from dotmatics_azuread_group.handlers import TYPE_NAME
from pytest_mock import MockFixture
from .test_data import standard_create_request


def test_delete_success_in_progress(mocker: MockFixture) -> None:
    # Mock sessionproxy
    session_proxy = mocker.MagicMock()

    # API Client Mocking
    api_client = mocker.MagicMock()

    groups_client = mocker.MagicMock()
    api_client.groups = groups_client

    groups_client.delete = mocker.MagicMock()

    # Disable Common class
    common_class = mocker.MagicMock()
    common_class.generate_api_client = mocker.MagicMock(return_value=api_client)
    mocker.patch(target="dotmatics_azuread_group.delete_handler.Common", new=common_class)

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
    type_name = TYPE_NAME
    dbresource = mocker.MagicMock()

    # Final Mock
    db_ops.read_model = mocker.MagicMock(return_value=r.desiredResourceState)
    # Execute
    dh = DeleteHandler(
        session=session_proxy,
        request=r,
        callback_context=callback_context,
        type_name=type_name,
        db_resource=dbresource,
        total_timeout_in_minutes=5,
    )

    with mocker.patch.context_manager(target=dh, attribute="delete_resource", return_value=db_context):
        pe = dh.execute()

        # What to assert
        assert pe.status == OperationStatus.IN_PROGRESS
        assert groups_client.delete.called


def test_delete_success_with_success(mocker: MockFixture) -> None:
    # Mock sessionproxy
    session_proxy = mocker.MagicMock()

    # API Client Mocking
    api_client = mocker.MagicMock()
    groups_client = mocker.MagicMock()

    api_client.groups = groups_client

    groups_client.exists_by_name = mocker.MagicMock()
    groups_client.exists_by_name.side_effect = [True, False, True, False, False, False, False, False]

    # Disable Common class

    mocker.patch("time.sleep")

    common_class = mocker.MagicMock()
    common_class.generate_api_client = mocker.MagicMock(return_value=api_client)
    mocker.patch(target="dotmatics_azuread_group.delete_handler.Common", new=common_class)

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
    callback_context.update({"_delete_group": True})
    type_name = TYPE_NAME
    dbresource = mocker.MagicMock()

    # Final Mock
    db_ops.read_model = mocker.MagicMock(return_value=r.desiredResourceState)

    # Execute
    dh = DeleteHandler(
        session=session_proxy,
        request=r,
        callback_context=callback_context,
        type_name=type_name,
        db_resource=dbresource,
        total_timeout_in_minutes=5,
    )

    with mocker.patch.context_manager(target=dh, attribute="delete_resource", return_value=db_context):
        pe = dh.execute()

        # What to assert

        # We get to the ReadHandler
        assert pe.status == OperationStatus.SUCCESS

        # callback_context has
        assert "_stabilize_group_deletion_not_found_times" in callback_context
