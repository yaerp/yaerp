from dataclasses import dataclass, field
from typing import Any
import uuid

# from yaerp.accounting.journal import Journal
from yaerp.accounting.account_entry import AccountEntry

# @dataclass(frozen=False)
class JournalEntry:
    '''
    * Journal Entry

      Journal Entry contains the data significant to a single event
    involving the movement/exchange of value (such as money, goods, services).
    These events must be measurable in monetary value so the company can
    record them for accounting purposes. 

    Example of business transactions the Journal Entry handle:
     - sale,
     - purchase,
     - adjustment,
     - depreciation.
    '''

    def __init__(self, journal):
        self.journal = journal
        self.post = None
        if self.journal:
            self.fields = self.journal.define_fields(self)
        else:
            self.fields = {}

    def is_balanced(self):
        result_dt, result_ct = 0, 0
        for field in self.fields.values():
            if isinstance(field, AccountEntry):
                if field.side != 0 and field.side != 1:
                    raise ValueError('account side must be equal to 0 or 1')
                if field.amount and not field.account:
                    raise ValueError('entry with no account has non zero amount')
                if field.side == 0:
                    result_dt += field.amount
                else:
                    result_ct += field.amount
            elif isinstance(field, list):
                for account_entry in field:
                    if account_entry.side != 0 and account_entry.side != 1:
                        raise ValueError('account side must be equal to 0 or 1')
                    if account_entry.amount and not account_entry.account:
                        raise ValueError('entry with no account has non zero amount')
                    if account_entry.side == 0:
                        result_dt += account_entry.amount
                    else:
                        result_ct += account_entry.amount
        return result_dt == result_ct

    def info(self, field_tag: str, field_value: Any):
        ''' Set info field '''
        if field_tag not in self.fields.keys():
            raise RuntimeError(f'unknown field \'{field_tag}\'')
        self.fields[field_tag] = field_value

    def debit(self, field_tag: str, account, amount: int):
        ''' Set debit entry '''
        self.flow(field_tag, account, amount, 0)

    def credit(self, field_tag: str, account, amount: int):
        ''' Set credit entry '''
        self.flow(field_tag, account, amount, 1)

    def flow(self, field_tag: str, account, amount: int, side: int):
        ''' Set account entry '''
        if field_tag not in self.fields.keys():
            raise RuntimeError(f'unknown field \'{field_tag}\'')
        if side != 0 and side != 1:
            raise ValueError('account side must be equal to 0 (Dr) or 1 (Cr)')

        if isinstance(self.fields[field_tag], AccountEntry):
            if self.fields[field_tag].side != side:
                raise ValueError(f'Journal field \'{field_tag}\' expects the other side of an account entry.')
            self.fields[field_tag] = AccountEntry(account, amount, side, self, None)
        elif isinstance(self.fields[field_tag], list):
            self.fields[field_tag].append(AccountEntry(account, amount, side, self, None))
        else:
            raise RuntimeError(f'Journal field \'{field_tag}\' is not dedicated for debit/credit entries.')

    def post_to_ledger(self):
        ''' Post this journal entry to the ledger (single post) '''
        if not self.is_balanced():
            raise RuntimeError('not balanced journal entry')
        if self.journal is None:
            raise ValueError('journal entry has no parent journal')
        self.journal.validate_new_journal_entry(self)
        self.journal.ledger.post_journal_entry(self.journal, self)
        # self.journal.post_separate(self)

    def _set_posted(self, post):
        if not post:
            raise ValueError('post is None')
        for name, value in self.fields.items():
            if isinstance(value, AccountEntry):
                if value.amount and value.account:
                        self.fields[name] = AccountEntry(
                            value.account,
                            value.amount,
                            value.side,
                            value.journal_entry,
                            post
                            )
            elif isinstance(value, list):
                for idx, account_entry in enumerate(value):
                    if account_entry.amount and account_entry.account:
                        value[idx] = AccountEntry(
                            account_entry.account,
                            account_entry.amount,
                            account_entry.side,
                            account_entry.journal_entry,
                            post
                            )
        self.post = post

    def __str__(self):
        post_info = '/not posted/'
        if self.post:
            if self.post.summary_entry:
                post_info = '/aggregated post/'
            else:
                post_info = '/simple post/'
        return ' '.join([
            f"{self.journal.tag}:  ",
            "; ".join([f"{str(value)}" for value in self.fields.values() if isinstance(value, (str, int, float))]),
            f'{post_info}'
        ])
