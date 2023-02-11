import unittest
from yaerp.accounting.account import Account
from yaerp.accounting.transaction import Transaction
from yaerp.accounting.journal import Journal
from yaerp.accounting.ledger import Ledger
from yaerp.accounting.entry import Entry

class TestEntry(unittest.TestCase):

    def setUp(self) -> None:
        self.ledger = Ledger('GL')
        self.journal = Journal('test journal', self.ledger)
        self.account = Account('1', self.ledger)

    def test_init_post(self):
        tran = Transaction(None, {}, [], [])
        post = Entry(self.account, 234, 1, tran)
        self.assertEqual(post.account, self.account)
        self.assertEqual(post.amount, 234)
        self.assertEqual(post.side, 1)
        self.assertEqual(post.transaction, tran)

if __name__ == '__main__':
    unittest.main()