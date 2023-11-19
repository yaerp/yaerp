def shortify(text, max_width=10):
    return (text[:max_width-2] + '..') if len(text) > max_width else text

def justify(text, width=37, **kw):
    words = text.split()
    res, cur, num_of_letters = [], [], 0
    for w in words:
        if num_of_letters + len(w) + len(cur) > width:
            for i in range(width - num_of_letters):
                cur[i%(len(cur)-1 or 1)] += ' '
            res.append(''.join(cur))
            cur, num_of_letters = [], 0
        cur += [w]
        num_of_letters += len(w)
    return res + [' '.join(cur).ljust(width)]