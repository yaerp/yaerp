from dataclasses import dataclass, field

from .post import Post

@dataclass()
class Entry:
    entry_info: dict = field(default_factory=dict)
    debit_records: list[Post] = field(default_factory=list)
    credit_records: list[Post] = field(default_factory=list)

    def is_balanced(self):
        result = 0
        for dr in self.debit_records:
            result += dr.amount
        for cr in self.credit_records:
            result -= cr.amount
        return result == 0 