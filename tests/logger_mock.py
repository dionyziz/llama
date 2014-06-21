class LoggerMock():
    """Mock of a proper logger for testing purposes"""

    def __init__(self):
        pass

    errors = 0
    warnings = 0

    def error(self, *args):
        self.errors += 1

    def warning(self, *args):
        self.warnings += 1

    def debug(self, *args):
        pass

    def info(self, *args):
        pass

    @property
    def success(self):
        return self.errors == 0

    @property
    def perfect_success(self):
        return self.errors == 0 and self.warnings == 0
