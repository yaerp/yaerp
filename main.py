from copy import copy, deepcopy
from decimal import Decimal
import locale
import operator
import textwrap
from accounting_system import AccountingSystem, setup_tiny_accounting_system
from yaerp.accounting.lib import AccountTypes, GeneralJournal, GeneralLedger
from yaerp.accounting.ledger import Ledger
from yaerp.accounting.journal import Journal
from yaerp.accounting.journal import JournalEntry
from yaerp.accounting.account import Account
from yaerp.accounting.account import AccountSide
from yaerp.accounting.account import AccountRecord
# from yaerp.accounting.lib import 
from yaerp.accounting.marker import Assets, BalanceSheet, Clearing, Equity, Expenses, IncomeStatement, Liabilities, Revenues
from yaerp.accounting.reports.t_account import T_account, render_journal_entries, render_journal_entries2, render_journal_entry, render_journal_entry2, render_layout
from yaerp.model.money import Money
from yaerp.model.currency import Currency
from yaerp.report.typesetting.columns import simultaneous_column_generator as typeset
from yaerp.tools.text import justify
from yaerp.tools.sorted_collection import SortedCollection

def run():
    currency = Currency('PLN', '985', 100, "Polish Złoty", 'zł', 'gr')
    # print(currency.amount2raw(100.78))
    # print(currency.raw2str(10078))
    # money = M(12300, c)
    # print(money)

    # locale.setlocale(locale.LC_ALL, 'pl')
    # print(locale.currency(123235534.7, international=True, grouping=True))

    # c = C('USD', '840', 100, 'United States dollar', '$', '\u00A2')
    # money = M(12300, c)
    # print(money)

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
    # entry1.info('Date', '2022-12-30')
    # entry1.info('Description', 'Correction')
    entry1.date = '2022-12-30'
    entry1.description = "Correction"
    entry1.debit('Account', currency.amount2raw(1897.20), account100)
    entry1.credit('Account', currency.amount2raw(1897.20), account200)
    # entry1.debit('Account', account100, currency.amount2raw(-897.20))
    # entry1.credit('Account', account200, currency.amount2raw(-897.20))
    entry1.add_record("Account", currency.amount2raw(-897.20), account=account100, side=AccountSide.DEBIT)
    entry1.add_record("Account", currency.amount2raw(-897.20), account=account200, side=AccountSide.CREDIT)
    # entry1.post_to_ledger()

    class SaleJournal(Journal):
        def initialize_fields(self, journal_entry):
            return {
                'Cash': AccountRecord(account100, 0, AccountSide.DEBIT, journal_entry, None),
                'Sale': AccountRecord(account200, 0, AccountSide.CREDIT, journal_entry, None),
                'Tax': AccountRecord(None, 0, AccountSide.CREDIT, journal_entry, None)
            }

    sale_journal = SaleJournal('SJ', 'Sale Journal', ledger)

    entry2 = JournalEntry(journal=sale_journal)
    entry2.date = '2023-01-01'
    entry2.description = 'Example of Sales'
    #entry2.credit('Sale', account200, 3553300)
    entry2.add_record("Sale", 355330000)
    # entry2.debit('Cash', account100, 3553300)
    entry2.add_record("Cash", 355330000)
    entry2.post_this()
 
    # entry2.commit()




    # TODO: if Entry above contain specified account this means the account is fixed



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
    entry4.post_this()

    entry5 = JournalEntry(journal=journal)
    entry5.date = '2023-01-04'
    entry5.description = 'Accept the printer as a cost'
    entry5.credit('Account', 258, account500)
    entry5.debit('Account', 258, account400)
    # entry5.commit()

    entry6 = JournalEntry(journal=journal)
    entry6.date = '2023-01-05'
    entry6.description = 'Accept the printer as a cost'
    entry6.debit('Account', 258, account500)
    entry6.credit('Account', 258, account400)
    # entry6.commit()

    info = JournalEntry(journal=journal)
    # info.date = '2023-01-14'
    # info.description = 'Summary entry'
    journal.post_aggregated([entry5, entry6, entry5, entry5, entry5], '2023-01-14', 'Summary entry')

    entry1.post_this()

    def entries():
        yield entry1
        yield entry2
        yield entry3
        yield entry4
        yield entry5
        yield entry6

    print(render_journal_entries2(entries(), layout=render_layout['terminal-120-3']))


    currency = Currency('PLN', '985', 100, 'Polski Złoty', 'zł', 'gr',
                        fraction_char=',',
                        group_separator_char='\u00A0',
                        separator_positions=(3, 6, 9, 12, 15, 18))
    print(f"1{currency.national_unit_symbol} (1{currency.symbol}) = {currency.ratio_of_subunits_to_unit}{currency.national_subunit_symbol}")
    print(f"1{currency.national_subunit_symbol} = 1/{currency.ratio_of_subunits_to_unit} {currency.national_unit_symbol}") 
    raw_amount1 = currency.amount2raw(4543.5)
    raw_amount2 = currency.amount2raw("434345543.5")
    print(raw_amount1, raw_amount2)
    print(currency.raw2amount(raw_amount1), currency.raw2amount(raw_amount2))
    print()
    currency = Currency('MRU', '929', 5, 'Mauritanian Ouguiya', 'أوقية', 'خمس', 
                        fraction_char='.',
                        group_separator_char=',',
                        separator_positions=(3, 6, 9, 12, 15, 18))
    print(f"{currency.national_unit_symbol} 1 (1{currency.symbol}) = {currency.national_subunit_symbol} {currency.ratio_of_subunits_to_unit}")
    print(f"{currency.national_subunit_symbol} 1 = {currency.national_unit_symbol} 1/{currency.ratio_of_subunits_to_unit}")  
    raw_amount1 = currency.amount2raw(4543.6)
    raw_amount2 = currency.amount2raw("48979543.6")
    print(raw_amount1, raw_amount2)
    print(currency.raw2amount(raw_amount1), currency.raw2amount(raw_amount2), sep="   ")
    print()
    currency = Currency('INR', '356', 100, 'Indian rupee', '\u20B9', 'paise', 
                        fraction_char='.',
                        group_separator_char=',',
                        separator_positions=(3, 5, 7, 9, 11, 13, 15, 17, 19))
    print(f"{currency.national_unit_symbol}1 (1{currency.symbol}) = {currency.ratio_of_subunits_to_unit} {currency.national_subunit_symbol}")
    print(f"1 {currency.national_subunit_symbol} = {currency.national_unit_symbol} 1/{currency.ratio_of_subunits_to_unit}")  

    raw_amount2 = currency.amount2raw("48979543.6")
    print(raw_amount1, raw_amount2)
    print(currency.raw2amount(raw_amount1), currency.raw2amount(raw_amount2), sep="   ")


    money = Money(currency, amount=9)

    print('----------------------------')
    for account_entry in ledger.posts:
        print(account_entry)
    print('----------------------------')

    a = Account("Sale", GeneralLedger(), currency)
    b = Account("Goods", GeneralLedger(), currency)
    j = JournalEntry(GeneralJournal())

    j.date = '2023-01-03'
    j.description = 'Purchase of the printer'
    j.credit("Account", 100, a)
    j.debit("Account", 100, b)
    j.post_this()

    print('----------------------------')
    for account_entry in GeneralLedger().posts:
        print(account_entry)
    print('----------------------------')


    at = AccountTypes()
    at.append_property_value(BalanceSheet.ASSETS, None)
    at.append_property_value(Assets.RECEIVABLES, BalanceSheet.ASSETS)
    at.append_property_value(Assets.TAX_RECEIVABLES, BalanceSheet.ASSETS)
    at.append_property_value(Assets.BANK, BalanceSheet.ASSETS)
    at.append_property_value(Assets.CASH, BalanceSheet.ASSETS)

    at.append_property_value(BalanceSheet.LIABILITIES, None)
    at.append_property_value(Liabilities.PAYABLES, BalanceSheet.LIABILITIES)
    at.append_property_value(Liabilities.TAX_PAYABLES, BalanceSheet.LIABILITIES)

    at.append_property_value(BalanceSheet.EQUITY, None)
    at.append_property_value(Equity.OWNERS_CAPITAL, BalanceSheet.EQUITY)
    at.append_property_value(Equity.DIVIDENDS, BalanceSheet.EQUITY)
    at.append_property_value(Equity.PROFIT, BalanceSheet.EQUITY)
    at.append_property_value(Equity.RETAINED_EARNINGS, BalanceSheet.EQUITY)

    at.append_property_value(IncomeStatement.REVENUES, None)
    at.append_property_value(Revenues.SALES, IncomeStatement.REVENUES)
    at.append_property_value(Revenues.OTHER_INCOME, IncomeStatement.REVENUES)

    at.append_property_value(IncomeStatement.EXPENSES, None)
    at.append_property_value(Expenses.COST_OF_GOODS_SOLD, IncomeStatement.EXPENSES)
    at.append_property_value(Expenses.DEPRECIATION_EXPENSE, IncomeStatement.EXPENSES)
    at.append_property_value(Expenses.OTHER_EXPENSE, IncomeStatement.EXPENSES)

    at.append_property_value(Clearing.ASSET_CLEARING_ACCOUNT, None)
    at.append_property_value(Clearing.LIABILITY_CLEARING_ACCOUNT, None)
    at.append_property_value(Clearing.PURCHASE_CLEARING_ACCOUNT, None)
    at.append_property_value(Clearing.SALES_CLEARING_ACCOUNT, None)

    assert at.has_all_of_values(Assets.CASH, BalanceSheet.ASSETS, Assets.CASH) == True
    assert at.has_any_of_value(Assets.CASH, BalanceSheet.ASSETS)
    assert at.has_type(Assets.CASH, BalanceSheet)
    at.append_property_value(Assets.CASH, Assets.BANK)
    at.remove_type(Assets.CASH, Assets)
    print(at.has_any_of_value(Assets.CASH, IncomeStatement.EXPENSES, IncomeStatement.REVENUES, BalanceSheet.ASSETS))
    # operator.

    #print(account100.get_debit(predicate=lambda post: '2022' in post.transaction.fields['Date']))
    #print(account100.get_debit(predicate=lambda post: '2023' in post.transaction.fields['Date']))

    #print(account200.get_credit(predicate=lambda post: '2022' in post.transaction.fields['Date']))
    #print(account200.get_credit(predicate=lambda post: '2023' in post.transaction.fields['Date']))

    i = 1
    c = 37
    g = 3

    # t_account1 = T_account(account100.tag, 'ABCmnndfs', max_length=c, max_amount_length=8, leading_spaces=0, new_line='', box=T_account.ascii_bold_table_box)
    # t_account2 = T_account(account200.tag, 'XYZYXNMCV', max_length=c, max_amount_length=8, leading_spaces=0, new_line='', box=T_account.unicode_bold_table_box)  

    # def a1_gen():
    #     yield from t_account1.header_generator()
    #     yield t_account1.row('1 kj jkdf hjkdf hgkjd hfk gh', 33335.01, 0)
    #     yield t_account1.split_line()
    #     yield t_account1.row('2 bnm b  xnb vnxbc vnbxc', 256, 0)
    #     yield t_account1.end_line()


    # def a2_gen():
    #     yield from t_account2.header_generator()
    #     yield from t_account2.row_generator('(3 x  xc )', 2442, 0)
    #     yield from t_account2.empty_row_generator()
    #     yield from t_account2.row_generator('(4a xc xc xc vxcv )', 321, 1)
    #     yield from t_account2.row_generator('(4b)', 578, 0)
    #     yield from t_account2.row_generator('(4c xcv xc xc xc xc)', 212, 0)
    #     yield from t_account2.row_generator('4d', 32, 0)
    #     yield from t_account2.row_generator('4e', "7877", 1)
    #     yield from t_account2.row_generator('4f', 8, 1)
    #     yield from t_account2.row_generator('4g', 33, 0)
    #     yield from t_account2.row_generator('4h', 83, 1)
    #     yield from t_account2.row_generator('4i', 921, 0)
    #     yield from t_account2.row_generator('4j', 677, 1)
    #     yield from t_account2.row_generator('4k', 112, 0)
    #     yield from t_account2.row_generator('4l', 122, 1)
    #     yield from t_account2.split_line_generator()
    #     yield from t_account2.row_generator('5', 8976, 0)
    #     yield from t_account2.end_line_generator()

    # def a3_gen():
    #     yield from t_account1.header_generator()
    #     yield from t_account1.row_generator('6', 33335, 0)
    #     yield from t_account1.split_line_generator()
    #     yield from t_account1.row_generator('7', 256, 0)
    #     yield from t_account1.end_line_generator()
    #     yield t_account1.blank_row()
    #     yield t_account1.blank_row()
    #     yield from t_account2.header_generator()
    #     yield from t_account2.row_generator('3', 2442, 0)
    #     yield from t_account2.empty_row_generator()
    #     yield from t_account2.row_generator('4', 321, 1)
    #     yield from t_account2.split_line_generator()
    #     yield from t_account2.row_generator('5', 8976, 0)
    #     yield from t_account2.end_line_generator()


    # print()
    # with open('out.txt', 'w', encoding='utf-8') as f:
    #     for line in typeset([a1_gen(), a2_gen(), a3_gen()], 
    #                         [t_account1.blank_row(), t_account2.blank_row(), t_account1.blank_row()], 
    #                         indent_width=1, gutter_width=4):
            
    #         print(line, end='')
    #         f.write(line)

    # canvas = render_entry(entry1, col=3, col_len=37)
    # print(canvas)

    # canvas = render_entry(entry2, col=3, col_len=37)
    # print(canvas)



    # canvas = render_journal_entries([entry1, entry2, entry3, entry4, entry5, entry6], layout=render_layout['terminal-120-2'])

    acc_sys = AccountingSystem()
    for tag, journal in acc_sys.journals.items():
        print(f"{tag}")

    # print(acc_sys.get_oid(acc_sys))
    # print(acc_sys.get_oid(acc_sys))

    print(32*"=")
    a = setup_tiny_accounting_system()
    je = a.new_journal_entry("SJ")
    je.date = "2023-02-02"
    je.add_record('Cash', 1000)
    je.add_record("Sale", 900)
    je.add_record("Tax", 100)
    je.put_this()
    if je.is_ready_to_post():
        je.post_this()
    # print(a.get_oid(je))
    je = a.new_journal_entry("SJ")
    je.date = "2023-02-03"
    je.add_record('Cash', 30000003)
    je.add_record("Sale", 27000002)
    je.add_record("Tax", 3000001)
    print(je)
    je.post_this()
    je = a.new_journal_entry("PJ")
    je.date = "2023-02-03"
    je.add_record('Cash', 6000000000)
    je.add_record("Payables", 6000000000)
    je.post_this()
    acc = a.get_account("110")
    print(acc.tag, end='/')
    print(acc.guid, end='/')
    print()
    # for key, value in a.
    #     print(f"{key}: {value}")
    print(acc.header_str())
    print(acc)
    print()
    print(acc.records_header_str())
    for ae in acc.posted_records:
        print(ae)
    
    print(str(dir(je)))

    je2 = copy(je)
    print(str(dir(je2)))

    je3 = deepcopy(je)
    print(str(dir(je3)))

#     text = (
# '''wer wrrtert er t e  e ert e erte er te y rfghfgh fgh fg hfh fg hfg hf hgh fg hf hf hfgh fg hf ghfgh f hf  fgh fg hf hfg f'''
# ''''''
#     )

#     for line in fullJustify(text, width=23):
#         print(line)

if __name__ == "__main__":
    run()
