import datetime

from pytest_mock import MockerFixture

import cf_extension_core as lib
import pytest  # noqa: F401
from typing import MutableMapping, Any, Dict


def test_init_handler_use_case() -> None:

    callback_context: MutableMapping[str, Any] = {}
    lib.initialize_handler(callback_context, 3)
    # Assertion is we dont cause an exception.


def test_gen_identifier_with_value_for_stack_id_and_logical_id() -> None:

    # use case - Contract tests send in None for stack id.  Logical resource id we are covering for good measure.
    myval1 = lib.CustomResourceHelpers.generate_id_read_only_resource(stack_id="as",
                                                                      logical_resource_id="qwe")
    assert "as" in myval1
    assert "qwe" in myval1
    assert lib.CustomResourceHelpers.STANDARD_SEPARATOR in myval1

    myval = lib.CustomResourceHelpers.generate_id_resource(stack_id="as",
                                                           logical_resource_id="qwe",
                                                           resource_identifier="123")
    assert "as" in myval
    assert "qwe" in myval
    assert "123" in myval
    assert lib.CustomResourceHelpers.STANDARD_SEPARATOR in myval


def test_gen_identifier_with_null_stack_id_and_logical_id() -> None:

    # use case - Contract tests send in None for stack id.  Logical resource id we are covering for good measure.
    lib.CustomResourceHelpers.generate_id_read_only_resource(stack_id=None,
                                                             logical_resource_id=None)
    lib.CustomResourceHelpers.generate_id_resource(stack_id=None,
                                                   logical_resource_id=None,
                                                   resource_identifier="123")


def test_non_timeout_handler() -> None:
    # No time has happened between so should not be timed out.
    callback: Dict[str, Any] = {}
    lib.CustomResourceHelpers._callback_add_handler_entry_time(callback)
    assert lib.CustomResourceHelpers.should_return_in_progress_due_to_handler_timeout(callback) is False


def test_timeout_handler_with_timeout(mocker: MockerFixture) -> None:
    callback: Dict[str, Any] = {}
    lib.CustomResourceHelpers._callback_add_handler_entry_time(callback)

    # Adding the full 60 + 5 is defintely after time and it should return  - aka True
    target_val = datetime.datetime.utcnow() + datetime.timedelta(
                     seconds=lib.CustomResourceHelpers.ALL_HANDLER_TIMEOUT_THAT_SUPPORTS_IN_PROGRESS + 5)

    with mocker.mock_module.patch("datetime.datetime") as m:
        m.utcnow.return_value = target_val
        assert lib.CustomResourceHelpers.should_return_in_progress_due_to_handler_timeout(callback) is True

    # Adding just 5 seconds is not late enough - so it should continue running - return False
    target_val2 = datetime.datetime.utcnow() + datetime.timedelta(seconds=5)
    with mocker.mock_module.patch("datetime.datetime") as m:
        m.utcnow.return_value = target_val2
        assert lib.CustomResourceHelpers.should_return_in_progress_due_to_handler_timeout(callback) is False
