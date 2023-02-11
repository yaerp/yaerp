import locale
from yaerp.accounting.ledger import Ledger
from yaerp.accounting.journal import Journal
from yaerp.accounting.account import Account
from yaerp.accounting.transaction import Transaction
from yaerp.accounting.reports.t_account import T_account, render_entries, render_entry, render_layout
from yaerp.model.money import Money as M
from yaerp.model.currency import Currency as C
from yaerp.report.typesetting.columns import simultaneous_column_generator as typeset

def run():
    currency = C('PLN', '985', 100, "Polish Złoty", 'zł', 'gr')
    print(currency.amount2raw(100.78))
    print(currency.raw2str(10078))
    # money = M(12300, c)
    # print(money)

    # locale.setlocale(locale.LC_ALL, 'pl')
    # print(locale.currency(123235534.7, international=True, grouping=True))

    # c = C('USD', '840', 100, 'United States dollar', '$', '\u00A2')
    # money = M(12300, c)
    # print(money)

    ledger = Ledger('GL')
    journal = Journal('GJ', ledger)
    account100 = Account('100', ledger, currency, name='Cash')
    account200 = Account('200', ledger, currency, name='Sales')
    account300 = Account('300', ledger, currency, name='Sales Tax')
    account400 = Account('400', ledger, currency, name='Purchases')
    account500 = Account('500', ledger, currency, name='Cost')
    account600 = Account('600', ledger, currency, name='Assets')
    account700 = Account('700', ledger, currency, name='Liabilities')


    entry1 = Transaction(journal=journal)
    entry1.info('date', '2022-12-30')
    entry1.debit('cash', account100, currency.amount2raw(1897.20))
    entry1.credit('sale', account200, currency.amount2raw(1897.20))
    entry1.commit()

    entry2 = Transaction(journal=journal)
    entry2.info('date', '2023-01-04')
    entry2.credit('cash', account100, 3553300)
    entry2.debit('purchase', account200, 3553300)
    entry2.commit()

    entry3 = Transaction(journal=journal)
    entry3.info('date', '2023-01-03')
    entry3.debit('cash paynment', account100, 25000)
    entry3.credit('sale', account200, 21000)
    entry3.credit('tax', account300, 4000)
    entry3.commit()

    entry4 = Transaction(journal=journal)
    entry4.info('date', '2023-01-03')
    entry4.credit('cash widrawn', account100, 58)
    entry4.debit('purchases', account400, 58)
    entry4.commit()

    entry5 = Transaction(journal=journal)
    entry5.info('date', '2023-01-03')
    entry5.debit('cost', account500, 58)
    entry5.credit('purchase', account400, 58)
    entry5.commit()

    print(account100.get_debit(predicate=lambda post: '2022' in post.transaction.fields['date']))
    print(account100.get_debit(predicate=lambda post: '2023' in post.transaction.fields['date']))

    print(account200.get_credit(predicate=lambda post: '2022' in post.transaction.fields['date']))
    print(account200.get_credit(predicate=lambda post: '2023' in post.transaction.fields['date']))

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

    canvas = render_entries([entry1, entry2, entry3, entry4, entry5], layout=render_layout['sweet'], col=3, col_len=37)
    
    for field in entry1.fields.values():
        print(field)

if __name__ == "__main__":
    run()
