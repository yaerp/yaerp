import operator
import uuid
from yaerp.accounting.account import AccountRecord
from yaerp.accounting.post import Post
from yaerp.tools.sid import SID
from yaerp.tools.sorted_collection import SortedCollection


class Ledger:
    '''
    Accounting book
    '''
    def __init__(self, tag: str, name: str):
        self.tag = tag
        self.name = name
        self.posts = SortedCollection(
            [], 
            key=operator.attrgetter('journal_entry.date', 'journal_entry.time', 'journal_entry.sid')
        ) # ledger's main container
        self.accounts = {} # associated accounts
        self.journals = {} # associated journals

    def post_journal_entry(self, journal, journal_entry, use_guid=False):
        self.__validate_journal_entry(journal, journal_entry)
        if journal_entry.is_zeroed():
            raise ValueError("posted entry must contain non-zero amounts")
        if use_guid:
            new_post_id = uuid.uuid4().int
        else:
            new_post_id = SID().new()
        post = Post(new_post_id, False)
        for name, field in journal_entry.fields.items():
            if isinstance(field, AccountRecord) and field.raw_amount:
                posted_record = AccountRecord(field.account, 
                                                    field.raw_amount, 
                                                    field.side, 
                                                    field.journal_entry, 
                                                    post)
                self.__append_account_record(posted_record)
                journal_entry.fields[name] = posted_record
            elif isinstance(field, list):
                for idx, element in enumerate(field):
                    posted_record = AccountRecord(element.account, 
                                                        element.raw_amount, 
                                                        element.side, 
                                                        element.journal_entry, 
                                                        post)
                    self.__append_account_record(posted_record)
                    field[idx] = posted_record 

        ## czy to jest konieczne? kontener moze przechowywac zarowno nowe jak i zaksiegowane
        # journal.journal_entries.insert_right(journal_entry)

        journal_entry.post = post
        
    def post_summary_entry(self, journal, summary_journal_entry, use_guid=False):
        self.__validate_journal_entry(journal, summary_journal_entry)
        if use_guid:
            new_post_id = uuid.uuid4().int
        else:
            new_post_id = SID().new()
        summary_post = Post(new_post_id, True)
        for name, field in summary_journal_entry.fields.items():
            if isinstance(field, AccountRecord):
                raise RuntimeError(f'not expected field "{name}"')
            elif isinstance(field, list):
                for idx, element in enumerate(field):
                    posted_record = AccountRecord(element.account, 
                                                        element.raw_amount, 
                                                        element.side, 
                                                        element.journal_entry, 
                                                        summary_post)
                    self.__append_account_record(posted_record)
                    field[idx] = posted_record           
        return summary_post

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
            raise ValueError('account entry has parent account associated with an another ledger')
        # if entry.transaction is None:
        #     raise ValueError('parent transaction is None')
        # if entry.transaction.journal is None:
        #     raise ValueError('parent journal is None')           
        # if entry.transaction.journal != journal:
        #     raise ValueError('parent journal should be the same as the posting journal')
        # if entry.transaction.journal not in self.journals.values():
            # raise ValueError('parent journal not associated whith this ledger') 
        if account_record in self.posts:
            raise ValueError('this account entry already exist in the ledger')

    def __append_account_record(self, account_record):
        self.posts.insert_right(account_record)
        account_record.account.append_record(account_record)

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
