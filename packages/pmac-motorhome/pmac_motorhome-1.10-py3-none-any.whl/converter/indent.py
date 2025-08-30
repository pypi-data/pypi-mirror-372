class Indenter:
    def __init__(self, level):
        self.level = level

    def format_text(self, text):
        return "    " * self.level + text + "\n"
