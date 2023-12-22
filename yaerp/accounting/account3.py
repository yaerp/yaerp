from copy import copy, deepcopy
from enum import IntEnum, auto
from dataclasses import dataclass
import operator
from typing import Any
from uuid import uuid4

from yaerp.model.money import Money
from yaerp.tools.sid import SID
from yaerp.tools.sorted_collection import SortedCollection
from yaerp.tools.text import shortify

def restrict(txt):
    if txt in ['root', 'tag', 'name', 'mark', 'journal', 'ledger']:
        raise ValueError('illegal text')

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

    def records_gen(self, posted=True, not_posted=True, side=None):
        acc_entries = self.ledger.account_records_gen(posted=posted,
                                                      not_posted=not_posted,
                                                      side=side,
                                                      account=self)
        return acc_entries

    def get_debit(self, predicate=None):
        dr_entries = self.records_gen(side=AccountSide.Dr)
        return sum(entry.raw_amount for entry in dr_entries)

    def get_credit(self, predicate=None):
        cr_entries = self.records_gen(side=AccountSide.Cr)
        return sum(entry.raw_amount for entry in cr_entries)

    def get_balance(self, predicate=None):
        return self.get_debit(predicate) - self.get_credit(predicate)

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
        return self.short_str()

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
    and at least one Account Record on credit side.
    """
    account: Any
    raw_amount: int
    side: AccountSide
    journal_entry: Any
    post: int

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
            record_counter = 0
            record_number = 0
            journal_entry_field_name = ''
            for key, field in self.journal_entry.fields.items():
                if isinstance(field, AccountRecord) and field.account and field.side and field.raw_amount:
                    record_counter += 1
                    if field == self:
                        journal_entry_field_name = f'{key}'
                        record_number = record_counter
                if isinstance(field, list):
                    for record in field:
                        if isinstance(record, AccountRecord) and record.account and record.side and record.raw_amount:
                            record_counter += 1
                            if record == self:
                                # journal_entry_field_name = '<Unrestricted>'
                                record_number = record_counter
            return (journal_entry_field_name, record_number, record_counter)             

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

    def dr_amount_str(self, length=16, empty_str='--'):
        if self.account and self.side == AccountSide.Dr:
            return str.rjust(self.account.currency.raw2amount(self.raw_amount), length)
        return str.center(empty_str, length)

    def cr_amount_str(self, length=16, empty_str='--'):
        if self.account and self.side == AccountSide.Cr:
            return str.rjust(self.account.currency.raw2amount(self.raw_amount), length)
        return str.center(empty_str, length)

    def __str__(self) -> str:
        if self.side and self.account:
            if self.post:
                post_str = f'POST {SID.print_form(self.post)}'
            else:
                post_str = 'NOT POSTED'
            je = self.journal_entry
            je_str = f'{SID.print_form(je.sid)}  {je.date}  "{shortify(je.description, 32)}"'
            amount_str = self.account.currency.raw2amount(self.raw_amount, new_group_separator_char='_')
            field_name, record_number, record_counter = self.get_info()
            if field_name:
                je_info = f'"{field_name}" record ({record_number} of {record_counter}) in {je.journal.name} entry'
            else:
                je_info = f'Record {record_number} of {record_counter} in {je.journal.name} entry'
            return f'{ str(self.side) + "/" + self.account.tag + "/" + amount_str:<26}  {post_str},  {je_info}: {je_str}'
            # return f'{ str(self.side) + "/" + self.account.tag + "/" + amount_str:<20}  (Part {record_number} of {record_counter} in j/e {je_id_str}, {journal_name}, {field_name})'
        return f'Empty AccountRecord   (j/e {je_str})'

def Dr(account: Account, raw_amount: int, journal_entry):
    ''' Initialize a "Dr" Account Record '''
    return AccountRecord(account=account, raw_amount=raw_amount, side=AccountSide.Dr, journal_entry=journal_entry)

def Cr(account: Account, raw_amount: int, journal_entry):
    ''' Initialize a "Cr" Account Record '''
    return AccountRecord(account=account, raw_amount=raw_amount, side=AccountSide.Cr, journal_entry=journal_entry)
