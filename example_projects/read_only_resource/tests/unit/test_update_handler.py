from typing import MutableMapping, Any

from dotmatics_sso_groupinfo.update_handler import UpdateHandler
from dotmatics_sso_groupinfo.handlers import TYPE_NAME
from pytest_mock import MockFixture
from .test_data import standard_update_request


def test_update_fail_in_context(mocker: MockFixture) -> None:
    session_proxy = mocker.MagicMock()

    common_class = mocker.MagicMock()
    common_class.find_group_id = mocker.MagicMock(side_effect=NotImplementedError("Random"))
    mocker.patch(target="dotmatics_sso_groupinfo.update_handler.Common", new=common_class)

    # Parameters
    r = standard_update_request()

    callback_context: MutableMapping[str, Any] = {}
    type_name = TYPE_NAME
    dbresource = mocker.MagicMock()

    db_context = mocker.MagicMock()
    db_ops = mocker.MagicMock()
    db_context.__enter__ = mocker.MagicMock(return_value=db_ops)

    ch = UpdateHandler(
        session=session_proxy,
        request=r,
        callback_context=callback_context,
        type_name=type_name,
        db_resource=dbresource,
        total_timeout_in_minutes=2,  # Should match Schema value - https://shorturl.at/gHK46
    )
    with mocker.patch.context_manager(target=ch, attribute="update_resource", return_value=db_context):
        try:
            ch.execute()
            assert False
        except NotImplementedError:
            assert True
    # Asserts
    db_context.__enter__.assert_called_once()
    db_context.__exit__.assert_called_once()
    db_ops.update_model.assert_not_called()


def test_update_success(mocker: MockFixture) -> None:

    # Mock sessionproxy
    session_proxy = mocker.MagicMock()

    # We are calling ReadHandler - so disable that
    read_handler_mock_class = mocker.MagicMock()
    mocker.patch(target="dotmatics_sso_groupinfo.update_handler.ReadHandler", new=read_handler_mock_class)

    # We are calling the common class, disable that
    common_class = mocker.MagicMock()
    common_class.find_group_id = mocker.MagicMock(return_value="1")
    mocker.patch(target="dotmatics_sso_groupinfo.update_handler.Common", new=common_class)

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

    uh = UpdateHandler(
        session=session_proxy,
        request=r,
        callback_context=callback_context,
        type_name=type_name,
        db_resource=dbresource,
        total_timeout_in_minutes=2,  # Should match Schema value - https://shorturl.at/gHK46
    )
    with mocker.patch.context_manager(target=uh, attribute="update_resource", return_value=db_context):

        uh.execute()

    # What should we assert?

    # This should be updated since ReadHandler is called with it
    assert uh.request.desiredResourceState is not None
    assert r.desiredResourceState is not None

    # update_resource code was called and setting the model in the db tier was called
    db_context.__enter__.assert_called_once()
    db_context.__exit__.assert_called_once()
    db_ops.update_model.assert_called()

    # Read handler was called
    read_handler_mock_class().execute.assert_called_once()
