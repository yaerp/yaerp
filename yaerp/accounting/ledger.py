from .exception import AccountingError


class LedgerError(AccountingError):
    def __init__(self, message):
        super().__init__(message)

class Ledger:

    def __init__(self, tag: str):
        self.tag = tag
        self.posts = [] # main ledger's container 
        self.accounts = {}
        self.journals = {}

    def commit_journal_entry(self, journal, entry):
        self._validate_entry(journal, entry)         
        for dr in entry.debit_fields:
            self._append_post(dr)
        for cr in entry.credit_fields:
            self._append_post(cr)
        journal.accounting_entries.append(entry)
        

    def _validate_entry(self, journal, entry):
        if not self._is_balanced_entry(entry):
            raise LedgerError('validate Entry failed: not balanced Entry')
        for dr in entry.debit_fields:
            self._validate_post(journal, dr)
        for cr in entry.credit_fields:
            self._validate_post(journal, cr)

    def _append_post(self, post):
        self.posts.append(post)
        post.account.append_post(post)

    def _validate_post(self, journal, post):
        if post.account is None:
            raise LedgerError('validate Post - failed: Account None')
        if post.account not in self.accounts.values():
            raise LedgerError('validate Post - failed: unknown Account')
        if post.entry is None:
            raise LedgerError('validate Post - failed: empty parent Entry')
        if post.entry.journal is None:
            raise LedgerError('validate Post - failed: empty parent Journal')           
        if post.entry.journal != journal:
            raise LedgerError('validate Post - failed: Entry is assigned to another Journal')
        if post.entry.journal not in self.journals.values():
            raise LedgerError('validate Post - failed: Journal is assigned to another Ledger') 
        if post in self.posts:
            raise LedgerError('validate Post - failed: Post already added')       

    def _is_balanced_entry(self, entry):
        result_dt, result_ct = 0, 0
        for dr in entry.debit_fields:
            if dr.side != 0:
                raise LedgerError('is balanced Entry - failed: wrong Post in debit container')
            result_dt += dr.amount
        for cr in entry.credit_fields:
            if cr.side != 1:
                raise LedgerError('is balance Entry - failed: wrong Post in debit container')
            result_ct += cr.amount
        return result_dt == result_ct

    def register_account(self, account):
        if account is None:
            raise LedgerError('register Account - failed: Account is None')  
        if account.ledger != self and account.ledger is Ledger and account in account.ledger.accounts.values():
            raise LedgerError('register Account - failed: Account is already registered to another Ledger')         
        self.accounts[account.tag] = account
        account.ledger = self
 
    def register_journal(self, journal):
        if journal is None:
            raise LedgerError('register Journal - failed: Journal is None')  
        if journal.ledger != self and journal.ledger is Ledger and journal in journal.ledger.journals.values():
            raise LedgerError('register Journal - failed: Journal is already registered to another Ledger') 
        self.journals[journal.tag] = journal
        journal.ledger = self
