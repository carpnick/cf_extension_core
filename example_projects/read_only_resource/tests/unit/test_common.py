from dotmatics_sso_groupinfo.common import Common
from dotmatics_sso_groupinfo.handlers import TYPE_NAME
from pytest_mock import MockFixture
from .test_data import standard_create_resource_model
from cloudformation_cli_python_lib import exceptions


def test_find_group_id_success(mocker: MockFixture) -> None:
    # Mock full session proxy
    session_proxy = mocker.MagicMock()
    boto3client = mocker.MagicMock()
    boto3client.list_groups = mocker.MagicMock(return_value={"Groups": [{"GroupId": "1"}]})
    session_proxy.client = mocker.MagicMock(return_value=boto3client)

    s = standard_create_resource_model()

    r = Common.find_group_id(session=session_proxy, model=s, type_name=TYPE_NAME)
    assert r == "1"


def test_find_group_id_too_many_groups(mocker: MockFixture) -> None:
    # Mock full session proxy
    session_proxy = mocker.MagicMock()
    boto3client = mocker.MagicMock()
    boto3client.list_groups = mocker.MagicMock(return_value={"Groups": [{"GroupId": "1"}, {"GroupId": "2"}]})
    session_proxy.client = mocker.MagicMock(return_value=boto3client)

    s = standard_create_resource_model()

    try:
        Common.find_group_id(session=session_proxy, model=s, type_name=TYPE_NAME)
        assert False
    except exceptions.HandlerInternalFailure:
        assert True


def test_find_group_id_no_groups(mocker: MockFixture) -> None:
    # Mock full session proxy
    session_proxy = mocker.MagicMock()
    boto3client = mocker.MagicMock()
    boto3client.list_groups = mocker.MagicMock(return_value={"Groups": []})
    session_proxy.client = mocker.MagicMock(return_value=boto3client)

    s = standard_create_resource_model()

    try:
        Common.find_group_id(session=session_proxy, model=s, type_name=TYPE_NAME)
        assert False
    except exceptions.NotFound:
        assert True
