import copy
import operator
from yaerp.accounting.account import AccountRecord, AccountSide
from yaerp.tools.sorted_collection import SortedCollection


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
        self.journal_entries = SortedCollection([], key=operator.attrgetter('date'))

    def post_aggregated(self, journal_entries, summary_date, summary_description,
                        summary_reference=None, **summary_info_fields):
        ''' 
        Aggregate journal entries into the 'summary entry' and post this to the ledger. 
        (many-to-one)
        '''
        if not hasattr(journal_entries, '__iter__'):
            ValueError('\'journal_entries\' must be iterable')

        # Build empty summary entry (similar to General Journal entry):
        summary_journal_entry = JournalEntry(self)
        
        summary_journal_entry.date = summary_date
        summary_journal_entry.description = summary_description
        summary_journal_entry.reference = summary_reference
        for field_name, field_value in summary_info_fields.items():
            summary_journal_entry.add_info(field_name, field_value)
        
        # Remove current account fields and put new, all-purpose 'Account' field:
        clone = JournalEntry(self)        
        for key, value in clone.fields.items():
            if isinstance(value, (AccountRecord, list)):
                del summary_journal_entry.fields[key]
        summary_journal_entry.fields['Account'] = []


        # Group and accumulate account entries:

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
                summary_account_entries[key] = AccountRecord(
                    account_entry.account,
                    account_entry.amount,
                    account_entry.side,
                    summary_journal_entry,
                    None)

        for journal_entry in set(journal_entries):
            self.validate_new_journal_entry(journal_entry)
            for value in journal_entry.fields.values():
                if isinstance(value, AccountRecord):
                    add_to_summary(value)
                    continue
                if isinstance(value, list):
                    for account_entry in value:
                        add_to_summary(account_entry)

        # for sum_key in sorted(summary_account_entries.keys()):
        #     print(f"{sum_key}: {summary_account_entries[sum_key]}")

        # Copy aggregated data into summary entry:
        for key in sorted(summary_account_entries):
            summary_journal_entry.fields['Account'].append(summary_account_entries[key])
        self.validate_new_journal_entry(summary_journal_entry)

        # Post summary entry to the ledger:
        post = self.ledger.post_summary_entry(self, summary_journal_entry)
        for journal_entry in journal_entries:
            journal_entry._set_posted(post)

    def retrieve_entry(self, post):
        if post.summary_entry:
            pass
        else:
            pass

    def define_fields(self, journal_entry):
        '''
        Data structure for Journal Entries.
        Each transaction is stored as set of the following pairs:

        FIELD_NAME: FIELD_VALUE

         FIELD_NAME is always a string,

         FIELD_VALUE can contain the following kind of variables:

          - 'AccountRecord' object means: 'this is the place for single account entry'
            For example:
                        'Cash': AccountRecord(None, 0, AccountSide.DEBIT, transaction)
                        'Sale': AccountRecord(SaleAcount, 0, AccountSide.CREDIT, transaction)
                        'Sale Tax': AccountRecord(None, 0, AccountSide.CREDIT, transaction)

          - 'list' [] means: 'this is the place for multiple account records'
            For example
                        'Account': []

          - 'None' value means: 'this is info field'. 
            For example:
                        'Info': None
            Note that fields "data", "description" and "reference" are 
            already defined in JournalEntry class and defining these is not needed

        '''
        return {
            'Account':      []      # debit/credit account records
        }

    def validate_new_journal_entry(self, journal_entry):
        if journal_entry.journal and self != journal_entry.journal:
            raise ValueError('the specified entry is binded to another journal')
        if journal_entry in self.journal_entries:
            raise ValueError('the specified entry already exist in the journal')
        if not journal_entry.date:
            raise ValueError('the specified entry has empty date')
        for field in journal_entry.fields.values():
            if isinstance(field, AccountRecord):
                if not field.journal_entry:
                    raise ValueError('account record has no journal entry')
                if field.journal_entry != journal_entry:
                    raise ValueError('account record has invalid journal entry')
    
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
        self.date = None
        self.description = None
        self.reference = None
        self.post = None
        if self.journal:
            self.fields = self.journal.define_fields(self)
        else:
            self.fields = {}

    def is_balanced(self):
        return self.get_debit() == self.get_credit()

    def add_info(self, field_tag: str, value):
        ''' Fill the Journal's Entry "info field" with the new value '''
        if field_tag not in self.fields.keys():
            raise RuntimeError(f'usage of unexpected (unknown?) field \'{field_tag}\'')
        self.fields[field_tag] = value

    def debit(self, field_tag: str, amount: int, account):
        ''' Fill the Journal's Entry with the new debit Record '''
        # self.flow(field_tag, account, amount, AccountSide.DEBIT)
        self.add_record(field_tag, amount, account=account, side=AccountSide.DEBIT)

    def credit(self, field_tag: str, amount: int, account):
        ''' Fill the Journal's Entry with the new credit Record '''
        # self.flow(field_tag, account, amount, AccountSide.CREDIT)
        self.add_record(field_tag, amount, account=account, side=AccountSide.CREDIT)

    def flow(self, field_tag: str, amount: int, account, side: AccountSide):
        ''' Add new Account Record '''
        if field_tag not in self.fields.keys():
            raise RuntimeError(f'unknown field \'{field_tag}\'')
        if side != AccountSide.DEBIT and side != AccountSide.CREDIT:
            raise ValueError('account side must be DEBIT or CREDIT')
        if isinstance(self.fields[field_tag], AccountRecord):
            if self.fields[field_tag].side != side:
                raise ValueError(f'Journal field \'{field_tag}\' expects {self.fields[field_tag].side} operation.')
            self.fields[field_tag] = AccountRecord(account, amount, side, self, None)
        elif isinstance(self.fields[field_tag], list):
            self.fields[field_tag].append(AccountRecord(account, amount, side, self, None))
        else:
            raise RuntimeError(f'Journal field "{field_tag}" is not dedicated for debit/credit entries.')

    def add_record(self, field_tag: str, amount: int, /, account = None, side: AccountSide = None):
        ''' 
        Fill the Journal's Entry "account field" with the new Record.

        If no 'account' or no 'side' argument provided then method tries get these 
        values from the Journal Entry field definition.
        '''
        if field_tag not in self.fields.keys():
            raise RuntimeError(f'unknown field "{field_tag}"')

        if isinstance(self.fields[field_tag], AccountRecord):
            if self.fields[field_tag].account and not account:
                account = self.fields[field_tag].account
            if self.fields[field_tag].side and not side:
                side = self.fields[field_tag].side
        elif isinstance(self.fields[field_tag], list):
            if not account or not side:
                raise ValueError(f'field "{field_tag}" intended for a list of account records expects both \'account\' and \'side\' arguments provided')
        else:
            raise RuntimeError(f'Journal field "{field_tag}" is not dedicated for Account Records.')

        if not account:
            raise ValueError(f'the Account cannot be determined (no \'account\' argument provided and no account defined for the field "{field_tag}")')
        if not side:
            raise ValueError(f'the Account Side cannot be determined (no \'side\' argument provided and no side defined for the field "{field_tag}")')

        if isinstance(self.fields[field_tag], AccountRecord):
            self.fields[field_tag] = AccountRecord(account, amount, side, self, None)
        elif isinstance(self.fields[field_tag], list):
            self.fields[field_tag].append(AccountRecord(account, amount, side, self, None))

    def get_debit(self):
        return self._get_side_sum(AccountSide.DEBIT)

    def get_credit(self):
        return self._get_side_sum(AccountSide.CREDIT)

    def _get_side_sum(self, side):
        result = 0
        for field in self.fields.values():
            if isinstance(field, AccountRecord):
                if field.side != AccountSide.DEBIT and field.side != AccountSide.CREDIT:
                    raise ValueError('account side must be DEBIT or CREDIT')
                if field.amount and not field.account:
                    raise ValueError('entry with no account has non zero amount')
                if field.side == side:
                    result += field.amount
            elif isinstance(field, list):
                for account_entry in field:
                    if account_entry.side != AccountSide.DEBIT and account_entry.side != AccountSide.CREDIT:
                        raise ValueError('account side must be DEBIT or CREDIT')
                    if account_entry.amount and not account_entry.account:
                        raise ValueError('entry with no account has non zero amount')
                    if account_entry.side == side:
                        result += account_entry.amount
        return result

    def _get_currency(self):
        for field in self.fields.values():
            if isinstance(field, AccountRecord):
                return field.account.currency
            elif isinstance(field, list):
                for account_entry in field:
                    return account_entry.account.currency

    def post_this(self):
        ''' Post this journal entry to the ledger (single post - one-to-one) '''
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
            if isinstance(value, AccountRecord):
                if value.amount and value.account:
                        self.fields[name] = AccountRecord(
                            value.account,
                            value.amount,
                            value.side,
                            value.journal_entry,
                            post
                            )
            elif isinstance(value, list):
                for idx, account_entry in enumerate(value):
                    if account_entry.amount and account_entry.account:
                        value[idx] = AccountRecord(
                            account_entry.account,
                            account_entry.amount,
                            account_entry.side,
                            account_entry.journal_entry,
                            post
                            )
        self.post = post

    def __str__(self):
        currency = self._get_currency()
        post_info = 'not posted'
        if self.post:
            if self.post.summary_entry:
                post_info = 'posted aggregated entries'
            else:
                post_info = 'posted single entry'
        return ' '.join([
            f"{str(self.date)}, {self.description}, {currency.raw2amount(self.get_debit())}",
            f"({self.journal.tag}, {post_info})"
        ])
