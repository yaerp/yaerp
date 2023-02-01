from dataclasses import dataclass, field
from typing import Any

import yaerp.accounting.journal
import yaerp.accounting.post

@dataclass(frozen=False)
class Entry:
    journal: yaerp.accounting.journal.Journal = field(default_factory=yaerp.accounting.journal.Journal)
    fields: dict = field(default_factory=dict)

    def is_balanced(self):
        result_dt, result_ct = 0, 0
        for post in self.fields.values():
            if not isinstance(post, yaerp.accounting.post.Post):
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
            raise RuntimeError('field tag already exist in this entry')
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
            raise RuntimeError('field tag already exist in this entry')
        if side != 0 and side != 1:
            raise ValueError('account side must be equal to 0 (dr) or 1 (cr)')
        self.fields[field_tag] = yaerp.accounting.post.Post(account, amount, side, self)

    def commit(self):
        ''' Post this entry to the ledger '''
        if not self.is_balanced():
            raise RuntimeError('not balanced entry')
        if self.journal is None:
            raise ValueError('entry has no parent journal')
        # create new Posts if current ones are foreign
        for key, draft in self.fields.items():
            if isinstance(draft, yaerp.accounting.post.Post) and draft.entry != self:
                self.fields[key] = yaerp.accounting.post.Post(draft.account, draft.amount, draft.side, self)
        self.journal.commit_entry(self)