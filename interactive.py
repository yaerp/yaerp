#!/usr/bin/env python
"""A simple cmd2 application."""
import argparse
from typing import Dict, Iterable, List, Optional, TextIO
import cmd2
from cmd2.command_definition import CommandSet

from accounting_system import AccountingSystem


class FirstApp(cmd2.Cmd):
    """A simple cmd2 application."""
    def __init__(self, completekey: str = 'tab', stdin: TextIO | None = None, stdout: TextIO | None = None, *, persistent_history_file: str = '', persistent_history_length: int = 1000, startup_script: str = '', silence_startup_script: bool = False, include_py: bool = False, include_ipy: bool = False, allow_cli_args: bool = True, transcript_files: List[str] | None = None, allow_redirection: bool = True, multiline_commands: List[str] | None = None, terminators: List[str] | None = None, shortcuts: Dict[str, str] | None = None, command_sets: Iterable[CommandSet] | None = None, auto_load_commands: bool = True) -> None:
        self.acc_sys = AccountingSystem()
        self.update_prompt()
        shortcuts = cmd2.DEFAULT_SHORTCUTS
        shortcuts.update({'&': 'speak'})
        super().__init__(completekey, stdin, stdout, persistent_history_file=persistent_history_file, persistent_history_length=persistent_history_length, startup_script=startup_script, silence_startup_script=silence_startup_script, include_py=include_py, include_ipy=include_ipy, allow_cli_args=allow_cli_args, transcript_files=transcript_files, allow_redirection=allow_redirection, multiline_commands=multiline_commands, terminators=terminators, shortcuts=shortcuts, command_sets=command_sets, auto_load_commands=auto_load_commands)

        # Make maxrepeats settable at runtime
        self.maxrepeats = 3
        self.add_settable(cmd2.Settable('maxrepeats', int, 'max repetitions for speak command', self))

    def update_prompt(self):
        self.prompt_part_1 = self.acc_sys.active_journal_name
        self.prompt_part_2 = self.acc_sys.active_date_argument
        self.prompt_part_3 = self.acc_sys.active_time_argument
        self.prompt = f"(\"{self.prompt_part_1}\"/{self.prompt_part_2}/{self.prompt_part_3}) "

    speak_parser = cmd2.Cmd2ArgumentParser()
    speak_parser.add_argument('-p', '--piglatin', action='store_true', help='atinLay')
    speak_parser.add_argument('-s', '--shout', action='store_true', help='N00B EMULATION MODE')
    speak_parser.add_argument('-r', '--repeat', type=int, help='output [n] times')
    speak_parser.add_argument('param', nargs='*', help='\"argument value\"')

    date_parser = cmd2.Cmd2ArgumentParser()
    date_parser.add_argument('-S', '--set-current-date', action='store_true', help='set current date (\"RRRR-MM-DD\", \"today\", \"opening\" or \"closing\")')
    date_parser.add_argument('-D', '--add-days', default=5, action='store_true', help='adds days to current date')
    date_parser.add_argument('-W', '--add-weeks', action='store_true', help='adds days to current date')    
    date_parser.add_argument('-M', '--add-months', action='store_true', help='adds months to current date')
    date_parser.add_argument('-Y', '--add-years', action='store_true', help='adds years to current date')  
    date_parser.add_argument('-LD', '--last-day-in-month', action='store_true', help='adds months to current date')
    date_parser.add_argument('param', nargs='+', help='\"argument value\"')

    time_parser = cmd2.Cmd2ArgumentParser()
    time_parser.add_argument('-s', '--set-current-time', action='store_true', default='now', help='set current time (\"HH:MM\" or \"now\"')
    time_parser.add_argument('-H', '--add-hours', action='store_true', help='adds hours to the current time')
    time_parser.add_argument('-M', '--add-minutes', action='store_true', help='adds minutes to the current time') 
    time_parser.add_argument('param', nargs='*', help='\"argument value\"')

    journal_parser = cmd2.Cmd2ArgumentParser()
    journal_parser.add_argument('-s', '--set-current-journal',  help='select current journal')    
    journal_parser.add_argument('-i', '--info',  help='print journal parameters (names, fields, entry stats)')
    journal_parser.add_argument('-N', '--new-journal', default='all', help='creates new journal (without the account fields)')
    journal_parser.add_argument('-AF', '--append-field', default='all', help='append new field to the current journal')
    journal_parser.add_argument('-RF', '--remove-field', default='all', help='remove field from the current journal')
    journal_parser.add_argument('param', nargs='*', help='\"argument value\"')

    entry_parser = cmd2.Cmd2ArgumentParser()
    entry_parser.add_argument('-n', '--new-entry', default=5, action='store_true', help='new journal entry')
    entry_parser.add_argument('-r', '--remove-entry', action='store_true', help='remove journal entry (if not posted)')
    entry_parser.add_argument('-i', '--info', action='store_true', help='print entry info')
    entry_parser.add_argument('-POST', '--post-entry', type=int, help='post the entry into the ledger')
    entry_parser.add_argument('-STORNO', '--storno-entry', action='store_true', help='reverse the posted Entry by new Entry with negative amounts (red storno)')
    entry_parser.add_argument('param', nargs='+', help='\"argument value\"')

    ledger_parser = cmd2.Cmd2ArgumentParser()
    ledger_parser.add_argument('-i', '--info', action='store_true', help='print ledger info')
    ledger_parser.add_argument('-list', '--list-ledger-entries', type=int, help='list journal entries that already posted to the ledger')
    ledger_parser.add_argument('-bs', '--balance-sheet', action='store_true', help='calculate and print the Balance Sheet')
    ledger_parser.add_argument('-is', '--income-statement', action='store_true', help='calculate and print the Income Statement (P&L)')
    ledger_parser.add_argument('param', nargs='*', help='\"argument value\"')

    account_parser = cmd2.Cmd2ArgumentParser()
    account_parser.add_argument('-i', '--info', action='store_true', help='print account info')
    account_parser.add_argument('-list', '--list-account-entries', type=int, help='list account entries')
    account_parser.add_argument('-bl', '--balance', action='store_true', help='calculate account balance')
    account_parser.add_argument('-cr', '--credit', action='store_true', help='calculate credit summary without internal accounts')
    account_parser.add_argument('-dr', '--debit', action='store_true', help='calculate debit summary without internal accounts')    
    account_parser.add_argument('-crr', '--credit-recursive', action='store_true', help='calculate credit summary including internal accounts')
    account_parser.add_argument('-drr', '--debit-recursive', action='store_true', help='calculate debit summary including internal accounts')  
    account_parser.add_argument('param', nargs='*', help='\"argument value\"')

    list_parser = cmd2.Cmd2ArgumentParser()
    list_parser.add_argument('-j', '--journals', action='store_true', help='print a list of journals')
    list_parser.add_argument('-a', '--accounts', type=int, help='print a list of accounts')
    list_parser.add_argument('-je', '--journal-entries', action='store_true', help='print a list of journal entries')
    list_parser.add_argument('-jenp', '--journal-entries-not-posted', action='store_true', help='print not posted journal entries')
    list_parser.add_argument('-jep', '--journal-entries-posted', action='store_true', help='print posted journal entries')
    list_parser.add_argument('-lp', '--ledger-posts', action='store_true', help='print a list of jurnals entries posted in ledger')

    @cmd2.with_argparser(speak_parser)
    def do_speak(self, args):
        """Repeats what you tell me to."""
        words = []
        for word in args.words:
            if args.piglatin:
                word = '%s%say' % (word[1:], word[0])
            if args.shout:
                word = word.upper()
            words.append(word)
        repetitions = args.repeat or 1
        for _ in range(min(repetitions, self.maxrepeats)):
            # .poutput handles newlines, and accommodates output redirection too
            self.poutput(' '.join(words))
            self.read_input()
            

# 
# admin add journal "Sales Journal" -> mode define "journal fields"
# 
# 

    @cmd2.with_argparser(date_parser)
    def do_date(self, args):
        """ date functions"""
        sauce = self.select('sweet salty dfg bnmb wewrr iop fgjghj qweqw vbcvb zxczxc etertry iuopio', 'Sauce? ', )
        result = '{food} with {sauce} sauce, yum!'
        result = result.format(food='meat', sauce=sauce)
        self.stdout.write(result + '\n')
        self.acc_sys.active_date_argument = args.param[0]
        self.update_prompt()

    @cmd2.with_argparser(time_parser)
    def do_time(self, args):
        """ time functions"""
        self.acc_sys.active_time_argument = args.param[0]
        self.update_prompt()

    @cmd2.with_argparser(journal_parser)
    def do_journal(self, args):
        """ journal functions"""
        self.acc_sys.active_journal_name = args.param[0]
        self.update_prompt()

    @cmd2.with_argparser(entry_parser)
    def do_entry(self, args):
        """ journal entry functions"""
        self.poutput(args)

    @cmd2.with_argparser(ledger_parser)
    def do_ledger(self, args):
        """ ledger functions"""
        self.prompt_part_2 = args.param[0]
        self.prompt = f"({self.prompt_part_1} / {self.prompt_part_2}) "

    @cmd2.with_argparser(account_parser)
    def do_account(self, args):
        """ account functions"""
        self.prompt_part_2 = args.param[0]
        self.prompt = f"({self.prompt_part_1} / {self.prompt_part_2}) "  

    @cmd2.with_argparser(list_parser)
    def do_list(self, args):
        """ list queries"""
        self.prompt_part_2 = args.param[0]
        self.prompt = f"({self.prompt_part_1} / {self.prompt_part_2}) "  

if __name__ == '__main__':
    import sys
    c = FirstApp()
    sys.exit(c.cmdloop("\n  Accounting Commander   v0.1.0\n"))


    