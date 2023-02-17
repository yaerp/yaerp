import unittest

from yaerp.accounting.journal_entry import JournalEntry
from yaerp.accounting.account import Account

class TestTransaction(unittest.TestCase):

    def test_init_blank_tran(self):
        tran = JournalEntry(journal=None)
        self.assertEqual(len(tran.info_fields.values()), 0)
        self.assertEqual(tran.debit_fields, [])
        self.assertEqual(tran.credit_fields, [])

    def test_init_tran(self):
        account1 = Account('test account 1', None)
        account2 = Account('test account 2', None)
        tran = JournalEntry(journal=None)
        tran.info('Title', 'Entry 1')
        tran.debit(account1, 599)
        tran.credit(account1, 599)
        self.assertEqual(tran.info_fields['Title'], 'Entry 1')
        self.assertEqual(tran.debit_fields[0].amount, 599)
        self.assertEqual(tran.credit_fields[0].account, account1)

    def test_is_balanced(self):
        empty_tran = JournalEntry({}, [], [])
        self.assertTrue(empty_tran.is_balanced())
        account1 = Account('test account 1', None)
        account2 = Account('test account 2', None)
        balanced_tran = JournalEntry(journal=None)
        balanced_tran.debit(account1, 599)
        balanced_tran.credit(account2, 500)
        balanced_tran.credit(account2, 99)
        self.assertTrue(balanced_tran.is_balanced())
        not_balanced_tran = JournalEntry({'Title': 'Entry 1'})
        not_balanced_tran.debit(account1, 599)
        not_balanced_tran.credit(account2, 500)
        not_balanced_tran.credit(account2, 99)        
        not_balanced_tran.credit(account2, 1)
        self.assertFalse(not_balanced_tran.is_balanced())


if __name__ == '__main__':
    unittest.main()