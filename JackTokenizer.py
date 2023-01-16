import re
from Pattern import Pattern

COMMENT = "(//.*)|(/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/)"
EMPTY_TEXT_PATTERN = re.compile("\s*")
KEY_WORD_PATTERN = re.compile("^\s*("
                              "class|constructor|function|method|static|field"
                              "|var|int|char|boolean|void|true|false|null|this|"
                              "let|do|if|else|while|return)\s*")
SYMBOL_PATTERN = re.compile("^\s*([{}()\[\].,;+\-*/&|<>=~])\s*")
DIGIT_PATTERN = re.compile("^\s*(\d+)\s*")
STRING_PATTERN = re.compile("^\s*\"(.*)\"\s*")
IDENTIFIER_PATTERN = re.compile("^\s*([a-zA-Z_][a-zA-Z1-9_]*)\s*")


class JackTokenizer:
    KEYWORD = 0
    SYMBOL = 1
    INT_CONST = 2
    STRING_CONST = 3
    IDENTIFIER = 4

    def __init__(self, input_path):
        self.text = self._get_pure_data(input_path)
        self.pattern = Pattern()
        self._tokenType = None
        self._currentToken = None

    def _get_pure_data(self, input_path):
        file_data = self._read_file(input_path)
        return self._clean_data(file_data)

    def _read_file(self, input_path):
        with open(input_path, "r") as file:
            data = file.read()
        file.close()

        return data

    def _clean_data(self, data):
        return re.sub(COMMENT, "", data)

    def hasMoreTokens(self):
        if re.fullmatch(self.pattern.empty_text, self.text):
            return False
        else:
            return True

    def advance(self):
        if self.hasMoreTokens():
            current_match = re.match(self.pattern.keyword, self.text)
            if current_match is not None:
                self.text = re.sub(self.pattern.keyword, "", self.text)
                self._tokenType = JackTokenizer.KEYWORD
                self._currentToken = current_match.group(1)
            else:
                current_match = re.match(self.pattern.symbol, self.text)
                if current_match is not None:
                    self.text = re.sub(self.pattern.symbol, "", self.text)
                    self._tokenType = JackTokenizer.SYMBOL
                    self._currentToken = current_match.group(1)
                else:
                    current_match = re.match(self.pattern.digit, self.text)
                    if current_match is not None:
                        self.text = re.sub(self.pattern.digit, "", self.text)
                        self._tokenType = JackTokenizer.INT_CONST
                        self._currentToken = current_match.group(1)
                    else:
                        current_match = re.match(self.pattern.string, self.text)
                        if current_match is not None:
                            self.text = re.sub(self.pattern.string, "", self.text)
                            self._tokenType = JackTokenizer.STRING_CONST
                            self._currentToken = current_match.group(1)
                        else:
                            current_match = re.match(self.pattern.identifier, self.text)
                            if current_match is not None:
                                self.text = re.sub(self.pattern.identifier, "", self.text)
                                self._tokenType = JackTokenizer.IDENTIFIER
                                self._currentToken = current_match.group(1)

    def get_token_type(self):
        return self._tokenType

    def get_keyword(self):
        return self._currentToken

    def get_symbol(self):
        return self._currentToken

    def get_identifier(self):
        return self._currentToken

    def get_int_val(self):
        return int(self._currentToken)

    def get_string_val(self):
        return self._currentToken

if __name__ == "__main__":
    tokenizer = JackTokenizer("Square/Square.jack")
    while tokenizer.hasMoreTokens():
        tokenizer.advance()
        print(tokenizer.get_keyword())