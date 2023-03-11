import operator
import uuid
from yaerp.accounting.account import AccountEntry
from yaerp.accounting.post import Post
from yaerp.tools.sorted_collection import SortedCollection


class Ledger:

    def __init__(self, tag: str):
        self.tag = tag
        self.account_entries = SortedCollection([], key=operator.attrgetter('journal_entry.date')) # main ledger's container
        self.accounts = {} # associated accounts
        self.journals = {} # associated journals

    def post_journal_entry(self, journal, journal_entry):
        self.__validate_journal_entry(journal, journal_entry)
        post = Post(uuid.uuid4().int, False)
        for name, field in journal_entry.fields.items():
            if isinstance(field, AccountEntry) and field.amount:
                posted_account_entry = AccountEntry(field.account, 
                                                    field.amount, 
                                                    field.side, 
                                                    field.journal_entry, 
                                                    post)
                self.__append_account_entry(posted_account_entry)
                journal_entry.fields[name] = posted_account_entry
            elif isinstance(field, list):
                for idx, element in enumerate(field):
                    posted_account_entry = AccountEntry(element.account, 
                                                        element.amount, 
                                                        element.side, 
                                                        element.journal_entry, 
                                                        post)
                    self.__append_account_entry(posted_account_entry)
                    field[idx] = posted_account_entry 
        journal.journal_entries.insert_right(journal_entry)
        journal_entry.post = post
        
    def post_summary_entry(self, journal, summary_journal_entry):
        self.__validate_journal_entry(journal, summary_journal_entry)
        summary_post = Post(uuid.uuid4().int, True)
        for name, field in summary_journal_entry.fields.items():
            if isinstance(field, AccountEntry):
                raise RuntimeError('not expected this kind of field')
            elif isinstance(field, list):
                for idx, element in enumerate(field):
                    posted_account_entry = AccountEntry(element.account, 
                                                        element.amount, 
                                                        element.side, 
                                                        element.journal_entry, 
                                                        summary_post)
                    self.__append_account_entry(posted_account_entry)
                    field[idx] = posted_account_entry           
        return summary_post

    def __validate_journal_entry(self, journal, journal_entry):
        if not journal_entry.is_balanced():
            raise RuntimeError('journal entry not balanced')
        for field in journal_entry.fields.values():
            if isinstance(field, AccountEntry):
                self.__validate_account_entry(journal, field)
            elif isinstance(field, list):
                for element in field:
                    self.__validate_account_entry(journal, element)

    def __validate_account_entry(self, journal, account_entry):
        if account_entry.amount and not account_entry.account:
            raise ValueError('account entry has no parent account')
        if account_entry.account and account_entry.account not in self.accounts.values():
            raise ValueError('account entry has parent account associated with an another ledger')
        # if entry.transaction is None:
        #     raise ValueError('parent transaction is None')
        # if entry.transaction.journal is None:
        #     raise ValueError('parent journal is None')           
        # if entry.transaction.journal != journal:
        #     raise ValueError('parent journal should be the same as the posting journal')
        # if entry.transaction.journal not in self.journals.values():
            # raise ValueError('parent journal not associated whith this ledger') 
        if account_entry in self.account_entries:
            raise ValueError('this account entry already exist in the ledger')

    def __append_account_entry(self, account_entry):
        self.account_entries.insert_right(account_entry)
        account_entry.account.append_entry(account_entry)

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
