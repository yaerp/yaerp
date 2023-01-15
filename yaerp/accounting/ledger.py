class Ledger:

    def __init__(self, tag: str):
        self.tag = tag
        self.posts = [] # main ledger's container 
        self.accounts = {}
        self.journals = {}

    def commit_journal_entry(self, journal, entry):
        self.validate_entry(journal, entry)         
        for dr in entry.debit_fields:
            self._append_post(dr)
        for cr in entry.credit_fields:
            self._append_post(cr)
        journal.accounting_entries.append(entry)
        

    def validate_entry(self, journal, entry):
        if not entry.is_balanced():
            raise RuntimeError('not balanced Entry')
        for dr in entry.debit_fields:
            self._validate_post(journal, dr)
        for cr in entry.credit_fields:
            self._validate_post(journal, cr)

    def _append_post(self, post):
        self.posts.append(post)
        post.account.append_post(post)

    def _validate_post(self, journal, post):
        if post.account is None:
            raise RuntimeError('Account is None')
        if post.account not in self.accounts.values():
            raise RuntimeError('unknown Account')
        if post.entry is None:
            raise RuntimeError('Post has not set parent Entry') 
        if post.entry.journal is None:
            raise RuntimeError('Entry has not set parent Journal')           
        if post.entry.journal != journal:
            raise RuntimeError('incorrect Journal')
        if post.entry.journal not in self.journals.values():
            raise RuntimeError('Entry has unknown Journal') 
        if post in self.posts:
            raise RuntimeError('Post already exist in Ledger')       

    def bind_and_subscribe_account(self, account):
        if account is None:
            raise RuntimeError('Account is None')            
        if account in self.accounts.values():
            raise RuntimeError('Account already added')
        self.accounts[account.tag] = account
        account.ledger = self
 
    def register_journal(self, journal):
        if journal is None:
            raise RuntimeError('Journal is None')  
        if journal in self.journals.values():
            raise RuntimeError('Journal already added')
        self.journals[journal.tag] = journal
        journal.ledger = self
