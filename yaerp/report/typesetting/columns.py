from itertools import zip_longest


def simultaneous_column_generator(column_generators: list, empty_column_lines: list,
                indent_width = 1, gutter_width = 4):
    if len(column_generators) != len(empty_column_lines):
        RuntimeError()
    indent = ' ' * indent_width
    gutter = ' ' * gutter_width
    text = indent
    for row_parts in zip_longest(*column_generators, fillvalue=None):
        text = indent
        for idx, part in enumerate(row_parts, 0):
            if idx > 0:
                text += gutter
            if part is not None:
                text += part
            else:
                text += empty_column_lines[idx]
        text += '\n'
        yield text
