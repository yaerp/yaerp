from ..lib import YaerpError

class ModelError(YaerpError):
    def __init__(self, message):
        super().__init__(message)