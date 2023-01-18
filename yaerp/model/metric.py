from .exception import ModelError

class MetricError(ModelError):
    def __init__(self, message):
        super().__init__(message)

class Metric:
    pass