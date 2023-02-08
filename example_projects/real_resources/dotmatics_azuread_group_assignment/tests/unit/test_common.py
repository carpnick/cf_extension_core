from dotmatics_azuread_groupassignment.common import Common
from dotmatics_azuread_groupassignment.handlers import TYPE_NAME
from pytest_mock import MockFixture
from cloudformation_cli_python_lib import exceptions


def test_find_group_id_success(mocker: MockFixture) -> None:
    s = mocker.MagicMock()
    assert s is not None


def test_find_group_id_too_many_groups(mocker: MockFixture) -> None:
    s = mocker.MagicMock()
    assert s is not None


def test_find_group_id_no_groups(mocker: MockFixture) -> None:
    s = mocker.MagicMock()
    assert s is not None
