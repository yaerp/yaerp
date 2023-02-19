from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class Post:
    ''' Flag object binding journal entries with ledger '''
    identifier: int
    summary_entry: bool
