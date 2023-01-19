import unittest
from yaerp.accounting.account import Account
from yaerp.accounting.entry import Entry
from yaerp.accounting.journal import Journal
from yaerp.accounting.ledger import Ledger
from yaerp.accounting.post import Post

class TestPost(unittest.TestCase):

    def setUp(self) -> None:
        self.ledger = Ledger('GL')
        self.journal = Journal('test journal', self.ledger)
        self.account = Account('1', self.ledger)

    def test_init_post(self):
        entry = Entry(None, {}, [], [])
        post = Post(self.account, 234, 1, entry)
        self.assertEqual(post.account, self.account)
        self.assertEqual(post.amount, 234)
        self.assertEqual(post.side, 1)
        self.assertEqual(post.entry, entry)

if __name__ == '__main__':
    unittest.main()