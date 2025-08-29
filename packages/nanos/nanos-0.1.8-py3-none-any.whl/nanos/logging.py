import logging
from functools import cached_property


class LoggerMixin:  # pylint: disable=too-few-public-methods
    """Simple mixin for logging.

    Adds a ``logger`` property to the class and sets the logger name
    to the module and class name of the class:

        >>> class MyClass(LoggerMixin):
        ...     pass
        ...
        >>> my_class = MyClass()
        >>> my_class.logger.name
        'mymodule.MyClass'
    """

    @cached_property
    def logger(self) -> logging.Logger:
        """Logger instance for this class.

        The logger name is determined by the module and class name of this class.
        For example, if the class is named `MyClass` and it's in the module
        `mymodule`, the logger name will be `mymodule.MyClass`.

        Returns:
            Logger: Logger instance for this class.
        """
        name = ".".join([self.__class__.__module__, self.__class__.__name__])
        return logging.getLogger(name)


def set_level_for_logger(
    logger_names: str | list[str] | tuple[str, ...], level: int = logging.WARNING
) -> None:
    """Change logging level for one or more loggers.

    Args:
        logger_names (str | list[str] | tuple[str, ...]): Logger name(s) to change level for.
        level (int, optional): Logging level to set. Defaults to ``logging.WARNING``.

    Returns:
        None
    """
    if isinstance(logger_names, str):
        logging.getLogger(logger_names).setLevel(level)
    elif isinstance(logger_names, (tuple, list)):
        for logger_name in logger_names:
            logging.getLogger(logger_name).setLevel(level)
    else:
        raise TypeError(
            f"Expected logger_names to be str, tuple or list, got {type(logger_names)} instead"
        )


def get_simple_logger(
    name: str = "root",
    console: bool = True,
    log_file: str | None = None,
    log_level: str | int = logging.DEBUG,
) -> logging.Logger:
    """Creates simple instance of logger.

    Useful for simple scripts, where precise configuration is not needed. Output
    example:

        >>> import logging
        >>> logger = get_simple_logger()
        >>> logger.debug("Hello, world!")
        2023-05-01T12:34:56 root DEBUG Hello, world!

    Args:
        name (str | None, optional): Name of logger. Defaults to "root".
        console (bool, optional): Add console handler. Defaults to True.
        log_level (str | int, optional): Log level. Defaults to ``logging.DEBUG``.
        log_file (str | None, optional): File name to write log to. Defaults to None.

    Returns:
        logging.Logger
    """
    log_formatter = logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s")
    log_formatter.datefmt = "%Y-%m-%dT%H:%M:%S"
    logger = logging.getLogger()
    logger.name = name
    logger.setLevel(log_level)
    if log_file:
        file_handler = logging.FileHandler(log_file, mode="a")
        file_handler.setFormatter(log_formatter)
        logger.addHandler(file_handler)

    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(log_formatter)
        logger.addHandler(console_handler)
    return logger
