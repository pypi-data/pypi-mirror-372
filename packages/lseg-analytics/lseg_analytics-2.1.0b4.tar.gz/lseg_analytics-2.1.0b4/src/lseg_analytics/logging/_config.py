import enum
import logging
import typing
from typing import List, Optional

if typing.TYPE_CHECKING:
    from lseg_analytics.logging._logger import LibraryLogger


class LoggingOutput(enum.Enum):
    """
    Enum class for logging output types.

    Attributes
    ----------
    STDOUT : str
        Output to standard output.
    FILE : str
        Output to a file.

    Examples
    --------
    Add file output for SDK logging.

    >>> Configuration["logging"].add_output(LoggingOutput.FILE)

    Remove standard output for SDK logging.

    >>> Configuration["logging"].remove_output(LoggingOutput.STDOUT)

    """

    STDOUT = "stdout"
    """ Output to standard output. """
    FILE = "file"
    """ Output to a file. """


class LoggingConfiguration:
    def __init__(
        self,
        level: Optional[int] = None,
        outputs: Optional[List[LoggingOutput]] = None,
    ):
        self._level = level
        # TODO: Improve Output configuration by adding file path, etc.
        if outputs is None:
            outputs = []
        self._outputs = outputs
        self._loggers: List["LibraryLogger"] = []

    def set_log_level(self, level: int):
        self._level = level
        for logger in self._loggers:
            logger.set_level(level)

    def get_log_level(self):
        return self._level

    @property
    def outputs(self):
        return self._outputs

    def add_output(self, output: LoggingOutput):
        if output in self._outputs:
            return
        self._outputs.append(output)
        for logger in self._loggers:
            logger.set_output(self._outputs)

    def remove_output(self, output: LoggingOutput):
        self._outputs.remove(output)
        for logger in self._loggers:
            logger.set_output(self._outputs)

    def add_logger(self, logger: "LibraryLogger"):
        self._loggers.append(logger)


logging_config = LoggingConfiguration(
    level=logging.ERROR,
    outputs=[LoggingOutput.STDOUT],
)
