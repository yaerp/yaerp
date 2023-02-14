from dataclasses import dataclass, field
from typing import Any
import uuid

import yaerp.accounting.journal
import yaerp.accounting.entry

# @dataclass(frozen=False)
class Transaction:
    '''
    * Transaction

      Business transaction contains the data significant to a single event
    involving the movement/exchange of value (such as money, goods, services).
    These events must be measurable in monetary value so the company can
    record them for accounting purposes.

    Example of business transactions:
     - sale,
     - purchase,
     - adjustment,
     - depreciation,
     - opening and closing entries.

      Range of data required to store the transaction is determined by Journal.
    Look into define_fields() method in Journal class to find out what and how
    is stored there.
    '''

    def __init__(self, journal):
        self.journal = journal
        if self.journal:
            self.fields = self.journal.define_fields(self)
        else:
            self.fields = {}

    def is_balanced(self):
        result_dt, result_ct = 0, 0
        for post in self.fields.values():
            if not isinstance(post, yaerp.accounting.entry.Entry):
                continue
            if post.side != 0 and post.side != 1:
                raise ValueError('account side must be equal to 0 or 1')
            if post.side == 0:
                result_dt += post.amount
            else:
                result_ct += post.amount
        return result_dt == result_ct

    def info(self, field_tag: str, field_value: Any):
        ''' Set info field '''
        if field_tag not in self.fields.keys():
            raise RuntimeError(f'unknown field \'{field_tag}\'')
        self.fields[field_tag] = field_value

    def debit(self, field_tag, account, amount: int):
        ''' Set debit entry '''
        self.flow(field_tag, account, amount, 0)

    def credit(self, field_tag, account, amount:int):
        ''' Set credit entry '''
        self.flow(field_tag, account, amount, 1)

    def flow(self, field_tag, account, amount, side):
        ''' Set account entry '''
        if field_tag not in self.fields.keys():
            raise RuntimeError(f'unknown field \'{field_tag}\'')
        if side != 0 and side != 1:
            raise ValueError('account side must be equal to 0 (Dr) or 1 (Cr)')

        if isinstance(self.fields[field_tag], yaerp.accounting.entry.Entry):
            if self.fields[field_tag].side != side:
                raise ValueError(f'Journal field \'{field_tag}\' expects the other side of an account entry.')
            self.fields[field_tag] = yaerp.accounting.entry.Entry(account, amount, side, self)
        elif isinstance(self.fields[field_tag], list):
            self.fields[field_tag].append(yaerp.accounting.entry.Entry(account, amount, side, self))
        else:
            raise RuntimeError(f'Journal field \'{field_tag}\' is not dedicated for debit/credit entries.')

    def commit(self):
        ''' Posting transaction to the ledger '''
        if not self.is_balanced():
            raise RuntimeError('not balanced entries in this transaction')
        if self.journal is None:
            raise ValueError('transaction has no parent journal')
        # create new Posts if current ones are foreign
        #for key, draft in self.fields.items():
        #    if isinstance(draft, yaerp.accounting.entry.Entry):
        #        self.fields[key] = yaerp.accounting.entry.Entry(draft.account, draft.amount, draft.side, self)
        #    elif isinstance(draft, list):
        #       pass
        self.journal.commit_transaction(self)

    def __str__(self):
        return ''.join([
            f"{self.journal.tag}:  ",
            "; ".join([f"{str(value)}" for value in self.fields.values() if isinstance(value, (str, int, float))])
        ])
