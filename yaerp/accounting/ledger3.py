import heapq
import operator
import uuid
from yaerp.accounting.account3 import AccountRecord
# from yaerp.accounting.post import Post
from yaerp.tools.sid import SID
from yaerp.tools.sorted_collection import SortedCollection


class Ledger:
    '''
    Accounting book
    '''
    def __init__(self, tag: str, name: str):
        self.tag = tag
        self.name = name
        self.posts = SortedCollection([], key=None) # post register
        self.accounts = {} # associated accounts
        self.journals = {} # associated journals

    def journal_entries_gen(self, posted=True, not_posted=True, date_beg=None, date_end=None):
        sources_of_journal_entries = []
        for journal in self.journals.values():
            sources_of_journal_entries.append(journal.journal_entries_gen(posted, not_posted, date_beg, date_end))
        return heapq.merge(*sources_of_journal_entries)

    def account_records_gen(self, posted=True, not_posted=True, date_beg=None, date_end=None, side=None, account=None):
        for je in self.journal_entries_gen(posted, not_posted, date_beg, date_end):
            yield from je.account_records_gen(side, account)

    def post_journal_entry(self, journal, journal_entry, define_post_id=None):
        self.__validate_journal_entry(journal, journal_entry)
        if journal_entry.is_zeroed():
            raise ValueError("posted entry must contain non-zero amounts")
        if define_post_id:
            new_post_id = define_post_id
        else:
            new_post_id = SID().new()
        for name, field in journal_entry.fields.items():
            # create new AccountRecord instances to overwrite the older ones
            if isinstance(field, AccountRecord) and field.raw_amount:
                posted_record = AccountRecord(field.account, 
                                                    field.raw_amount, 
                                                    field.side, 
                                                    field.journal_entry, 
                                                    new_post_id)
                journal_entry.fields[name] = posted_record
            elif isinstance(field, list):
                for idx, element in enumerate(field):
                    posted_record = AccountRecord(element.account, 
                                                        element.raw_amount, 
                                                        element.side, 
                                                        element.journal_entry, 
                                                        new_post_id)
                    field[idx] = posted_record 
        if not define_post_id:
            self.register_post(new_post_id)
        journal_entry.post = new_post_id

    def __validate_journal_entry(self, journal, journal_entry):
        if not journal_entry.is_balanced():
            raise RuntimeError('journal entry not balanced')
        for field in journal_entry.fields.values():
            if isinstance(field, AccountRecord):
                self.__validate_account_record(journal, field)
            elif isinstance(field, list):
                for element in field:
                    self.__validate_account_record(journal, element)

    def __validate_account_record(self, journal, account_record):
        if account_record.raw_amount and not account_record.account:
            raise ValueError('account entry has no parent account')
        if account_record.account and account_record.account not in self.accounts.values():
            raise ValueError(f'account entry has parent account associated with an another ledger. [j/e {account_record.journal_entry.sid}]')
        # if entry.transaction is None:
        #     raise ValueError('parent transaction is None')
        # if entry.transaction.journal is None:
        #     raise ValueError('parent journal is None')           
        # if entry.transaction.journal != journal:
        #     raise ValueError('parent journal should be the same as the posting journal')
        # if entry.transaction.journal not in self.journals.values():
            # raise ValueError('parent journal not associated whith this ledger') 
        if account_record.post:
            if account_record.post in self.posts:
                raise ValueError(f'Posting identifier {SID.print_form(account_record.post)} already exist in the ledger. [j/e {SID.print_form(account_record.journal_entry.sid)}]')

    def register_post(self, new_post_identifier):
        if new_post_identifier in self.posts:
            raise ValueError("Post already exist in register")
        self.posts.insert(new_post_identifier)

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
