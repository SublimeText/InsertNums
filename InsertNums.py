import sublime_plugin


class PromptInsertNumsCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.window.show_input_panel(
            'Enter a starting number/character, step and padding.',
            '1 1 0',
            self.insertNums,
            self.insertNums,
            None
        )
        pass

    def insertNums(self, text):
        try:
            (current, step, padding) = map(str, text.split(" "))

            if self.window.active_view():
                self.window.active_view().run_command(
                    "insert_nums",
                    {"current": current, "step": step, "padding": padding}
                )
        except ValueError:
            pass


class InsertNumsCommand(sublime_plugin.TextCommand):
    digits = '0123456789'
    alpha = 'abcdefghijklmnopqrstuvwxyz'

    def run(self, edit, current, step, padding):
        if current in self.digits:
            def tick(counter):
                return str('%0*d' % (int(padding), int(current) + counter))

        elif current in self.alpha:
            current = self.decode(current)

            def tick(counter):
                return self.encode(current + counter)

        elif current in self.alpha.upper():
            current = self.decode(current.lower())

            def tick(counter):
                return self.encode(current + counter).upper()

        else:
            return

        # Do the stuff
        counter = 0
        for region in self.view.sel():
            self.view.replace(edit, region, tick(counter))
            counter += int(step)

    def encode(self, num):
        res = ''

        while num > 0:
            num -= 1
            if(num >= 0):
                res = self.alpha[int(num) % 26] + res
                num /= 26

        return res

    def decode(self, str):
        res = 0

        for i in str:
            res *= 26
            res += self.alpha.index(i) + 1

        return res