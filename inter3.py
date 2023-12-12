import argparse
from datetime import datetime
from hashlib import blake2s
from dateutil.tz import *
from dateutil.relativedelta import *
from itertools import repeat
import cmd2
from cmd2 import CommandSet, CompletionMode, with_argparser, with_category, with_default_category, ansi
from accounting_system import AccountingSystem, setup_tiny_accounting_system as s
from yaerp.accounting.account import AccountRecord, AccountSide
from yaerp.accounting.journal import Journal, JournalEntry
from yaerp.accounting.tree import AccountTree
from yaerp.tools.file import append_file
from yaerp.tools.sid import SID
from yaerp.tools.text import dict_to_str, iter_to_str

accounting_system = None
sec_token = ''

def update_sec_token(command_args):
    h = blake2s(digest_size=8)
    h.update(globals()["sec_token"].encode())
    for arg in command_args:
        h.update(arg.encode())
    return h.hexdigest()

prompt_part_1 = ""
prompt_part_2 = ""
prompt = ""

def set_prompt_part_1(p1):
    globals()["prompt_part_1"] = p1
    update_global_prompt()

def set_prompt_part_2(p2):
    globals()["prompt_part_2"] = p2
    update_global_prompt()

def update_global_prompt():
    globals()["prompt"] = f'{globals()["prompt_part_1"]} @ {globals()["prompt_part_2"]}> '


@with_default_category('ChartsOfAccounts')
class LoadableChartsOfAccounts(CommandSet):

    def __init__(self):
        super().__init__()

    # def do_journalcommand(self, _: cmd2.Statement):
    #     self._cmd.poutput('Apple')

    coa_parser = cmd2.Cmd2ArgumentParser()
    coa_parser.add_argument('-n', '--name', required=True)

    @cmd2.as_subcommand_to('create', 'chart-of-accounts', coa_parser)
    def create_coa(self, ns: argparse.Namespace):
        """Create Charts of Accounts"""
        accounting_system.add_chart_of_accounts(ns.name)
        self._cmd.poutput('creating new chart of accounts: ' + ns.name)

    @cmd2.as_subcommand_to('read', 'chart-of-accounts', coa_parser)
    def read_coa(self, ns: argparse.Namespace):
        """Read Charts of Accounts"""
        coa = accounting_system.get_chart_of_accounts(ns.name)
        self._cmd.poutput(coa)
        for node in coa.get_internals_gen():
            self._cmd.poutput(node)

    @cmd2.as_subcommand_to('delete', 'chart-of-accounts', coa_parser)
    def delete_coa(self, ns: argparse.Namespace):
        """Delete Charts of Accounts"""
        self._cmd.poutput('deleting new chart of accounts: ' + ns.name)

    update_coa_parser = cmd2.Cmd2ArgumentParser()
    update_coa_parser.add_argument('-n', '--name', required=True)
    update_coa_parser.add_argument('-add', '--add-accounts', required=False, nargs=(1,))
    update_coa_parser.add_argument('-move', '--move-accounts', required=False, nargs=(1,))
    update_coa_parser.add_argument('-p', '--parent-account', required=False)
    update_coa_parser.add_argument('-del', '--del-accounts', required=False, nargs=(1,))
    update_coa_parser.add_argument('-nn', '--new-name', required=False)

    @cmd2.as_subcommand_to('update', 'chart-of-accounts', update_coa_parser)
    def update_coa(self, ns: argparse.Namespace):
        """Update Charts of Accounts"""
        coa = accounting_system.get_chart_of_accounts(ns.name)
        if ns.add_accounts:
            for ac_tag in ns.add_accounts:
                accounting_system.add_node(coa_name=ns.name, account_tag=ac_tag, parent_account_tag=ns.parent_account)
        if ns.move_accounts:
            for ac_tag in ns.move_accounts:
                accounting_system.move_node(coa_name=ns.name, account_tag=ac_tag, new_parent_account_tag=ns.parent_account)
        if ns.del_accounts:
            for ac_tag in ns.del_accounts:
                accounting_system.delete_node(coa_name=ns.name, account_tag=ac_tag)

    list_coa = cmd2.Cmd2ArgumentParser()
    @cmd2.as_subcommand_to('list', 'charts-of-accounts', list_coa)
    def list_coa(self, _: argparse.Namespace):
        for tag, coa in accounting_system.charts_of_accounts.items():
            self._cmd.poutput(f'{tag}:  {coa}')

@with_default_category('Journal')
class LoadableJournals(CommandSet):

    def __init__(self):
        super().__init__()

    # def do_journalcommand(self, _: cmd2.Statement):
    #     self._cmd.poutput('Apple')

    journal_parser = cmd2.Cmd2ArgumentParser()
    # journal_parser.add_argument('direction', choices=['discs', 'lengthwise'])

    @cmd2.as_subcommand_to('create', 'journal', journal_parser)
    def create_journal(self, ns: argparse.Namespace):
        """Create journal"""
        self._cmd.poutput('creating new journal: ' + ns.direction)

    @cmd2.as_subcommand_to('read', 'journal', journal_parser)
    def read_journal(self, ns: argparse.Namespace):
        """read journal"""
        self._cmd.poutput('read journal: ' + ns.direction)

    @cmd2.as_subcommand_to('update', 'journal', journal_parser)
    def update_journal(self, ns: argparse.Namespace):
        """update journal"""
        self._cmd.poutput('update journal: ' + ns.direction)

    @cmd2.as_subcommand_to('delete', 'journal', journal_parser)
    def delete_journal(self, ns: argparse.Namespace):
        """delete journal"""
        self._cmd.poutput('delete journal: ' + ns.direction)

    @cmd2.as_subcommand_to('open', 'journal', journal_parser)
    def open_journal(self, ns: argparse.Namespace):
        """open journal"""
        self._cmd.poutput('open journal (enable operations): ' + ns.direction)

    @cmd2.as_subcommand_to('close', 'journal', journal_parser)
    def close_journal(self, ns: argparse.Namespace):
        """close journal"""
        self._cmd.poutput('close journal (disable operations): ' + ns.direction)

    select_journal_parser = cmd2.Cmd2ArgumentParser()
    select_journal_parser.add_argument('journal_name')
    @cmd2.as_subcommand_to('select', 'journal', select_journal_parser)
    def select_journal(self, ns: argparse.Namespace):
        """select journal"""
        if ns.journal_name not in accounting_system.journals.keys(): 
            self._cmd.poutput('"select journal" possible arguments:')
            for tag, journal in accounting_system.journals.items():
                self._cmd.poutput(f'  {tag}:  {journal.name}')
            return
        accounting_system.selected["journal"] = ns.journal_name
        set_prompt_part_2(ns.journal_name)


    list_journals_parser = cmd2.Cmd2ArgumentParser()
    @cmd2.as_subcommand_to('list', 'journals', journal_parser)
    def list_journals(self, _: argparse.Namespace):
        # print(f"{accounting_system=}")
        # print(f"{accounting_system.__dir__()=}")
        for tag, journal in accounting_system.journals.items():
            self._cmd.poutput(f'{tag}:  {journal.name}')

@with_default_category('Accounts')
class LoadableAccounts(CommandSet):
    def __init__(self):
        super().__init__()

    # def do_accountcommand(self, _: cmd2.Statement):
    #     self._cmd.poutput('Arugula')

    create_account_parser = cmd2.Cmd2ArgumentParser()
    create_account_parser.add_argument('-t', '--tag', required=True, help='Unique tag identifier')
    create_account_parser.add_argument('-p', '--parent', required=False, help='Parent account (tag) in the "Chart of Accounts"')
    create_account_parser.add_argument('-l', '--ledger', required=True, help='General Ledger')
    create_account_parser.add_argument('-n', '--name', required=True, help='Full account name')
    create_account_parser.add_argument('-c', '--currency', required=True, help='Currency symbol (3-character)')
    create_account_parser.add_argument('-m', '--markers', nargs=(0,), help='Flag marker(s) for automation and reporting')

    @cmd2.as_subcommand_to('create', 'account', create_account_parser)
    def create_account(self, ns: argparse.Namespace):
        accounting_system.add_account(ns.tag, ns.ledger, ns.currency, ns.name)
        if not ns.parent:
            pass # add to root node if parent argument is not provided

        if ns.markers:
            ac = accounting_system.get_account(ns.tag)
            
        self._cmd.poutput('creating account')

    account_parser = cmd2.Cmd2ArgumentParser()
    account_parser.add_argument('-t', '--tag', required=False)
    account_parser.add_argument('-n', '--name', required=False)  

    @cmd2.as_subcommand_to('read', 'account', account_parser)
    def read_account(self, _: argparse.Namespace):
        self._cmd.poutput('read account')  

    update_account_parser = cmd2.Cmd2ArgumentParser()
    update_account_parser.add_argument('-t', '--tag', required=True)
    create_account_parser.add_argument('-np', '--new-parent', required=False)
    update_account_parser.add_argument('-nn', '--new-name', required=False)
    update_account_parser.add_argument('-nt', '--new-tag', required=False)
    update_account_parser.add_argument('-nc', '--new-currency', required=False)
    update_account_parser.add_argument('-am', '--add-markers', required=False, nargs=(1,))
    update_account_parser.add_argument('-dm', '--del-markers', required=False, nargs=(1,)) 

    @cmd2.as_subcommand_to('update', 'account', update_account_parser)
    def update_account(self, ns: argparse.Namespace):
        self._cmd.poutput('update account')        

    delete_account_parser = cmd2.Cmd2ArgumentParser()
    delete_account_parser.add_argument('-t', '--tag', required=True, nargs=(1,), help="Tag identifier(s)")

    @cmd2.as_subcommand_to('delete', 'account', delete_account_parser)
    def delete_account(self, ns: argparse.Namespace):
        self._cmd.poutput('deleting account' + str(ns.tag))

    @cmd2.as_subcommand_to('open', 'account', account_parser)
    def open_account(self, _: argparse.Namespace):
        self._cmd.poutput('opening account (enable operations)')  

    @cmd2.as_subcommand_to('close', 'account', account_parser)
    def close_account(self, _: argparse.Namespace):
        self._cmd.poutput('close account (disable operations)') 

    @cmd2.as_subcommand_to('list', 'accounts', account_parser)
    def list_accounts(self, _: argparse.Namespace):
        for tag, account in accounting_system.accounts.items():
            self._cmd.poutput(f'{tag}:  {account.name}')


@with_default_category('Entries')
class LoadableEntries(CommandSet):
    def __init__(self):
        super().__init__()

    # def do_entriescommand(self, _: cmd2.Statement):
    #     self._cmd.poutput('Ent..')

    entry_parser = cmd2.Cmd2ArgumentParser()
    entry_parser.add_argument('style', choices=['q', 'd'])

    create_entry_parser = cmd2.Cmd2ArgumentParser()
    create_entry_parser.add_argument('-date', '--entry-date', required=None)
    create_entry_parser.add_argument('-desc', '--entry-description', required=True) 
    create_entry_parser.add_argument('-ref', '--reference', default=None)  

    def puts_journal_entry(self, je: JournalEntry):

        def puts_side(side):
            if side == AccountSide.Dr:
                self._cmd.poutput("  ", end='')
            elif side == AccountSide.Cr:
                self._cmd.poutput("      ", end='')
            else:
                raise ValueError()

        sid_str = str(je.sid)
        self._cmd.poutput(f'{je.date}  ({je.journal.tag}:{sid_str})  "{je.description}"', end='')
        # self._cmd.poutput(je.str_header())
        if je.reference:
            self._cmd.poutput(f'  [{je.reference}]', end='')
        if je.post:
            self._cmd.poutput(f'  POSTED', end='')
        else:
            self._cmd.poutput(f'  NEW', end='')
        self._cmd.poutput()

        for key, value in je.fields.items():
            if isinstance(value, AccountRecord):
                puts_side(value.side)
                self._cmd.poutput(f'"{value.account.name}"  {value.account.currency.raw2amount(value.raw_amount)}')
            elif isinstance(value, list):
                for record in value:
                    puts_side(record.side)
                    self._cmd.poutput(f'  "{record.account.name}"  {record.account.currency.raw2amount(record.raw_amount)}')

    # @cmd2.as_subcommand_to('create', 'entry', create_entry_parser)
    # def create_entry(self, ns: argparse.Namespace):
    #     journal_tag = accounting_system.selected["journal"]
    #     journal_entry = accounting_system.new_journal_entry(journal_tag)
    #     if ns.entry_date:
    #         journal_entry.date = ns.entry_date
    #     else:
    #         journal_entry.date = accounting_system.get_active_date()
    #     journal_entry.description = ns.entry_description
    #     journal_entry.reference = ns.reference

    #     account_text = None
    #     side_text = None
    #     amount_text = None

    #     account = None
    #     side = None
    #     amount = None

    #     for key, value in journal_entry.fields.items():
    #         # input_text = self._cmd.read_input(f'{key} <<< ')
    #         # self._cmd.poutput(f'{key}={input_text}')
    #         if value is None:
    #             '''Get info '''
    #             input_text = self._cmd.read_input(f'"{key}" info field: ')
    #             journal_entry.add_info(key, input_text)
    #         elif isinstance(value, AccountRecord):
    #             ''' Get account field (specific) '''
    #             if not value.account:
    #                 if not value.side:
    #                     account_req_mesg = f'"{key}": Account to impact: '
    #                 else:
    #                     if value.side == AccountSide.DEBIT:
    #                         account_req_mesg = f'"{key}" Dr Account to impact: '
    #                     else:
    #                         account_req_mesg = f'"{key}" Cr Account to impact: '
    #             side_req_mesg = f'"{key}": Account Side: '
    #             if not value.side:
    #                 amount_req_mesg = f'"{key}": Amount: '
    #             else:
    #                 if value.side == AccountSide.DEBIT:
    #                     amount_req_mesg = f'"{key}" Dr Amount: '
    #                 else:
    #                     amount_req_mesg = f'"{key}" Cr Amount: '
    #             if not value.account:
    #                 # account_tag = self._cmd.read_input(f'"{key}" field: Account to impact: ')
    #                 account_tag = self._cmd.read_input(account_req_mesg)
    #                 if not account_tag:
    #                     self._cmd.poutput(f'  Interrupted')
    #                     return
    #                 account = accounting_system.get_account(account_tag)
    #             if not value.side:
    #                 # side_text = self._cmd.read_input(f'"{key}" field: Account Side: ', completion_mode=CompletionMode.CUSTOM , choices=['Dr', 'Cr'])
    #                 side_text = self._cmd.read_input(side_req_mesg, completion_mode=CompletionMode.CUSTOM , choices=['Dr', 'Cr'])
    #                 if not side_text:
    #                     self._cmd.poutput(f'  Interrupted')
    #                     return
    #                 if side_text == "Dr":
    #                     side = AccountSide.DEBIT
    #                 elif side_text == "Cr":
    #                     side = AccountSide.CREDIT
    #                 else:
    #                     ValueError("Incorrect account side argument. Expecting: 'Dr' or 'Cr'")
    #             # input_prompt = f'"{key}" field: Amount: '
    #             # amount_text = self._cmd.read_input(input_prompt)
    #             amount_text = self._cmd.read_input(amount_req_mesg)
    #             if not amount_text:
    #                 self._cmd.poutput(f'  Interrupted')
    #                 return
    #             amount = int(amount_text)
    #             journal_entry.add_record(key, amount, account=account, side=side)
    #         elif isinstance(value, list):
    #             ''' Get account field (unspecified) '''
    #             self._cmd.poutput(f'MANUAL ACCOUNT ENTRIES')
    #             for number, _ in enumerate(repeat(True), 1):
    #                 self._cmd.poutput(f' {str.rjust(str(number), 2)}. {key} Entry:')
    #                 account_text = self._cmd.read_input(f'      Name/Tag = ')
    #                 side_text = self._cmd.read_input(f'      Side = ', completion_mode=CompletionMode.CUSTOM , choices=['Dr', 'Cr'])
    #                 amount_text = self._cmd.read_input(f'      Amount = ', )
    #                 if not account_text and not side_text and not amount_text:
    #                     break
    #                 account = accounting_system.get_account(account_text)
    #                 if side_text == "Dr":
    #                     side = AccountSide.DEBIT
    #                 elif side_text == "Cr":
    #                     side = AccountSide.CREDIT
    #                 else:
    #                     ValueError("Incorrect account side argument. Expecting: 'Dr' or 'Cr'")
    #                 raw_amount = account.currency.amount2raw(amount_text)                    
    #                 journal_entry.add_record(key, raw_amount, account=account, side=side)
    #         else:
    #             ValueError(f"Incorrect type of {key} field")
    #     accounting_system.add_journal_entry(journal_entry)
    #     head = f'------ New {journal_tag} entry ------'
    #     self._cmd.poutput(head)
    #     self.puts_journal_entry(journal_entry)
    #     self._cmd.poutput('-' * len(head))



    create2_entry_parser = cmd2.Cmd2ArgumentParser()
    create2_entry_parser.add_argument('journal', help="Journal tag")
    create2_entry_parser.add_argument('date', help="Local date and (optional) time in form 'RRRR-MM-DD hh:mm:ss' (i.e 2023-11-23 11:57:24) or one of the following phrases:\n    'now', 'today', 'prev_month_last_day', 'this_month_last_day', 'next_month_last_day'")
    create2_entry_parser.add_argument('description', help='transaction description, i.e "Purchase of materials"') 
    create2_entry_parser.add_argument('-ref', '--reference', default=None)
    create2_entry_parser.add_argument('-token', '--token', default=None, help="Secure token to seal commands stored in script. ")
    create2_entry_parser.add_argument('fields', nargs=(2,), help='debit/credit entry or info data in order of apperance in the journal. One of the following formats "Amount" (i.e 100.00) or "Account/Amount" (i.e 450/100.00) or "Side/Account/Amount" (i.e Dr/450/100.00) or "Some text" (for info fields)')

    def fill_entry_fields(self, journal_entry: JournalEntry, field_data_list):
        def parse_field_data(field_str: str) -> tuple:
            if not field_str:
                raise ValueError()
            tmp = field_str.split('/', maxsplit=3)
            tmp_len = len(tmp)
            side = None
            account = None
            amount_text = ""
            if tmp_len == 1:
                amount_text = tmp[0]
            elif tmp_len == 2:
                if tmp[0]:
                    account = accounting_system.get_account(tmp[0])
                amount_text = tmp[1]
            elif tmp_len == 3:
                if tmp[0].lower() in ("dr", "dt", "debit", "wn", "winien"):
                    side = AccountSide.Dr
                if tmp[0].lower() in ("cr", "ct", "credit", "ma"):
                    side = AccountSide.Cr
                if tmp[1]:
                    account = accounting_system.get_account(tmp[1])
                amount_text = tmp[2]
            return (side, account, amount_text)

        def autobalance(journal_entry, balancing_side) -> int:
            if not journal_entry.is_zeroed() and not journal_entry.is_balanced():
                balance = journal_entry.get_debit() - journal_entry.get_credit()
                self._cmd.poutput(f'Autobalance')
                if balance > 0 and balancing_side == AccountSide.Cr:
                    result_raw_amount = balance
                elif balance < 0 and balancing_side == AccountSide.Dr:
                    result_raw_amount = -balance
                else:
                    raise ValueError(f'"{balancing_side}" record cannot auto-balance this journal entry. Use "{balancing_side.opposite()}"')
            else:
                result_raw_amount = 0
            return result_raw_amount

        def autobalance2(journal_entry) -> (AccountSide, int):
            if not journal_entry.is_zeroed() and not journal_entry.is_balanced():
                balance = journal_entry.get_debit() - journal_entry.get_credit()
                # self._cmd.poutput(f'Autobalance2')
                if balance > 0:
                    return (AccountSide.Cr, balance)
                if balance < 0:
                    return (AccountSide.Dr, -balance)
            else:
                return (None, 0)

        field_arg_counter = len(field_data_list)

        for index, field_name in enumerate(journal_entry.fields.keys()):
            if index == field_arg_counter:
                break
            if journal_entry.fields[field_name] is None:
                '''Info field '''
                # self._cmd.poutput(f'{index}: "{field_name}" info field: "{field_data_list[index]}"')
                journal_entry.add_info(field_name, field_data_list[index])
            elif isinstance(journal_entry.fields[field_name], AccountRecord):
                '''Single (and bounded) AccountEntry'''
                # self._cmd.poutput(f'{index}: "{field_name}" bounded account record field: "{field_data_list[index]}"')
                default_side = journal_entry.fields[field_name].side
                default_account = journal_entry.fields[field_name].account
                arg_side, arg_account, amount_text = parse_field_data(field_data_list[index])

                if arg_account:
                    ''' is arg_account match to default account'''
                    if default_account and False:
                        raise ValueError()
                else:
                    if default_account:
                        arg_account = default_account  
                    else:
                        raise ValueError()
                    
                if arg_side:
                    ''' is arg_side match to default account side'''
                    if default_side and arg_side != default_side:
                        raise ValueError(f'Journal "{journal_entry.journal.tag}", field "{field_name}" -> default account side defined; expects empty "/../.." or "{default_side}/../.." instead of: {field_data_list[index]}')
                else:
                    if default_side:
                        arg_side = default_side
                    # else:
                    #     raise ValueError(f'Journal "{journal_entry.journal.tag}", field "{field_name}" -> no default account side defined; expects "{AccountSide.Dr}/../.." or "{AccountSide.Cr}/../.." (debit or credit) instead of: {field_data_list[index]}')

                if not amount_text or amount_text == '*':
                    ''' If no amount provided - try to auto-balance the journal entry '''
                    ctrl_side, arg_raw_amount = autobalance2(journal_entry)
                    if arg_side:
                        if arg_side != ctrl_side:
                            raise ValueError(f'"{arg_side}" record cannot auto-balance this journal entry. It shoul be "{ctrl_side}" instead.')
                    else:
                        arg_side = ctrl_side
                else:
                    arg_raw_amount = arg_account.currency.amount2raw(amount_text)
                journal_entry.add_record(field_name, arg_raw_amount, 
                                         account=arg_account, side=arg_side)
            elif isinstance(journal_entry.fields[field_name], list):
                '''List of free AccountEntries. Reading until the end'''
                # self._cmd.poutput(f'Free account records expected from: "{field_data_list[index]}" until the end.')
                
                for uindex in range(index, field_arg_counter):
                    # self._cmd.poutput(f'{uindex}:Free account record: "{field_data_list[uindex]}"')
                    arg_side, arg_account, amount_text = parse_field_data(field_data_list[uindex])

                    if not arg_account:
                        raise ValueError(f'Incorrect account record: "{field_data_list[uindex]}". Expecting "../AccTag/.." (account tag).')

                    if not amount_text or amount_text == '*':
                        ''' If no amount provided - try to balance the journal entry '''
                        ctrl_side, arg_raw_amount = autobalance2(journal_entry)
                        if arg_side:
                            if arg_side != ctrl_side:
                                raise ValueError(f'"{arg_side}" record cannot auto-balance this journal entry. It shoul be "{ctrl_side}" instead.')
                        else:
                            arg_side = ctrl_side
                    else:
                        arg_raw_amount = arg_account.currency.amount2raw(amount_text)

                    if not arg_side:
                        raise ValueError(f'Cannot determine account side for provided argument "{field_data_list[uindex]}". Expecting "{AccountSide.Dr}/../.." or "{AccountSide.Cr}/../.." (debit or credit).')

                    journal_entry.add_record(field_name, arg_raw_amount, 
                                         account=arg_account, side=arg_side)
                # self._cmd.poutput(f'{uindex}:End of free account records.')
                return

    def get_datetime_str(self, input: str):
        if not input:
            raise ValueError
        input = input.lower().strip()
        if input == '*':
            input = accounting_system.get_active_date()
        tz = tzlocal()
        moment = datetime.now(tz=tz)
        match(input):
            case 'now':
                pass
            case 'today':
                moment = datetime(year=moment.year, month=moment.month, day=moment.day, tzinfo=tz)
            case 'first_day_prev_month':
                moment = datetime(year=moment.year, month=moment.month, day=1, tzinfo=tz)
                moment = moment + relativedelta(month=-1)
            case 'last_day_prev_month':
                moment = datetime(year=moment.year, month=moment.month, day=1, tzinfo=tz)
                moment = moment + relativedelta(days=-1)
            case 'first_day_this_month':
                moment = datetime(year=moment.year, month=moment.month, day=1, tzinfo=tz)
            case 'last_day_this_month':
                moment = datetime(year=moment.year, month=moment.month, day=1, tzinfo=tz)
                moment = moment + relativedelta(month=+1, days=-1)
            case 'first_day_next_month':
                moment = datetime(year=moment.year, month=moment.month, day=1, tzinfo=tz)
                moment = moment + relativedelta(month=+1)
            case 'last_day_next_month':
                moment = datetime(year=moment.year, month=moment.month, day=1, tzinfo=tz)
                moment = moment + relativedelta(month=+2, seconds=-1)
            case 'first_day_prev_year':
                moment = datetime(year=moment.year, month=1, day=1, tzinfo=tz)
                moment = moment + relativedelta(days=-1)
            case 'first_day_this_year':
                moment = datetime(year=moment.year, month=12, day=31, tzinfo=tz)
            case 'first_day_next_year':
                moment = datetime(year=moment.year, month=12, day=31, tzinfo=tz)
                moment = moment + relativedelta(years=+1)
            case 'last_day_prev_year':
                moment = datetime(year=moment.year, month=1, day=1, tzinfo=tz)
                moment = moment + relativedelta(seconds=-1)
            case 'last_day_this_year':
                moment = datetime(year=moment.year, month=1, day=1, tzinfo=tz)
                moment = moment + relativedelta(years=+1, seconds=-1)
            case 'last_day_next_year':
                moment = datetime(year=moment.year, month=1, day=1, tzinfo=tz)
                moment = moment + relativedelta(years=+2, seconds=-1)
            case _:
                return input
        return moment.isoformat(sep=' ')

    @cmd2.as_subcommand_to('create', 'entry', create2_entry_parser)
    def create_entry(self, ns: argparse.Namespace):
        journal_tag = ns.journal
        # journal_tag = accounting_system.selected["journal"]
        journal_entry = accounting_system.new_journal_entry(journal_tag)
        journal_entry.date = self.get_datetime_str(ns.date)
        journal_entry.description = ns.description
        journal_entry.reference = ns.reference
        self.fill_entry_fields(journal_entry, ns.fields)

        command_args = []
        command_args.append("create")
        command_args.append("entry")
        command_args.append(journal_tag)
        command_args.append(journal_entry.date)
        command_args.append(journal_entry.description)
        if journal_entry.reference:
            command_args.extend(['-ref', journal_entry.reference])
        command_args.extend(ns.fields)
        calculated_token = update_sec_token(command_args)



        if not self._cmd.in_script() and not self._cmd.in_pyscript():
            # If interactive session:
            # - output info in console and append command to startup script
            # head = f'------ New {journal_tag} entry ------'
            # self._cmd.poutput(head)
            # self.puts_journal_entry(journal_entry)
            self._cmd.poutput(journal_entry.full_str())

            with append_file("commands.txt") as comm:
                # comm.append("create")
                # comm.append("entry")
                # comm.append(journal_tag)
                # comm.append(journal_entry.date)
                # comm.append(journal_entry.description)
                # if journal_entry.reference:
                #     comm.extend(['-ref', journal_entry.reference])
                # comm.extend(ns.fields)
                # new_token = update_sec_token(comm)
                
                comm.extend(command_args)
                comm.extend(['--token', calculated_token])
        else:
            # Non-interactive session: token verification
            if calculated_token != ns.token:
                self._cmd.poutput(f"token mismatch; stored in file:{ns.token}, calculated from data in file:{calculated_token}")
                # raise ValueError(f"token mismatch; got {calculated_token}, expected {ns.token}")

        accounting_system.add_journal_entry(journal_entry)
        globals()["sec_token"] = calculated_token

    rud_entry_parser = cmd2.Cmd2ArgumentParser()
    rud_entry_parser.add_argument('-sid', '--sequence-identifier', required=True, type=int)
    rud_entry_parser.add_argument('-j', '--journal-symbol')

    @cmd2.as_subcommand_to('read', 'entry', rud_entry_parser)
    def read_entry(self, ns: argparse.Namespace):
        if ns.journal_symbol:
            journal_symbol = ns.journal_symbol
        else:
            journal_symbol = accounting_system.selected["journal"]
        journal: Journal = accounting_system.journals.get(journal_symbol, None)
        if not journal:
            raise ValueError(f'Unknown Journal tag "{journal_symbol}"')
        je: JournalEntry = None
        je = journal.get_by_sid(ns.sequence_identifier)
        if not je:
            raise ValueError(f'Journal Entry sid={ns.sequence_identifier} not found in journal "{journal_symbol}" ({journal.tag})')
        head = f'------ Read {journal_symbol} ({je.journal.tag}) entry {ns.sequence_identifier} ------'
        self._cmd.poutput(head)
        self.puts_journal_entry(je)
        self._cmd.poutput('-' * len(head))

    @cmd2.as_subcommand_to('update', 'entry', rud_entry_parser)
    def update_entry(self, ns: argparse.Namespace):
        self._cmd.poutput('updateing entry (if not closed)....')

    @cmd2.as_subcommand_to('delete', 'entry', rud_entry_parser)
    def delete_entry(self, ns: argparse.Namespace):
        if ns.journal_symbol:
            journal_symbol = ns.journal_symbol
        else:
            journal_symbol = accounting_system.selected["journal"]
        journal: Journal = accounting_system.journals.get(journal_symbol, None)

        if not journal:
            raise ValueError(f'Unknown Journal tag "{journal_symbol}"')
        je: JournalEntry = None
        je = journal.get_by_sid(ns.object_identifier)
        # if not je:
        #     raise ValueError(f'Journal Entry sid={ns.sequence_identifier} not found in journal "{journal_symbol}" ({journal.tag})')
        if je.post:
            raise ValueError(f'Journal Entry {ns.sequence_identifier} is posted in the ledger. Delete is not possible. Use "cancel entry" command to post correction into the ledger.')
        journal.journal_entries.remove(je)
        head = f'------ Delete {journal_symbol} ({je.journal.tag}) entry {ns.sequence_identifier} ------'
        self._cmd.poutput(head)
        self.puts_journal_entry(je)
        self._cmd.poutput('-' * len(head))
        self._cmd.poutput('DELETED')

    close_entry_parser = cmd2.Cmd2ArgumentParser()
    # close_entry_parser.add_argument('-s', '--selected-entry')
    close_entry_parser.add_argument('-j', '--journal-symbol', required=False, help="parent journal")
    close_entry_parser.add_argument('sid', nargs=(1,), help='single or multiple identfiers')

    @cmd2.as_subcommand_to('close', 'entry', close_entry_parser)
    def close_entry(self, ns: argparse.Namespace):
        if ns.journal_symbol:
            journal_symbol = ns.journal_symbol
        else:
            journal_symbol = accounting_system.selected["journal"]
        journal: Journal = accounting_system.journals.get(journal_symbol, None)
        if not journal:
            raise ValueError(f'Unknown Journal "{journal_symbol}"')
        
        journal_entries_to_post: list[JournalEntry] = []
        
        for je_sid in ns.sid:
            journal_entries_to_post.append(journal.get_by_sid(je_sid))

         # can the whole list of journal entries be posted?
        for je in journal_entries_to_post:
            je.can_post_this()

        # post the whole list of journal entries
        for je in journal_entries_to_post:
            je.post_this()
            self._cmd.poutput(f'POST: {je.post}')
            

    @cmd2.as_subcommand_to('cancel', 'entry', entry_parser)
    def cancel_entry(self, _: argparse.Namespace):
        self._cmd.poutput('If an entry is open (not posted yet), the cancel command simply removes the specified entry from journal.')
        self._cmd.poutput('If the entry is closed (posted into a ledger) - there are two methods available to cancel this entry:')
        self._cmd.poutput('  1) "reverse" method generates a duplicate of the original entry with reverse debit and credit accounts,')
        self._cmd.poutput('  2) "storno" method generates a duplicate of the original entry, but the amounts are registered with a negative sign.')

    list_entries_parser = cmd2.Cmd2ArgumentParser()
    list_entries_parser.add_argument('-date', '--matching-date', default=None, help='entry date RRRR-MM-DD')
    list_entries_parser.add_argument('-desc', '--matching-description', default=None, help='text in description')   
    list_entries_parser.add_argument('-ref', '--matching-reference', default=None, help='text in reference')

    @cmd2.as_subcommand_to('list', 'entries', list_entries_parser)
    def list_entries(self, ns: argparse.Namespace):
        # self._cmd.poutput('-SID-  ---Date---  -Status-  Description')
        self._cmd.poutput(JournalEntry.str_header())

        journal = accounting_system.get_journal(accounting_system.selected["journal"])
        for number, entry in enumerate(journal.journal_entries, 1):
            self._cmd.poutput(f'{entry}')
        self._cmd.poutput()      

@with_default_category('Period')
class LoadablePeriod(CommandSet):
    def __init__(self):
        super().__init__()

    # def do_accountingcommand(self, _: cmd2.Statement):
    #     self._cmd.poutput('Accounting command..')

    period_parser = cmd2.Cmd2ArgumentParser()
    period_parser.add_argument('style', choices=['YYYY', 'MM'])

    @cmd2.as_subcommand_to('create', 'period', period_parser)
    def create_period(self, _: argparse.Namespace):
        self._cmd.poutput('create period ....')

    @cmd2.as_subcommand_to('read', 'period', period_parser)
    def read_period(self, _: argparse.Namespace):
        self._cmd.poutput('read period ....')

    @cmd2.as_subcommand_to('delete', 'period', period_parser)
    def delete_period(self, _: argparse.Namespace):
        self._cmd.poutput('delete period ....')

    @cmd2.as_subcommand_to('close', 'period', period_parser)
    def close_period(self, _: argparse.Namespace):
        self._cmd.poutput('close period ....')

    @cmd2.as_subcommand_to('select', 'period', period_parser)
    def select_period(self, _: argparse.Namespace):
        self._cmd.poutput('select period ....')

class ExampleApp(cmd2.Cmd):
    """
    CommandSets are automatically loaded. Nothing needs to be done.
    """

    def __init__(self, *args, **kwargs):
        # gotta have this or neither the plugin or cmd2 will initialize
        super().__init__(*args, auto_load_commands=True, **kwargs)

        self._charts_of_accounts = LoadableChartsOfAccounts()
        self._journals = LoadableJournals()
        self._accounts = LoadableAccounts()
        self._entries = LoadableEntries()
        self._period = LoadablePeriod()

    load_parser = cmd2.Cmd2ArgumentParser()
    load_parser.add_argument('cmds', choices=['chart-of-accounts', 'journals', 'accounts', 'entries', 'accounting'])

    @with_argparser(load_parser)
    @with_category('Command Loading')
    def do_load(self, ns: argparse.Namespace):
        if ns.cmds == 'chart-of-accounts':
            try:
                self.register_command_set(self._charts_of_accounts)
                self.poutput('chart-of-accounts loaded')
            except ValueError:
                self.poutput('chart-of-accounts already loaded')

        if ns.cmds == 'journals':
            try:
                self.register_command_set(self._journals)
                self.poutput('Journals loaded')
            except ValueError:
                self.poutput('Journals already loaded')

        if ns.cmds == 'accounts':
            try:
                self.register_command_set(self._accounts)
                self.poutput('Accounts loaded')
            except ValueError:
                self.poutput('Accounts already loaded')

        if ns.cmds == 'entries':
            try:
                self.register_command_set(self._entries)
                self.poutput('Entries loaded')
            except ValueError:
                self.poutput('Entires already loaded')

        if ns.cmds == 'period':
            try:
                self.register_command_set(self._period)
                self.poutput('Period loaded')
            except ValueError:
                self.poutput('Period already loaded')

    unload_parser = cmd2.Cmd2ArgumentParser()
    unload_parser.add_argument('cmds', choices=['journals', 'accounts', 'entries', 'period'])

    @with_argparser(unload_parser)
    def do_unload(self, ns: argparse.Namespace):
        if ns.cmds == 'journals':
            self.unregister_command_set(self._journals)
            self.poutput('Journals unloaded')

        if ns.cmds == 'accounts':
            self.unregister_command_set(self._accounts)
            self.poutput('Acounts unloaded')

        if ns.cmds == 'entries':
            self.unregister_command_set(self._entries)
            self.poutput('Entries unloaded')

        if ns.cmds == 'period':
            self.unregister_command_set(self._period)
            self.poutput('period unloaded')

    create_parser = cmd2.Cmd2ArgumentParser()
    create_subparsers = create_parser.add_subparsers(title='item', help='item to create')

    @with_argparser(create_parser)
    def do_create(self, ns: argparse.Namespace):
        handler = ns.cmd2_handler.get()
        if handler is not None:
            # Call whatever subcommand function was selected
            handler(ns)
        else:
            # No subcommand was provided, so call help
            self.poutput('This command does nothing without sub-parsers registered')
            self.do_help('create')

    read_parser = cmd2.Cmd2ArgumentParser()
    read_subparsers = read_parser.add_subparsers(title='item', help='item to read')

    @with_argparser(read_parser)
    def do_read(self, ns: argparse.Namespace):
        handler = ns.cmd2_handler.get()
        if handler is not None:
            # Call whatever subcommand function was selected
            handler(ns)
        else:
            # No subcommand was provided, so call help
            self.poutput('This command does nothing without sub-parsers registered')
            self.do_help('read')

    update_parser = cmd2.Cmd2ArgumentParser()
    update_subparsers = update_parser.add_subparsers(title='item', help='update item')

    @with_argparser(update_parser)
    def do_update(self, ns: argparse.Namespace):
        handler = ns.cmd2_handler.get()
        if handler is not None:
            # Call whatever subcommand function was selected
            handler(ns)
        else:
            # No subcommand was provided, so call help
            self.poutput('This command does nothing without sub-parsers registered')
            self.do_help('update')

    delete_parser = cmd2.Cmd2ArgumentParser()
    delete_subparsers = delete_parser.add_subparsers(title='item', help='item to delete')

    @with_argparser(delete_parser)
    def do_delete(self, ns: argparse.Namespace):
        handler = ns.cmd2_handler.get()
        if handler is not None:
            # Call whatever subcommand function was selected
            handler(ns)
        else:
            # No subcommand was provided, so call help
            self.poutput('This command does nothing without sub-parsers registered')
            self.do_help('delete')

    open_parser = cmd2.Cmd2ArgumentParser()
    open_subparsers = open_parser.add_subparsers(title='item', help='item to open')

    @with_argparser(open_parser)
    def do_open(self, ns: argparse.Namespace):
        handler = ns.cmd2_handler.get()
        if handler is not None:
            # Call whatever subcommand function was selected
            handler(ns)
        else:
            # No subcommand was provided, so call help
            self.poutput('This command does nothing without sub-parsers registered')
            self.do_help('open')

    close_parser = cmd2.Cmd2ArgumentParser()
    close_subparsers = close_parser.add_subparsers(title='item', help='item toclose')

    @with_argparser(close_parser)
    def do_close(self, ns: argparse.Namespace):
        handler = ns.cmd2_handler.get()
        if handler is not None:
            # Call whatever subcommand function was selected
            handler(ns)
        else:
            # No subcommand was provided, so call help
            self.poutput('This command does nothing without sub-parsers registered')
            self.do_help('close')

    select_parser = cmd2.Cmd2ArgumentParser()
    select_subparsers = select_parser.add_subparsers(title='item', help='set item as currenly active')

    @with_argparser(select_parser)
    def do_select(self, ns: argparse.Namespace):
        handler = ns.cmd2_handler.get()
        if handler is not None:
            # Call whatever subcommand function was selected
            handler(ns)
            self.prompt = ansi.style(globals()["prompt"], fg=ansi.Fg.CYAN)
        else:
            # No subcommand was provided, so call help
            self.poutput('This command does nothing without sub-parsers registered')
            self.do_help('select')

    list_parser = cmd2.Cmd2ArgumentParser()
    list_subparsers = list_parser.add_subparsers(title='filter', help='filter items')

    @with_argparser(list_parser)
    def do_list(self, ns: argparse.Namespace):
        handler = ns.cmd2_handler.get()
        if handler is not None:
            # Call whatever subcommand function was selected
            handler(ns)
        else:
            # No subcommand was provided, so call help
            self.poutput('This command does nothing without sub-parsers registered')
            self.do_help('list')  

    cancel_parser = cmd2.Cmd2ArgumentParser()
    cancel_subparsers = cancel_parser.add_subparsers(title='item', help='entry to post')

    @with_argparser(cancel_parser)
    def do_cancel(self, ns: argparse.Namespace):
        handler = ns.cmd2_handler.get()
        if handler is not None:
            # Call whatever subcommand function was selected
            handler(ns)
        else:
            # No subcommand was provided, so call help
            self.poutput('This command does nothing without sub-parsers registered')
            self.do_help('cancel')

    def do_status(self, args):
        self.poutput('+---------------------------------------------+')
        self.poutput('|  Period | Ledger |   GJ   |   SJ   |   PJ   |')
        self.poutput('|---------------------------------------------|')
        self.poutput('| 2023-BB |     1  |        |  ----  |  ----  |')
        self.poutput('| 2023-01 |    16  |    66  |     5  |     8  |')
        self.poutput('| 2023-02 |    55  |*    3 *|     3  |     2  |')
        self.poutput('| 2023 03 |    23  |     2  |     5  |     3  |') 
        self.poutput('| 2023 04 |    85  |     6  |     5  |     8  |')
        self.poutput('| 2023 05 |    95  |     1  |     3  |     2  |')
        self.poutput('| 2023 06 |    72  |     2  |     5  |     3  |')
        self.poutput('| 2023 07 |  ----  |  ----  |  ----  |  ----  |') 
        self.poutput('| 2023 08 |  ----  |  ----  |  ----  |  ----  |') 
        self.poutput('| 2023 09 |  ----  |  ----  |  ----  |  ----  |') 
        self.poutput('| 2023 10 |  ----  |  ----  |  ----  |  ----  |') 
        self.poutput('| 2023 11 |  ----  |  ----  |  ----  |  ----  |') 
        self.poutput('| 2023 12 |  ----  |  ----  |  ----  |  ----  |') 
        self.poutput('| 2023 13 |  ----  |  ----  |  ----  |  ----  |') 
        self.poutput('+---------------------------------------------+')

        # self.poutput('         [BB]  [01]  [02]  [03]  [04]  [05]  [06]  [07]  [08]  [09]  [10]  [11]  [12]  [13]')
        # self.poutput('            -     -     -     -     -     -     3     2     6     7     -     -     -     -')       
        # self.poutput('           27    28    19    17    17    29    37    13     -     -     -     -     -     -')

if __name__ == '__main__':
    import sys
    app = ExampleApp(include_py=True, include_ipy=True, 
                    startup_script='commands.txt',
                    persistent_history_file='ac_history.dat')
    app.self_in_py = True  # Enable access to "self" within the py command
    app.debug = True  # Show traceback if/when an exception occurs
    accounting_system = s()
    # load_state(accounting_system)

    set_prompt_part_1(accounting_system.selected["period"])
    set_prompt_part_2(accounting_system.selected["journal"])
    app.prompt = prompt

    app.cmdloop(f"Accounting Commander")

    

    