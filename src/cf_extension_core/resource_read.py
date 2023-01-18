import logging
import types
from typing import Type, Literal, TYPE_CHECKING, Optional

import cloudformation_cli_python_lib.exceptions
from cloudformation_cli_python_lib.interface import BaseResourceHandlerRequest, BaseModel

from cf_extension_core.resource_base import ResourceBase as _ResourceBase

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource
else:
    DynamoDBServiceResource = object

# Module Logger
logger = logging.getLogger(__name__)


class ResourceRead(_ResourceBase):
    # with dynamodb_read(primary_identifier=self._request.previousResourceState.ReadOnlyIdentifier,
    #                      request=self._request) as DB:
    #
    #     #Arbitrary Code
    #     res_model = DB.read_model()

    def __init__(
        self,
        request: BaseResourceHandlerRequest,
        db_resource: DynamoDBServiceResource,
        primary_identifier: str,
        type_name: str,
    ):

        super().__init__(
            request=request,
            db_resource=db_resource,
            primary_identifier=primary_identifier,
            type_name=type_name,
        )

        self._updated_model: Optional[BaseModel] = None
        self._was_model_updated = False

    def read_model(
        self,
        model_type: Type[_ResourceBase.T],
    ) -> _ResourceBase.T:

        if self._primary_identifier is None:
            raise Exception("Primary Identifier cannot be Null")

        return self._db_item_get_model(model_type=model_type)

    def update_model(
        self,
        updated_model: _ResourceBase.T,
    ) -> None:

        if self._primary_identifier is None:
            raise Exception("Primary Identifier cannot be Null")

        if updated_model is None:
            raise Exception("The current_model cannot be Null")

        self._was_model_updated = True
        self._updated_model = updated_model

    def __enter__(self) -> "ResourceRead":
        logger.info("DynamoRead Enter... ")

        # Check to see if the row/resource is not found
        self._not_found_check()

        logger.info("DynamoRead Enter Completed")
        return self

    def __exit__(
        self,
        exception_type: Optional[Type[BaseException]],
        exception_value: Optional[BaseException],
        traceback: Optional[types.TracebackType],
    ) -> Literal[False]:

        logger.info("DynamoRead Exit...")

        try:
            if exception_type is None:
                logger.info("Has Failure = False")

                if self._was_model_updated:
                    logger.info("Row being Updated")
                    self._db_item_update_model(model=self._updated_model)
                else:
                    logger.info("Row not updated")

                return False

            else:

                # We failed in read logic
                logger.info("Has Failure = True, row No Op")

                # Log the internal error
                logger.error(exception_value, exc_info=True)

                # We failed hard so we should raise a different exception that the
                raise cloudformation_cli_python_lib.exceptions.HandlerInternalFailure(
                    "Broken in Custom resource - READ, contact resource owner"
                ) from exception_value

        finally:

            logger.info("DynamoRead Exit Completed")

        # let exception flourish always
