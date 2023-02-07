import typing
from typing import MutableMapping, Any

from cloudformation_cli_python_lib.interface import OperationStatus

from dotmatics_azuread_group.models import ResourceModel
from dotmatics_azuread_group.read_handler import ReadHandler
from dotmatics_azuread_group.handlers import TYPE_NAME
from pytest_mock import MockFixture


def test_read_success(mocker: MockFixture) -> None:
    s = mocker.MagicMock()
    assert s is not None
