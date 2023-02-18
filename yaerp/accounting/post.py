from dataclasses import dataclass
from typing import Any, Optional

@dataclass
class Post:
    ''' Flag object binding journal entries with ledger '''
    identifier: Any
    summary_entry: Any
