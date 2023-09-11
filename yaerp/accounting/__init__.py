from yaerp.accounting.journal import Journal
from yaerp.accounting.ledger import Ledger


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class GL(Ledger, metaclass=Singleton):
    def __init__(self):
        super().__init__("General Ledger")

class GJ(Journal, metaclass=Singleton):
    def __init__(self):
        super().__init__("General Journal", GL())
