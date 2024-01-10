
from accounting_system import AccountingSystem, setup_tiny_accounting_system
from yaerp.accounting.lib import AccountTypes, GeneralJournal, GeneralLedger
from yaerp.accounting.ledger3 import Ledger
from yaerp.accounting.journal3 import Journal
from yaerp.accounting.journal3 import JournalEntry
from yaerp.accounting.account3 import Account
from yaerp.accounting.account3 import AccountSide
from yaerp.accounting.account3 import AccountRecord
from yaerp.accounting.marker import Assets, BalanceSheet, Clearing, Equity, Expenses, IncomeStatement, Liabilities, Revenues
from yaerp.accounting.reports.t_account import T_account, render_journal_entries, render_journal_entries2, render_journal_entry, render_journal_entry2, render_layout
from yaerp.model.money import Money
from yaerp.model.currency import Currency
from yaerp.report.typesetting.columns import simultaneous_column_generator as typeset
from yaerp.tools.secure_token import secure_token
from yaerp.tools.text import justify
from yaerp.tools.sorted_collection import SortedCollection


def run():
    currency = Currency('PLN', '985', 100, "Polish Złoty", 'zł', 'gr')

    ledger = Ledger('GL', 'General Ledger')
    journal = Journal('GJ', 'General Journal', ledger)
    account100 = Account('100', ledger, currency, name='Cash')
    account200 = Account('200', ledger, currency, name='Sales')
    account300 = Account('300', ledger, currency, name='Sales Tax')
    account400 = Account('400', ledger, currency, name='Purchases')
    account500 = Account('500', ledger, currency, name='Cost')
    account600 = Account('600', ledger, currency, name='Assets')
    account700 = Account('700', ledger, currency, name='Liabilities')

    class AdjustingJournal(Journal):
        def initialize_fields(self, transaction):
            return {
                'Account': []
            }

    adjusting_journal = AdjustingJournal('CJ', 'Correction Journal', ledger)

    entry1 = JournalEntry(journal=adjusting_journal)
    entry1.date = '2022-12-30'
    entry1.description = "Correction"
    entry1.debit('Account', currency.amount2raw(1897.20), account100)
    entry1.credit('Account', currency.amount2raw(1897.20), account200)
    entry1.add_record("Account", currency.amount2raw(-897.20), account=account100, side=AccountSide.Dr)
    entry1.add_record("Account", currency.amount2raw(-897.20), account=account200, side=AccountSide.Cr)

    class SaleJournal(Journal):
        def initialize_fields(self, journal_entry):
            return {
                'Cash': AccountRecord(account100, 0, AccountSide.Dr, journal_entry, None),
                'Sale': AccountRecord(account200, 0, AccountSide.Cr, journal_entry, None),
                'Tax': AccountRecord(None, 0, AccountSide.Cr, journal_entry, None)
            }

    sale_journal = SaleJournal('SJ', 'Sale Journal', ledger)

    entry2 = JournalEntry(journal=sale_journal)
    entry2.date = '2023-01-01'
    entry2.description = 'Example of Sales'
    entry2.add_record("Sale", 355330000)
    entry2.add_record("Cash", 355330000)
    entry2.put_into_journal()
    entry2.post_this()

    entry3 = JournalEntry(journal=sale_journal)
    entry3.date = '2023-01-03'
    entry3.description = 'Sold 3 books'
    entry3.debit('Cash', 25000, account100)
    entry3.credit('Sale', 21000, account200)
    entry3.credit('Tax', 4000, account300)
    entry3.post_this()

    entry4 = JournalEntry(journal=journal)
    entry4.date= '2023-01-03'
    entry4.description = 'Purchase of the printer'
    entry4.credit('Account', 158, account100)
    entry4.debit('Account', 158, account400)
    entry4.put_into_journal()
    # entry4.post_this()

    entry5 = JournalEntry(journal=journal)
    entry5.date = '2023-01-04'
    entry5.description = 'Accept the printer as a cost'
    entry5.credit('Account', 258, account500)
    entry5.debit('Account', 258, account400)

    entry6 = JournalEntry(journal=journal)
    entry6.date = '2023-01-05'
    entry6.description = 'Accept the printer as a cost'
    entry6.debit('Account', 258, account500)
    entry6.credit('Account', 258, account400)

    info = JournalEntry(journal=journal)
    journal.post_these([entry5, entry6, entry5, entry5, entry5])

    entry1.post_this()
    
    for je in ledger.journal_entries_gen(not_posted=False):
        print(je)

    for ar in ledger.account_records_gen():
        print(ar)

    print(account200.short_str())

    sec_tok = secure_token(open_number=True)
    print(sec_tok.update("hsdfgjgsf"))
    print(sec_tok.update("hsdfgjgsf"))
    print(secure_token().token())

    print()
    print(account100.currency.toStringForm(account100.get_balance()))
    print(account100.currency.toInternalForm(3554548.42))

if __name__ == "__main__":
    run()
