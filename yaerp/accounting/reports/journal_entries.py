from yaerp.accounting.journal import Journal
from yaerp.accounting.journal_entry import JournalEntry
from yaerp.accounting.account_entry import AccountEntry


def transaction_sheet_header(journal):
    header = journal.define_fields()
    first_row = []
    content_row = []
    third_row = []
    for name in header.keys():
        first_row.append("----")
        content_row.append(f"{name}")
        third_row.append("----")
    return '\n'.join([
        ''.join(first_row),
        ''.join(content_row),
        ''.join(third_row)
    ])

def transaction_sheet_footer(journal):
    header = journal.define_fields()
    # ...
    pass

def transaction_sheet_line(transaction):
    for name, value in transaction.fields.items():
        pass

def transaction_sheet_gen(journal, transaction_predicate=None):
    if not transaction_predicate:
        transaction_predicate = True
    yield transaction_sheet_header(journal)
    for tran in filter(journal.transactions, transaction_predicate):
        yield transaction_sheet_line(tran)
