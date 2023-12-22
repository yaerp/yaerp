from yaerp.accounting.journal3 import Journal
from yaerp.accounting.ledger3 import Ledger
from yaerp.accounting.marker import PropertyContainer
from yaerp.tools.singleton import Singleton


class GeneralLedger(Ledger, metaclass=Singleton):
    ''' Get General Ledger instance '''
    def __init__(self):
        super().__init__("GL", "General Ledger")


class GeneralJournal(Journal, metaclass=Singleton):
    ''' Get General Journal instance '''
    def __init__(self):
        super().__init__("GJ", "General Journal", GeneralLedger())


class AccountTypes(PropertyContainer):
    ''' Get Account Types container instance '''
    def __init__(self):
        super().__init__()
