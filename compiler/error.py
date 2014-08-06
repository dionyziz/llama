"""
# ----------------------------------------------------------------------
# error.py
#
# Error logging and reporting module. Utilizes python logging.
#
# Author: Nick Korasidis <Renelvon@gmail.com>
# ----------------------------------------------------------------------
"""

import logging


def _format(f):
    def new_f(self, fmt, *args):
        msg = fmt % args  # Let it throw, let it throw, let it throw
        f(self, msg)
    return new_f


class LoggerInterface:
    """
    Interface and minimal implementation of a logger.
    Mainly used for testing purposes.
    """

    errors = 0
    warnings = 0

    def __init__(self):
        raise NotImplementedError

    def clear(self):
        """Reset logger state for testability"""

        self.errors = 0
        self.warnings = 0

    @_format
    def debug(self, msg):
        pass

    @_format
    def info(self, msg):
        pass

    @_format
    def warning(self, msg):
        self.warnings += 1

    @_format
    def error(self, msg):
        self.errors += 1

    @property
    def success(self):
        """Operation is successful iff zero errors are logged."""
        return self.errors == 0

    @property
    def perfect_success(self):
        """
        Operation is perfectly successful iff zero errors/warnings
        are logged.
        """
        return self.errors == 0 and self.warnings == 0


class LoggerMock(LoggerInterface):
    """Mock of a full logger. Mainly used for testing purposes."""

    def __init__(self):
        """Make a new mock loggger."""
        pass


class Logger(LoggerInterface):
    """
    Simple error logger for the llama compiler. Provides methods for
    logging and reporting errors of varying severities.
    It is intended that all modules share one instance of this class.
    """

    # Number of Logger instances created
    _instances = 0

    # The logger instance, as constructed by the logging module
    _logger = None

    def __init__(self, inputfile="<stdin>", level=logging.WARNING):
        """Create a new logger for the llama compiler."""
        self._logger = logging.getLogger('llama%d' % Logger._instances)
        Logger._instances += 1
        self._logger.setLevel(level)
        formatter = logging.Formatter(inputfile + ": %(message)s")
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)

    @_format
    def error(self, msg):
        """Add an error to the logger."""
        self._logger.error(msg)
        self.errors += 1

    @_format
    def warning(self, msg):
        """Add a warning to the logger."""
        self._logger.warning(msg)
        self.warnings += 1

    @_format
    def debug(self, msg):
        """Add some debug info to the logger."""
        self._logger.debug(msg)

    @_format
    def info(self, msg):
        """Add some general info to the logger."""
        self._logger.info(msg)
