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

def container2str(item):
        par='"'
        if isinstance(item, (list, tuple)):
            result = iter_to_str(item, i_beg='', i_sep=' ', i_end='', 
                                    i_mapper=container2str)
        elif isinstance(item, dict):
            result = dict_to_str(item, d_show_keys=False, d_show_values=True, 
                d_beg='', d_kv_sep=':', d_pair_sep=' ', d_end='', 
                d_k_mapper=container2str, d_v_mapper=container2str)
        else:
            if item is None:
                return None
            else:
                result = str(item)
            if ' ' in result:
                if not result.startswith(('\'', '"', '`')):
                    result = ''.join([par, result, par])
        return result

def dict_to_str(source_dict: dict, d_show_keys=False, d_show_values=True, 
                d_beg='', d_kv_sep=':', d_pair_sep=' ', d_end='', 
                d_k_mapper=container2str, d_v_mapper=container2str):
    if not d_show_keys and not d_show_values:
        raise ValueError('keys=False and values=False are not allowed')
    if not isinstance(source_dict, dict):
        raise ValueError("expected dict instance in 1st argument")
    tmp_list = []
    for k, v in source_dict.items():
        if d_show_keys:
            semi_k = d_k_mapper(k)
            if semi_k:
                tmp_list.append(semi_k)
        if d_show_keys and d_show_values:
            tmp_list.append(d_kv_sep)
        if d_show_values:
            semi_v = d_v_mapper(v)
            if semi_v:
                tmp_list.append(semi_v)

        # if keys and values:
        #     tmp_list.append(''.join([k_str, kv_sep, v_str]))
        # elif not keys and values:
        #     tmp_list.append(v_str)
        # elif keys and not values:
        #     tmp_list.append(k_str)

    return ''.join([d_beg, *d_pair_sep.join(tmp_list), d_end]) 

def iter_to_str(iterable, i_beg='', i_sep=' ', i_end='', 
                i_mapper=container2str):
    tmp_list = []
    for element in iterable:
        semi_elem = i_mapper(element)
        if semi_elem:
            tmp_list.append(semi_elem)
    return ''.join([i_beg, *i_sep.join(tmp_list), i_end])

def args_to_command(*args):
    return container2str(args)

# print(iter_to_str([2, {4:5, "we434 rw":None}, 789, "wer wer", [3, '99 00', ['555']]]))

# print(dict_to_str({"123": [3,4,None,6,7]}))

# print(args_to_command("5", 7, None, {2:"55 66"}))
