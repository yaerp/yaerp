from dataclasses import dataclass
from itertools import chain
import textwrap

from yaerp.accounting.transaction import Transaction
from yaerp.accounting.entry import Entry
from yaerp.report.typesetting.columns import simultaneous_column_generator

@dataclass
class RenderParameters:
    t_account_width: int
    t_account_amount_width: int
    number_of_columns: int
    gutter_between_columns: int
    first_column_indend: int


render_layout = {
    "1x31": RenderParameters(29, 8, 1, 0, 0),
    "1x39": RenderParameters(37, 12, 1, 0, 0),
    "1x57": RenderParameters(55, 18, 1, 0, 0),  
    "1x75": RenderParameters(73, 18, 1, 0, 0),
    "2x31": RenderParameters(29, 8, 2, 2, 0),  
    "2x39": RenderParameters(37, 12, 2, 2, 0),
    "old terminal": RenderParameters(37, 12, 2, 2, 0),
    "2x57": RenderParameters(55, 18, 2, 2, 0),
    "modern terminal": RenderParameters(55, 18, 2, 2, 0),
    "2x75": RenderParameters(73, 18, 2, 2, 0),
    "3x31": RenderParameters(29, 8, 3, 2, 0), 
    "3x39": RenderParameters(37, 12, 3, 2, 0), 
    "sweet": RenderParameters(37, 12, 3, 2, 0), 
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
        if side == 0:
            result += self.single_side_text(0, description, amount)
            result += self.box['|']
            result += ' ' * self.side_length
        elif side == 1:
            result += ' ' * self.side_length
            result += self.box['|']
            result += self.single_side_text(1, description, amount)
        result += self.new_line
        return result

    def row_generator(self, description, amount, side):
        result = self.leading_space
        if side == 0:
            result += self.single_side_text(0, description, amount)
            result += self.box['|']
            result += ' ' * self.side_length
        elif side == 1:
            result += ' ' * self.side_length
            result += self.box['|']
            result += self.single_side_text(1, description, amount)
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
        if side == 0:
            side_formatter = '{:<' + str(max_desc_length) + '} {:>' + str(self.max_amount_length) + '}'
            return side_formatter.format(description, amount)
        elif side == 1:
            side_formatter = '{:<' + str(self.max_amount_length) + '} {:>' + str(max_desc_length) + '}'
            return side_formatter.format(amount, description)


def render_entry(entry: Transaction, col=2, col_len=37):
    account_set = set(field.account for field in entry.fields.values() if isinstance(field, Entry))
    account_list = list(account_set)
    account_list.sort(key=lambda acc: acc.tag)
    return render(*account_list, post_predicate = lambda post: post.entry == entry, col=col, col_len=col_len)

def render_entries(entry_list, layout=None, col=3, col_len=37):
    entry_counter = {}
    number_label = 0
    accounts_dict = {}
    for entry in entry_list:
        # set 'label' for entry
        if entry in entry_counter.keys():
            continue
        number_label += 1
        entry_counter[entry] = number_label
        # find engaged accounts
        for field in entry.fields.values():
            if isinstance(field, Entry):
                accounts_dict[field.account] = field.account
    account_list = list(accounts_dict.values())
    account_list.sort(key=lambda acc: acc.tag)
    # render

    print(render(*account_list, post_predicate=lambda post: post.transaction in entry_list, 
                    layout=layout, col=col, col_len=col_len, entry_counter=entry_counter))

    for entry in entry_counter.keys():
        print(entry_counter[entry])


def render(*accounts, post_predicate=None, layout=None, col=2, col_len=37, entry_counter=None):

    col_len = layout.t_account_width
    column_generators = []
    empty_column = []
    col_idx = 0
    for account_idx, account in enumerate(accounts):
        if account_idx < col:
            # if first run
            col_idx = account_idx
            column_generators.append([])   
            empty_column.append(blank_row(col_len))
        else:
            # if next run
            col_idx = account_idx % col
            column_generators[col_idx].append(vertical_space_gen(col_len))
        column_generators[col_idx].append(t_form_gen(account, post_predicate, col_len, entry_counter=entry_counter))


    for col_idx, column in enumerate(column_generators):
        # convert list of generators to the chain
        column_generators[col_idx] = chain.from_iterable(column_generators[col_idx])

    result = ''
    for line in simultaneous_column_generator(
                    column_generators=column_generators,
                    empty_column_lines=empty_column,
                    indent_width = 1, 
                    gutter_width = 2):
        result += line
    return result

def t_form_gen(account, post_predicate, col_len, entry_counter=None):
    t_account = T_account(account.tag, account.name, max_length=col_len, max_amount_length=10, leading_spaces=0, new_line='', box=T_account.unicode_bold_table_box)  
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
        description = f'({entry_counter[post.transaction]})'
        yield from t_account.row_generator(description, currency.raw2str(post.amount), post.side)

def vertical_space_gen(col_len):
    yield blank_row(col_len)
    yield blank_row(col_len)

def blank_row(col_len):
    t_account = T_account('', '', max_length=col_len, max_amount_length=10, leading_spaces=0, new_line='', box=T_account.unicode_bold_table_box)  
    return t_account.blank_row()