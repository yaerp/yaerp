class Journal:

    def __init__(self, tag: str, ledger):
        if not tag:
            raise RuntimeError()
        self.tag = tag
        self.accounting_entries = []
        self.ledger = ledger
        if ledger:
            ledger.register_journal(self)
        

    def commit_entry(self, entry):
        if entry in self.accounting_entries: 
            raise RuntimeError('the Entry already exist in this Journal')  
        for debit_post in entry.debit_fields:
            if debit_post.entry is None:
                raise RuntimeError('Post has no set Entry')
            elif debit_post.entry != entry:
                raise RuntimeError('Post has set unknown Entry')
        for credit_post in entry.credit_fields:
            if credit_post.entry is None:
                raise RuntimeError('Post has no set Entry')
            elif credit_post.entry != entry:
                raise RuntimeError('Post has set unknown Entry') 
        self.ledger.commit_journal_entry(self, entry)
