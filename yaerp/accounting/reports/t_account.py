from dataclasses import dataclass
from itertools import chain
import textwrap

from yaerp.accounting.journal import JournalEntry
from yaerp.accounting.account import AccountRecord, AccountSide
from yaerp.report.typesetting.columns import simultaneous_column_generator

@dataclass
class RenderParameters:
    t_account_width: int
    t_account_amount_width: int
    number_of_columns: int
    gutter_between_columns: int
    first_column_indent: int


render_layout = {
    "1x31": RenderParameters(29, 8, 1, 0, 0),
    "1x39": RenderParameters(37, 12, 1, 0, 0),
    "1x57": RenderParameters(55, 18, 1, 0, 0),  
    "1x75": RenderParameters(73, 18, 1, 0, 0),
    "2x31": RenderParameters(29, 8, 2, 2, 0),  
    "2x39": RenderParameters(37, 12, 2, 2, 0),
    "terminal-80-2": RenderParameters(37, 12, 2, 4, 0),
    "2x57": RenderParameters(55, 18, 2, 2, 0),
    "terminal-120-2": RenderParameters(55, 18, 2, 7, 0),
    "2x75": RenderParameters(73, 18, 2, 2, 0),
    "3x31": RenderParameters(29, 8, 3, 2, 0), 
    "3x39": RenderParameters(37, 12, 3, 2, 0), 
    "terminal-120-3": RenderParameters(37, 12, 3, 3, 0), 
    "3x57": RenderParameters(55, 18, 3, 2, 0),
    "3x75": RenderParameters(73, 18, 3, 2, 0),
    "4x31": RenderParameters(29, 8, 4, 2, 0), 
    "4x39": RenderParameters(37, 12, 4, 2, 0), 
    "4x57": RenderParameters(55, 18, 4, 2, 0),
    "4x75": RenderParameters(73, 18, 4, 2, 0),
}

class T_account:

    unicode_bold_table_box = {
        '-': '\u2500',
        'b-': '\u2501', ## bold '-'
        '|': '\u2502',
        'T': '\u252c', 
        'bT': '\u252F', ## bold 'T'
        '+': '\u253c',
        '_|_': '\u2534',
        '=': '\u2550',
        '=|=': '\u2567',
        '...': '\u2026',
        ' ': ' '
    }

    unicode_simple_table_box = {
        '-': '\u2500',
        'b-': '\u2500',
        '|': '\u2502',
        'T': '\u252c', 
        'bT': '\u252c',
        '+': '\u253c',
        '_|_': '\u2534',
        '=': '\u2550',
        '=|=': '\u2567',
        '...': '\u2026',
        ' ': ' '
    }

    ascii_bold_table_box = {
        '-': '-',
        'b-': '=',
        '|': '|',
        'T': '-',
        'bT': '=',
        '+': '+',
        '_|_': '-',
        '=': '=',
        '=|=': '=',
        '...': '...',
        ' ': ' '
    }

    ascii_simple_table_box = {
        '-': '-',
        'b-': '-',
        '|': '|',
        'T': '-',
        'bT': '-',
        '+': '+',
        '_|_': '-',
        '=': '=',
        '=|=': '=',
        '...': '...',
        ' ': ' '
    }

    def __init__(self, account_tag, account_name = '', 
                    max_length = 39, max_data_length = 10, max_amount_length = 10, 
                    box=unicode_simple_table_box, new_line='\n', leading_spaces=0):
        self.account_tag = account_tag
        self.account_name = account_name
        self.linelength = max_length
        self.max_data_length = max_data_length
        self.max_amount_length = max_amount_length
        self.box = box
        self.new_line = new_line
        self.leading_space = ' ' * leading_spaces

    def set_line_length(self, length):
        self.linelength = length
        if self.linelength % 2 == 0:
            self.linelength -= 1
 
    def truncate(self, text, max_length) -> str:
        return textwrap.shorten(text, width=max_length, placeholder=self.box['...'])

    def header(self) -> str:
        result = self.leading_space
        name = '[{}] {}'.format(self.account_tag, self.account_name)
        name = self.truncate(name, self.linelength - 2)
        name = name.strip(' ')
        formatter = '{{:^{0}}}'.format(self.linelength)
        self.side_length = self.linelength // 2
        result += formatter.format(name)
        result += '\n'
        result += self.leading_space
        result += self.box['b-'] * self.side_length
        result += self.box['bT']
        result += self.box['b-'] * self.side_length
        result += self.new_line
        return result

    def header_generator(self):
        result = self.leading_space
        name = '[{}] {}'.format(self.account_tag, self.account_name)
        name = self.truncate(name, self.linelength - 2)
        name = name.strip(' ')
        formatter = '{{:^{0}}}'.format(self.linelength)
        self.side_length = self.linelength // 2
        result += formatter.format(name)
        yield result
        result = self.leading_space
        result += self.box['b-'] * self.side_length
        result += self.box['bT']
        result += self.box['b-'] * self.side_length
        result += self.new_line
        yield result

    def row(self, description, amount, side):
        result = self.leading_space
        if side == AccountSide.DEBIT:
            result += self.single_side_text(AccountSide.DEBIT, description, amount)
            result += self.box['|']
            result += ' ' * self.side_length
        elif side == AccountSide.CREDIT:
            result += ' ' * self.side_length
            result += self.box['|']
            result += self.single_side_text(AccountSide.CREDIT, description, amount)
        result += self.new_line
        return result

    def row_generator(self, description, amount, side):
        result = self.leading_space
        if side == AccountSide.DEBIT:
            result += self.single_side_text(AccountSide.DEBIT, description, amount)
            result += self.box['|']
            result += ' ' * self.side_length
        elif side == AccountSide.CREDIT:
            result += ' ' * self.side_length
            result += self.box['|']
            result += self.single_side_text(AccountSide.CREDIT, description, amount)
        result += self.new_line
        yield result

    def line(self, plain_char, crossing_char):
        result = self.leading_space
        space_length = self.side_length - self.max_amount_length
        separator_length = self.side_length - space_length
        result += ' ' * space_length
        result += self.box[plain_char] * separator_length
        result += self.box[crossing_char]
        result += self.box[plain_char] * separator_length
        result += ' ' * space_length
        result += self.new_line
        return result

    def split_line(self):
        return self.line(plain_char='-', crossing_char='+')

    def split_line_generator(self):
        yield self.line(plain_char='-', crossing_char='+')

    def balance(self, balance):
        pass

    def balance_generator(self, balance):
        pass

    def end_line(self):
        return self.line(plain_char='=', crossing_char='=|=')

    def end_line_generator(self):
        yield self.end_line()

    # both empty debit and credit sides on T account
    def empty_row(self):
        return self.line(plain_char=' ', crossing_char='|')

    def empty_row_generator(self):
        yield self.empty_row()

    # just whitespaces for indenting
    def blank_row(self) -> str:
        result = self.leading_space
        result += ' ' * self.linelength
        return result

    def blank_row_generator(self):
        yield self.blank_row()

    def single_side_text(self, side, description, amount):
        max_desc_length = self.side_length - self.max_amount_length - 1
        description = self.truncate(description, max_desc_length)
        if side == AccountSide.DEBIT:
            side_formatter = '{:<' + str(max_desc_length) + '} {:>' + str(self.max_amount_length) + '}'
            return side_formatter.format(description, amount)
        elif side == AccountSide.CREDIT:
            side_formatter = '{:<' + str(self.max_amount_length) + '} {:>' + str(max_desc_length) + '}'
            return side_formatter.format(amount, description)

def render_journal_entry(entry: JournalEntry, col=2, col_len=37):
    account_set = set(field.account for field in entry.fields.values() if isinstance(field, AccountRecord))
    account_list = list(account_set)
    account_list.sort(key=lambda acc: acc.tag)
    return render(*account_list, account_entry_predicate = lambda post: post.entry == entry, col=col, col_len=col_len)

def render_journal_entry2(journal_entry: JournalEntry, layout):
    accounts_engaged = []
    accounts_entries = []
    for field in journal_entry.fields.values():
        if isinstance(field, AccountRecord):
            if field.account and field.raw_amount:
                accounts_engaged.append(field.account)
                accounts_entries.append(field)
        elif isinstance(field, list):
            for account_entry in field:
                if account_entry.account and account_entry.amount:
                    accounts_engaged.append(account_entry.account)
                    accounts_entries.append(account_entry)
    # remove recurring accounts
    accounts_engaged = list(set(accounts_engaged))
    accounts_engaged.sort(key=lambda acc: acc.tag)
    return render2(accounts_engaged, accounts_entries, layout=layout)

def render_journal_entries(journal_entry_list, layout=None):
    journal_entry_counter = {}
    number_label = 0
    accounts_dict = {}
    for journal_entry in journal_entry_list:
        # set 'label' for entry
        if journal_entry in journal_entry_counter:
            continue
        number_label += 1
        journal_entry_counter[journal_entry] = number_label
        # find engaged accounts
        for field in journal_entry.fields.values():
            if isinstance(field, AccountRecord) and field.account:
                accounts_dict[field.account] = field.account
            elif isinstance(field, list):
                for account_entry in field:
                    if account_entry.account:
                        accounts_dict[account_entry.account] = account_entry.account
    account_list = list(accounts_dict.values())
    account_list.sort(key=lambda acc: acc.tag)
    # render

    # def select_account_entry(account_entry):
        # account_entry.post == 

    print(render(*account_list,
        # account_entry_predicate=select_account_entry, 
        account_entry_predicate=lambda entry: entry.journal_entry in journal_entry_list, 
        layout=layout,
        entry_counter=journal_entry_counter))

    for journal_entry in journal_entry_counter:
        print(f"{journal_entry_counter[journal_entry]}. {journal_entry}")

def render_journal_entries2(journal_entry_list, layout=None):
    journal_entry_counter = {}
    number_label = 0
    accounts_engaged = []
    accounts_entries = []
    for journal_entry in journal_entry_list:
        # set 'label' for entry
        if journal_entry in journal_entry_counter:
            continue
        number_label += 1
        journal_entry_counter[journal_entry] = number_label
        # find engaged accounts
        for field in journal_entry.fields.values():
            if isinstance(field, AccountRecord):
                if field.account and field.raw_amount:
                    accounts_engaged.append(field.account)
                    accounts_entries.append(field)
            elif isinstance(field, list):
                for account_entry in field:
                    if account_entry.account and account_entry.raw_amount:
                        accounts_engaged.append(account_entry.account)
                        accounts_entries.append(account_entry)
    # remove recurring accounts
    accounts_engaged = list(set(accounts_engaged))
    accounts_engaged.sort(key=lambda acc: acc.tag)

    print(render2(accounts_engaged, accounts_entries, layout=layout, entry_counter=journal_entry_counter))

    for journal_entry in journal_entry_counter:
        print(f"{journal_entry_counter[journal_entry]}. {journal_entry}")

def render(*accounts, account_entry_predicate=None, layout=None, entry_counter=None):
    # col = layout.number_of_columns
    # col_len = layout.t_account_width
    # amount_width = layout.t_account_amount_width

    column_generators = []
    empty_column = []
    col_idx = 0
    for account_idx, account in enumerate(accounts):
        if account_idx < layout.number_of_columns:
            # if first run
            col_idx = account_idx
            column_generators.append([])   
            empty_column.append(blank_row(layout.t_account_width))
        else:
            # if next run
            col_idx = account_idx % layout.number_of_columns
            column_generators[col_idx].append(vertical_space_gen(layout.t_account_width))
        column_generators[col_idx].append(t_form_gen(account, account_entry_predicate, None, layout=layout, entry_counter=entry_counter))


    for col_idx, column in enumerate(column_generators):
        # convert list of generators to the chain
        column_generators[col_idx] = chain.from_iterable(column_generators[col_idx])

    result = ''
    for line in simultaneous_column_generator(
                    column_generators=column_generators,
                    empty_column_lines=empty_column,
                    indent_width = layout.first_column_indent, 
                    gutter_width = layout.gutter_between_columns):
        result += line
    return result

def render2(accounts, accounts_entries, layout=None, entry_counter=None):
    column_generators = []
    empty_column = []
    col_idx = 0
    for account_idx, account in enumerate(accounts):
        if account_idx < layout.number_of_columns:
            # if first run
            col_idx = account_idx
            column_generators.append([])   
            empty_column.append(blank_row(layout.t_account_width))
        else:
            # if next run
            col_idx = account_idx % layout.number_of_columns
            column_generators[col_idx].append(vertical_space_gen(layout.t_account_width))
        column_generators[col_idx].append(t_form_gen2(account, accounts_entries, layout=layout, entry_counter=entry_counter))


    for col_idx, column in enumerate(column_generators):
        # convert list of generators to the chain
        column_generators[col_idx] = chain.from_iterable(column_generators[col_idx])

    result = ''
    for line in simultaneous_column_generator(
                    column_generators=column_generators,
                    empty_column_lines=empty_column,
                    indent_width = layout.first_column_indent, 
                    gutter_width = layout.gutter_between_columns):
        result += line
    return result

def t_form_gen(account, post_predicate, col_len,layout=None, entry_counter=None):
    t_account = T_account(account.tag, account.name, max_length=layout.t_account_width, max_amount_length=layout.t_account_amount_width, leading_spaces=0, new_line='', box=T_account.unicode_bold_table_box)  
    yield from t_account.header_generator()

    if not entry_counter:
        entry_counter = {}
        counter = 0
        for post in filter(post_predicate, account.posts):
            # collect entries
            if post.entry in entry_counter.keys():
                continue
            counter += 1
            entry_counter[post.entry] = counter

    currency = account.currency
    for post in filter(post_predicate, account.posts):
        post_info = post.get_info()        
        # description = f'({entry_counter[post.entry]}.{post_info[1]})'
        description = f'({entry_counter[post.journal_entry]})'
        yield from t_account.row_generator(description, currency.raw2str(post.amount), post.side)

def t_form_gen2(account, account_entry_list, layout=None, entry_counter=None):
    t_account = T_account(account.tag, account.name, max_length=layout.t_account_width, max_amount_length=layout.t_account_amount_width, leading_spaces=0, new_line='', box=T_account.unicode_bold_table_box)  
    yield from t_account.header_generator()

    if not entry_counter:
        entry_counter = {}
        counter = 0
        for account_entry in account_entry_list:
            # collect entries
            if account_entry.journal_entry in entry_counter.keys():
                continue
            counter += 1
            entry_counter[account_entry.journal_entry] = counter

    currency = account.currency
    for account_entry in account_entry_list:
        if account_entry.account != account:
            continue
        # post_info = account_entry.get_info()        
        # description = f'({entry_counter[post.entry]}.{post_info[1]})'
        description = f'({entry_counter[account_entry.journal_entry]})'
        yield from t_account.row_generator(description, currency.raw2amount(account_entry.raw_amount), account_entry.side)

def vertical_space_gen(col_len):
    yield blank_row(col_len)
    yield blank_row(col_len)

def blank_row(col_len):
    t_account = T_account('', '', max_length=col_len, max_amount_length=10, leading_spaces=0, new_line='', box=T_account.unicode_bold_table_box)  
    return t_account.blank_row()
