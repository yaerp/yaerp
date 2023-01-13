class Account:
    
    def __init__(self, tag: str, ledger) -> None:
        self.tag = tag
        self.debit = 0
        self.credit = 0
        self.ledger = ledger
        if self.ledger:
            ledger.bind_and_subscribe_account(self)
