import sublime, sublime_plugin

class PromptInsertNumsCommand(sublime_plugin.WindowCommand):
    def run(self):
        self.window.show_input_panel('Enter a starting number and step.', '1 1', self.on_done, None, None)
        pass

    def on_done(self, text):
        try:
            (current, step) = map(str, text.split(" "))
            if self.window.active_view():
                self.window.active_view().run_command("insert_nums", {"current" : current, "step" : step} )
        except ValueError:
            pass

class InsertNumsCommand(sublime_plugin.TextCommand):
    def run(self, edit, current, step):
        current = int(current)
        for region in self.view.sel():
            sublime.status_message("Inserting #" + str(current))
            self.view.replace(edit, region, str(current))
            current = current + int(step)