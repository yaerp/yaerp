class Ledger:

    def __init__(self, tag: str):
        self.tag = tag
        self.posts = []      
        self.accounts = {}
        self.journals = {}

    def append_post(self, post):
        if not post.account:
            raise RuntimeError()
        self.posts.append(post)
        if post.account in self.accounts.values():
            post.take_into_account()

    def bind_and_subscribe_account(self, account):
        if not account:
            raise RuntimeError()            
        if account in self.accounts.values():
            raise RuntimeError()
        self.accounts[account.tag] = account
        account.ledger = self
        ## immediately update if matching posts already exist
        for post in self.posts:
            if post.account == account:
                post.take_into_account()
 
    def register_journal(self, journal):
        if journal in self.journals.values():
            raise RuntimeError()
        self.journals[journal.tag] = journal
        journal.ledger = self
