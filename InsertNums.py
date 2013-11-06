import sublime_plugin


class PromptInsertNumsCommand(sublime_plugin.WindowCommand):
    def run(self, automatic = True):
        self.window.show_input_panel(
            'Enter a starting number/character, step and padding.',
            '1 1 0',
            self.insertNums,
            self.insertNums if automatic else None,
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
    alpha = 'abcdefghijklmnopqrstuvwxyz'

    def run(self, edit, current, step, padding):
        if current.isdigit():
            def tick(counter):
                return str('%0*d' % (int(padding) + 1, int(current) + counter))

        elif current in self.alpha:
            current = self.decode(current)

            def tick(counter):
                return self.encode(current + counter)

        elif current in self.alpha.upper():
            current = self.decode(current.lower())

            def tick(counter):
                return self.encode(current + counter).upper()

        elif current[0] == 'x':
            current = int(current[1:])
            
            def tick(counter):
                return str('%0*x' % (int(padding) + 1, int(current) + counter))

        elif current[0] == '0' and current[1] == 'x':
            current = int(current[2:])
            padding = int(padding)

            def tick(counter):
                if(step == "<<"):
                    return str("0x%d" % int(counter + (current << padding)))
                elif(step == ">>"):
                    return str("0x%d" % int(counter + (current >> padding)))

        else:
            return

        # Do the stuff
        counter = 0
        for region in self.view.sel():
            self.view.replace(edit, region, tick(counter))
            if(step == "<<" or step == ">>"):
                counter += 1
            else:
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