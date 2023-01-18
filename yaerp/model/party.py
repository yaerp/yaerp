from .exception import ModelError

class PartyError(ModelError):
    def __init__(self, message):
        super().__init__(message)

class Party:
    pass