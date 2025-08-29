import logging
import logging.config

from bugsnag.handlers import BugsnagHandler
from fluidattacks_core.logging import PRODUCT_LOGGING


def configure_logger(*, log_to_remote: bool) -> None:
    logging.config.dictConfig(PRODUCT_LOGGING)

    if log_to_remote:
        logger = logging.getLogger()

        bugsnag_handler = BugsnagHandler(extra_fields={"extra": ["extra"]})
        bugsnag_handler.setLevel(logging.ERROR)
        logger.addFilter(bugsnag_handler.leave_breadcrumbs)
        logger.addHandler(bugsnag_handler)


def modify_logger_level() -> None:
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
