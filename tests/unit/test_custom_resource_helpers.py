import cf_extension_core as lib
import pytest  # noqa: F401
from typing import MutableMapping, Any


def test_init_handler_use_case() -> None:

    callback_context: MutableMapping[str, Any] = {}
    lib.initialize_handler(callback_context, 3)
    # Assertion is we dont cause an exception.
