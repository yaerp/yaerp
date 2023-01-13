import unittest

from yaerp.accounting.account import Account

class TestAccount(unittest.TestCase):

    def test_init_without_ledger(self):
        account = Account('100', None)
        self.assertEqual(account.tag, '100')
        self.assertEqual(account.debit, 0)
        self.assertEqual(account.credit, 0)
        self.assertEqual(account.ledger, None)

    def test_init_with_ledger(self):
        from yaerp.accounting.ledger import Ledger
        ledger = Ledger('GL')
        account = Account('200', ledger)
        self.assertEqual(account.tag, '200')
        self.assertEqual(account.debit, 0)
        self.assertEqual(account.credit, 0)
        self.assertEqual(account.ledger, ledger)

if __name__ == '__main__':
    unittest.main()
