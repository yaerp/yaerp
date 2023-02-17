import unittest

from yaerp.accounting.journal_entry import JournalEntry
from yaerp.accounting.ledger import Ledger
from yaerp.accounting.journal import Journal
from yaerp.accounting.account import Account
from yaerp.accounting.account_entry import AccountEntry

class TestLedger(unittest.TestCase):

    def setUp(self) -> None:
        self.ledger = Ledger('test ledger')

    def test_init_ledger(self):
        ledger = Ledger('TEST LEDGER')
        self.assertEqual(len(ledger.journals), 0)
        self.assertEqual(len(ledger.accounts), 0)
        self.assertEqual(len(ledger.posts), 0)
        self.assertEqual(ledger.tag, 'TEST LEDGER')

    # def test_append_post(self):
    #     account1 = Account('account 1', None)
    #     account2 = Account('account 2', None)
    #     self.assertEqual(len(self.ledger.posts), 0)
    #     post1 = Post(account1, 567, 0, None)
    #     self.ledger.__append_post(post1)
    #     self.assertEqual(len(self.ledger.posts), 1)        
    #     self.assertEqual(self.ledger.posts[0], post1)
    #     post2 = Post(account2, 890, 1, None)
    #     self.ledger.__append_post(post2)
    #     self.assertEqual(len(self.ledger.posts), 2)        
    #     self.assertEqual(self.ledger.posts[1], post2)

    def test_register_journal(self):
        self.assertEqual(len(self.ledger.journals.values()), 0)
        journal1 = Journal('test journal 1', None)
        self.ledger.register_journal(journal1)
        self.assertEqual(len(self.ledger.journals.values()), 1)        
        self.assertEqual(self.ledger.journals['test journal 1'], journal1)
        self.ledger.register_journal(journal1)
        self.assertEqual(len(self.ledger.journals.values()), 1)
        journal2 = Journal('test journal 2', None)
        self.ledger.register_journal(journal2)
        self.assertEqual(len(self.ledger.journals), 2)        
        self.assertEqual(self.ledger.journals['test journal 2'], journal2)

    def test_register_account(self):
        self.assertEqual(len(self.ledger.accounts.values()), 0)
        account1 = Account('test account 1', None)
        self.ledger.register_account(account1)
        self.assertEqual(len(self.ledger.accounts.values()), 1)        
        self.assertEqual(self.ledger.accounts['test account 1'], account1)
        self.ledger.register_account(account1)
        self.assertEqual(len(self.ledger.accounts.values()), 1)        
        account2 = Account('test account 2', None)
        self.ledger.register_account(account2)
        self.assertEqual(len(self.ledger.accounts), 2)        
        self.assertEqual(self.ledger.accounts['test account 2'], account2)


if __name__ == '__main__':
    unittest.main()