import copy
# from yaerp.accounting.ledger import Ledger
from yaerp.accounting.account import AccountEntry, AccountSide
# from yaerp.accounting.journal_entry import JournalEntry
# from yaerp.accounting.post import Post

class Journal:
    '''
    * Journal
    Journal is a book that contain a sequence of business transactions.

      Business transaction, also known as 'Journal Entry', contains the data
    significant to a single event involving the movement/exchange of value
    (such as money, goods, services). These events must be measurable
    in monetary value so the company can record them for accounting purposes.

    Example of business transactions that can be a Journal Entry:
     - sale,
     - purchase,
     - adjustment,
     - depreciation,
     - opening and closing entries.

      Range of data required to store in each Journal Entry is determined by Journal.
    Look into define_fields() method to read the actual Journal Entry structure.
    Note that new Journal class, derived from this class can define completly new
    set of fields.
    '''
    def __init__(self, tag: str, ledger):
        if not tag:
            raise ValueError('tag is blank')
        self.tag = tag
        self.ledger = ledger
        if ledger:
            ledger.register_journal(self)       
        self.journal_entries = []

    def post_to_ledger(self, journal_entries, summary_info):
        ''' Aggregate journal entries into the 'total entry' and post this to the ledger. '''
        if not hasattr(journal_entries, '__iter__'):
            ValueError('\'journal_entries\' must be iterable')

        for journal_entry in journal_entries:
            self.validate_new_journal_entry(journal_entry)

        summary_account_entries = {}

        def add_to_summary(account_entry):
            if not account_entry.amount or not account_entry.account:
                return
            if account_entry.post:
                raise RuntimeError(f'already posted: account entry \'{account_entry}\', journal entry \'{account_entry.journal_entry}\'')
            key = f'{account_entry.side}@{account_entry.account.tag}'
            if key in summary_account_entries:
                summary_account_entries[key] += account_entry
            else:
                summary_account_entries[key] = AccountEntry(
                    account_entry.account,
                    account_entry.amount,
                    account_entry.side,
                    summary_info,
                    None)

        for journal_entry in journal_entries:
            for name, value in journal_entry.fields.items():
                if isinstance(value, AccountEntry):
                    add_to_summary(value)
                if isinstance(value, list):
                    for account_entry in value:
                        add_to_summary(account_entry)

        for sum_key in sorted(summary_account_entries.keys()):
            print(f"{sum_key}: {summary_account_entries[sum_key]}")

        # Build aggregated entry:

        summary_journal_entry = copy.deepcopy(summary_info)
        for key, value in summary_info.fields.items():
            if isinstance(value, (AccountEntry, list)):
                del summary_journal_entry.fields[key]
        # 
        summary_journal_entry.fields['Account'] = []
        for key in sorted(summary_account_entries):
            summary_journal_entry.fields['Account'].append(summary_account_entries[key])
        # 
        self.validate_new_journal_entry(summary_journal_entry)
        post = self.ledger.post_summary_entry(self, summary_journal_entry)
        for journal_entry in journal_entries:
            journal_entry._set_posted(post)

    def define_fields(self, journal_entry):
        '''
        Data structure for Journal Entries.
        Each transaction is stored as set of the following pairs:

        FIELD_NAME: FIELD_VALUE

         FIELD_NAME is always a string,

         FIELD_VALUE can contain the following variables:
          - None value means: 'this is info field'
                for example
                            'Date': None
                            'Description': None
          - Entry object means: 'this is the place for single account entry' (fixed side)
                for example
                            'Cash': Entry(None, 0, 0, transaction)
                            'Sale': Entry(None, 0, 1, transaction)
                            'Sale Tax': Entry(None, 0, 1, transaction)
          - [] (list) means: 'this is the place for multiple account entries' (free side)
                for example
                            'Account': []
        '''
        return {
            'Date':         None,   # info
            'Description':  None,   # info
            'Account':      []      # debit/credit account entries
            # 'Debit': AccountEntry(None, 0, 0, journal_entry, None),    # debit entry
            # 'Credit': AccountEntry(None, 0, 1, journal_entry, None)    # credit entry
        }

    def validate_new_journal_entry(self, journal_entry):
        if journal_entry in self.journal_entries:
            raise ValueError('the specified entry already exist in the journal')
        for field in journal_entry.fields.values():
            if isinstance(field, AccountEntry):
                if not field.journal_entry:
                    raise ValueError('account entry has no journal entry')
                if field.journal_entry != journal_entry:
                    raise ValueError('account entry has invalid journal entry')
    
    def __str__(self) -> str:
        return self.tag


class JournalEntry:
    '''
    * Journal Entry

      Journal Entry contains the data significant to a single event
    involving the movement/exchange of value (such as money, goods, services).
    These events must be measurable in monetary value so the company can
    record them for accounting purposes. 

    Example of business transactions the Journal Entry handle:
     - sale,
     - purchase,
     - adjustment,
     - depreciation.
    '''

    def __init__(self, journal):
        self.journal = journal
        self.post = None
        if self.journal:
            self.fields = self.journal.define_fields(self)
        else:
            self.fields = {}

    def is_balanced(self):
        result_dt, result_ct = 0, 0
        for field in self.fields.values():
            if isinstance(field, AccountEntry):
                if field.side != AccountSide.DEBIT and field.side != AccountSide.CREDIT:
                    raise ValueError('account side must be DEBIT or CREDIT')
                if field.amount and not field.account:
                    raise ValueError('entry with no account has non zero amount')
                if field.side == AccountSide.DEBIT:
                    result_dt += field.amount
                else:
                    result_ct += field.amount
            elif isinstance(field, list):
                for account_entry in field:
                    if account_entry.side != AccountSide.DEBIT and account_entry.side != AccountSide.CREDIT:
                        raise ValueError('account side must be DEBIT or CREDIT')
                    if account_entry.amount and not account_entry.account:
                        raise ValueError('entry with no account has non zero amount')
                    if account_entry.side == AccountSide.DEBIT:
                        result_dt += account_entry.amount
                    else:
                        result_ct += account_entry.amount
        return result_dt == result_ct

    def info(self, field_tag: str, field_value):
        ''' Set info field '''
        if field_tag not in self.fields.keys():
            raise RuntimeError(f'unknown field \'{field_tag}\'')
        self.fields[field_tag] = field_value

    def debit(self, field_tag: str, account, amount: int):
        ''' Set debit entry '''
        self.flow(field_tag, account, amount, AccountSide.DEBIT)

    def credit(self, field_tag: str, account, amount: int):
        ''' Set credit entry '''
        self.flow(field_tag, account, amount, AccountSide.CREDIT)

    def flow(self, field_tag: str, account, amount: int, side: AccountSide):
        ''' Set account entry '''
        if field_tag not in self.fields.keys():
            raise RuntimeError(f'unknown field \'{field_tag}\'')
        if side != AccountSide.DEBIT and side != AccountSide.CREDIT:
            raise ValueError('account side must be DEBIT or CREDIT')

        if isinstance(self.fields[field_tag], AccountEntry):
            if self.fields[field_tag].side != side:
                raise ValueError(f'Journal field \'{field_tag}\' expects {self.fields[field_tag].side} entry.')
            self.fields[field_tag] = AccountEntry(account, amount, side, self, None)
        elif isinstance(self.fields[field_tag], list):
            self.fields[field_tag].append(AccountEntry(account, amount, side, self, None))
        else:
            raise RuntimeError(f'Journal field \'{field_tag}\' is not dedicated for debit/credit entries.')

    def post_to_ledger(self):
        ''' Post this journal entry to the ledger (single post) '''
        if not self.is_balanced():
            raise RuntimeError('not balanced journal entry')
        if self.journal is None:
            raise ValueError('journal entry has no parent journal')
        self.journal.validate_new_journal_entry(self)
        self.journal.ledger.post_journal_entry(self.journal, self)
        # self.journal.post_separate(self)

    def _set_posted(self, post):
        if not post:
            raise ValueError('post is None')
        for name, value in self.fields.items():
            if isinstance(value, AccountEntry):
                if value.amount and value.account:
                        self.fields[name] = AccountEntry(
                            value.account,
                            value.amount,
                            value.side,
                            value.journal_entry,
                            post
                            )
            elif isinstance(value, list):
                for idx, account_entry in enumerate(value):
                    if account_entry.amount and account_entry.account:
                        value[idx] = AccountEntry(
                            account_entry.account,
                            account_entry.amount,
                            account_entry.side,
                            account_entry.journal_entry,
                            post
                            )
        self.post = post

    def __str__(self):
        post_info = '/not posted/'
        if self.post:
            if self.post.summary_entry:
                post_info = '/aggregated post/'
            else:
                post_info = '/simple post/'
        return ' '.join([
            f"{self.journal.tag}:  ",
            "; ".join([f"{str(value)}" for value in self.fields.values() if isinstance(value, (str, int, float))]),
            f'{post_info}'
        ])
