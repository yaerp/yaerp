from ..lib import YaerpError

class InventoryError(YaerpError):
    def __init__(self, message):
        super().__init__(message)