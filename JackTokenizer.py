import re
import Patterns as pattern


class JackTokenizer:
    KEYWORD = 0
    SYMBOL = 1
    DIGIT = 2
    STRING = 3
    IDENTIFIER = 4

    def __init__(self, input_path):
        self.text = self._get_pure_data(input_path)
        self._token_type = None
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
            self._update_properties_if(pattern.KEY_WORD, JackTokenizer.KEYWORD)
            self._update_properties_if(pattern.SYMBOL, JackTokenizer.SYMBOL)
            self._update_properties_if(pattern.DIGIT, JackTokenizer.DIGIT)
            self._update_properties_if(pattern.STRING, JackTokenizer.STRING)
            self._update_properties_if(pattern.IDENTIFIER, JackTokenizer.IDENTIFIER)

    def _update_properties(self, pattern, token_type, current_match):
        self.text = re.sub(pattern, "", self.text)
        self._token_type = token_type
        self._currentToken = current_match.group(1)

    def _update_properties_if(self, pattern, token_type):
        current_match = re.match(pattern, self.text)
        if current_match is not None:
            self._update_properties(pattern, token_type, current_match)
    def get_token_type(self):
        return self._token_type

    def get_keyword(self):
        return self._currentToken

    def get_symbol(self):
        return self._currentToken

    def get_identifier(self):
        return self._currentToken

if __name__ == "__main__":
    tokenizer = JackTokenizer("Square/Square.jack")
    while tokenizer.hasMoreTokens():
        tokenizer.advance()
        print(tokenizer.get_keyword())