import unittest

from yaerp.accounting.entry import Entry
from yaerp.accounting.ledger import Ledger
from yaerp.accounting.journal import Journal
from yaerp.accounting.account import Account
from yaerp.accounting.post import cr, dr

class TestEntry(unittest.TestCase):

    def test_init_blank_entry(self):
        entry = Entry({}, [], [])
        self.assertEqual(len(entry.entry_info.values()), 0)
        self.assertEqual(entry.debit_records, [])
        self.assertEqual(entry.credit_records, [])

    def test_init_entry(self):
        account1 = Account('test account 1', None)
        account2 = Account('test account 2', None)
        debit_records = [dr(account1, 599, None)]      
        credit_records = [cr(account2, 599, None)]
        entry = Entry({'Title': 'Entry 1'}, debit_records, credit_records)
        self.assertEqual(entry.entry_info['Title'], 'Entry 1')
        self.assertEqual(entry.debit_records, debit_records)
        self.assertEqual(entry.credit_records, credit_records)

    def test_is_balanced(self):
        account1 = Account('test account 1', None)
        account2 = Account('test account 2', None)
        debit_records1 = [dr(account1, 599, None)]      
        credit_records1 = [cr(account2, 500, None), cr(account2, 99, None)]
        balanced_entry = Entry({'Title': 'Entry 1'}, debit_records1, credit_records1)
        self.assertTrue(balanced_entry.is_balanced())
        debit_records2 = [dr(account1, 599, None)]      
        credit_records2 = [cr(account2, 500, None), cr(account2, 99, None), cr(account2, 1, None)]
        not_balanced_entry = Entry({'Title': 'Entry 1'}, debit_records2, credit_records2)
        self.assertFalse(not_balanced_entry.is_balanced())


if __name__ == '__main__':
    unittest.main()