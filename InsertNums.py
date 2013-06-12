import re

import sublime
import sublime_plugin

# Compatability
if int(sublime.version()) > 3000:
    basestring = str

module_name = "InsertNums"


# TODO: expressions for "step" (e.g. "_**2")
# TODO: expressions only for the value, independant of the actual "step"


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
            "Enter a Format string like '1:1':",
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
        signedint     ::=  [+-]? {integer}

        # float and numeric
        pointfloat    ::=  {integer}? \. \d+ | {integer} \.
        exponentfloat ::=  (?:{integer} | {pointfloat}) [eE] [+-]? \d+
        float         ::=  {pointfloat} | {exponentfloat}
        numeric       ::=  {integer} | {float}
        signednum     ::=  [+-]? {numeric}

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
        insertnum     ::=  ^ (?P<start> {signednum})
                           (: (?P<step> {signednum}) )?
                           (~ (?P<format> {format}) )?
                           (?P<reverse> !)? $

        insertalpha   ::=  ^ (?P<start> {alphastart})
                           (: (?P<step> {signedint}) )?
                           (~ (?P<format> {alphaformat})
                              (?P<wrap> w)? )?
                           (?P<reverse> !)? $
    """

    # Our most important variable
    repository = {}

    # Parse the stuff
    split = repository_source.split("::=  ")
    key, i = "", 0
    while i < len(split):
        # Split at last line break
        try:
            pattern, next_key = split[i].rsplit("\n", 1)
        except ValueError:
            # First key and no line break at the beginning
            next_key = split[i]

        if key:
            # Remove comments and multiple whitespaces and wrap in non-capturing group
            pattern = "(?:%s)" % strip_line_spaces(re.sub(r"(?m)\s#\s.*$", '', pattern))

            # Now, replace format strings (requires correct order)
            repository[key] = pattern.format(**repository)

        # Prepare for next step
        key = next_key.strip()
        i += 1

    if ret:
        # Return the values asked for, in order
        return tuple(repository[k] for k in ret)
    else:
        return repository


class InsertNumsCommand(sublime_plugin.TextCommand):
    # Regular expressions for format syntax
    insertnum, insertalpha = get_rexexps("insertnum", "insertalpha")

    def run(self, edit, format=''):
        if not format or not isinstance(format, basestring):
            return self.status("Format string is not a string or empty: %r" % format)

        # Parse "format"
        m = re.match(self.insertnum, format, re.X) or re.match(self.insertalpha, format, re.X)
        if not m:
            return self.status("Format string is invalid: %s" % format)
        m = m.groupdict()

        # Read values
        ALPHA = 'wrap' in m
        start  = ALPHA and m['start'] or int_or_float(m['start'])
        step   = int_or_float(m['step']) if m['step'] else 1
        format = m['format']

        # Reverse the regions if requested | by default, this works like an iterator
        selections = self.view.sel()
        if m['reverse']:
            # Construct a real list and reverse that, won't affect the regions
            # since we're going backwards
            selections = reversed(reg for reg in selections)

        # Do the stuff
        if not ALPHA:
            value = start
            # Convert to float if precision in format string
            if ((format and '.' in format or isinstance(step, float))
                    and isinstance(value, int)):
                value = float(value)

            for region in selections:
                if format:
                    replace = "{value:{format}}".format(value=value, format=format)
                else:
                    replace = str(value)
                self.view.replace(edit, region, replace)

                value += step
        else:
            UPPER = ALPHA and m['start'][0].isupper()
            WRAP = ALPHA and bool(m['wrap'])

            # Always calculate with lower alphas and 0-based integers here
            lenght = len(start) if WRAP else 0
            value = self.alpha_to_num(start.lower())

            for region in selections:
                replace = self.num_to_alpha(value, lenght)
                if UPPER:
                    replace = replace.upper()
                if format:
                    replace = "{value:{format}}".format(value=replace, format=format)
                self.view.replace(edit, region, replace)

                value += step

    def num_to_alpha(self, num, lenght=0):
        res = ''

        if lenght:
            num = (num - 1) % (26 ** lenght) + 1

        while num > 0:
            num -= 1
            res = chr(97 + (num % 26)) + res  # ord("a") == 97
            num //= 26

        return res

    def alpha_to_num(self, alpha):
        res = 0

        for c in alpha:
            res *= 26
            res += ord(c) - 96  # ord("a") == 97

        return res

    def status(self, msg):
        print("[%s] %s" % (module_name, msg))
        sublime.status_message(msg)
