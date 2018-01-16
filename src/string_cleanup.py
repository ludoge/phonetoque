import re


class StringCleanup:
    def __init__(self, config):
        self.separators = config['separators']
        self.simplifying = config['simplifying']
        self.stop_chars = config['stop_chars']

    def read_pronunciation_file_as_dict(self, filename):
        data = open(filename, mode="r", encoding="utf8").read()
        dictionary = {}
        for line in data.splitlines():
            dictionary[line.split()[0]] = line.split()[1:]
        return dictionary

    def read_pronunciation_file_as_list(self, filename):
        data = open(filename, mode="r", encoding="utf8").read()
        res = []
        for line in data.splitlines():
            if line.split()[1:]:
                for p in line.split()[1:]:
                    res.append(p)
        return res

    def remove_stop_chars(self, string):
        return string.translate(str.maketrans(self.stop_chars, ' '*len(self.stop_chars))).replace(" ","")

    def strip_tags(self, string):
        return string.translate(str.maketrans('[]/()', '     ')).replace(" ","")

    def simplify_separators(self, string):
        """
        Replaces all separators with dashes '-'
        :param string:
        :return:
        """
        res = string.translate(str.maketrans(self.separators, ' '*len(self.separators))).strip().replace(' ','-')
        res = re.sub(r'(-)\1+', r'\1', res)
        return res

    def simplify_chars(self, string):
        s = lambda x: self.simplifying[x] if x in self.simplifying else x
        res = "".join(list(map(s,string)))
        return res

    def cleanup(self, string):
        return self.simplify_chars(self.strip_tags(self.remove_stop_chars(string)))