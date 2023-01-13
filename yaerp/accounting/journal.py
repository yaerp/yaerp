class Journal:

    def __init__(self, tag: str, ledger):
        self.tag = tag
        self.accounting_entries = []
        self.ledger = ledger
        if ledger:
            ledger.register_journal(self)

    def add_entry(self, entry):
        if not entry.is_balanced():
            raise RuntimeError()
        if entry in self.accounting_entries: 
            raise RuntimeError()
        self.accounting_entries.append(entry)
        for dt in entry.debit_records:
            self.ledger.post(dt)
        for cr in entry.credit_records:
            self.ledger.post(cr)
