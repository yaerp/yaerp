from .party import Party, PartyError


class PersonError(PartyError):
    def __init__(self, message):
        super().__init__(message)

class Person(Party):
    pass
    