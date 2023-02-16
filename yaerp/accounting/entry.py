from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class Entry:
    """ 
    Account entry - primal part of journal transaction.
    A transaction in double-entry bookkepping always affect at least two account,
    always includes at least one entry on debit side and one entry on credit side.
    """
    account: Any
    amount: int
    side: int
    identifier: Any

    def get_info(self):
        ''' Return tuple with 3 elements:
                - source field name in journal,
                - number of entry in the Transaction,
                - total number of entries in the Transaction
        '''
        if self.identifier:
            posts_counter = 0
            this_post_number = 0
            this_post_name = ''
            for key, field in self.identifier.fields.items():
                if isinstance(field, Entry):
                    posts_counter += 1
                if field == self:
                    this_post_name = key
                    this_post_number = posts_counter
        return (this_post_name, this_post_number, posts_counter)

    def __iadd__(self, other):
        if self.side != other.side:
            ValueError('cannot add two entries with different account sides')
        if self.account != other.account:
            ValueError('cannot add two entries with different accounts')
        return Entry(
            self.account,
            self.amount + other.amount,
            self.side,
            self.identifier)

    def __str__(self) -> str:
        info = self.get_info()
        journal_field_name = info[0]
        currency = self.account.currency
        if self.side == 0:
            return f'Dr(\"[{self.account.tag}] {self.account.name}\", {currency.raw2str(self.amount)}) - src: \"{self.identifier.journal.tag}/{journal_field_name}\"'
        else:
            return f'Cr(\"[{self.account.tag}] {self.account.name}\", {currency.raw2str(self.amount)}) - src: \"{self.identifier.journal.tag}/{journal_field_name}\"'
