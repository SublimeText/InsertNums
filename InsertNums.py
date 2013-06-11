import re

import sublime
import sublime_plugin

# Compatability
if int(sublime.version()) > 3000:
    basestring = str

module_name = "InsertNums"


def strip_line_spaces(string):
    return "\n".join([line.strip() for line in string.strip().split("\n")])


def int_or_float(value):
    try:
        return int(value)
    except ValueError:
        return float(value)


class PromptInsertNumsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.window().show_input_panel(
            'Enter a Format string like "1:1".',
            '',
            lambda x: self.view.run_command("insert_nums", {"format": x}),
            None,  # TODO: Preview
            None
        )


def get_rexexps(*ret):
    # Construct regexp for format string
    # Spacing doesn't matter due to (?x); escape normal } using }}
    repository_source = r"""
        # base
        integer       ::=  [1-9]\d* | 0

        # float and numeric
        pointfloat    ::=  {integer}? \. \d+ | {integer} \.
        exponentfloat ::=  (?:{integer} | {pointfloat}) [eE] [+-] \d+
        float         ::=  {pointfloat} | {exponentfloat}
        numeric       ::=  {integer} | {float}

        # (format) specific
        format        ::=  ([^}}]?[<>=^])?   # (fill)align
                           [-+ ]?            # sign
                           \#?               # "#"
                           0?                # "0"
                           {integer}?        # width
                           (\.\d+)?          # .precision
                           [bcdeEfFgGnoxX%]? # type
        alphastart    ::=  [a-z]+ | [A-Z]+
        alphaformat   ::=  ([^}}]?[<>=^])?   # (fill)align
                           {integer}?        # width

        # finals
        insertnum     ::=  ^ (?P<start> {numeric})
                           (: (?P<step> {numeric}) )?
                           (~ (?P<format> {format}) )? $

        insertalpha   ::=  ^ (?P<start> {alphastart})
                           (: (?P<step> {integer}) )?
                           (~ (?P<format> {alphaformat})
                              (?P<wrap> w)? )? $
    """

    # An ordereddict would be useful here, but Py2.6 ...
    repository = {}
    repository_list = []
    # Parse the stuff
    split = repository_source.split("::=  ")
    while len(split) > 1:
        # Do stuff backwards
        # Alternative idea: use a temporary "key" variable for the next section
        pattern = split[-1]
        before_pattern, key = split[-2].rsplit("\n", 1)
        if not key:
            key = before_pattern

        # Remove comments and multiple whitespaces and wrap in non-capturing group
        pattern = "(?:%s)" % strip_line_spaces(re.sub(r"(?<!\\)#.*$", '', pattern))

        repository_list.append((key.strip(), pattern))
        # Prepare for next step
        split[-2] = before_pattern
        del split[-1]

    # Now, replace format strings in order (of appearance)
    for i, (k, v) in enumerate(reversed(repository_list)):
        repository[k] = v.format(**repository)

    return tuple(repository[k] for k in ret)


class InsertNumsCommand(sublime_plugin.TextCommand):
    alpha = 'abcdefghijklmnopqrstuvwxyz'

    insertnum, insertalpha = get_rexexps("insertnum", "insertalpha")

    def run(self, edit, format=''):
        if not format or not isinstance(format, basestring):
            return self.status("Format string is not a string or empty: %r" % format)

        # Parse "format"
        m = re.match(self.insertnum, format, re.X) or re.match(self.insertalpha, format, re.X)
        if not m:
            return self.status("Format string is invalid: %s" % format)
        m = m.groupdict()
        # print(m)

        # Booleans interesting for alpha insertions
        ALPHA = 'wrap' in m
        # UPPER = ALPHA and m['start'][0].isupper()
        # WRAP = ALPHA and bool(m['wrap'])

        # Read values
        start  = ALPHA and m['start'] or int_or_float(m['start'])
        step   = int_or_float(m['step']) if m['step'] else 1
        format = m['format']

        # Do the stuff
        if not ALPHA:
            value = start
            # Convert to float if precision in format string
            if format and '.' in format and isinstance(value, int):
                value = float(value)

            for region in self.view.sel():
                if format:
                    replace = "{value:{format}}".format(value=value, format=format)
                else:
                    replace = str(value)
                self.view.replace(edit, region, replace)
                value += step
        else:
            # TODO
            pass

    def encode(self, num):
        res = ''

        while num > 0:
            num -= 1
            if num >= 0:
                res += self.alpha[int(num) % 26]
                num /= 26

        return res

    def decode(self, str):
        res = 0

        for i in str:
            res *= 26
            res += self.alpha.index(i) + 1

        return res

    def status(self, msg):
        print("[%s] %s" % (module_name, msg))
        sublime.status_message(msg)
