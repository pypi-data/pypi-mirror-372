import logging

# Create a logger for the library
logger = logging.getLogger("yutipy")
logger.setLevel(logging.CRITICAL)


def enable_logging(level=logging.INFO, handler=None):
    """Enable logging for the library.

    Parameters
    ----------
    level : int, optional
        The logging level to set, by default logging.INFO.
    handler : logging.Handler, optional
        A custom logging handler to add, by default None (uses console handler).
    """
    logger.setLevel(level)

    # If no handler is provided, use the default console handler
    if handler is None:
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "[%(asctime)s] | %(name)s | [%(levelname)s] → %(module)s : line %(lineno)d : %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S %Z",
        )
        console_handler.setFormatter(formatter)
        handler = console_handler

    # Add the handler if it is not already added
    if handler not in logger.handlers:
        logger.addHandler(handler)

    # Disable propagation to avoid duplicate logs
    logger.propagate = False


def disable_logging():
    """Disable logging for the library."""
    logger.setLevel(logging.NOTSET)
    for handler in logger.handlers[:]:  # Remove all handlers
        logger.removeHandler(handler)
