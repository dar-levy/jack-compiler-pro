import re


class Pattern:
    def __init__(self):
        self.comment = "(//.*)|(/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/)"
        self.empty_text = re.compile("\s*")
        self.keyword = re.compile("^\s*("
                                  "class|constructor|function|method|static|field"
                                  "|var|int|char|boolean|void|true|false|null|this|"
                                  "let|do|if|else|while|return)\s*")
        self.symbol = re.compile("^\s*([{}()\[\].,;+\-*/&|<>=~])\s*")
        self.digit = re.compile("^\s*(\d+)\s*")
        self.string = re.compile("^\s*\"(.*)\"\s*")
        self.identifier = re.compile("^\s*([a-zA-Z_][a-zA-Z1-9_]*)\s*")
