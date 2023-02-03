class Account:
    
    def __init__(self, tag: str, ledger, currency, name = None, guid = None) -> None:
        self.tag = tag
        self.name = name
        self.guid = guid
        self.ledger = ledger
        if self.ledger:
            ledger.register_account(self)
        self.currency = currency
        self.posts = [] # only Ledger should modify this list

    def append_post(self, post):
        ''' A ledger invoke this function when Entry is in the process of posting. '''
        if post.account != self:
            raise ValueError('post is assigned to an another account')
        if post in self.posts:
            raise ValueError('post is already added')
        self.posts.append(post)

    def get_debit(self, predicate=None):
        ''' Amount (raw integer) of debit posts. '''
        return sum(post.amount for post in self.post_iter(
            dt_posts=True, predicate=predicate))

    def get_credit(self, predicate=None):
        ''' Amount (raw integer) of credit posts. '''
        return sum(post.amount for post in self.post_iter(
            ct_posts=True, predicate=predicate))

    def post_iter(self, dt_posts=False, ct_posts=False, predicate=None):
        ''' Create post iterator. '''
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
