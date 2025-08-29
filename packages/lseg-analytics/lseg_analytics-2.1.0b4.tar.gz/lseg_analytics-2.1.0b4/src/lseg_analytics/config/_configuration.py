import enum

from ..exceptions import LibraryException
from ..logging._config import logging_config


class ConfigurationMeta(type):
    def __getitem__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]
        else:
            raise LibraryException(f"Configuration item '{item}' does not exist!")


class Configuration(metaclass=ConfigurationMeta):
    """
    Configuration class for the SDK. This class is used to configure the SDK.

    Attributes
    ----------
    logging : LoggingConfig
        Logging configuration for the SDK.

    Examples
    --------
    Retrieve the logging configuration and set logging DEBUG output.

    >>> Configuration["logging"].set_log_level(logging.DEBUG)

    Retrieve the logging configuration and add file output for SDK logging.

    >>> Configuration["logging"].add_output(LoggingOutput.FILE)

    """

    logging = logging_config
    """ Logging configuration for the SDK. """
