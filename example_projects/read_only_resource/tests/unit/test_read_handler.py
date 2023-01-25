import typing
from typing import MutableMapping, Any

from cloudformation_cli_python_lib.interface import OperationStatus

from dotmatics_sso_groupinfo.models import ResourceModel
from dotmatics_sso_groupinfo.read_handler import ReadHandler
from dotmatics_sso_groupinfo.handlers import TYPE_NAME
from pytest_mock import MockFixture
from .test_data import standard_create_request


def test_read_success(mocker: MockFixture) -> None:

    # Mock sessionproxy
    session_proxy = mocker.MagicMock()

    # We are calling the common class, disable that
    common_class = mocker.MagicMock()
    common_class.find_group_id = mocker.MagicMock(return_value="1")
    mocker.patch(target="dotmatics_sso_groupinfo.read_handler.Common", new=common_class)

    # Parameters
    r = standard_create_request()
    assert r.desiredResourceState is not None  # Mypy
    r.desiredResourceState.GeneratedReadOnlyId = "1"

    callback_context: MutableMapping[str, Any] = {}
    type_name = TYPE_NAME
    dbresource = mocker.MagicMock()

    # Execute
    # Need a wrapper around DB context manager
    db_context = mocker.MagicMock()
    db_ops = mocker.MagicMock()
    db_ops.read_model = mocker.MagicMock(return_value=r.desiredResourceState)
    db_context.__enter__ = mocker.MagicMock(return_value=db_ops)

    rh = ReadHandler(
        session=session_proxy,
        request=r,
        callback_context=callback_context,
        type_name=type_name,
        db_resource=dbresource,
        total_timeout_in_minutes=2,  # Should match Schema value - https://shorturl.at/gHK46
    )
    with mocker.patch.context_manager(target=rh, attribute="read_resource", return_value=db_context):

        pe = rh.execute()

        model: ResourceModel = typing.cast(ResourceModel, pe.resourceModel)

        # What should we assert?

        # Assert PE
        assert pe.status == OperationStatus.SUCCESS
        assert model.GroupId == "1"
        assert model.GroupName == r.desiredResourceState.GroupName
        assert model.IdentityStoreId == r.desiredResourceState.IdentityStoreId
        assert model.GeneratedReadOnlyId == "1"

    # read_resource code was called and setting the model in the db tier was called
    db_context.__enter__.assert_called_once()
    db_context.__exit__.assert_called_once()
    db_ops.read_model.assert_called_once()

    common_class.find_group_id.assert_called_once()
