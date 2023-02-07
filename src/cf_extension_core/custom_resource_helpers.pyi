from typing import Any, MutableMapping, Optional

class CustomResourceHelpers:
    ALL_HANDLER_TIMEOUT_THAT_SUPPORTS_IN_PROGRESS: int
    READ_LIST_HANDLER_TIMEOUT: int
    STANDARD_SEPARATOR: str
    HANDLER_ENTRY_TIME: Any

    @staticmethod
    def init_logging() -> None: ...
    @staticmethod
    def generate_id_resource(
        stack_id: Optional[str],
        logical_resource_id: Optional[str],
        resource_identifier: str,
    ) -> str: ...
    @staticmethod
    def generate_id_read_only_resource(
        stack_id: Optional[str],
        logical_resource_id: Optional[str],
    ) -> str: ...
    @staticmethod
    def get_naked_resource_identifier_from_string(primary_identifier: str) -> str: ...
    @staticmethod
    def generate_unique_resource_name(
        stack_id: str,
        logical_resource_name: str,
        client_request_token: str,
        max_length: int = 255,
    ) -> str: ...
    @staticmethod
    def _callback_add_handler_entry_time(callback_context: MutableMapping[str, Any]) -> None: ...
    @staticmethod
    def _callback_add_resource_end_time(
        callback_context: MutableMapping[str, Any],
        total_allowed_time_in_minutes: int,
    ) -> None: ...
    @staticmethod
    def should_return_in_progress_due_to_handler_timeout(callback_context: MutableMapping[str, Any]) -> bool: ...
    @staticmethod
    def _return_failure_due_to_timeout(callback_context: MutableMapping[str, Any]) -> None: ...
