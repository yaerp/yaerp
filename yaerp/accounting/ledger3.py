import heapq
import operator
from yaerp.accounting.account3 import AccountRecord
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
        self.accounts = SortedCollection([], key=operator.attrgetter('tag')) # associated accounts
        self.journals = SortedCollection([], key=operator.attrgetter('tag')) # associated journals

    def journal_entries_gen(self, posted=True, unposted=True, date_beg=None, date_end=None, only_journal=None, reverse=False):
        sources_of_journal_entries = []
        for journal in self.journals:
            if only_journal and only_journal != journal:
                continue
            sources_of_journal_entries.append(journal.entries_gen(posted, unposted, date_beg, date_end, reverse=reverse))
        return heapq.merge(*sources_of_journal_entries, reverse=reverse)

    def account_records_gen(self, posted=True, unposted=True, date_beg=None, date_end=None, side=None, account=None, reverse=False):
        for je in self.journal_entries_gen(posted, unposted, date_beg, date_end, reverse=reverse):
            yield from je.account_records_gen(side, account)

    def get_account(self, account_tag):
        return self.accounts.find(account_tag)

    def get_journal(self, journal_tag):
        return self.journals.find(journal_tag)

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
        if account_record.account and account_record.account not in self.accounts:
            raise ValueError(f'account entry has parent account associated with an another ledger. [j/e {account_record.journal_entry.sid}]')
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
        if account in self.accounts._items:
            # if already exist - reinsert account (tag change was possible)
            self.accounts.remove(account)      
        self.accounts.insert(account)
        account.ledger = self

    def update_account_tag(self, new_tag: str, current_tag: str, account): # SortedCollection (self.account) needs special work
        if not account:
            raise ValueError('account is None')  
        if account.ledger and account.ledger != self:
            raise ValueError('account already associated with an another Ledger')  
        if current_tag in self.accounts._keys and new_tag not in self.accounts._keys:
            if self.accounts.find(current_tag) != account:
                raise ValueError("account do not match to old tag")
            self.accounts.remove(account)   
            account.tag =  new_tag
            self.accounts.insert(account)

    def register_journal(self, journal):
        if not journal:
            raise ValueError('journal is None')  
        if journal.ledger and journal.ledger != self:
            raise ValueError('journal already associated with an another Ledger') 
        if journal in self.journals:
            raise ValueError('journal tag already exist in the Ledger') 
        self.journals.insert(journal)
        journal.ledger = self

    def unregister_account(self, account):
        if not account:
            raise ValueError('account is None')  
        if account.ledger and account.ledger != self:
            raise ValueError('account already associated with an another Ledger')  
        if account not in self.accounts:
            raise ValueError('account tag not exist in the Ledger')       
        for je in self.journal_entries_gen():
            for _ in je.account_records_gen(account=account):
                raise ValueError('Journal Entry/ies associated with this Account exist in the Ledger') 
        self.accounts.remove(account)
        account.ledger = None
 
    def unregister_journal(self, journal):
        if not journal:
            raise ValueError('"journal" argument has None value')  
        if journal.ledger and journal.ledger != self:
            raise ValueError('Journal already associated with an another Ledger') 
        if journal not in self.journals:
            raise ValueError('Journal tag not exist in the Ledger') 
        for je in journal.journal_entries_gen():
            raise ValueError('Journal Entry/ies exist in this Journal') 
        self.journals.remove(journal)
        journal.ledger = None