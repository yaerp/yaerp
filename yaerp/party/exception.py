from ..lib import YaerpError

class PartyError(YaerpError):
    def __init__(self, message):
        super().__init__(message)