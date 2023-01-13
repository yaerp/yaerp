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
        suspension = self.box['...']
        suspension_length = len(suspension)
        text = (text[:max_length - suspension_length] + suspension) if len(text) > max_length else text
        return text

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
