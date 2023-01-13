from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class Post:
    account: Any
    amount: int
    side: int
    journal: Any

    def take_into_account(self):
        if self.side == 0:
            self.account.debit += self.amount
        elif self.side == 1:
            self.account.credit += self.amount

def dr(account, amount, journal):
    return Post(account, amount, 0, journal)

def cr(account, amount, journal):
    return Post(account, amount, 1, journal)    
