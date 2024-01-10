from .exception import YaerpError

class MetricError(YaerpError):
    def __init__(self, message):
        super().__init__(message)

class Metric:
    def __init__(self, name, symbol, definition) -> None:
        self.name = name
        self.symbol = symbol
        self.definition = definition

    def toStringForm(self, internal_value, /, *params):
        raise NotImplementedError()

    def toInternalForm(self, external_value, /, *params):
        raise NotImplementedError()