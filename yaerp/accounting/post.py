from dataclasses import dataclass


@dataclass
class Post:
    ''' Flag object binding journal entries with ledger '''
    identifier: int
    summary_entry: bool
