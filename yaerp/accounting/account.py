from enum import IntEnum, auto
from dataclasses import dataclass
from typing import Any

from yaerp.model.money import Money

class AccountSide(IntEnum):
    DEBIT = auto()
    CREDIT = auto()

class Account:
    
    def __init__(self, tag: str, ledger, currency, name = None, guid = None) -> None:
        if not tag:
            raise ValueError("'tag' parameter must be non empty string")
        self.tag = tag
        if not ledger:
            raise ValueError("'ledger' parameter cannot be empty")
        self.ledger = ledger
        if not currency:
            raise ValueError("'currency' parameter cannot be empty")
        self.currency = currency
        self.name = name
        self.guid = guid
        if self.ledger:
            ledger.register_account(self)
        self.posted_entries = [] # only Ledger should modify this list

    def append_entry(self, post):
        ''' A ledger invoke this function when Entry is in the process of posting. '''
        if post.account != self:
            raise ValueError('post is assigned to an another account')
        if post in self.posted_entries:
            raise ValueError('post is already added')
        self.posted_entries.append(post)

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
                return filter(predicate, self.posted_entries)
            else:
                return iter(self.posted_entries)
        if dt_posts and not ct_posts:
            if predicate:
                return filter(predicate, filter(lambda p: p.side == AccountSide.DEBIT, self.posted_entries))
            else:
                return filter(lambda p: p.side == AccountSide.DEBIT, self.posted_entries)
        if not dt_posts and ct_posts:
            if predicate:
                return filter(predicate, filter(lambda p: p.side == AccountSide.CREDIT, self.posted_entries))
            else:
                return filter(lambda p: p.side == AccountSide.CREDIT, self.posted_entries)
        return iter([])

@dataclass(frozen=True)
class AccountEntry:
    """ 
    Account entry - essential part of journal entry. 
    A transaction in double-entry bookkepping always affect at least two account,
    always includes at least one entry on debit side and one entry on credit side.
    """
    account: Any
    amount: int
    side: AccountSide
    journal_entry: Any
    post: Any

    def get_info(self):
        ''' Return tuple with 3 elements:
                - source field name in journal,
                - number of entry in the Transaction,
                - total number of entries in the Transaction
        '''
        if self.journal_entry:
            posts_counter = 0
            this_post_number = 0
            this_post_name = ''
            for key, field in self.journal_entry.fields.items():
                if isinstance(field, AccountEntry):
                    posts_counter += 1
                if field == self:
                    this_post_name = key
                    this_post_number = posts_counter
        return (this_post_name, this_post_number, posts_counter)

    def __iadd__(self, other):
        if self.side != other.side:
            ValueError('cannot add two entries with different account sides')
        if self.account != other.account:
            ValueError('cannot add two entries with different accounts')
        return AccountEntry(
            self.account,
            self.amount + other.amount,
            self.side,
            self.journal_entry,
            self.post)

    def __str__(self) -> str:
        # info = self.get_info()
        # journal_field_name = info[0]
        currency = self.account.currency
        if self.side == AccountSide.DEBIT:
            return f'Dr(\"[{self.account.tag}] {self.account.name}\", {currency.raw2amount(self.amount)})'
            #return f'Dr(\"[{self.account.tag}] {self.account.name}\", {currency.raw2str(self.amount)}) - src: \"{self.journal_entry.journal.tag}/{journal_field_name}\"'
        elif self.side == AccountSide.CREDIT:
            return f'Cr(\"[{self.account.tag}] {self.account.name}\", {currency.raw2amount(self.amount)})'
            # return f'Cr(\"[{self.account.tag}] {self.account.name}\", {currency.raw2str(self.amount)}) - src: \"{self.journal_entry.journal.tag}/{journal_field_name}\"'
        return 'Incorrect Account Entry'

def Dr(account: Account, amount: int, journal_entry):
    return AccountEntry(account=account, amount=amount, side=AccountSide.DEBIT, journal_entry=journal_entry)

def Cr(account: Account, amount: int, journal_entry):
    return AccountEntry(account=account, amount=amount, side=AccountSide.CREDIT, journal_entry=journal_entry)
