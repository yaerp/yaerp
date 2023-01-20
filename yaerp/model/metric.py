from .exception import YaerpError

class MetricError(YaerpError):
    def __init__(self, message):
        super().__init__(message)

class Metric:
    def __init__(self, name, symbol, definition) -> None:
        self.name = name
        self.symbol = symbol
        self.definition = definition