import logging


def configure_logger():
    logging.disable(logging.NOTSET)
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__package__)
    logger.error("we are here")
    logging.error("we are here")
