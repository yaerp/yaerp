import unittest

from yaerp.accounting.account import Account
from yaerp.accounting.ledger import Ledger

class TestAccount(unittest.TestCase):

    def test_init_without_ledger(self):
        account = Account('100', None)
        self.assertEqual(account.tag, '100')
        self.assertEqual(account.get_debit(), 0)
        self.assertEqual(account.get_credit(), 0)
        self.assertEqual(account.ledger, None)

    def test_init_with_ledger(self):
        from yaerp.accounting.ledger import Ledger
        ledger = Ledger('GL')
        account = Account('200', ledger)
        self.assertEqual(account.tag, '200')
        self.assertEqual(account.get_debit(), 0)
        self.assertEqual(account.get_credit(), 0)
        self.assertEqual(account.ledger, ledger)

    def test_register_account_in_ledger(self):
        ledger = Ledger('GL')
        account1 = Account('test account 1', None)
        self.assertEqual(len(ledger.accounts.values()), 0)
        ledger.register_account(account1)
        self.assertEqual(len(ledger.accounts.values()), 1)        
        self.assertEqual(ledger.accounts['test account 1'], account1)
        self.assertEqual(account1.ledger, ledger)
        ledger.register_account(account1)
        self.assertEqual(len(ledger.accounts.values()), 1)        
        account2 = Account('test account 2', None)
        ledger.register_account(account2)
        self.assertEqual(len(ledger.accounts), 2)        
        self.assertEqual(ledger.accounts['test account 2'], account2)

if __name__ == '__main__':
    unittest.main()
