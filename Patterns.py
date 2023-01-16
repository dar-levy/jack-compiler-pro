import re

COMMENT = "(//.*)|(/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/)"
EMPTY_TEXT = re.compile("\s*")
KEY_WORD = re.compile("^\s*("
                              "class|constructor|function|method|static|field"
                              "|var|int|char|boolean|void|true|false|null|this|"
                              "let|do|if|else|while|return)\s*")
SYMBOL = re.compile("^\s*([{}()\[\].,;+\-*/&|<>=~])\s*")
DIGIT = re.compile("^\s*(\d+)\s*")
STRING = re.compile("^\s*\"(.*)\"\s*")
IDENTIFIER = re.compile("^\s*([a-zA-Z_][a-zA-Z1-9_]*)\s*")