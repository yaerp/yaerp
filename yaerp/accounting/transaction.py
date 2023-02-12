from dataclasses import dataclass, field
from typing import Any
import uuid

import yaerp.accounting.journal
import yaerp.accounting.entry

# @dataclass(frozen=False)
class Transaction:
    """ Journal Transaction (a.k.a Journal Entry) stores single accounting record 
    related to sale, purchase, adjustment, depreciation, opening, closing, etc. 
    """

    def __init__(self, journal):
        self.journal = journal
        self.fields = {}
    # journal: yaerp.accounting.journal.Journal = field(default_factory=yaerp.accounting.journal.Journal)
    # fields: dict = field(default_factory=dict)

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
        ''' Insert new data field. '''
        if field_tag in self.fields.keys():
            raise RuntimeError('field tag already exist in this transaction')
        self.fields[field_tag] = field_value

    def debit(self, field_tag, account, amount: int):
        ''' Insert new debit field. '''
        self.flow(field_tag, account, amount, 0)

    def credit(self, field_tag, account, amount:int):
        ''' Insert new credit field. '''
        self.flow(field_tag, account, amount, 1)

    def flow(self, field_tag, account, amount, side):
        ''' Insert new post field (debit or credit) '''
        if field_tag in self.fields.keys():
            raise RuntimeError('field tag already exist in this transaction')
        if side != 0 and side != 1:
            raise ValueError('account side must be equal to 0 (dr) or 1 (cr)')
        self.fields[field_tag] = yaerp.accounting.entry.Entry(account, amount, side, self)

    def commit(self):
        ''' Post this transaction to the ledger '''
        if not self.is_balanced():
            raise RuntimeError('not balanced entries in this transaction')
        if self.journal is None:
            raise ValueError('transaction has no parent journal')
        # create new Posts if current ones are foreign
        for key, draft in self.fields.items():
            if isinstance(draft, yaerp.accounting.entry.Entry) and draft.transaction != self:
                self.fields[key] = yaerp.accounting.entry.Entry(draft.account, draft.amount, draft.side, self)
        self.journal.commit_transaction(self)

    def __str__(self):
        return ''.join([
            '; '.join([f"{key}:{str(value)}" for key, value in self.fields.items() if isinstance(value, (str, int, float))]),
            '\n    ',
            '\n    '.join([f"{str(value)}" for value in self.fields.values() if isinstance(value, yaerp.accounting.entry.Entry)]),
            '\n'
            ])
    
