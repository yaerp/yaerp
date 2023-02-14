import uuid
import yaerp.accounting.entry


class Ledger:

    def __init__(self, tag: str):
        self.tag = tag
        self.posts = [] # main ledger's container 
        self.accounts = {} # associated accounts
        self.journals = {} # associated journals

    def commit_transaction(self, journal, transaction):
        self.__validate_entries(journal, transaction)         
        for field in transaction.fields.values():
            if isinstance(field, yaerp.accounting.entry.Entry):
                self.__append_entry(field)
            elif isinstance(field, list):
                for element in field:
                    self.__append_entry(element)
        journal.transactions.append(transaction)
        
    def __validate_entries(self, journal, transaction):
        if not transaction.is_balanced():
            raise RuntimeError('not balanced Transaction')
        for field in transaction.fields.values():
            if isinstance(field, yaerp.accounting.entry.Entry):
                self.__validate_entry(journal, field)
            elif isinstance(field, list):
                for element in field:
                    self.__validate_entry(journal, element)

    def __validate_entry(self, journal, entry):
        if entry.account is None:
            raise ValueError('parent account is None')
        if entry.account not in self.accounts.values():
            raise ValueError('parent account not associated with this ledger')
        if entry.transaction is None:
            raise ValueError('parent transaction is None')
        if entry.transaction.journal is None:
            raise ValueError('parent journal is None')           
        if entry.transaction.journal != journal:
            raise ValueError('parent journal should be the same as the posting journal')
        if entry.transaction.journal not in self.journals.values():
            raise ValueError('parent journal not associated whith this ledger') 
        if entry in self.posts:
            raise ValueError('entry already exist in the ledger posts')

    def __append_entry(self, entry):
        self.posts.append(entry)
        entry.account.append_entry(entry)

    def register_account(self, account):
        if not account:
            raise ValueError('account is None')  
        if account.ledger and account.ledger != self:
            raise ValueError('account already associated with an another Ledger')         
        self.accounts[account.tag] = account
        account.ledger = self
 
    def register_journal(self, journal):
        if not journal:
            raise ValueError('journal is None')  
        if journal.ledger and journal.ledger != self:
            raise ValueError('journal already associated with an another Ledger') 
        self.journals[journal.tag] = journal
        journal.ledger = self
