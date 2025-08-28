import logging

from gsv.exceptions import InvalidLoggingLevelError


def get_logger(logger_name, logging_level):
    """
    Get Logger object for GSVRetriever logs.

    Arguments
    ---------
    logging_level : str
        Minimum severity level for log messages to be printed.
        Options are 'DEBUG', 'INFO', 'WARNING', 'ERROR' and
        'CRITICAL'.

    Returns
    -------
    logging.Logger
        Logger object for GSVRetriever logs.
    """
    if isinstance(logging_level, str):
        logging_level = logging_level.upper()

    logger = logging.getLogger(logger_name)

    try:
        logger.setLevel(logging_level)
    except ValueError:
        raise InvalidLoggingLevelError(logging_level)

    if not logger.handlers:  # was the logger already initialized?
        formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
    return logger
