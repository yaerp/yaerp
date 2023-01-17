from .exception import PartyError

class AddressError(PartyError):
    def __init__(self, message):
        super().__init__(message)

class Address:
    def __init__(self, valid_from = None, valid_to = None) -> None:
        self.set_valid_from = valid_from
        self.set_valid_to = valid_to

class EmailAddress(Address):
    def __init__(self, email_address, valid_from=None, valid_to=None) -> None:
        super().__init__(valid_from, valid_to)
        self.email_address = email_address

class Telephone(Address):
    def __init__(self, country_code, national_prefix, area_code, number, extension, valid_from=None, valid_to=None) -> None:
        super().__init__(valid_from, valid_to)
        self.telephone['country_code'] = country_code
        self.telephone['national_preix'] = national_prefix
        self.telephone['area_code'] = area_code
        self.telephone['number'] = number
        self.telephone['extension'] = extension
