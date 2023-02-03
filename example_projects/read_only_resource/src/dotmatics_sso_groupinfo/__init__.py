import logging
from cf_extension_core import CustomResourceHelpers

# Do this here, so we get logs from all the handler classes
logging.getLogger(__name__).setLevel(logging.DEBUG)

# Add more output to logs by default
CustomResourceHelpers.init_logging()
