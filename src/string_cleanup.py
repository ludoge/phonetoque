import re

def read_pronunciation_file_as_dict(filename):
    data = open(filename, mode="r", encoding="utf8").read()
    dictionary = {}
    for line in data.splitlines():
        dictionary[line.split()[0]] = line.split()[1:]
    return dictionary

def read_pronunciation_file_as_list(filename):
    data = open(filename, mode="r", encoding="utf8").read()
    res = []
    for line in data.splitlines():
        if line.split()[1:]:
            for p in line.split()[1:]:
                res.append(p)
    return res


def remove_stop_chars(string, config):
    stop_chars = config['stop_chars']
    return string.translate(str.maketrans(stop_chars, ' '*len(stop_chars))).replace(" ","")


def strip_tags(string):
    return string.translate(str.maketrans('[]/()','     ')).replace(" ","")


def simplify_separators(string, config):
    separators = config['separators']
    res = string.translate(str.maketrans(separators, ' '*len(separators))).strip().replace(' ','-')
    res = re.sub(r'(-)\1+', r'\1', res)
    return res


def simplify_chars(string, config):
    simplify = config['simplifying']
    s = lambda x: simplify[x] if x in simplify else x
    res = "".join(list(map(s,string)))
    return res


def cleanup(string, config):
    return simplify_chars(strip_tags(remove_stop_chars(string, config)),config)
