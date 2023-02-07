from typing import MutableMapping, Any

from cloudformation_cli_python_lib.interface import OperationStatus

from dotmatics_azuread_group.create_handler import CreateHandler
from dotmatics_azuread_group.handlers import TYPE_NAME
from pytest_mock import MockFixture
from .test_data import standard_create_request


def test_create_success_in_progress(mocker: MockFixture) -> None:
    # Mock sessionproxy
    session_proxy = mocker.MagicMock()

    # We are calling ReadHandler - so disable that
    read_handler_mock_class = mocker.MagicMock()
    mocker.patch(target="dotmatics_azuread_group.create_handler.ReadHandler", new=read_handler_mock_class)

    # API Client Mocking
    api_client = mocker.MagicMock()
    applications_client = mocker.MagicMock()
    groups_client = mocker.MagicMock()

    api_client.applications = applications_client
    api_client.groups = groups_client

    applications_client.get_by_application_name = mocker.MagicMock(return_value={"appId": "1"})
    applications_client.get_service_principal_by_app_id = mocker.MagicMock(return_value={"id": "2"})

    groups_client.create = mocker.MagicMock(return_value="gid")

    # Disable Common class
    common_class = mocker.MagicMock()
    common_class.generate_api_client = mocker.MagicMock(return_value=api_client)
    mocker.patch(target="dotmatics_azuread_group.create_handler.Common", new=common_class)

    # Hide DynamoDB stuff
    db_context = mocker.MagicMock()
    db_ops = mocker.MagicMock()
    db_context.__enter__ = mocker.MagicMock(return_value=db_ops)

    # Parameters
    r = standard_create_request()
    callback_context: MutableMapping[str, Any] = {}
    type_name = TYPE_NAME
    dbresource = mocker.MagicMock()

    # Execute
    ch = CreateHandler(
        session=session_proxy,
        request=r,
        callback_context=callback_context,
        type_name=type_name,
        db_resource=dbresource,
        total_timeout_in_minutes=5,
    )

    with mocker.patch.context_manager(target=ch, attribute="create_resource", return_value=db_context):
        pe = ch.execute()

        # What to assert
        assert pe.status == OperationStatus.IN_PROGRESS
        assert groups_client.create.called


def test_create_success_with_success(mocker: MockFixture) -> None:
    # Mock sessionproxy
    session_proxy = mocker.MagicMock()

    # We are calling ReadHandler - so disable that
    read_handler_mock_class = mocker.MagicMock()
    mocker.patch(target="dotmatics_azuread_group.create_handler.ReadHandler", new=read_handler_mock_class)

    # API Client Mocking
    api_client = mocker.MagicMock()
    groups_client = mocker.MagicMock()

    api_client.groups = groups_client

    groups_client.exists_by_name = mocker.MagicMock()
    groups_client.exists_by_name.side_effect = [True, False, True, True, True, True, True]

    # Disable Common class

    mocker.patch("time.sleep")

    common_class = mocker.MagicMock()
    common_class.generate_api_client = mocker.MagicMock(return_value=api_client)
    mocker.patch(target="dotmatics_azuread_group.create_handler.Common", new=common_class)

    # Hide DynamoDB stuff
    db_context = mocker.MagicMock()
    db_ops = mocker.MagicMock()
    db_context.__enter__ = mocker.MagicMock(return_value=db_ops)

    # Parameters
    r = standard_create_request()
    callback_context: MutableMapping[str, Any] = {}
    callback_context.update({"_create_action1": True})
    type_name = TYPE_NAME
    dbresource = mocker.MagicMock()

    # Execute
    ch = CreateHandler(
        session=session_proxy,
        request=r,
        callback_context=callback_context,
        type_name=type_name,
        db_resource=dbresource,
        total_timeout_in_minutes=5,
    )

    with mocker.patch.context_manager(target=ch, attribute="create_resource", return_value=db_context):
        ch.execute()

        # What to assert

        # We get to the ReadHandler
        assert read_handler_mock_class.called

        # callback_context has
        assert "_stabilize_group_creation_done" in callback_context
