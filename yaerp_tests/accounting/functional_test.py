import unittest

from yaerp.accounting import Account, Journal, Ledger, Entry

class TestEntry(unittest.TestCase):

    def setUp(self) -> None:
        self.ledger = Ledger('General Ledger')
        self.journal = Journal('General Journal', ledger=self.ledger)
        self.account100 = Account(tag='100 sales', ledger=self.ledger)
        self.account200 = Account(tag='200 income', ledger=self.ledger)
        self.account300 = Account(tag='300 tax', ledger=self.ledger)

    def test_ledger(self):
        entry = Entry(self.journal)
        entry.field('date', '2023-01-03')
        entry.field('description', 'retail sale')
        entry.debit(self.account100, 200)
        entry.credit(self.account200, 180)
        entry.credit(self.account300, 20)
        self.journal.commit_entry(entry)

        self.assertEqual(self.account100.get_debit(), 200)
        self.assertEqual(self.account100.get_credit(), 0)
        self.assertEqual(self.account200.get_debit(), 0)
        self.assertEqual(self.account200.get_credit(), 180)
        self.assertEqual(self.account300.get_debit(), 0)
        self.assertEqual(self.account300.get_credit(), 20)

        self.assertEqual(self.ledger.posts[0].entry, entry)
        self.assertEqual(self.ledger.posts[0].entry.journal, self.journal)
        self.assertEqual(self.ledger.posts[0].account, self.account100)
        self.assertEqual(self.ledger.posts[1].account, self.account200)
        self.assertEqual(self.ledger.posts[2].account, self.account300)
