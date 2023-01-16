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
    def get_debit(self, predicate=None):
        return sum(post.amount for post in self.post_iter(
            dt_posts=True, predicate=predicate))

    ##
    ##  amount of credit Posts
    ##
    def get_credit(self, predicate=None):
        return sum(post.amount for post in self.post_iter(
            ct_posts=True, predicate=predicate))

    def post_iter(self, dt_posts=False, ct_posts=False, predicate=None):
        if dt_posts and ct_posts:
            if predicate:
                return filter(predicate, self.posts)
            else:
                return iter(self.posts)
        if dt_posts and not ct_posts:
            if predicate:
                return filter(predicate, filter(lambda p: p.side == 0, self.posts))
            else:
                return filter(lambda p: p.side == 0, self.posts)
        if not dt_posts and ct_posts:
            if predicate:
                return filter(predicate, filter(lambda p: p.side == 1, self.posts))
            else:
                return filter(lambda p: p.side == 1, self.posts)
        return iter([])
