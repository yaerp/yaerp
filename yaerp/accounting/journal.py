import copy
# from yaerp.accounting.ledger import Ledger
from yaerp.accounting.account_entry import AccountEntry
from yaerp.accounting.journal_entry import JournalEntry
from yaerp.accounting.post import Post

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

    def post_separate(self, journal_entries):
        ''' Post journal entries to the ledger.
            Each journal entry involves new account entries in the ledger. '''
        if not hasattr(journal_entries, '__iter__'):
            self.validate_new_journal_entry(journal_entries)
            self.ledger.post_journal_entry(self, journal_entries)
            return
        for journal_entry in journal_entries:
            self.validate_new_journal_entry(journal_entry)
        for journal_entry in journal_entries:
            self.ledger.post_journal_entry(self, journal_entry)

    def post_cumulate(self, journal_entries, summary_info):
        ''' Post journal entries to the ledger.
            Summary of all journal entries involves new account entries in the ledger. '''
        if not hasattr(journal_entries, '__iter__'):
            ValueError('\'journal_entries\' must be iterable')

        for journal_entry in journal_entries:
            self.validate_new_journal_entry(journal_entry)

        summary_account_entries = {}
        for journal_entry in journal_entries:
            for name, value in journal_entry.fields.items():
                if isinstance(value, AccountEntry):
                    key = f'{value.side}@{value.account.tag}'
                    if key in summary_account_entries:
                        summary_account_entries[key] += value
                    else:
                        summary_account_entries[key] = AccountEntry(
                            value.account,
                            value.amount,
                            value.side,
                            summary_info,
                            None)

                if isinstance(value, list):
                    NotImplemented('not yet')

        # for sum_key in sorted(summary_account_entries.keys()):
        #     print(f"{sum_key}: {summary_account_entries[sum_key]}")

        summary_journal_entry = copy.deepcopy(summary_info)
        for key, value in summary_info.fields.items():
            if isinstance(value, (AccountEntry, list)):
                del summary_journal_entry.fields[key]

        summary_journal_entry.fields['Account'] = []
        for key in sorted(summary_account_entries):
            summary_journal_entry.fields['Account'].append(summary_account_entries[key])

        self.validate_new_journal_entry(summary_journal_entry)
        post = self.ledger.post_summary_entry(self, summary_journal_entry)
        for journal_entry in journal_entries:
            journal_entry.post = post


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

# class GeneralJournal(Journal):
#     def define_fields(self, journal_entry):
#         return {
#             'Date':         None,   # info
#             'Description':  None,   # info
#             'Account':      []      # debit/credit account entries
#         }