from copy import copy, deepcopy
from enum import IntEnum, auto
from dataclasses import dataclass
import operator
from typing import Any
from uuid import uuid4

from yaerp.model.money import Money
from yaerp.tools.sorted_collection import SortedCollection
from yaerp.tools.text import shortify

class AccountSide(IntEnum):
    Dr = 1
    Cr = 2

    def opposite(self) -> int:
        if self == AccountSide.Dr:
            return AccountSide.Cr
        return AccountSide.Dr

    def __str__(self) -> str:
        if self == AccountSide.Dr:
            return "Dr"
        elif self == AccountSide.Cr:
            return "Cr"

class Account:
    def __init__(self, tag: str, ledger, currency, name = None) -> None:
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
        self.guid = uuid4().hex
        if self.ledger:
            ledger.register_account(self)
        self.posted_records = SortedCollection(
            [], 
            key=operator.attrgetter('journal_entry.date', 'journal_entry.time', 'journal_entry.sid')
        ) # only Ledger should modify this list

    def append_record(self, account_record):
        ''' A Ledger invoke this function when Account Record is in the process of posting. '''
        if account_record.account != self:
            raise ValueError('post is assigned to an another account')
        if account_record in self.posted_records:
            raise ValueError('post is already added')
        self.posted_records.insert_right(account_record)

    def get_debit(self, predicate=None):
        ''' Amount (raw integer) of debit posts. '''
        return sum(post.raw_amount for post in self.post_iter(
            dt_posts=True, predicate=predicate))

    def get_credit(self, predicate=None):
        ''' Amount (raw integer) of credit posts. '''
        return sum(post.raw_amount for post in self.post_iter(
            ct_posts=True, predicate=predicate))

    def get_balance(self, predicate=None):
        ''' Amount (raw integer) of credit posts. '''
        balance = 0
        for record in self.post_iter(dt_posts=True, ct_posts=True, predicate=predicate):
            if record.side == AccountSide.Dr:
                balance += record.raw_amount
            else:
                balance -= record.raw_amount
        return balance

    def post_iter(self, dt_posts=False, ct_posts=False, predicate=None):
        ''' Create post iterator. '''
        if dt_posts and ct_posts:
            if predicate:
                return filter(predicate, self.posted_records)
            else:
                return iter(self.posted_records)
        if dt_posts and not ct_posts:
            if predicate:
                return filter(predicate, filter(lambda p: p.side == AccountSide.Dr, self.posted_records))
            else:
                return filter(lambda p: p.side == AccountSide.Dr, self.posted_records)
        if not dt_posts and ct_posts:
            if predicate:
                return filter(predicate, filter(lambda p: p.side == AccountSide.Cr, self.posted_records))
            else:
                return filter(lambda p: p.side == AccountSide.Cr, self.posted_records)
        return iter([])

    def get_account_record(self, account_record_sid: str | int = None, post_sid: str | int = None):
        if account_record_sid and post_sid:
            raise ValueError('fill only one argument: account_record_sid or post_sid')
        if not account_record_sid and not post_sid:
            raise ValueError('fill one argument: account_record_sid or post_sid')
        if account_record_sid:
            if isinstance(account_record_sid, str):
                account_record_sid = int(account_record_sid)
            for ae in self.posted_records:
                if ae.sid == account_record_sid:
                    return ae
        elif post_sid:
            if isinstance(post_sid, str):
                post_sid = int(post_sid)
            for ae in self.posted_records:
                if ae.post.identifier == post_sid:
                    return ae
        return None

    def header_str(self, account_section_length=33, total_section_length=16, balance_section_length=16) -> str:
        return (
f'''-------------Account-------------  -------------------Summary-[{self.currency.symbol}]--------------------\n'''
f'''<Tag> Name                                Dr                Cr              Balance     \n'''
f'''---------------------------------  ----------------  ----------------  ----------------'''
)
    
    def account_str(self, length=33):
        tag_to_print = self.tag
        max_name_len = length - len(tag_to_print) - 3
        if self.name:
            name = self.name
        else:
            name = ""
        name_to_print = shortify(name, max_width=max_name_len)
        return str.ljust(f'<{self.tag}> {name_to_print}', length)

    def full_str(self):
        txt = []
        ac_caption = f'"{self.name}"'
        txt.append(f'--------------------------------------------------------------\n')
        txt.append(f'A/C:  {"/" + self.tag + "/":<11}  {self.name:>43}\n')
        txt.append(f'+------------------------------------------------------------+\n')
        txt.append(f'| {"Dr":^16} | {"Cr":^16} | {"Balance " + self.currency.symbol:>20} |\n')
        txt.append(f'+==================|==================|======================|\n')
        txt.append(f'| {self.dr_total_amount_str(16):^16} | {self.cr_total_amount_str(16):^16} | {self.balance_amount_str(20):>20} |\n')
        txt.append(f'+------------------+------------------+----------------------+\n')
        return ''.join(txt)

    def short_str(self):
        txt = []
        txt.append(f'{"/" + self.tag + "/":<10} ')
        txt.append(f'{self.name + " ":.<26}.')
        txt.append(f'{" " + self.dr_total_amount_str(0):.>10}  ')
        txt.append(f'{" " + self.cr_total_amount_str(0):.>10}  ')
        txt.append(f'{" " + self.balance_amount_str(0) + " " + self.currency.symbol:.>15}')
        return ''.join(txt)

    def dr_total_amount_str(self, length=16):
        return str.rjust(self.currency.raw2amount(self.get_debit()), length)

    def cr_total_amount_str(self, length=16):
        return str.rjust(self.currency.raw2amount(self.get_credit()), length)
    
    def balance_amount_str(self, length=16):
        return str.rjust(self.currency.raw2amount(self.get_balance()), length)

    def __str__(self):
        return f'{self.account_str()}  {self.dr_total_amount_str()}  {self.cr_total_amount_str()}  {self.balance_amount_str()}'

    def records_header_str(self) -> str:
        return (
f'''--J/E--  -------------Account-------------  ----------Amount-[{self.currency.symbol}]------------\n'''
f'''  SID    <Tag> Name                                Dr                Cr       \n'''
f'''-------  ---------------------------------  ----------------  ----------------'''
)

    def __hash__(self):
        return hash(id(self))
    
    def __eq__(self, other):
        return self is other


@dataclass(frozen=True)
class AccountRecord:
    """ 
    Account Record (a.k.a Account Entry) - an essential part of Ledgers and Journal Entries.
    Each Account Record describes Debit or Credit operation on specified Account.
    
    A transaction in double-entry bookkepping always affect at least two accounts.
    This transaction always includes at least one Account Record on debit side 
    and one Account Record on credit side.
    """
    account: Any
    raw_amount: int
    side: AccountSide
    journal_entry: Any
    post: Any

    # def __copy__(self):
    #     raise RuntimeError("explicit copying is not possible - parent journal entry manage copy() operation")

    # def __deepcopy__(self, memo):
    #     raise RuntimeError("explicit deep copying is not possible - parent journal entry manage copy() operation")

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
                if isinstance(field, AccountRecord):
                    posts_counter += 1
                if field == self:
                    this_post_name = key
                    this_post_number = posts_counter
        return (this_post_name, this_post_number, posts_counter)

    def __iadd__(self, other):
        if self.side != other.side:
            ValueError('addition error: expecting the same account side')
        if self.account != other.account:
            ValueError('addition error: expecting the same account')
        if self.post or other.post:
            ValueError('addition error: expecting not posted account entries')
        return AccountRecord(
            self.account,
            self.raw_amount + other.raw_amount,
            self.side,
            self.journal_entry,
            None)

    # def account_str(self, length=33):
    #     tag_to_print = self.account.tag
    #     max_name_len = length - len(tag_to_print) - 3
    #     if self.account.name:
    #         name = self.account.name
    #     else:
    #         name = ""
    #     name_to_print = (name[:max_name_len] + '..') if len(name) > max_name_len else name
    #     return str.ljust(f'<{self.account.tag}> {name_to_print}', 33)

    def dr_amount_str(self, length=16, empty_str='--', ):
        if self.side == AccountSide.Dr:
            return str.rjust(self.account.currency.raw2amount(self.raw_amount), length)
        return str.center(empty_str, length)

    def cr_amount_str(self, length=16, empty_str='--'):
        if self.side == AccountSide.Cr:
            return str.rjust(self.account.currency.raw2amount(self.raw_amount), length)
        return str.center(empty_str, length)

    def __str__(self) -> str:
        je_id_str = str.rjust(str(self.journal_entry.sid), 7)
        return f'{je_id_str}  {self.account.account_str()}  {self.dr_amount_str()}  {self.cr_amount_str()}'

def Dr(account: Account, raw_amount: int, journal_entry):
    ''' Initialize a "Dr" Account Record '''
    return AccountRecord(account=account, raw_amount=raw_amount, side=AccountSide.Dr, journal_entry=journal_entry)

def Cr(account: Account, raw_amount: int, journal_entry):
    ''' Initialize a "Cr" Account Record '''
    return AccountRecord(account=account, raw_amount=raw_amount, side=AccountSide.Cr, journal_entry=journal_entry)
