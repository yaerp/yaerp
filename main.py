from decimal import Decimal
import locale
from yaerp.accounting.ledger import Ledger
from yaerp.accounting.journal import Journal
from yaerp.accounting.journal import JournalEntry
from yaerp.accounting.account import Account
from yaerp.accounting.account import AccountSide
from yaerp.accounting.account import AccountEntry
from yaerp.accounting.reports.t_account import T_account, render_journal_entries, render_journal_entries2, render_journal_entry, render_journal_entry2, render_layout
from yaerp.model.money import Money
from yaerp.model.currency import Currency
from yaerp.report.typesetting.columns import simultaneous_column_generator as typeset

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

    ledger = Ledger('GL')
    journal = Journal('General Journal', ledger)
    account100 = Account('100', ledger, currency, name='Cash')
    account200 = Account('200', ledger, currency, name='Sales')
    account300 = Account('300', ledger, currency, name='Sales Tax')
    account400 = Account('400', ledger, currency, name='Purchases')
    account500 = Account('500', ledger, currency, name='Cost')
    account600 = Account('600', ledger, currency, name='Assets')
    account700 = Account('700', ledger, currency, name='Liabilities')

    class AdjustingJournal(Journal):
        def define_fields(self, transaction):
            return {
                'Date': None,
                'Description': 'Adjusting',
                'Account': []
            }

    adjusting_journal = AdjustingJournal('Adjusting Journal', ledger)

    entry1 = JournalEntry(journal=adjusting_journal)
    entry1.info('Date', '2022-12-30')
    entry1.info('Description', 'Correction')
    entry1.debit('Account', account100, currency.amount2raw(1897.20))
    entry1.credit('Account', account200, currency.amount2raw(1897.20))
    entry1.debit('Account', account100, currency.amount2raw(-897.20))
    entry1.credit('Account', account200, currency.amount2raw(-897.20))
    # entry1.post_to_ledger()

    class SaleJournal(Journal):
        def define_fields(self, transaction):
            return {
                'Date': None,
                'Description': None,
                'Cash': AccountEntry(None, 0, AccountSide.DEBIT, transaction, None),
                'Sale': AccountEntry(None, 0, AccountSide.CREDIT, transaction, None),
                'Tax': AccountEntry(None, 0, AccountSide.CREDIT, transaction, None)
            }

    sale_journal = SaleJournal('Sale Journal', ledger)

    entry2 = JournalEntry(journal=sale_journal)
    entry2.info('Date', '2023-01-04')
    entry2.info('Description', 'Example of Sales')
    entry2.credit('Sale', account200, 3553300)
    # entry2.credit('Tax', account300, 0)
    entry2.debit('Cash', account100, 3553300)
    # entry2.commit()




    # TODO: if Entry above contain specified account this means the account is fixed



    entry3 = JournalEntry(journal=sale_journal)
    entry3.info('Date', '2023-01-03')
    entry3.info('Description', 'Sold 3 books')
    entry3.debit('Cash', account100, 25000)
    entry3.credit('Sale', account200, 21000)
    entry3.credit('Tax', account300, 4000)
    entry3.post_to_ledger()



    entry4 = JournalEntry(journal=journal)
    entry4.info('Date', '2023-01-03')
    entry4.info('Description', 'Purchase of the printer')
    entry4.credit('Account', account100, 158)
    entry4.debit('Account', account400, 158)
    entry4.post_to_ledger()

    entry5 = JournalEntry(journal=journal)
    entry5.info('Date', '2023-01-04')
    entry5.info('Description', 'Accept the printer as a cost')
    entry5.credit('Account', account500, 258)
    entry5.debit('Account', account400, 258)
    # entry5.commit()

    entry6 = JournalEntry(journal=journal)
    entry6.info('Date', '2023-01-05')
    entry6.info('Description', 'Accept the printer as a cost')
    entry6.debit('Account', account500, 258)
    entry6.credit('Account', account400, 258)
    # entry6.commit()

    info = JournalEntry(journal=journal)
    info.info('Date', '2023-01-14')
    info.info('Description', 'Summary entry')
    journal.post_to_ledger([entry5, entry6], info)

    entry1.post_to_ledger()

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


    money = Money(currency, 9)

    # print(money+Money(currency, 20))
    # print(money-Money(currency, 20))
    # print(money*0.98)
    # print(money*50)
    # print(money/2)
    # print(money/3)
    # print(money/4)
    # print(money//2)
    # print(money//3)
    # print(money//4)
    # for m in money.allocate([2,5,7,8,9]):
    #     print(m) 
    # for m in money.allocate(list(reversed([2,5,7,8,9]))):
    #     print(m)

    print(f"entry1 post: {entry1.post}")
    print(f"entry2 post: {entry2.post}")
    print(f"entry3 post: {entry3.post}")
    print(f"entry4 post: {entry4.post}")
    print(f"entry5 post: {entry5.post}")
    print(f"entry6 post: {entry6.post}")

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

if __name__ == "__main__":
    run()
