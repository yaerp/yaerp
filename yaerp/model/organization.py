from .party import Party, PartyError

class OrganizationError(PartyError):
    def __init__(self, message):
        super().__init__(message)

class Organization(Party):
    pass