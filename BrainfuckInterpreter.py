import sublime
import sublime_plugin
import re

VERSION = int(sublime.version())


class BrainfuckInterpreterCommand(sublime_plugin.TextCommand):
    """Implementation of interpreter for Brainfuck"""

    def run(self, edit):
        sels = self.view.sel()
        self.edit = edit
        self.window = sublime.active_window()

        if sels[0].empty():
            self.view.run_command('select_all')

        for s in sels:
            if not s.empty():
                selected = self.view.substr(s)
                self.code = re.sub(r'([^><\+\-\.,\[\]])', '', selected)

                if self.code.count('[') != self.code.count(']'):
                    msg = 'Brainfuck Interpreter: Bad loops count'
                    sublime.error_message(msg)
                elif self.code.count(','):
                    msg = 'Brainfuck Interpreter type value:'
                    self.window.show_input_panel(msg, '', self.read_input, None, None)
                else:
                    self.bf()

    def bf(self):
        self.cells = {}
        self.pointer = 0
        self.buffer = []
        self.code_pointer = 0
        self.output = ''

        while self.code_pointer < len(self.code):
            self.interpret(self.code[self.code_pointer])
            self.code_pointer += 1

        view = self.window.new_file()
        view.run_command('brainfuck_result', {'result': self.output})

    def interpret(self, command):
        if self.pointer not in self.cells:
            self.cells[self.pointer] = 0

        if command == '>':
            self.pointer += 1

        elif command == '<':
            self.pointer -= 1

        elif command == '+':
            if self.cells[self.pointer] < 255:
                self.cells[self.pointer] += 1
            else:
                self.cells[self.pointer] = 0
        elif command == '-':
            if self.cells[self.pointer] > 0:
                self.cells[self.pointer] -= 1
            else:
                self.cells[self.pointer] = 255

        elif command == '.':
            if self.pointer in self.cells:
                self.output += chr(self.cells[self.pointer])

        elif command == ',':
            if self.input != []:
                self.cells[self.pointer] = self.input.pop(0)

        elif command == '[':
            if self.cells[self.pointer] == 0:
                loop = 1

                while (loop > 0) and (self.code_pointer + 1 < len(self.code)):
                    self.code_pointer += 1
                    if self.code[self.code_pointer] == '[':
                        loop += 1
                    elif self.code[self.code_pointer] == ']':
                        loop -= 1
            else:
                self.buffer.append(self.code_pointer)

        elif command == ']':
            self.code_pointer = self.buffer.pop() - 1

        return True

    def read_input(self, input):
        self.input = list(input.encode('ascii', 'ignore'))
        self.bf()

    def enc(self):
        if self.view.encoding() == 'Undefined':
            return self.view.settings().get('default_encoding', 'UTF-8')
        else:
            return self.view.encoding()


class BrainfuckResultCommand(sublime_plugin.TextCommand):
    """Print result of Brainfuck interpreter"""

    def run(self, edit, result):
        self.view.insert(edit, 0, result)
