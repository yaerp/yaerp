import argparse
from datetime import datetime
from hashlib import blake2s
from dateutil.tz import *
from dateutil.relativedelta import *
from itertools import repeat
import cmd2
from cmd2 import CommandSet, CompletionMode, with_argparser, with_category, with_default_category, ansi
from accounting_system3 import empty_accounting_system, setup_tiny_accounting_system
from yaerp.accounting.account3 import AccountRecord, AccountSide
from yaerp.accounting.journal3 import Journal, JournalEntry
from yaerp.accounting.marker import Marker
from yaerp.accounting.tree3 import AccountTree
from yaerp.tools.dt import datetime_str
from yaerp.tools.file import append_file
from yaerp.tools.secure_token import secure_token
from yaerp.tools.sid import SID
from yaerp.tools.text import dict_to_str, iter_to_str

accounting_system = None

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


def store_command(cmd, command_args, token_from_file, output_info):
    secure_token().update(command_args)
    # inp = secure_token().plain()

    if not cmd.in_script() and not cmd.in_pyscript():
        # If interactive session:
        cmd.poutput(output_info)

        file_name = f"{globals()['session_name']}.ac"

        with append_file(file_name) as comm:
            comm.extend(command_args)
            comm.extend(['--token', secure_token().token()])
    else:
        # Non-interactive session: token verification
        if secure_token().token() != token_from_file:
            cmd.poutput(f"token mismatch; stored in file:{token_from_file}, calculated from data in file:{secure_token().token()}")

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
        txt = []
        txt.append(f'{" [Tag]":<10} {" [Name]":<26} {"[Sum Dr]":>10}  {"[Sum Cr]":>10}  {"[Sum Balance]":>14}')
        for node in accounting_system.coa.get_internals_gen():
            txt.append(' '*len(node.get_node_path()) + node.short_str())
        self._cmd.poutput('\n'.join(txt))

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
    create_account_parser.add_argument('-p', '--parent', required=False, help='Parent account tag in the Chart of Accounts or "root"')
    create_account_parser.add_argument('-l', '--ledger', required=True, help='General Ledger')
    create_account_parser.add_argument('-n', '--name', required=True, help='Full account name')
    create_account_parser.add_argument('-c', '--currency', required=True, help='Currency symbol (3-character code)')
    create_account_parser.add_argument('-token', '--token', default=None, help="Secure token to seal commands stored in script. ")
    create_account_parser.add_argument('-m', '--markers', nargs=(0,), help='Flag marker(s) semi-colon separated, i.e: "-m ASSETS" or "-m ASSETS STOCK"')

    @cmd2.as_subcommand_to('create', 'account', create_account_parser)
    def create_account(self, ns: argparse.Namespace):
        # prepare command
        ac = accounting_system.accounts.get(ns.tag, None)
        if ac:
            raise ValueError(f"Another Account exist with tag {ns.tag}")
        
        par_tree = None
        if ns.parent:
            if ns.parent == "root":
                par_tree = accounting_system.coa
            else:
                par_tree = accounting_system.coa.get_node(tag=ns.parent)
            if not par_tree:
                raise ValueError(f"Not found parent node {ns.parent}")
        else:
            par_tree = accounting_system.coa

        mark_list = []
        if ns.markers:
            for m_str in ns.markers:
                m = Marker.instance_mark_by_name(m_str)
                if m not in mark_list:
                    mark_list.append(m)
            
        # run command
        accounting_system.add_account(ns.tag, ns.ledger, ns.currency, ns.name)
        ac = accounting_system.accounts.get(ns.tag)
        if par_tree:
            AccountTree(ac, parent=par_tree)
        ac_node = accounting_system.coa.get_node(tag=ac.tag)
        if mark_list:
            for m in mark_list:
                ac_node.marker.add(m)
        ac_node.marker.extend(par_tree.marker.to_list()) # copy parent marks (inheritance)
        # store command
        command_args = []
        command_args.extend(["create", "account"])
        command_args.extend(["--tag", ac.tag])
        command_args.extend(["--currency", ac.currency])
        command_args.extend(["--ledger", ac.ledger.tag])
        command_args.extend(["--name", ac.name])
        if ns.parent:
            command_args.extend(["--parent", ns.parent])
        if mark_list:
            command_args.append("--markers")
            for m in mark_list:
                command_args.append(str(m))
        store_command(self._cmd, command_args, ns.token, ac_node.full_str())

    account_parser = cmd2.Cmd2ArgumentParser()
    account_parser.add_argument('-t', '--tag', required=False)
    account_parser.add_argument('-n', '--name', required=False)

    @cmd2.as_subcommand_to('read', 'account', account_parser)
    def read_account(self, ns: argparse.Namespace):
        if ns.tag:
            ac = accounting_system.get_account(ns.tag)
            ac_node = accounting_system.coa.get_node(tag=ac.tag)
            ac_path = ac_node.get_account_path()
            for index, tag in enumerate(ac_path):
                if index == 0 and tag is None:
                    pass
                    # self._cmd.poutput('Chart of Accounts')
                else:
                    self._cmd.poutput(f'{" "*index}{tag}')
            self._cmd.poutput(ac_node.full_str()) 
        elif ns.name:
            raise NotImplementedError()

    update_account_parser = cmd2.Cmd2ArgumentParser()
    update_account_parser.add_argument('-t', '--tag', required=True)
    update_account_parser.add_argument('-nn', '--new-name', required=False)
    update_account_parser.add_argument('-nt', '--new-tag', required=False)
    update_account_parser.add_argument('-m', '--markers', required=False, nargs=(1,), help='Create new set of mark(s) in the account tree, i.e: "-m ASSETS" or "-m ASSETS STOCK"') 
    update_account_parser.add_argument('-am', '--add-markers', required=False, nargs=(1,), help='Add mark(s) to exsting marker set in the account tree, i.e: 1 marker: "-am ASSETS" or more than 1: "-am EXPENSES COST_OF_GOODS_SOLD"')
    update_account_parser.add_argument('-dm', '--del-markers', required=False, nargs=(1,), help='Delete mark(s) from existing marker set in the account tree, i.e: "-dm ASSETS" or "-dm ASSETS STOCK"') 
    update_account_parser.add_argument('-token', '--token', default=None, help='Secure token to seal commands stored in script. ')
    
    @cmd2.as_subcommand_to('update', 'account', update_account_parser)
    def update_account(self, ns: argparse.Namespace):

        ac = accounting_system.get_account(ns.tag)
        ac_tree = accounting_system.coa.get_node(tag=ac.tag)
        if ns.markers:
            if ns.add_markers or ns.del_markers:
                raise ValueError('-m / --markers cannot be used with -am / --add-markers / -dm / --del-markers')
        # run command
        if ns.new_name:
            ac.name = ns.new_name

        mark_list = []
        if ns.markers:
            for m_str in ns.markers:
                m = Marker.instance_mark_by_name(m_str)
                if m not in mark_list:
                    mark_list.append(m)
            ac_tree.marker = Marker(*mark_list) 
            for internal_nodes in ac_tree.get_internals_gen():
                internal_nodes.marker = Marker(*mark_list)

        add_mark_set = set()          
        if ns.add_markers:
            for m_str in ns.add_markers:
                m = Marker.instance_mark_by_name(m_str)
                add_mark_set.add(m)

        del_mark_set = set()
        if ns.del_markers:
            for m_str in ns.del_markers:
                m = Marker.instance_mark_by_name(m_str)
                del_mark_set.add(m)

        if add_mark_set or del_mark_set:
            marks_to_really_add = add_mark_set.difference(del_mark_set)
            marks_to_really_del = del_mark_set.difference(add_mark_set)
            ac_tree.marker.extend(marks_to_really_add)
            ac_tree.marker.reduce(marks_to_really_del)
            for internal_nodes in ac_tree.get_internals_gen():
                internal_nodes.marker.extend(marks_to_really_add)
                internal_nodes.marker.reduce(marks_to_really_del)

        if ns.new_tag: # at the very end change tag if 
            if ns.new_tag in accounting_system.accounts.keys():
                raise ValueError(f'New tag found in existing Account "{ns.new_tag}"')
            ac.tag = ns.new_tag
            accounting_system.accounts[ac.tag] = ac
            ac = accounting_system.get_account(ns.new_tag)
            del accounting_system.accounts[ns.tag]
            if not ac:
                raise ValueError("cannot get account with changed tag")
        # store command
        command_args = []
        command_args.extend(["update", "account"])
        command_args.extend(["--tag", ns.tag])
        if ns.new_tag:
            command_args.extend(["--new-tag", ac.tag])
        if ns.new_name:
            command_args.extend(["--new-name", ac.name])
        if mark_list:
            command_args.append('--markers')
            for m in mark_list:
                command_args.append(str(m))
        if add_mark_set:
            command_args.append('--add-markers')
            for m in add_mark_set:
                command_args.append(str(m))
        if del_mark_set:
            command_args.append('--del-markers')
            for m in del_mark_set:
                command_args.append(str(m))
        store_command(self._cmd, command_args, ns.token, ac_tree.full_str())

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
        txt = []
        txt.append(f'{" [Tag]":<10} {" [Name]":<26} {"[Dr]":>10}  {"[Cr]":>10}  {"[Balance]":>11}')
        for account in accounting_system.accounts.values():
            txt.append(account.short_str())
        self._cmd.poutput('\n'.join(txt))

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
                # return
                break

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

    create2_entry_parser = cmd2.Cmd2ArgumentParser()
    create2_entry_parser.add_argument('journal', help="Journal tag")
    create2_entry_parser.add_argument('date', help="Local date and (optional) time in form 'RRRR-MM-DD hh:mm:ss' (i.e 2023-11-23 11:57:24) or one of the following phrases:\n    'now', 'today', 'prev_month_last_day', 'this_month_last_day', 'next_month_last_day'")
    create2_entry_parser.add_argument('description', help='transaction description, i.e "Purchase of materials"') 
    create2_entry_parser.add_argument('-ref', '--reference', default=None)
    create2_entry_parser.add_argument('-token', '--token', default=None, help="Secure token to seal commands stored in script. ")
    create2_entry_parser.add_argument('fields', nargs=(2,), help='debit/credit entry or info data in order of apperance in the journal. One of the following formats "Amount" (i.e 100.00) or "Account/Amount" (i.e 450/100.00) or "Side/Account/Amount" (i.e Dr/450/100.00) or "Some text" (for info fields)')

    @cmd2.as_subcommand_to('create', 'entry', create2_entry_parser)
    def create_entry(self, ns: argparse.Namespace):
        # preparing command
        journal_tag = ns.journal
        journal_entry = accounting_system.new_journal_entry(journal_tag)
        journal_entry.date = datetime_str(ns.date)
        journal_entry.description = ns.description
        journal_entry.reference = ns.reference
        self.fill_entry_fields(journal_entry, ns.fields)
        if not journal_entry.is_balanced():
            raise ValueError('Unbalanced journal entry')
        if journal_entry.is_zeroed():
            raise ValueError('Empty journal entry')
        # executing command
        accounting_system.add_journal_entry(journal_entry)
        # storing command
        command_args = []
        command_args.append("create")
        command_args.append("entry")
        command_args.append(journal_tag)
        command_args.append(journal_entry.date)
        command_args.append(journal_entry.description)
        if journal_entry.reference:
            command_args.extend(['-ref', journal_entry.reference])
        command_args.extend(ns.fields)
        store_command(self._cmd, command_args, ns.token, journal_entry.full_str())

    rud_entry_parser = cmd2.Cmd2ArgumentParser()
    # rud_entry_parser.add_argument('-sid', '--sequence-identifier', required=True, type=int)
    # rud_entry_parser.add_argument('-j', '--journal-symbol', help='optional journal tag')
    rud_entry_parser.add_argument('sid', nargs=(1,), help='sid identfier(s)')

    @cmd2.as_subcommand_to('read', 'entry', rud_entry_parser)
    def read_entry(self, ns: argparse.Namespace):
        for sid in ns.sid:
            je = accounting_system.get_journal_entry(None, sid=sid)
            self._cmd.poutput(je.full_str())

    update_entry_parser = cmd2.Cmd2ArgumentParser()
    update_entry_parser.add_argument('-sid', help="Journal Entry (j/e) SID", required=True)
    update_entry_parser.add_argument('-date', '--date', 
help=
'''Local date and (optional) time in form 'RRRR-MM-DD hh:mm:ss' 
   (i.e 2023-11-23 11:57:24)
   or one of the following phrases:
    
    NOW, TODAY, YESTERDAY, TOMORROW

    FDPY, LDPY, LSPY (First Day / Last Day / Last Second of Previous Year),
    FDTY, LDTY, LSTY  (.. of This Year),
    FDNY, LDNY, LSNY  (.. of Next Year),

    FDPM, LDPM, LSPM (First Day/Last Day/Last Second of Previous Month),
    FDTM, LDTM, LSTM  (.. of This Month),
    FDNM, LDNM, LSNM  (.. of Next Month)
    ''')
    update_entry_parser.add_argument('-desc', '--description', help='transaction description, i.e "Purchase of materials"') 
    update_entry_parser.add_argument('-ref', '--reference', default=None)
    update_entry_parser.add_argument('-token', '--token', default=None, help="Secure token to seal commands stored in script. ")

    @cmd2.as_subcommand_to('update', 'entry', update_entry_parser)
    def update_entry(self, ns: argparse.Namespace):
        je = accounting_system.get_journal_entry(sid=ns.sid)
        if not je:
            raise ValueError(f"Journal Entry {ns.sid} not found")
        if je.post:
            raise ValueError(f"Journal Entry {ns.sid} is posted and cannot be updated.")
        # execute command
        if ns.date:
            je.del_from_journal() # remove this j/e from the journal (je.date is part of sorting key in journal collection)
            date = datetime_str(ns.date)
            je.date = date
            je.put_into_journal() # insert this j/e back into the journal (with new key)
        if ns.description:
            je.description = ns.description
        if ns.reference:
            je.reference = ns.reference
        # store command
        command_args = []
        command_args.extend(["update", "entry"])
        command_args.extend(['-sid', str(je.sid)])
        if ns.date:
            command_args.extend(["-date", je.date])
        if ns.description:
            command_args.extend(["-desc", je.description])
        if ns.reference:
            command_args.extend(["-ref", je.reference])
        store_command(self._cmd, command_args, ns.token, je.full_str())

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
    close_entry_parser.add_argument('-token', '--token', default=None, help="Secure token to seal commands stored in script. ")
    close_entry_parser.add_argument('sid', nargs=(1,), help='single or multiple identfiers')

    @cmd2.as_subcommand_to('close', 'entry', close_entry_parser)
    def close_entry(self, ns: argparse.Namespace):
        
        journal_entries_to_post: list[JournalEntry] = []
        
        for je_sid in ns.sid:
            je = accounting_system.get_journal_entry(ns.journal_symbol, sid=je_sid)
            if je not in journal_entries_to_post:
                journal_entries_to_post.append(je)

         # can the whole list of journal entries be posted?
        for je in journal_entries_to_post:
            je.can_post_this()

        # post the whole list of journal entries
        for je in journal_entries_to_post:
            je.post_this()

        command_args = []
        command_args.extend(["close", "entry"])
        if ns.journal_symbol:
            command_args.extend(["-j", ns.journal_symbol])
        for je in journal_entries_to_post:
            command_args.append(str(je.sid))
        store_command(self._cmd, command_args, ns.token, "POSTED")

    cancel_help = '\n'.join([
        'Canceling a Journal Entry depends on the status of the Journal Entry.',
        '',
        'If an Entry is not posted yet, the cancel command simply REMOVES ',
        'the specified Entry. ',
        '',
        'To cancel Entry that is posted in the ledger there are two methods ',
        'available : ',
        '  1) REVERSE method (-r) generates a duplicate of the original ',
        '     entry with reverse debit and credit accounts, ',
        '  2) STORNO method (default) generates a duplicate of the original ',
        '     entry, but the amounts are registered with a negative sign.',
        '  Note that canceling entries are posted immediately to the ledger.'
    ])
    cancel_entry_parser = cmd2.Cmd2ArgumentParser(description=cancel_help)
    cancel_entry_parser.add_argument('-m', '--method', choices=("REMOVE", "REVERSE", "STORNO"), default="STORNO", help="Canceling method (default STORNO)")
    cancel_entry_parser.add_argument('-token', '--token', default=None, help="Secure token to seal commands stored in script. ", )
    cancel_entry_parser.add_argument('-j', '--journal-symbol', required=False, help="parent journal")
    cancel_entry_parser.add_argument('sid', nargs=(1,), help='single or multiple identfiers')

    @cmd2.as_subcommand_to('cancel', 'entry', cancel_entry_parser, help=cancel_help)
    def cancel_entry(self, ns: argparse.Namespace):
        # prepare command
        je_sids_to_cancel: list[str] = []
        for je_sid in ns.sid:
            # ommit dublets
            if je_sid not in je_sids_to_cancel:
                je_sids_to_cancel.append(je_sid)
        # run command
        accounting_system.bulk_cancel_journal_entries(ns.journal_symbol, sids=je_sids_to_cancel, method=ns.method)
        # store command
        command_args = []
        command_args.extend(["cancel", "entry"])
        if ns.journal_symbol:
            command_args.extend(["-j", ns.journal_symbol])
        if ns.method != "STORNO":
            command_args.extend(["-m", ns.method])
        command_args.append(je_sids_to_cancel)
        store_command(self._cmd, command_args, ns.token, "POSTED")

    list_entries_parser = cmd2.Cmd2ArgumentParser()
    list_entries_parser.add_argument('-date', '--matching-date', default=None, help='entry date RRRR-MM-DD')
    list_entries_parser.add_argument('-desc', '--matching-description', default=None, help='text in description')   
    list_entries_parser.add_argument('-ref', '--matching-reference', default=None, help='text in reference')
    list_entries_parser.add_argument('-j', '--journal-symbol', default=None, help='journal')
    @cmd2.as_subcommand_to('list', 'entries', list_entries_parser)
    def list_entries(self, ns: argparse.Namespace):
        # self._cmd.poutput('-SID-  ---Date---  -Status-  Description')
        # self._cmd.poutput(JournalEntry.str_header())

        matching_je_generator = accounting_system.match_journal_entries_gen(
            ns.matching_date,
            ns.matching_description,
            ns.matching_reference,
            ns.journal_symbol)
        number = 0
        for number, entry in enumerate(matching_je_generator, 1):
            self._cmd.poutput(f'{entry}')
        self._cmd.poutput(f'{number} entries found')      

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

    if len(sys.argv) == 1:
        startup_script = "default.ac"
    elif len(sys.argv) == 2:
        startup_script = sys.argv[1]
        if not startup_script.lower().endswith(".ac"):
            startup_script += ".ac"
    else:
        raise ValueError('Expecting empty or one argument (startup text file)')

    secure_token(open_number=True)
    app = ExampleApp(include_py=True, include_ipy=True, 
                    startup_script=startup_script,
                    persistent_history_file='history.dat',
                    allow_cli_args=False)
    app.self_in_py = True  # Enable access to "self" within the py command
    app.debug = True  # Show traceback if/when an exception occurs
    accounting_system = empty_accounting_system()
    # load_state(accounting_system)

    # set_prompt_part_1(accounting_system.selected["period"])
    # set_prompt_part_2(accounting_system.selected["journal"])
    # app.prompt = prompt
    globals()['session_name'] = startup_script.removesuffix('.ac')
    app.prompt = globals()['session_name'] + '> '

    app.cmdloop(f"Accounting Commander")

    

    