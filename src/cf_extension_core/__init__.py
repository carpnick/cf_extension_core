import logging

# Public stuff
from cf_extension_core.interface import CustomResourceHelpers, generate_dynamodb_resource  # noqa: F401
from cf_extension_core.base_handler import BaseHandler  # noqa: F401


# Package Logger
# Set up logging to ``/dev/null`` like a library is supposed to.
# http://docs.python.org/3.3/howto/logging.html#configuring-logging-for-a-library
logging.getLogger(__name__).addHandler(logging.NullHandler())
