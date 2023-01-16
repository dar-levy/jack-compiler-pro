import re
import Patterns as pattern


class JackTokenizer:
    KEYWORD = 0
    SYMBOL = 1
    INT_CONST = 2
    STRING_CONST = 3
    IDENTIFIER = 4

    def __init__(self, input_path):
        self.text = self._get_pure_data(input_path)
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
        return re.sub(pattern.COMMENT, "", data)

    def hasMoreTokens(self):
        if re.fullmatch(pattern.EMPTY_TEXT, self.text):
            return False
        else:
            return True

    def advance(self):
        if self.hasMoreTokens():
            current_match = re.match(pattern.KEY_WORD, self.text)
            if current_match is not None:
                self.text = re.sub(pattern.KEY_WORD, "", self.text)
                self._tokenType = JackTokenizer.KEYWORD
                self._currentToken = current_match.group(1)
            else:
                current_match = re.match(pattern.SYMBOL, self.text)
                if current_match is not None:
                    self.text = re.sub(pattern.SYMBOL, "", self.text)
                    self._tokenType = JackTokenizer.SYMBOL
                    self._currentToken = current_match.group(1)
                else:
                    current_match = re.match(pattern.DIGIT, self.text)
                    if current_match is not None:
                        self.text = re.sub(pattern.DIGIT, "", self.text)
                        self._tokenType = JackTokenizer.INT_CONST
                        self._currentToken = current_match.group(1)
                    else:
                        current_match = re.match(pattern.STRING, self.text)
                        if current_match is not None:
                            self.text = re.sub(pattern.STRING, "", self.text)
                            self._tokenType = JackTokenizer.STRING_CONST
                            self._currentToken = current_match.group(1)
                        else:
                            current_match = re.match(pattern.IDENTIFIER, self.text)
                            if current_match is not None:
                                self.text = re.sub(pattern.IDENTIFIER, "", self.text)
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