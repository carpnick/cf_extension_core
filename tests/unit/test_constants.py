import cf_extension_core as lib  # noqa: F401
import pytest  # noqa: F401
from cf_extension_core.constants import DynamoDBValues


def test_quick() -> None:
    assert DynamoDBValues.TABLE_NAME == DynamoDBValues.TABLE_NAME
