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


class LoggerMock:
    """Mock of a proper logger for testing purposes"""

    def __init__(self):
        pass

    errors = 0
    warnings = 0

    def debug(self, *args):
        pass

    def info(self, *args):
        pass

    def warning(self, *args):
        self.warnings += 1

    def error(self, *args):
        self.errors += 1

    @property
    def success(self):
        return self.errors == 0

    @property
    def perfect_success(self):
        return self.errors == 0 and self.warnings == 0


class Logger:
    """
    Simple error logger for the llama compiler. Provides methods for
    logging and reporting errors of varying severities.
    It is intended that all modules share one instance of this class.
    """

    # Number of Logger instances created
    _instances = 0

    # The logger instance, as constructed by the logging module
    _logger = None

    errors = 0
    warnings = 0

    def __init__(self, inputfile, level=logging.WARNING):
        """Create a new logger for the llama compiler."""
        self._logger = logging.getLogger('llama%d' % Logger._instances)
        Logger._instances += 1
        self._logger.setLevel(level)
        formatter = logging.Formatter(inputfile + ": %(message)s")
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)

    def critical(self, *args):
        """Add a critical error to the logger."""
        self._logger.critical(*args)

    def error(self, *args):
        """Add an error to the logger."""
        self._logger.error(*args)
        self.errors += 1

    def debug(self, *args):
        """Add some debug info to the logger."""
        self._logger.debug(*args)

    def info(self, *args):
        """Add some general info to the logger."""
        self._logger.info(*args)

    def warning(self, *args):
        """Add a warning to the logger."""
        self._logger.warning(*args)
        self.warnings += 1
