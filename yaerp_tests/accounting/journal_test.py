import unittest

from yaerp.accounting.journal_entry import JournalEntry
from yaerp.accounting.ledger import Ledger
from yaerp.accounting.journal import Journal, JournalError
from yaerp.accounting.account import Account

class TestJournal(unittest.TestCase):

    def setUp(self) -> None:
        self.ledger = Ledger('GL')
        self.journal = Journal('test journal', self.ledger)
        self.account1 = Account('1', self.ledger)
        self.account2 = Account('2', self.ledger)

    def test_init_journal(self):
        empty_journal = Journal('TEST JOURNAL', None)
        self.assertEqual(len(empty_journal.transactions), 0)
        self.assertEqual(empty_journal.tag, 'TEST JOURNAL')
        self.assertIsNone(empty_journal.ledger)
        self.assertFalse(empty_journal in self.ledger.journals.values())
        self.ledger.register_journal(empty_journal)
        self.assertTrue(empty_journal in self.ledger.journals.values())     
        self.assertEqual(empty_journal.ledger, self.ledger)           
        empty_journal = Journal('TEST JOURNAL', self.ledger)
        self.assertIsInstance(empty_journal.ledger, Ledger)

    def test_commit_transaction(self):
        tran = JournalEntry(self.journal, {'Title': 'Entry 1'}, [], [])
        tran.debit(self.account1, 599)
        tran.credit(self.account2, 599)
        self.assertEqual(len(self.journal.transactions), 0)
        self.journal.commit_transaction(tran)
        self.assertEqual(len(self.journal.transactions), 1)
        try:
            self.journal.commit_transaction(tran)
            self.fail()
        except JournalError:
            self.assertEqual(len(self.journal.transactions), 1)
        same_records_tran = JournalEntry({'Title': 'Entry 2'}, tran.debit_fields, tran.credit_fields)
        try:
            self.journal.commit_transaction(same_records_tran)
            self.fail()
        except JournalError:
            self.assertEqual(len(self.journal.transactions), 1)
        new_tran = JournalEntry(self.journal, {'Title': 'Entry 3'}, [], [])
        new_tran.debit(self.account2, 12)
        new_tran.credit(self.account1, 12)
        self.journal.commit_transaction(new_tran)
        self.assertEqual(len(self.journal.transactions), 2)

    def test_register_journal_in_ledger(self):
        ledger = Ledger('GL')
        self.assertEqual(len(ledger.journals.values()), 0)
        journal1 = Journal('test journal 1', None)
        ledger.register_journal(journal1)
        self.assertEqual(len(ledger.journals.values()), 1)        
        self.assertEqual(ledger.journals['test journal 1'], journal1)
        self.ledger.register_journal(journal1)
        self.assertEqual(len(ledger.journals.values()), 1)
        journal2 = Journal('test journal 2', None)
        ledger.register_journal(journal2)
        self.assertEqual(len(ledger.journals), 2)        
        self.assertEqual(ledger.journals['test journal 2'], journal2)



    # def test_bind_and_subscribe_account2(self):
    #     self.assertEqual(len(self.ledger.accounts.values()), 0)
    #     account1 = Account('test account 1', None)
    #     account2 = Account('test account 2', None)
    #     self.ledger._append_post(Post(account1, 123, 0, None))
    #     self.ledger._append_post(cr(account2, 456, 1, None))
    #     self.ledger._append_post(dr(account2, 15, 0, None))
    #     self.ledger._append_post(dr(account2, 15, 0, None))
    #     self.assertEqual(account1.debit, 0)
    #     self.assertEqual(account1.credit, 0)   
    #     self.assertEqual(account2.debit, 0)
    #     self.assertEqual(account2.credit, 0)        
    #     self.ledger.register_account(account1)
    #     self.assertEqual(account1.debit, 123)
    #     self.assertEqual(account1.credit, 0)   
    #     self.assertEqual(account2.debit, 0)
    #     self.assertEqual(account2.credit, 0)  
    #     self.ledger.register_account(account2)     
    #     self.assertEqual(account1.debit, 123)
    #     self.assertEqual(account1.credit, 0)   
    #     self.assertEqual(account2.debit, 30)
    #     self.assertEqual(account2.credit, 456)


if __name__ == '__main__':
    unittest.main()