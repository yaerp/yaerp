from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class Post:
    account: Any
    amount: int
    side: int
    entry: Any

# class Post(NamedTuple):
#     account: Any
#     amount: int
#     side: int
#     entry: Any    
