# Real use case
import logging

from cf_extension_core import CustomResourceHelpers, generate_dynamodb_resource, BaseHandler
from tests.integration.gen_models import ResourceModel, ResourceHandlerRequest


class TestHandler(BaseHandler[ResourceModel, ResourceHandlerRequest]):
    def __init__(self) -> None:
        super().__init__(
            None,
            ResourceHandlerRequest("", None, None, None, None, None, None, None, None, None, None, None, None, None),
            {},
            "",
            generate_dynamodb_resource(None),
            1,
            logging.DEBUG,
        )

    def test_method(self) -> None:
        pass


def create_handler() -> None:
    CustomResourceHelpers.generate_id_resource(stack_id="", logical_resource_id="", resource_identifier="s")
    generate_dynamodb_resource(session_proxy=None)
