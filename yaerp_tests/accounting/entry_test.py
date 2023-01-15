import unittest

from yaerp.accounting.entry import Entry
from yaerp.accounting.account import Account

class TestEntry(unittest.TestCase):

    def test_init_blank_entry(self):
        entry = Entry(journal=None)
        self.assertEqual(len(entry.info_fields.values()), 0)
        self.assertEqual(entry.debit_fields, [])
        self.assertEqual(entry.credit_fields, [])

    def test_init_entry(self):
        account1 = Account('test account 1', None)
        account2 = Account('test account 2', None)
        entry = Entry(journal=None)
        entry.field('Title', 'Entry 1')
        entry.debit(account1, 599)
        entry.credit(account1, 599)
        self.assertEqual(entry.info_fields['Title'], 'Entry 1')
        self.assertEqual(entry.debit_fields[0].amount, 599)
        self.assertEqual(entry.credit_fields[0].account, account1)

    def test_is_balanced(self):
        empty_entry = Entry({}, [], [])
        self.assertTrue(empty_entry.is_balanced())
        account1 = Account('test account 1', None)
        account2 = Account('test account 2', None)
        balanced_entry = Entry(journal=None)
        balanced_entry.debit(account1, 599)
        balanced_entry.credit(account2, 500)
        balanced_entry.credit(account2, 99)
        self.assertTrue(balanced_entry.is_balanced())
        not_balanced_entry = Entry({'Title': 'Entry 1'})
        not_balanced_entry.debit(account1, 599)
        not_balanced_entry.credit(account2, 500)
        not_balanced_entry.credit(account2, 99)        
        not_balanced_entry.credit(account2, 1)
        self.assertFalse(not_balanced_entry.is_balanced())


if __name__ == '__main__':
    unittest.main()