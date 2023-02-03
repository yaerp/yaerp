from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class Post:
    account: Any
    amount: int
    side: int
    entry: Any

    def get_info(self):
        ''' Return tuple with 3 elements:
                - source field name in journal,
                - number of this post in the Entry,
                - count of posts in the Entry
        '''
        if self.entry:
            posts_counter = 0
            this_post_number = 0
            this_post_name = ''
            for key, field in self.entry.fields.items():
                if isinstance(field, Post):
                    posts_counter += 1
                if field == self:
                    this_post_name = key
                    this_post_number = posts_counter
        return (this_post_name, this_post_number, posts_counter)

    def __str__(self) -> str:
        info = self.get_info()
        journal_field_name = info[0]
        currency = self.account.currency
        if self.side == 0:
            return f'Dr(\"[{self.account.tag}] {self.account.name}\", {currency.raw2str(self.amount)}) - by \"{self.entry.journal.tag}\"/\"{journal_field_name}\"'
        else:
            return f'Cr(\"[{self.account.tag}] {self.account.name}\", {currency.raw2str(self.amount)}) - by \"{self.entry.journal.tag}\"/\"{journal_field_name}\"'
        