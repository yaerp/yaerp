import copy
import operator
from uuid import uuid4
from yaerp.accounting.account3 import AccountRecord, AccountSide
from yaerp.tools.sid import SID
from yaerp.tools.sorted_collection import SortedCollection
from yaerp.tools.text import shortify


class Journal:
    '''
    * Journal
    Journal is a book that contain a sequence of business transactions.

      Business transaction, also known as 'Journal Entry', contains the data
    significant to a single event involving the movement/exchange of value
    (such as money, goods, services). These events must be measurable
    in monetary value so the company can record them for accounting purposes.

    Example of business transactions that can be a Journal Entry:
     - sale,
     - purchase,
     - adjustment entry,
     - correction entry,
     - opening and closing entry.

      The range of data required to store in each Journal Entry is determined by the Journal.
    Look into initialize_fields() method to read the actual Journal Entry structure.
    Note that new Journal class, derived from this class can define completly new
    set of fields.
    '''
    def __init__(self, tag: str, name: str, ledger):
        if not tag:
            raise ValueError('tag is blank')
        self.tag = tag
        self.name = name
        self.ledger = ledger
        if ledger:
            ledger.register_journal(self)
        self.journal_entries = SortedCollection([], key=operator.attrgetter('date', 'time', 'sid'))

    def post_these(self, draft_journal_entries):
        ''' 
        Aggregate journal entries into a single post.
        '''
        if not hasattr(draft_journal_entries, '__iter__'):
            ValueError('argument \'draft_journal_entries\' is not iterable')

        # removing duplicates
        je_list = list(dict.fromkeys(draft_journal_entries))

        for je in je_list:
            if not je.can_post_this(self):
                raise ValueError(f"cannot post j/e {je.sid}")
            
        bulk_post_id = SID().new()
        self.ledger.register_post(bulk_post_id)
        for je in je_list:
            self.ledger.post_journal_entry(self, je, define_post_id=bulk_post_id)
            if je not in self.journal_entries:
                self.journal_entries.insert_right(je)

    def journal_entries_gen(self, posted: bool=True, not_posted: bool=True, date_beg: str=None, date_end: str=None, reverse=False):
        if posted and not_posted:
            for je in self.journal_entries:
                if date_beg and je.date < date_beg:
                    continue
                if date_end and je.date > date_end:
                    continue
                yield je
        elif posted and not not_posted:
            for je in self.journal_entries:
                if je.post:
                    if date_beg and je.date < date_beg:
                        continue
                    if date_end and je.date > date_end:
                        continue
                    yield je
        elif not posted and not_posted:
            for je in self.journal_entries:
                if not je.post:
                    if date_beg and je.date < date_beg:
                        continue
                    if date_end and je.date > date_end:
                        continue
                    yield je

    def entries_gen(self, posted: bool=True, unposted: bool=True, date_beg: str=None, date_end: str=None, reverse=False):
        if not reverse:
            entries_iterator = iter(self.journal_entries)
        else:
            entries_iterator = reversed(self.journal_entries)
        
        for je in entries_iterator:
            # posted/unposted
            if je.post:
                if not posted:
                    continue
            else:
                if not unposted:
                    continue
            # date_beg
            if date_beg and je.date < date_beg:
                continue
            # date_end
            if date_end and je.date > date_end:
                continue
            
            yield je

    def gen_new(self):
        for je in self.journal_entries:
            if not je.post:
                yield je

    def gen_posted(self):
        for je in self.journal_entries:
            if je.post:
                yield je

    def gen_by_sid(self, *, entry_sid: int = None, entry_sids: list[int] = None):
        for je in self.journal_entries:
            if entry_sid and entry_sid == je.sid:
                yield je
            if entry_sids and je.sid in entry_sids:
                yield je

    def get_by_sid(self, entry_sid: int | str, not_rise_exception=False):
        if isinstance(entry_sid, str):
            entry_sid = int(entry_sid)
        for je in self.journal_entries:
            if je.sid == entry_sid:
                return je
        if not_rise_exception:
            return None
        raise ValueError(f'Not found Journal Entry "{self.tag}:{entry_sid}"')
    
    def get_by_guid(self, entry_guid: int | str, not_rise_exception=False):
        if isinstance(entry_guid, str):
            entry_guid = int(entry_guid)
        for je in self.journal_entries:
            if je.guid == entry_guid:
                return je
        if not_rise_exception:
            return None
        raise ValueError(f'Not found Journal Entry "{self.tag}:GUID={entry_guid}"')

    def gen_by_post(self, post):
        ''' Source entry(ies) for specified post '''
        for je in self.gen_posted_entries():
            if je.post == post:
                yield je
                if not post.summary_entry:
                    return

    def initialize_fields(self, journal_entry):
        '''
        Returns a dictionary containing the structure of the Journal Entry

         A key in the dictionary is simply a filed name.
         A value ine the dictionary can contain the following kind of variables:

          - 'AccountRecord' object means: 'this is the place for single account entry'
            For example:
                        'Cash': AccountRecord(None, 0, AccountSide.DEBIT, transaction)
                        'Sale': AccountRecord(SaleAcount, 0, AccountSide.CREDIT, transaction)
                        'Sale Tax': AccountRecord(None, 0, AccountSide.CREDIT, transaction)

          - 'list' [] means: 'this is the place for multiple account records'
            For example
                        'Account': []

          - 'None' value means: 'this is info field'. 
            For example:
                        'Info': None

            Note that 3 fields names: "data", "description" and "reference" are not needed to define here.
            The variables with these names are part of JournalEntry class.

        '''
        return {
            'Account':      []      # debit/credit account records
        }

    def validate_new_journal_entry(self, journal_entry):
        if journal_entry.journal and self != journal_entry.journal:
            raise ValueError(f'journal entry {journal_entry.sid} is binded to another journal')
        # if journal_entry in self.journal_entries:
        #     raise ValueError('the specified entry already exist in the journal')
        if not journal_entry.date:
            raise ValueError(f'journal entry {journal_entry.sid} has empty date')
        for field in journal_entry.fields.values():
            if isinstance(field, AccountRecord):
                if not field.journal_entry:
                    raise ValueError('account record has no journal entry')
                if field.journal_entry != journal_entry:
                    raise ValueError(f'account record has invalid parent journal entry (current={field.journal_entry.sid}, expected={field.journal_entry})')

    def __str__(self) -> str:
        return self.tag


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

    def __init__(self, journal: Journal):
        # unique identifier: date+time+sid
        self.date: str = None    # RRRR-MM-DD
        self.time: str = "00:00:00"    # HH:MM:SS
        self.sid: int = SID().new()     # object identifier (sequence integer in the application)
        self.guid = uuid4().hex
        self.journal = journal
        self.description = None
        self.reference = None
        self.post = None
        if self.journal:
            self.fields = self.journal.initialize_fields(self)
        else:
            self.fields = {}

    def __hash__(self):
        return hash((self.date, self.time, self.sid))

    def __eq__(self, other):
        return (self.date, self.time, self.sid) == (other.date, other.time, other.sid)

    def __lt__(self, other):
        return (self.date, self.time, self.sid) < (other.date, other.time, other.sid)

    def __gt__(self, other):
        return (self.date, self.time, self.sid) > (other.date, other.time, other.sid)

    def __copy__(self):
        cls = self.__class__
        je_copy = cls.__new__(cls)
        # je_copy.__dict__.update(self.__dict__)
        je_copy.date = self.date
        je_copy.time = self.time
        je_copy.sid: int = SID().new()  # new SID
        je_copy.guid = uuid4().hex      # new GUID
        je_copy.journal = self.journal  # journal remains the same
        je_copy.description = self.description
        je_copy.reference = None    # empty reference
        je_copy.post = None         # empty post
        je_copy.fields = {}         # create journal field copies
        for name, value in self.fields.items():
            if isinstance(value, AccountRecord):
                ac = self.fields[name].account
                si = self.fields[name].side
                am = self.fields[name].raw_amount
                ar_copy = AccountRecord(ac, am, si, je_copy, None)
                je_copy.fields[name] = ar_copy
            elif isinstance(value, list):
                je_copy.fields[name] = list()
                for record in value:
                    ac = record.account
                    si = record.side
                    am = record.raw_amount
                    ar_copy = AccountRecord(ac, am, si, je_copy, None)
                    je_copy.fields[name].append(ar_copy)
            else:
                je_copy.fields[name] = copy.copy(value)
        return je_copy

    def __deepcopy__(self, memo):
        return copy.copy(self)

    def account_records_gen(self, side=None, account=None):
        for value in self.fields.values():
            if isinstance(value, AccountRecord):
                if value.side and value.account:
                    if side and value.side != side:
                        continue
                    if account and value.account != account:
                        continue
                    yield value
            elif isinstance(value, list):
                for record in value:
                    if record.side and record.account:
                        if side and record.side != side:
                            continue
                        if account and record.account != account:
                            continue
                        yield record

    def is_balanced(self):
        return self.get_debit() == self.get_credit()
    
    def is_zeroed(self):
        return self.get_debit() == 0 and self.get_credit() == 0
    
    def is_ready_to_post(self):
        if not self.is_balanced():
            return False
        if self.is_zeroed():
            return False
        if not self.journal:
            return False
        try:
            self.journal.validate_new_journal_entry(self)
        except ValueError:
            return False
        return True

    def add_info(self, field_tag: str, value):
        ''' Fill the Journal's Entry "info field" with the new value '''
        if field_tag not in self.fields.keys():
            raise RuntimeError(f'usage of unexpected (unknown?) field \'{field_tag}\'')
        self.fields[field_tag] = value

    def debit(self, field_tag: str, raw_amount: int, account):
        ''' Add a Debit Record '''
        # self.flow(field_tag, account, amount, AccountSide.DEBIT)
        self.add_record(field_tag, raw_amount, account=account, side=AccountSide.Dr)

    def credit(self, field_tag: str, raw_amount: int, account):
        ''' Add a Credit Record '''
        # self.flow(field_tag, account, amount, AccountSide.CREDIT)
        self.add_record(field_tag, raw_amount, account=account, side=AccountSide.Cr)

    def add_record(self, field_tag: str, raw_amount: int, /, account = None, side: AccountSide = None):
        ''' 
        Add Debit/Credit Record

        If no 'account' or no 'side' argument provided the method tries get these 
        values from the field definition.
        '''
        if field_tag not in self.fields.keys():
            raise RuntimeError(f'unknown field "{field_tag}"; use one of these {list(self.fields.keys())}')

        if isinstance(self.fields[field_tag], AccountRecord):
            if self.fields[field_tag].account and not account:
                account = self.fields[field_tag].account
            if self.fields[field_tag].side and not side:
                side = self.fields[field_tag].side
        elif isinstance(self.fields[field_tag], list):
            if not account or not side:
                raise ValueError(f'field "{field_tag}" intended for a list of account records expects both \'account\' and \'side\' arguments provided')
        else:
            raise RuntimeError(f'Journal field "{field_tag}" is not dedicated for Account Records.')

        if not account:
            raise ValueError(f'the Account cannot be determined (no \'account\' argument provided and no account defined for the field "{field_tag}")')
        if not side:
            raise ValueError(f'the Account Side cannot be determined (no \'side\' argument provided and no side defined for the field "{field_tag}")')

        if isinstance(self.fields[field_tag], AccountRecord):
            self.fields[field_tag] = AccountRecord(account, raw_amount, side, self, None)
        elif isinstance(self.fields[field_tag], list):
            self.fields[field_tag].append(AccountRecord(account, raw_amount, side, self, None))

    def get_debit(self):
        return self._get_side_sum(AccountSide.Dr)

    def get_credit(self):
        return self._get_side_sum(AccountSide.Cr)

    def _get_side_sum(self, side):
        sum = 0
        for record in self.account_records_gen(side=side, account=None):
            sum += record.raw_amount
        return sum

        # result = 0
        # for field in self.fields.values():
        #     if isinstance(field, AccountRecord):
        #         if field.side != AccountSide.Dr and field.side != AccountSide.Cr:
        #             raise ValueError('account side must be DEBIT or CREDIT')
        #         if field.raw_amount and not field.account:
        #             raise ValueError('entry with no account has non zero amount')
        #         if field.side == side:
        #             result += field.raw_amount
        #     elif isinstance(field, list):
        #         for account_entry in field:
        #             if account_entry.side != AccountSide.Dr and account_entry.side != AccountSide.Cr:
        #                 raise ValueError('account side must be DEBIT or CREDIT')
        #             if account_entry.raw_amount and not account_entry.account:
        #                 raise ValueError('entry with no account has non zero amount')
        #             if account_entry.side == side:
        #                 result += account_entry.raw_amount
        # return result

    def _get_currency(self):
        for field in self.fields.values():
            if isinstance(field, AccountRecord):
                return field.account.currency
            elif isinstance(field, list):
                for account_entry in field:
                    return account_entry.account.currency
        raise RuntimeError("currency not found")

    def put_into_journal(self):
        ''' Insert this entry to the journal '''
        if self.journal is None:
            raise ValueError('journal entry has no parent journal')
        if self in self.journal.journal_entries:
            raise ValueError('journal entry is already in the journal')
        if self.post:
            raise ValueError('calling this function for posted j/e make no sense')
        self.journal.journal_entries.insert_right(self)

    def del_from_journal(self):
        ''' Delete this entry from the journal '''
        if self.journal is None:
            raise ValueError('journal entry has no parent journal')
        if self not in self.journal.journal_entries:
            raise ValueError('journal entry not found in the journal')
        if self.post:
            raise ValueError('cannot delete posted journal entry')
        self.journal.journal_entries.remove(self)

    def can_post_this(self, use_exceptions=True):
        ''' Check possibility to post this journal entry to the ledger. '''
        if not self.is_balanced():
            if use_exceptions:
                raise RuntimeError(f'not balanced journal entry {self.sid}')
            return False
        if self.journal is None:
            if use_exceptions:
                raise ValueError(f'journal entry has no parent journal {self.sid}')
            return False
        try:
            self.journal.validate_new_journal_entry(self)  
        except:
            if use_exceptions:
                raise
            return False
        return True
    
    def post_this(self):
        ''' Post this journal entry to the ledger (single post) '''
        # if not self.is_balanced():
        #     raise RuntimeError('not balanced journal entry')
        # if self.journal is None:
        #     raise ValueError('journal entry has no parent journal')
        # if self not in self.journal.journal_entries:
        #     self.put_this()
        # self.journal.validate_new_journal_entry(self)
        if self.can_post_this(self):
            self.journal.ledger.post_journal_entry(self.journal, self)
            if self not in self.journal.journal_entries:
                self.journal.journal_entries.insert_right(self)

    def _set_posted(self, post_identifier):
        if not post_identifier or post_identifier <= 0:
            raise ValueError(f'incorrent post identifier {post_identifier}')
        for name, value in self.fields.items():
            if isinstance(value, AccountRecord):
                if value.raw_amount and value.account:
                        self.fields[name] = AccountRecord(
                            value.account,
                            value.raw_amount,
                            value.side,
                            value.journal_entry,
                            post_identifier
                            )
            elif isinstance(value, list):
                for idx, account_entry in enumerate(value):
                    if account_entry.raw_amount and account_entry.account:
                        value[idx] = AccountRecord(
                            account_entry.account,
                            account_entry.raw_amount,
                            account_entry.side,
                            account_entry.journal_entry,
                            post_identifier
                            )
        self.post = post_identifier

    def str_header():
        return '-SID-  ---Date---  --Status--  -Description-'

    def status_str(self, constant_size=False):
        if self.post:   
            status = 'POSTED'
        else:
            if self.is_balanced():
                status = 'NOT POSTED'
            else:
                status = 'UNBALANCED'
        return status  

    def __str__(self):
        status = self.status_str()
        result = f'SID:{self.sid:04}  {self.date:>10}  {status:^10}  "{self.description}"'
        return result
    
    def full_str(self):
        txt = []
        if self.post:   
            status = f'POST {self.post:>04}'
        else:
            if self.is_balanced():
                status = 'NOT POSTED'
            else:
                status = 'UNBALANCED'
        je_caption = f'j/e {self.sid:>04}  "{self.journal.tag}" ({status})'
        txt.append(f'----------------------------------------------------------------------------\n')
        txt.append(f'{self.date:<33}  {shortify(self.description, 41):>41}')
        txt.append('\n')
        txt.append(f' {je_caption:<35} +-------------------------------------+\n')
        txt.append(f' {shortify("ref: " + self.reference if self.reference else "", 39):^35} | {"Dr":^16} | {"Cr":^16} |\n')
        txt.append(f'+====================================|==================|==================|\n')
        for field_name, field_value in self.fields.items():
            if isinstance(field_value, AccountRecord):
                amount = field_value.account.currency.raw2amount(field_value.raw_amount)
                if field_value.side == AccountSide.Dr:
                    txt.append(f'| {shortify(field_name, 25):<25}          | {amount:>16} | {16*" "} |')
                elif field_value.side == AccountSide.Cr:
                    txt.append(f'|          {shortify(field_name, 25):<25} | {16*" "} | {amount:>16} |')
                txt.append('\n')
            elif isinstance(field_value, list):
                for acc_record in field_value:
                    amount = acc_record.account.currency.raw2amount(acc_record.raw_amount)
                    if acc_record.side == AccountSide.Dr:
                        txt.append(f'| {"/"+acc_record.account.tag+"/":<11} {shortify(acc_record.account.name, 22):<22} | {amount:>16} | {16*" "} |')
                    elif acc_record.side == AccountSide.Cr:
                        txt.append(f'| {"/"+acc_record.account.tag+"/":<11} {shortify(acc_record.account.name, 22):<22} | {16*" "} | {amount:>16} |')
                    txt.append('\n')
            else:
                txt.append(f'| {field_name}: {field_value}\n')
                txt.append('\n')

        txt.append(f'+------------------------------------+------------------+------------------+\n')
        return ''.join(txt)
