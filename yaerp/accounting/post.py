from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class Post:
    account: Any
    amount: int
    side: int
    entry: Any

    # def __str__(self):
    #     if self.side == 0:
    #         return 'Dt'
    #     else:
    #         return 'Ct'
