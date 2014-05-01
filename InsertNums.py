import re
import time

# Modules for expression evaluation
import math
import random

import sublime
import sublime_plugin

# Compatability
ST3 = int(sublime.version()) > 3000
if ST3:
    basestring = str

module_name = "Insert Nums"


# Utility functions ####################


def int_or_float(value):
    try:
        return int(value) if value is not None else None
    except ValueError:
        return float(value)


def num_to_alpha(num, length=0):
    res = ''

    if length:
        num = (num - 1) % (26 ** length) + 1

    while num > 0:
        num -= 1
        res = chr(97 + (num % 26)) + res  # ord("a") == 97
        num //= 26

    return res


def alpha_to_num(alpha):
    res = 0

    for c in alpha:
        res *= 26
        res += ord(c) - 96  # ord("a") == 97

    return res


def strip_line_spaces(string):
    return "\n".join([line.strip() for line in string.strip().split("\n")])


def get_regexps(*ret):
    # Construct regexp for format string
    # Spacing doesn't matter due to (?x); escape normal } using }}
    repository_source = r"""
        # 1:2~+03::i*2@i==10!
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

        cast          ::=  [ifsb]

        # generic python expression (keep it simple)
        # Considered using greedy '((?!!!).)+' for style, but non-greedy is
        # easier to use and backwards compatible
        expr          ::=  .+?
        stopexpr      ::=  .+?

        # finals
        exprmode      ::=  ^ (?P<cast> {cast})? \|
                           (~ (?P<format> {format}) ::)?
                           (?P<expr> {expr})
                           (@ (?P<stopexpr> {stopexpr}) )?
                           (?P<reverse> !)? $

        insertnum     ::=  ^
                           ( (?P<start> {signednum}) )?
                           (: (?P<step> {signednum}) )?
                           (~ (?P<format> {format}) )?
                           (:: (?P<expr> {expr}) )?
                           (@ (?P<stopexpr> {stopexpr}) )?
                           (?P<reverse> !)? $

        insertalpha   ::=  ^
                           (?P<start> {alphastart})
                           (: (?P<step> {signedint}) )?
                           (~ (?P<format> {alphaformat})
                              (?P<wrap> w)? )?
                           (@ (?P<stopexpr> {stopexpr}) )?
                           (?P<reverse> !)? $
    """
    # Our most important variable
    repository = {}

    # Parse the stuff
    split = repository_source.split("::=  ")
    key = ""
    for next_key in split:
        # Split at last line break
        try:
            pattern, next_key = next_key.rsplit("\n", 1)
        except ValueError:
            # First key and no line break at the beginning
            pass

        if key:
            # Remove comments and multiple whitespaces and wrap in non-capturing
            # group
            no_comments = re.sub(r"(?m)\s#\s.*$", '', pattern)
            pattern = "(?:%s)" % strip_line_spaces(no_comments)

            # Now, replace format strings (requires correct order)
            repository[key] = pattern.format(**repository)

        # Prepare for next step
        key = next_key.strip()

    if ret:
        # Return the values asked for, in order
        return tuple(repository[k] for k in ret)
    else:
        return repository


def status(msg):
    print("[%s] %s" % (module_name, msg))
    sublime.status_message(msg)


# The Environment #####################


# While this is not 0, the input panel is open
vid = 0
# These are required to let on_selection_modified know if the selection
# differs, abort in that case to prevent unexpectable behaviour
lastsel = []
initsel = []


class SelectionListener(sublime_plugin.EventListener):
    def on_selection_modified(self, view):
        global vid, initsel, lastsel

        # Test if selection differs from either before modification state or
        # from after the last insert_nums call. If yes, it has been modified
        # and could produce unexpectable results.
        if vid == view.id() and list(view.sel()) not in (initsel, lastsel):
            status("Selection has been modified by you or third-party. "
                   "Aborting.")
            # For some reason this does NOT undo the change by insert_nums
            view.window().run_command("hide_panel", {"cancel": True})


# The Commands #########################


class PromptInsertNumsCommand(sublime_plugin.TextCommand):

    # revert changes for clean undo history
    def revert_changes(self):
        global vid

        lcom = self.view.command_history(0)

        # Last command called should be "prompt_insert_nums" or "insert_nums"
        if lcom[0].endswith("insert_nums"):
            self.view.run_command("undo")

    def on_done(self, format):
        global vid
        if vid:  # Revert changes if previewed
            vid = 0
            self.revert_changes()
        self.view.run_command("insert_nums", {"format": format})

    def preview(self, format):
        global vid, initsel

        if not vid:
            # Init preview mode
            vid = self.view.id()
            initsel = list(self.view.sel())
        else:
            self.revert_changes()

        self.view.run_command("insert_nums", {"format": format, "quiet": True})

    def cancel(self):
        global vid, initsel, lastsel

        if vid:
            # Reset preview mode
            self.revert_changes()
            vid = 0
            initsel, lastsel = [], []

    def run(self, edit, preview=True):
        self.view.window().show_input_panel(
            "Enter a Format string (default: '1:1'):",
            '',
            self.on_done,  # on_done
            self.preview if preview else None,  # on_change
            self.cancel    # on_cancel
        )


class InsertNumsCommand(sublime_plugin.TextCommand):
    # Regular expressions for format syntax
    regexps = get_regexps("insertnum", "insertalpha", "exprmode")
    insertnum, insertalpha, exprmode = regexps
    casttable = dict(s=str, b=bool, i=int, f=float)
    if not ST3:
        casttable['s'] = unicode

    def run(self, edit, format='', quiet=False):
        global vid, lastsel

        if not isinstance(format, basestring):
            return status("Format string is not a string: %r" % format)

        # Parse "format"
        m = (re.match(self.insertnum, format, re.X)
             or re.match(self.insertalpha, format, re.X)
             or re.match(self.exprmode, format, re.X))
        if not m:
            msg = "Format string is invalid: %s" % format
            if quiet:
                # Do not spam the console in preview mode
                return sublime.status_message(msg)
            else:
                return status(msg)
        m = m.groupdict()

        # Read values
        EXPRMODE  = 'start' not in m
        ALPHA     = 'wrap' in m
        REVERSE   = bool(m['reverse'])
        step      = int_or_float(m['step']) if 'step' in m and m['step'] else 1
        format    = m['format']
        expr      = not ALPHA and m['expr']
        stop_expr = m['stopexpr']
        cast      = EXPRMODE and m['cast'] or "s"

        UPPER     = ALPHA and m['start'][0].isupper()
        WRAP      = ALPHA and bool(m['wrap'])

        # Reverse the regions if requested | by default, this works like an
        # iterator
        selections = self.view.sel()

        # Create a list that will store all generated values
        values = []

        # Do the stuff
        if EXPRMODE:
            pass
        elif not ALPHA:
            value = (int_or_float(m['start']) if m['start'] else 1)

            # Convert to float if precision in format string
            if format and '.' in format or isinstance(step, float):
                value = float(value)
        else:
            # Always calculate with lower alphas and 0-based integers here
            value = alpha_to_num(m['start'].lower())
            length = len(value) if WRAP else 0

        # Save the previously evaluated value for `p` (defaults to 0)
        eval_value = 0
        # Use a counter for the eval env and for break condition
        i = 0
        # Save a timestamp to circumvent infinite loops caused by the user
        start_time = time.time()
        # By default, do not process longer than 100ms!
        time_limit = 0.1

        # In case the (generated) value should be skipped
        skip = False

        while True:
            if (EXPRMODE or not stop_expr) and i == len(selections):
                break
            if time.time() > start_time + time_limit:
                sublime.status_message("Time limit of %.3fs exceeded" %
                                       time_limit)
                break

            if EXPRMODE:
                # Because exprmode depends on the actual value of the (previous)
                # selection we need to actually iterate the sels backwards
                reg = selections[i] if not REVERSE else selections[-i - 1]
                value = self.view.substr(reg)
                # Try to cast the value to what was requested (str is default)
                try:
                    value = self.casttable[cast](value)
                except Exception as e:
                    if quiet:
                        # Show status message if "quiet" (in preview) Alos print
                        # to console as this doesn't happen too often but might
                        # be really useful information
                        status("Unable to cast `%s` to '%s'" % (value, cast))
                        skip = True
                    else:
                        sublime.error_message(
                            "[%s] Invalid Expression\n\n"
                            "Selection `%s` could not be cast to '%s':\n\n"
                            "%r" % (module_name, value, cast, e)
                        )
                        return

            if not skip:
                # Build eval environment
                if expr or stop_expr:
                    env = dict(
                        _=value, i=i, p=eval_value, s=step, n=len(selections),
                        # Modules
                        math=math, random=random, re=re
                    )
                    if EXPRMODE:
                        del env['s']  # We don't need the step here

                if ALPHA:
                    # No expression evaluation for alpha mode
                    eval_value = num_to_alpha(value, length)
                    if UPPER:
                        eval_value = eval_value.upper()
                else:
                    # Evaluate the expression, if given
                    if expr:
                        try:
                            eval_value = eval(expr, env)
                        except Exception as e:
                            if quiet:
                                # Show unevaluated status if "quiet"
                                sublime.status_message("Invalid Expression: "
                                                       "`%s`" % expr)
                                if EXPRMODE:
                                    # No need to continue if in expr mode
                                    return
                            else:
                                sublime.error_message(
                                    "[%s] Invalid Expression\n\n"
                                    "The expression `%s` raised an exception:\n"
                                    "\n%r" % (module_name, expr, e)
                                )
                                return
                    else:
                        eval_value = value

                # Evaluate stop condition, if given
                if stop_expr:
                    # Re-use env that has potentially been used before but
                    # append the current evaluated value
                    env['c'] = eval_value
                    try:
                        if bool(eval(stop_expr, env)):
                            break
                    except Exception as e:
                        if quiet:
                            sublime.status_message("Invalid Stop Expression: "
                                                   "`%s`" % stop_expr)
                            # Reset the stop expression so that we can exit the
                            # loop when all selections have been processed
                            stop_expr = None
                        else:
                            sublime.error_message(
                                "[%s] Invalid Stop Expression\n\n"
                                "The expression `%s` raised an exception:\n\n"
                                "%r" % (module_name, stop_expr, e)
                            )
                            return

                # Format
                if format:
                    replace = "{value:{format}}".format(value=eval_value,
                                                        format=format)
                else:
                    replace = str(eval_value)

            values.append(replace if not skip else str(value))

            if not EXPRMODE:
                value += step
            i += 1
            skip = False

        if EXPRMODE:
            # Expr mode is different (in reverse mode especially)
            if REVERSE:
                selections = reversed(selections)
            for i, region in enumerate(selections):
                # If we have a stopexpr just don't touch the other selections
                if i == len(values):
                    break

                self.view.replace(edit, region, values[i])
        else:
            # Insert the values into the regions (possibly in reversed order)
            for i, region in enumerate(selections):
                if i >= len(values):
                    # print("More selections than values generated.")
                    # Start at 0, break or insert "" for the remaining?
                    text = ""

                elif i + 1 == len(selections) != len(values):
                    # Last selection and more than 1 values to go
                    other = (values[i:] if not REVERSE
                             else values[-i - 1::-1])  # splicesssss
                    text = "\n".join(other)

                else:
                    if REVERSE:
                        i = -i - 1
                    text = values[i]

                self.view.replace(edit, region, text)

        # We're done
        if vid:
            lastsel = list(self.view.sel())
