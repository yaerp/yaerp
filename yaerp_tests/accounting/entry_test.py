import unittest
from yaerp.accounting.account import Account
from yaerp.accounting.journal_entry import JournalEntry
from yaerp.accounting.journal import Journal
from yaerp.accounting.ledger import Ledger
from yaerp.accounting.account_entry import AccountEntry

class TestEntry(unittest.TestCase):

    def setUp(self) -> None:
        self.ledger = Ledger('GL')
        self.journal = Journal('test journal', self.ledger)
        self.account = Account('1', self.ledger)

    def test_init_post(self):
        tran = JournalEntry(None, {}, [], [])
        post = AccountEntry(self.account, 234, 1, tran)
        self.assertEqual(post.account, self.account)
        self.assertEqual(post.amount, 234)
        self.assertEqual(post.side, 1)
        self.assertEqual(post.post, tran)

if __name__ == '__main__':
    unittest.main()