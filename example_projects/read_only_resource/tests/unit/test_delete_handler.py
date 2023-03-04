from typing import MutableMapping, Any

from cloudformation_cli_python_lib.interface import OperationStatus

from dotmatics_sso_groupinfo.delete_handler import DeleteHandler
from dotmatics_sso_groupinfo.handlers import TYPE_NAME
from pytest_mock import MockFixture
from .test_data import standard_update_request


def test_delete_success(mocker: MockFixture) -> None:

    # Mock session proxy
    session_proxy = mocker.MagicMock()

    # Parameters
    r = standard_update_request()
    callback_context: MutableMapping[str, Any] = {}
    type_name = TYPE_NAME
    dbresource = mocker.MagicMock()

    # Execute
    # Need a wrapper around DB context manager
    db_context = mocker.MagicMock()
    db_ops = mocker.MagicMock()
    db_context.__enter__ = mocker.MagicMock(return_value=db_ops)

    dh = DeleteHandler(
        session=session_proxy,
        request=r,
        callback_context=callback_context,
        type_name=type_name,
        db_resource=dbresource,
        total_timeout_in_minutes=2,  # Should match Schema value - https://shorturl.at/gHK46
    )
    with mocker.patch.context_manager(target=dh, attribute="delete_resource", return_value=db_context):

        pe = dh.execute()
        assert pe.status == OperationStatus.SUCCESS

    # What should we assert?

    # delete_resource code was called and setting the model in the db tier was called
    db_context.__enter__.assert_called_once()
    db_context.__exit__.assert_called_once()
