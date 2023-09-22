from yaerp.accounting.journal import Journal
from yaerp.accounting.ledger import Ledger
from yaerp.accounting.marker import PropertyContainer


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class GeneralLedger(Ledger, metaclass=Singleton):
    ''' Get General Ledger instance '''
    def __init__(self):
        super().__init__("General Ledger")

class GeneralJournal(Journal, metaclass=Singleton):
    ''' Get General Journal instance '''
    def __init__(self):
        super().__init__("General Journal", GeneralLedger())

class AccountTypes(PropertyContainer):
    ''' Get Account Types container instance '''
    def __init__(self):
        super().__init__()
