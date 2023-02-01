import yaerp.accounting.journal
import yaerp.accounting.post

class Journal:

    def __init__(self, tag: str, ledger: yaerp.accounting.ledger.Ledger):
        if not tag:
            raise ValueError('tag is blank')
        self.tag = tag
        self.accounting_entries = []
        self.ledger = ledger
        if ledger:
            ledger.register_journal(self)
        
    def commit_entry(self, entry):
        ''' Post journal entry to the ledger.'''
        self.validate_new_entry(entry) 
        self.ledger.commit_journal_entry(self, entry)

    def validate_new_entry(self, entry):
        if entry in self.accounting_entries:
            raise ValueError('the specified entry already exist in the journal')  
        for field in entry.fields:
            if field is yaerp.accounting.post.Post:
                if not field.entry:
                    raise ValueError('post has no parent entry')
                if field.entry != entry:
                    raise ValueError('post has invalid parent entry')
