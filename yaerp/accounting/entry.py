from dataclasses import dataclass, field
from typing import Any

from .journal import Journal
from .post import Post

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
        self.debit_fields.append(Post(account, amount, 0, self))  

    def credit(self, account, amount):
        self.credit_fields.append(Post(account, amount, 1, self))

    def commit(self):
        self.journal.commit_entry(self)
