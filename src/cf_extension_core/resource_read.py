# pylint: disable=C0301,W0703,R1720,

import logging

import types

from typing import Type, Literal, TYPE_CHECKING
import cloudformation_cli_python_lib.exceptions
from typing import Optional

from cf_extension_core.resource_base import ResourceBase as _ResourceBase

from cloudformation_cli_python_lib.interface import BaseResourceHandlerRequest as _BaseResourceHandlerRequest

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource as _DynamoDBServiceResource
else:
    _DynamoDBServiceResource= object

# Module Logger
logger = logging.getLogger(__name__)


class ResourceRead(_ResourceBase):
    """
    Easily usable class that can be used to Read resources in the custom resource code.
    """
    # with dynamodb_read(primary_identifier=self._request.previousResourceState.ReadOnlyIdentifier,
    #                      request=self._request) as DB:
    #
    #     #Arbitrary Code
    #     res_model = DB.read_model()

    def __init__(self,
                 request: _BaseResourceHandlerRequest,
                 db_resource: _DynamoDBServiceResource,
                 primary_identifier: str,
                 type_name: str):

        super().__init__(request=request,
                         db_resource=db_resource,
                         primary_identifier=primary_identifier,
                         type_name=type_name)

    def read_model(self,  model_type: Type[_ResourceBase.T]) -> _ResourceBase.T:

        if self._primary_identifier is None:
            raise Exception("Primary Identifier cannot be Null")

        return self._db_item_get_model(model_type=model_type)

    def __enter__(self) -> 'ResourceRead':
        logger.info("DynamoRead Enter... ")

        #Check to see if the row/resource is not found
        self._not_found_check()

        logger.info("DynamoRead Enter Completed")
        return self

    def __exit__(self,
                 exception_type: Optional[Type[BaseException]],
                 exception_value: Optional[BaseException],
                 traceback: Optional[types.TracebackType]) -> Literal[False]:

        logger.info("DynamoRead Exit...")

        if exception_type is None:
            logger.info("Has Failure = False, row No Op")
        else:

            #We failed in update logic
            logger.info("Has Failure = True, row No Op")

        logger.info("DynamoRead Exit Completed")

        #let exception flourish always
        return False
