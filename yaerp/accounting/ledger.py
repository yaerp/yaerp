import yaerp.accounting.post


class Ledger:

    def __init__(self, tag: str):
        self.tag = tag
        self.posts = [] # main ledger's container 
        self.accounts = {} # associated accounts
        self.journals = {} # associated journals

    def commit_journal_entry(self, journal, entry):
        self.__validate_entry(journal, entry)         
        for field in entry.fields.values():
            if isinstance(field, yaerp.accounting.post.Post):
                self.__append_post(field)
        journal.accounting_entries.append(entry)
        
    def __validate_entry(self, journal, entry):
        if not entry.is_balanced():
            raise RuntimeError('not balanced Entry')
        for field in entry.fields:
            if isinstance(field, yaerp.accounting.post.Post):
                self.__validate_post(journal, field)

    def __validate_post(self, journal, post):
        if post.account is None:
            raise ValueError('post.account is None')
        if post.account not in self.accounts.values():
            raise ValueError('post.account not associated with this ledger')
        if post.entry is None:
            raise ValueError('post.entry is None')
        if post.entry.journal is None:
            raise ValueError('post.entry.journal is None')           
        if post.entry.journal != journal:
            raise ValueError('post.entry.journal should be the same as the posting journal')
        if post.entry.journal not in self.journals.values():
            raise ValueError('post.entry.journal not associated whith this ledger') 
        if post in self.posts:
            raise ValueError('post already exist in the ledger')

    def __append_post(self, post):
        self.posts.append(post)
        post.account.append_post(post)

    def register_account(self, account):
        if not account:
            raise ValueError('account is None')  
        if account.ledger and account.ledger != self:
            raise ValueError('account already associated with an another Ledger')         
        self.accounts[account.tag] = account
        account.ledger = self
 
    def register_journal(self, journal):
        if not journal:
            raise ValueError('journal is None')  
        if journal.ledger and journal.ledger != self:
            raise ValueError('journal already associated with an another Ledger') 
        self.journals[journal.tag] = journal
        journal.ledger = self
