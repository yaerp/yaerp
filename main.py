from yaerp.accounting import Ledger
from yaerp.accounting.journal import Journal
from yaerp.accounting.account import Account
from yaerp.accounting.entry import Entry
from yaerp.accounting.reports.t_account import T_account
from yaerp.reports.typesetting.columns import simultaneous_column_generator as typeset


def run():

    ledger = Ledger('GL')
    journal = Journal('GJ', ledger)
    account100 = Account('100', ledger)
    account200 = Account('200', ledger)

    entry = Entry(journal)
    entry.field('date', '2022-12-30')
    entry.debit(account100, 120)
    entry.credit(account200, 120)
    entry.commit()

    entry = Entry(journal)
    entry.field('date', '2023-01-03')
    entry.debit(account100, 250)
    entry.credit(account200, 250)
    entry.commit()

    entry = Entry(journal, )
    entry.field('date', '2023-01-04')
    entry.debit(account100, 300)
    entry.credit(account200, 300)
    entry.commit()

    print(account100.get_debit(predicate=lambda post: '2022' in post.entry.info_fields['date']))
    print(account100.get_debit(predicate=lambda post: '2023' in post.entry.info_fields['date']))

    print(account200.get_credit(predicate=lambda post: '2022' in post.entry.info_fields['date']))
    print(account200.get_credit(predicate=lambda post: '2023' in post.entry.info_fields['date']))

    i = 1
    c = 37
    g = 3

    t_account1 = T_account(account100.tag, 'ABCmnndfs', max_length=c, max_amount_length=8, leading_spaces=0, new_line='', box=T_account.ascii_bold_table_box)
    t_account2 = T_account(account200.tag, 'XYZYXNMCV', max_length=c, max_amount_length=8, leading_spaces=0, new_line='', box=T_account.unicode_bold_table_box)  

    def a1_gen():
        yield from t_account1.header_generator()
        yield t_account1.row('1', 33335.01, 0)
        yield t_account1.split_line()
        yield t_account1.row('2', 256, 0)
        yield t_account1.end_line()


    def a2_gen():
        yield from t_account2.header_generator()
        yield from t_account2.row_generator('(3)', 2442, 0)
        yield from t_account2.empty_row_generator()
        yield from t_account2.row_generator('(4a)', 321, 1)
        yield from t_account2.row_generator('(4b)', 578, 0)
        yield from t_account2.row_generator('(4c)', 212, 0)
        yield from t_account2.row_generator('4d', 32, 0)
        yield from t_account2.row_generator('4e', 7877, 1)
        yield from t_account2.row_generator('4f', 8, 1)
        yield from t_account2.row_generator('4g', 33, 0)
        yield from t_account2.row_generator('4h', 83, 1)
        yield from t_account2.row_generator('4i', 921, 0)
        yield from t_account2.row_generator('4j', 677, 1)
        yield from t_account2.row_generator('4k', 112, 0)
        yield from t_account2.row_generator('4l', 122, 1)
        yield from t_account2.split_line_generator()
        yield from t_account2.row_generator('5', 8976, 0)
        yield from t_account2.end_line_generator()

    def a3_gen():
        yield from t_account1.header_generator()
        yield from t_account1.row_generator('6', 33335, 0)
        yield from t_account1.split_line_generator()
        yield from t_account1.row_generator('7', 256, 0)
        yield from t_account1.end_line_generator()
        yield t_account1.blank_row()
        yield t_account1.blank_row()
        yield from t_account2.header_generator()
        yield from t_account2.row_generator('3', 2442, 0)
        yield from t_account2.empty_row_generator()
        yield from t_account2.row_generator('4', 321, 1)
        yield from t_account2.split_line_generator()
        yield from t_account2.row_generator('5', 8976, 0)
        yield from t_account2.end_line_generator()


    print()
    with open('out.txt', 'w', encoding='utf-8') as f:
        for line in typeset([a1_gen(), a2_gen(), a3_gen()], 
                                            [t_account1.blank_row(), t_account2.blank_row(), t_account1.blank_row()], 
                                            indent_width=i, gutter_width=g):
            
            print(line, end='')
            f.write(line)

if __name__ == "__main__":
    run()
