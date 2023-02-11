import yaerp.accounting.entry

class Journal:

    def __init__(self, tag: str, ledger):
        if not tag:
            raise ValueError('tag is blank')
        self.tag = tag
        self.ledger = ledger
        if ledger:
            ledger.register_journal(self)       
        self.transactions = []
        
    def commit_transaction(self, transaction):
        ''' Post transaction entries to the ledger.'''
        self.validate_new_transaction(transaction) 
        self.ledger.commit_transaction(self, transaction)

    def validate_new_transaction(self, transaction):
        if transaction in self.transactions:
            raise ValueError('the specified transaction already exist in the journal')  
        for field in transaction.fields.values():
            if isinstance(field, yaerp.accounting.entry.Entry):
                if not field.transaction:
                    raise ValueError('entry has no parent transaction')
                if field.transaction != transaction:
                    raise ValueError('entry has invalid parent transaction')
    
    def __str__(self) -> str:
        return self.tag
