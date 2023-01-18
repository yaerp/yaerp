from .exception import ModelError

class LocaleError(ModelError):
    def __init__(self, message):
        super().__init__(message)

class Locale:
    def __init__(self, identifier, name, description = None) -> None:
        if not identifier or not name:
            raise LocaleError('Locale initialization failed - both, identifier and name cannot be blank')
        self.identifier = identifier
        self.name = name
        self.description = description

class CountryCode(Locale):
    def __init__(self, identifier, name, description=None, ) -> None:
        super().__init__(identifier, name, description)