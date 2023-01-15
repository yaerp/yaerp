from dataclasses import dataclass, field
from typing import Any

from .journal import Journal
from .post import Post, DraftPost

@dataclass(frozen=False)
class Entry:
    journal: Journal = field(default_factory=Journal)
    info_fields: dict = field(default_factory=dict)
    debit_fields: list[Post] = field(default_factory=list)
    credit_fields: list[Post] = field(default_factory=list)

    def is_balanced(self):
        result_dt, result_ct = 0, 0
        for dr in self.debit_fields:
            if dr.side != 0:
                raise RuntimeError()
            result_dt += dr.amount
        for cr in self.credit_fields:
            if cr.side != 1:
                raise RuntimeError()
            result_ct += cr.amount
        return result_dt == result_ct

    def field(self, key: str, value: Any):
        self.info_fields[key] = value

    def debit(self, account, amount):
        self.debit_fields.append(DraftPost(account, amount, 0, self))  

    def credit(self, account, amount):
        self.credit_fields.append(DraftPost(account, amount, 1, self))

    def is_valid(self):
        try:
            self.journal.validate_new_entry(self)
            return True, None
        except RuntimeError:
            return False

    def commit(self):
        if self.is_valid():
            # convert drafts to posts
            for idx, draft in enumerate(self.debit_fields):
                self.debit_fields[idx] = Post(draft.account, draft.amount, 0, self)
            for idx, draft in enumerate(self.credit_fields):
                self.credit_fields[idx] = Post(draft.account, draft.amount, 1, self)
            self.journal.commit_entry(self)
