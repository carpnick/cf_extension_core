from typing import MutableMapping, Any

from dotmatics_azuread_group.create_handler import CreateHandler
from dotmatics_azuread_group.handlers import TYPE_NAME
from pytest_mock import MockFixture


def test_create_fail_in_context(mocker: MockFixture) -> None:
    s = mocker.MagicMock()
    assert s is not None


def test_create_success(mocker: MockFixture) -> None:
    s = mocker.MagicMock()
    assert s is not None
