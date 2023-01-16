from .exception import AccountingError


class JournalError(AccountingError):
    def __init__(self, message):
        super().__init__(message)

class Journal:

    def __init__(self, tag: str, ledger):
        if not tag:
            raise JournalError('Journal initialization failed: blank tag')
        self.tag = tag
        self.accounting_entries = []
        self.ledger = ledger
        if ledger:
            ledger.register_journal(self)
        

    def commit_entry(self, entry):
        self.validate_new_entry(entry) 
        self.ledger.commit_journal_entry(self, entry)


    def validate_new_entry(self, entry):
        if entry in self.accounting_entries:
            # return False, 'the Entry already exist in this Journal'
            raise JournalError('validate new Entry failed: the Entry already exist in this Journal')  
        for debit_post in entry.debit_fields:
            if debit_post.entry is None:
                # return False, 'Post has no set Entry'
                raise JournalError('validate new Entry failed: Post has no set Entry')
            elif debit_post.entry != entry:
                # return False, 'Post has set unknown Entry'
                raise JournalError('validate new Entry failed: Post has set unknown Entry')
        for credit_post in entry.credit_fields:
            if credit_post.entry is None:
                # return False, 'Post has no set Entry'
                raise JournalError('validate new Entry failed: Post has no set Entry')
            elif credit_post.entry != entry:
                # return False, 'Post has set unknown Entry'
                raise JournalError('validate new Entry failed: Post has set unknown Entry')
