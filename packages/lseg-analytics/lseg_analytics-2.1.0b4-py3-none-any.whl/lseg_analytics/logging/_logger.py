import logging
import os
import sys
from logging import Formatter, Logger, StreamHandler
from logging.handlers import RotatingFileHandler
from typing import List

from ._config import LoggingConfiguration, LoggingOutput, logging_config

# Disable logId for HTTP trace since it has no such ID
# _FORMAT = "[%(levelname)s]\t[%(asctime)s]\t[%(threadName)s]\t[%(name)s]\t[%(filename)s:%(lineno)d]\t[Log ID: %(logId)d] %(message)s"
_FORMAT = (
    "[%(levelname)s]\t[%(asctime)s]\t[%(threadName)s]\t[%(relativepath)s]\t[%(filename)s:%(lineno)d]\t %(message)s"
)

_formatter = Formatter(fmt=_FORMAT)
_pkg_name = "lseg_analytics"
_pkg_root = os.path.abspath(__file__).rsplit(_pkg_name, 1)[0]

_global_logger = None


def get_library_logger() -> "LibraryLogger":
    global _global_logger
    if _global_logger is None:
        _global_logger = _create_logger(_pkg_name)
    return _global_logger  # type: ignore


def _create_logger(name: str) -> "LibraryLogger":
    logging.setLoggerClass(LibraryLogger)
    logger = logging.getLogger(name)  # type: ignore
    logging.setLoggerClass(Logger)
    logger.apply_logging_config(logging_config)
    logging_config.add_logger(logger)
    return logger  # type: ignore


class PackagePathFilter(logging.Filter):
    def filter(self, record):
        record.relativepath = record.name
        pathname = os.path.dirname(record.pathname)
        if pathname.startswith(_pkg_root + _pkg_name):
            record.relativepath = pathname.replace(_pkg_root, "").replace(os.sep, ".")
        return True


class LibraryLogger(Logger):
    _file_handler = None

    def __init__(self, name: str):
        super().__init__(name=name)

    def apply_logging_config(self, log_conf: LoggingConfiguration):
        self.set_output(log_conf.outputs)
        self.set_level(log_conf.get_log_level())

    def set_level(self, level: int):
        self.setLevel(level)

    def set_output(self, outputs: List["LoggingOutput"]):
        self.handlers.clear()
        for output in outputs:
            if output == LoggingOutput.STDOUT:
                self._add_stdout_handler()
            elif output == LoggingOutput.FILE:
                self._add_file_handler()

    def _add_stdout_handler(self):
        handler = StreamHandler(stream=sys.stdout)
        handler.setFormatter(_formatter)
        handler.addFilter(PackagePathFilter())
        self.addHandler(handler)

    def _add_file_handler(self):
        if LibraryLogger._file_handler is None:
            LibraryLogger._init_file_handler()
        self.addHandler(LibraryLogger._file_handler)

    @classmethod
    def _init_file_handler(cls):
        cls._file_handler = RotatingFileHandler(
            filename="".join([_pkg_name, ".log"]), maxBytes=10 * 1024 * 1024, encoding="utf-8", mode="w"
        )
        cls._file_handler.setFormatter(_formatter)
        cls._file_handler.addFilter(PackagePathFilter())


# For HTTP trace debugging log
http_logger = _create_logger("corehttp")

# for flask trace debugging log
werkzeug_logger = _create_logger("werkzeug")
