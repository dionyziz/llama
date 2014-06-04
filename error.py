# ----------------------------------------------------------------------
# error.py
#
# Error logging and reporting module
#
# Author: Nick Korasidis <Renelvon@gmail.com>
# ----------------------------------------------------------------------

_logger = None  # Singleton


class ErrorLogger:
    """
    Simple error logger for the llama compiler. It provides methods
    for logging and reporting errors of varying severities. It is
    intended that all modules share a single instance of this class.
    """

    error, warn = False, False

    errors = None
    warnings = None
    input_file = None

    def __init__(self, input_file):
        """Initialize logger to empty state."""
        self.errors = []
        self.warnings = []
        self.input_file = input_file


def init_logger(input_file):
    """If the logger hasn't been created, do so."""
    global _logger
    if _logger is None:
        _logger = ErrorLogger(input_file)


def push_error(line, message):
    """Add an error to the logger."""
    global _logger
    _logger.error = True
    _logger.errors.append((line, message))


def push_warning(line, message):
    """Add a warning to the logger."""
    global _logger
    _logger.warn = True
    _logger.warnings.append((line, message))


def get_errors():
    """Yield all logged errors, in ascending line order."""
    for _, msg in sorted(_logger.errors):
        yield ''.join((_logger.input_file, ': ', msg))


def get_warnings():
    """Yield all logged warnings, in ascending line order."""
    for _, msg in sorted(_logger.warnings):
        yield ''.join((_logger.input_file, ': ', msg))


def get_all_signals():
    """Yield all logged signals, in ascending line order."""
    for _, msg in sorted(_logger.warnings + _logger.errors):
        yield ''.join((_logger.input_file, ': ', msg))
