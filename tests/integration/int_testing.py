# Real use case
import logging

import boto3

from cf_extension_core import CustomResourceHelpers, generate_dynamodb_resource, BaseHandler
from tests.integration.gen_models import ResourceModel, ResourceHandlerRequest
from cloudformation_cli_python_lib.boto3_proxy import SessionProxy


class TestHandler(BaseHandler[ResourceModel, ResourceHandlerRequest]):
    def __init__(self) -> None:
        super().__init__(
            SessionProxy(boto3._get_default_session()),
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
