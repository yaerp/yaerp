from .exception import AccountingError


class AccountError(AccountingError):
    def __init__(self, message):
        super().__init__(message)

class Account:
    
    def __init__(self, tag: str, ledger, name = None, guid = None) -> None:
        self.tag = tag
        self.name = name
        self.guid = guid
        self.ledger = ledger
        if self.ledger:
            ledger.register_account(self)
        self.posts = [] # only Ledger should modify this list

    ##
    ## called by Ledger when Journal Entry is commiting
    ##
    def append_post(self, post):
        if post.account != self:
            raise AccountError('append post - failed: Post is assigned to another Account')
        if post in self.posts:
            raise AccountError('append post - failed: Post already added')
        self.posts.append(post)

    ##
    ##  amount of debit Posts
    ##
    def get_debit(self, post_predicate=None):
        if post_predicate is None: 
            return sum(post.amount for post in filter(
                lambda p: p.side == 0, self.posts))
        return sum(post.amount for post in filter(
            post_predicate, filter(lambda p: p.side == 0, self.posts)))

    ##
    ##  amount of credit Posts
    ##
    def get_credit(self, post_predicate=None):
        if post_predicate is None: 
            return sum(post.amount for post in filter(
                lambda p: p.side == 1, self.posts))
        return sum(post.amount for post in filter(
            post_predicate, filter(lambda p: p.side == 1, self.posts)))
