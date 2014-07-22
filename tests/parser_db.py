from compiler import error, parse


class ParserDB():
    """A class for parsing with memoized parsers."""

    parsers = {}

    @classmethod
    def _parse(cls, data, start='program'):
        mock = error.LoggerMock()

        try:
            parser = cls.parsers[start]
        except KeyError:
            parser = cls.parsers[start] = parse.Parser(
                logger=mock,
                start=start
            )

        # Clear previous logger state prior to parsing.
        parser.logger.clear()

        tree = parser.parse(data=data)

        return tree
