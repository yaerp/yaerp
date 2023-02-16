import copy
# from yaerp.accounting.ledger import Ledger
from yaerp.accounting.entry import Entry
from yaerp.accounting.transaction import Transaction

class Journal:
    '''
    * Journal
    Journal is a book that contain a sequence of business transactions.

      Business transaction, also known as 'journal entry', contains the data
    significant to a single event involving the movement/exchange of value
    (such as money, goods, services). These events must be measurable
    in monetary value so the company can record them for accounting purposes.

    Example of business transactions:
     - sale,
     - purchase,
     - adjustment,
     - depreciation,
     - opening and closing entries.

      Range of data required to store in each transaction is determined by Journal.
    Look into define_fields() method to find out the actual format of transaction.
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
        self.transactions = []

    def commit_separate(self, transactions):
        ''' Post transaction entries to the ledger.
            Each transaction involves new ledger entries. '''
        if not hasattr(transactions, '__iter__'):
            self.validate_new_transaction(transactions)
            self.ledger.commit_transaction(self, transactions)
            return
        for transaction in transactions:
            self.validate_new_transaction(transaction)
        for transaction in transactions:
            self.ledger.commit_transaction(self, transaction)

    def commit_cumulate(self, transactions, summary_info):
        ''' Post transactions entries to the ledger.
            Summary of all transactions involves new ledger entries. '''
        if not hasattr(transactions, '__iter__'):
            ValueError('\'transactions\' parameter must be iterable')

        for transaction in transactions:
            self.validate_new_transaction(transaction)

        summary_entries = {}
        for transaction in transactions:
            for name, value in transaction.fields.items():
                if isinstance(value, Entry):
                    key = f'{value.side}@{value.account.tag}'
                    if key in summary_entries:
                        summary_entries[key] += value
                    else:
                        summary_entries[key] = Entry(value.account, value.amount,
                                                     value.side,
                                                     summary_info)

                if isinstance(value, list):
                    NotImplemented('not yet')

        for sum_key in sorted(summary_entries.keys()):
            print(f"{sum_key}: {summary_entries[sum_key]}")

        summary_transaction = copy.deepcopy(summary_info)
        for key, value in summary_info.fields.items():
            if isinstance(value, (Entry, list)):
                del summary_transaction.fields[key]

        summary_transaction.fields['Account'] = []
        for key in sorted(summary_entries):
            summary_transaction.fields['Account'].append(summary_entries[key])

        self.validate_new_transaction(summary_transaction)
        self.ledger.commit_transaction(self, summary_transaction)

    def define_fields(self, transaction):
        '''
        Define the data structure for transactions stored in this Journal.
        Each transaction is stored as set of the following pairs:

        FIELD_NAME: FIELD_VALUE

         FIELD_NAME is always a string,

         FIELD_VALUE can contain the following variables:
          - None value means: 'this is info field'
                for example
                            'Date': None
                            'Description': None
          - Entry object means: 'this is the place for single entry' (fixed side)
                for example
                            'Cash': Entry(None, 0, 0, transaction)
                            'Sale': Entry(None, 0, 1, transaction)
                            'Sale Tax': Entry(None, 0, 1, transaction)
          - [] (list) means: 'this is the place for multiple entries' (free side)
                for example
                            'Account': []
        '''
        return {
            'Date': None,                               # info
            'Description': None,                        # info
            'Debit': Entry(None, 0, 0, transaction),    # debit entry
            'Credit': Entry(None, 0, 1, transaction)    # credit entry
        }

    def validate_new_transaction(self, transaction):
        if transaction in self.transactions:
            raise ValueError('the specified transaction already exist in the journal')  
        for field in transaction.fields.values():
            if isinstance(field, Entry):
                if not field.identifier:
                    raise ValueError('entry has no parent identifier')
                if field.identifier != transaction:
                    raise ValueError('entry has invalid parent identifier')
    
    def __str__(self) -> str:
        return self.tag
