from typing import Any
import pytest

from dotmatics_sso_groupinfo.handlers import create_handler, update_handler, delete_handler, read_handler
from pytest_mock import MockFixture
from .test_data import standard_create_request

import os
import json


def get_json() -> Any:
    with open(os.getcwd() + os.sep + "dotmatics-sso-groupinfo.json", "r") as f:
        return json.load(f)


@pytest.mark.skip(reason="Temp")
def test_timeouts_for_each_entrypoint_match_schema(mocker: MockFixture) -> None:
    myjson = get_json()

    rh = mocker.MagicMock()
    mocker.patch(target="dotmatics_sso_groupinfo.handlers.ReadHandler", new=rh)

    uh = mocker.MagicMock()
    mocker.patch(target="dotmatics_sso_groupinfo.handlers.UpdateHandler", new=uh)

    dh = mocker.MagicMock()
    mocker.patch(target="dotmatics_sso_groupinfo.handlers.DeleteHandler", new=dh)

    ch = mocker.MagicMock()
    mocker.patch(target="dotmatics_sso_groupinfo.handlers.CreateHandler", new=ch)

    s = standard_create_request()
    session_proxy = mocker.MagicMock()

    # Create Handler
    create_handler(session_proxy, s, {})
    ch.assert_called_once()
    assert myjson["handlers"]["create"]["timeoutInMinutes"] == ch.call_args_list[0].kwargs["total_timeout_in_minutes"]

    # Update Handler
    update_handler(session_proxy, s, {})
    uh.assert_called_once()
    assert myjson["handlers"]["update"]["timeoutInMinutes"] == uh.call_args_list[0].kwargs["total_timeout_in_minutes"]

    # Delete Handler
    delete_handler(session_proxy, s, {})
    dh.assert_called_once()
    assert myjson["handlers"]["delete"]["timeoutInMinutes"] == dh.call_args_list[0].kwargs["total_timeout_in_minutes"]

    # Read Handler
    read_handler(session_proxy, s, {})
    rh.assert_called_once()
    assert myjson["handlers"]["read"]["timeoutInMinutes"] == rh.call_args_list[0].kwargs["total_timeout_in_minutes"]
