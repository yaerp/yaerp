import unittest

from yaerp.accounting.entry import Entry
from yaerp.accounting.ledger import Ledger
from yaerp.accounting.journal import Journal
from yaerp.accounting.account import Account
from yaerp.accounting.post import cr, dr

class TestJournal(unittest.TestCase):

    def setUp(self) -> None:
        self.ledger = Ledger('GL')
        self.journal = Journal('test journal', self.ledger)
        self.account1 = Account('1', self.ledger)
        self.account2 = Account('2', self.ledger)

    def test_init_journal(self):
        empty_journal = Journal('TEST JOURNAL', None)
        self.assertEqual(len(empty_journal.accounting_entries), 0)
        self.assertEqual(empty_journal.tag, 'TEST JOURNAL')
        self.assertIsNone(empty_journal.ledger)
        empty_journal = Journal('TEST JOURNAL', self.ledger)
        self.assertIsInstance(empty_journal.ledger, Ledger)

    def test_add_entry(self):
        debit_records1 = [dr(self.account1, 599, self.journal)]      
        credit_records1 = [cr(self.account2, 500, self.journal), cr(self.account2, 99, self.journal)]
        entry = Entry({'Title': 'Entry 1'}, debit_records1, credit_records1)
        self.assertEqual(len(self.journal.accounting_entries), 0)
        self.journal.commit_entry(entry)
        self.assertEqual(len(self.journal.accounting_entries), 1)
        try:
            self.journal.commit_entry(entry)
            self.fail()
        except RuntimeError:
            self.assertEqual(len(self.journal.accounting_entries), 1)
        same_records_entry = Entry({'Title': 'Entry 2'}, debit_records1, credit_records1)
        try:
            self.journal.commit_entry(same_records_entry)
            self.fail()
        except RuntimeError:
            self.assertEqual(len(self.journal.accounting_entries), 1)
        new_debit_records1 = [dr(self.account2, 12, self.journal)]      
        new_credit_records1 = [cr(self.account1, 12, self.journal)]
        new_entry = Entry({'Title': 'Entry 3'}, new_debit_records1, new_credit_records1)
        self.journal.commit_entry(new_entry)
        self.assertEqual(len(self.journal.accounting_entries), 2)

    def test_register_journal(self):
        self.assertEqual(len(self.ledger.journals.values()), 0)
        journal1 = Journal('test journal 1', None)
        self.ledger.register_journal(journal1)
        self.assertEqual(len(self.ledger.journals.values()), 1)        
        self.assertEqual(self.ledger.journals['test journal 1'], journal1)
        try:
            self.ledger.register_journal(journal1)
            self.fail()
        except RuntimeError:
            self.assertEqual(len(self.ledger.journals.values()), 1)
        journal2 = Journal('test journal 2', None)
        self.ledger.register_journal(journal2)
        self.assertEqual(len(self.ledger.journals), 2)        
        self.assertEqual(self.ledger.journals['test journal 2'], journal2)

    def test_bind_and_subscribe_account(self):
        self.assertEqual(len(self.ledger.accounts.values()), 0)
        account1 = Account('test account 1', None)
        self.ledger.bind_and_subscribe_account(account1)
        self.assertEqual(len(self.ledger.accounts.values()), 1)        
        self.assertEqual(self.ledger.accounts['test account 1'], account1)
        try:
            self.ledger.bind_and_subscribe_account(account1)
            self.fail()
        except RuntimeError:
            self.assertEqual(len(self.ledger.accounts.values()), 1)        
        account2 = Account('test account 2', None)
        self.ledger.bind_and_subscribe_account(account2)
        self.assertEqual(len(self.ledger.accounts), 2)        
        self.assertEqual(self.ledger.accounts['test account 2'], account2)

    def test_bind_and_subscribe_account2(self):
        self.assertEqual(len(self.ledger.accounts.values()), 0)
        account1 = Account('test account 1', None)
        account2 = Account('test account 2', None)
        self.ledger._append_post(dr(account1, 123, None))
        self.ledger._append_post(cr(account2, 456, None))
        self.ledger._append_post(dr(account2, 15, None))
        self.ledger._append_post(dr(account2, 15, None))
        self.assertEqual(account1.debit, 0)
        self.assertEqual(account1.credit, 0)   
        self.assertEqual(account2.debit, 0)
        self.assertEqual(account2.credit, 0)        
        self.ledger.bind_and_subscribe_account(account1)
        self.assertEqual(account1.debit, 123)
        self.assertEqual(account1.credit, 0)   
        self.assertEqual(account2.debit, 0)
        self.assertEqual(account2.credit, 0)  
        self.ledger.bind_and_subscribe_account(account2)     
        self.assertEqual(account1.debit, 123)
        self.assertEqual(account1.credit, 0)   
        self.assertEqual(account2.debit, 30)
        self.assertEqual(account2.credit, 456)


if __name__ == '__main__':
    unittest.main()