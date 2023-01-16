from JackTokenizer import JackTokenizer

OP_LIST = ["+", "-", "*", "/", "&", "|", "<", ">", "="]

class CompilationEngine:
    def __init__(self, input_file_path, output_path):
        self._indentation = 0
        self._tokenizer = JackTokenizer(input_file_path)
        self._output = open(output_path, "w+")

    def compileClass(self):
        if self._tokenizer.hasMoreTokens():
            self._tokenizer.advance()
            self._output.write("<class>\n")
            self._indentation += 1

            self._write_keyword()

            self._tokenizer.advance()
            self._write_identifier()

            self._tokenizer.advance()
            self._write_symbol()

            self._tokenizer.advance()
            while self._tokenizer.get_keyword() == "static" or \
                    self._tokenizer.get_keyword() == "field":
                self.compileClassVarDec()
            while self._tokenizer.get_keyword() == "constructor" or \
                    self._tokenizer.get_keyword() == "function" \
                    or self._tokenizer.get_keyword() == "method":
                self.compileSubroutine()

            self._write_symbol()

            self._indentation -= 1
            self._output.write("</class>\n")
            self._output.close()

    def compileClassVarDec(self):
        self._output.write("  " * self._indentation + "<classVarDec>\n")
        self._indentation += 1
        self._write_keyword()

        self._tokenizer.advance()
        self._compile_type_and_varName()

        self._indentation -= 1
        self._output.write("  " * self._indentation + "</classVarDec>\n")

    def compileSubroutine(self):
        self._output.write("  " * self._indentation + "<subroutineDec>\n")
        self._indentation += 1
        self._write_keyword()

        self._tokenizer.advance()
        if self._tokenizer.tokenType() == self._tokenizer.KEYWORD:
            self._write_keyword()
        elif self._tokenizer.tokenType() == self._tokenizer.IDENTIFIER:
            self._write_identifier()

        self._tokenizer.advance()
        self._write_identifier()

        self._tokenizer.advance()
        self._write_symbol()

        self._tokenizer.advance()
        self.compileParameterList()

        self._write_symbol()

        self._tokenizer.advance()
        # compile subroutineBody:
        self._output.write("  " * self._indentation + "<subroutineBody>\n")
        self._indentation += 1
        self._write_symbol()

        self._tokenizer.advance()
        while self._tokenizer.get_keyword() == "var":
            self.compileVarDec()

        self.compileStatements()

        self._write_symbol()
        self._indentation -= 1
        self._output.write("  " * self._indentation + "</subroutineBody>\n")
        self._indentation -= 1
        self._output.write("  " * self._indentation + "</subroutineDec>\n")
        self._tokenizer.advance()

    def compileParameterList(self):
        self._output.write("  " * self._indentation + "<parameterList>\n")
        self._indentation += 1
        while self._tokenizer.tokenType() != self._tokenizer.SYMBOL:
            if self._tokenizer.tokenType() == self._tokenizer.KEYWORD:
                self._write_keyword()
            elif self._tokenizer.tokenType() == self._tokenizer.IDENTIFIER:
                self._write_identifier()
            self._tokenizer.advance()
            self._write_identifier()
            self._tokenizer.advance()
            if self._tokenizer.get_symbol() == ",":
                self._write_symbol()
                self._tokenizer.advance()

        self._indentation -= 1
        self._output.write("  " * self._indentation + "</parameterList>\n")

    def compileVarDec(self):
        self._output.write("  " * self._indentation + "<varDec>\n")
        self._indentation += 1

        self._write_keyword()
        self._tokenizer.advance()
        self._compile_type_and_varName()

        self._indentation -= 1
        self._output.write("  " * self._indentation + "</varDec>\n")

    def compileStatements(self):
        self._output.write("  " * self._indentation + "<statements>\n")
        self._indentation += 1
        while self._tokenizer.tokenType() == self._tokenizer.KEYWORD:
            if self._tokenizer.get_keyword() == "let":
                self.compileLet()
            elif self._tokenizer.get_keyword() == "if":
                self.compileIf()
            elif self._tokenizer.get_keyword() == "while":
                self.compileWhile()
            elif self._tokenizer.get_keyword() == "do":
                self.compileDo()
            elif self._tokenizer.get_keyword() == "return":
                self.compileReturn()
        self._indentation -= 1
        self._output.write("  " * self._indentation + "</statements>\n")

    def compileDo(self):
        self._output.write("  " * self._indentation + "<doStatement>\n")
        self._indentation += 1
        self._write_keyword()

        self._tokenizer.advance()
        #subroutineCall
        self._write_identifier()
        self._tokenizer.advance()
        if self._tokenizer.get_symbol() == ".":
            self._write_symbol()
            self._tokenizer.advance()
            self._write_identifier()
            self._tokenizer.advance()

        self._write_symbol()

        self._tokenizer.advance()
        self.compileExpressionList()

        self._write_symbol()

        self._tokenizer.advance()
        self._write_symbol()

        self._indentation -= 1
        self._output.write("  " * self._indentation + "</doStatement>\n")
        self._tokenizer.advance()

    def compileLet(self):
        self._output.write("  " * self._indentation + "<letStatement>\n")
        self._indentation += 1
        self._write_keyword()

        self._tokenizer.advance()
        self._write_identifier()

        self._tokenizer.advance()
        if self._tokenizer.get_symbol() == "[":
            self._write_symbol()
            self._tokenizer.advance()
            self.compileExpression()
            self._write_symbol()
            self._tokenizer.advance()

        self._write_symbol()

        self._tokenizer.advance()
        self.compileExpression()
        self._write_symbol()

        self._indentation -= 1
        self._output.write("  " * self._indentation + "</letStatement>\n")
        self._tokenizer.advance()

    def compileWhile(self):
        self._output.write("  " * self._indentation + "<whileStatement>\n")
        self._indentation += 1
        self._write_keyword()

        self._tokenizer.advance()
        self._write_symbol()

        self._tokenizer.advance()
        self.compileExpression()

        self._write_symbol()

        self._tokenizer.advance()
        self._write_symbol()

        self._tokenizer.advance()
        self.compileStatements()

        self._write_symbol()

        self._indentation -= 1
        self._output.write("  " * self._indentation + "</whileStatement>\n")
        self._tokenizer.advance()

    def compileReturn(self):
        self._output.write("  " * self._indentation + "<returnStatement>\n")
        self._indentation += 1
        self._write_keyword()

        self._tokenizer.advance()
        if self._tokenizer.tokenType() != self._tokenizer.SYMBOL and \
                self._tokenizer.get_symbol() != ";":
            self.compileExpression()

        self._write_symbol()

        self._indentation -= 1
        self._output.write("  " * self._indentation + "</returnStatement>\n")
        self._tokenizer.advance()

    def compileIf(self):
        self._output.write("  " * self._indentation + "<ifStatement>\n")
        self._indentation += 1
        self._write_keyword()

        self._tokenizer.advance()
        self._write_symbol()

        self._tokenizer.advance()
        self.compileExpression()

        self._write_symbol()

        self._tokenizer.advance()
        self._write_symbol()

        self._tokenizer.advance()
        self.compileStatements()

        self._write_symbol()

        self._tokenizer.advance()
        if self._tokenizer.tokenType() == self._tokenizer.KEYWORD and \
                self._tokenizer.get_keyword() == "else":
            self._write_keyword()

            self._tokenizer.advance()
            self._write_symbol()

            self._tokenizer.advance()
            self.compileStatements()

            self._write_symbol()
            self._tokenizer.advance()

        self._indentation -= 1
        self._output.write("  " * self._indentation + "</ifStatement>\n")


    def compileExpression(self):
        """
        Note that tokenizer must be advanced before this is called!!!
        :return:
        """
        self._output.write("  " * self._indentation + "<expression>\n")
        self._indentation += 1

        self.compileTerm()
        while self._tokenizer.tokenType() == self._tokenizer.SYMBOL and \
                self._tokenizer.get_symbol() in OP_LIST:
            self._write_symbol()
            self._tokenizer.advance()
            self.compileTerm()

        self._indentation -= 1
        self._output.write("  " * self._indentation + "</expression>\n")

    def compileTerm(self):
        # debugging - not finished!!
        sanity_check = True
        self._output.write("  " * self._indentation + "<term>\n")
        self._indentation += 1
        if self._tokenizer.tokenType() == self._tokenizer.INT_CONST:
            self._write_int_const()
        elif self._tokenizer.tokenType() == self._tokenizer.STRING_CONST:
            self._write_str_const()
        elif self._tokenizer.tokenType() == self._tokenizer.KEYWORD:
            self._write_keyword()
        elif self._tokenizer.tokenType() == self._tokenizer.IDENTIFIER:
            self._write_identifier()


            self._tokenizer.advance()
            sanity_check = False
            if self._tokenizer.get_symbol() == "[":
                sanity_check = True
                self._write_symbol()
                self._tokenizer.advance()
                self.compileExpression()
                self._write_symbol()
            elif self._tokenizer.get_symbol() == ".":  ## subroutine case
                sanity_check = True
                self._write_symbol()
                self._tokenizer.advance()
                self._write_identifier()
                self._tokenizer.advance()
                self._write_symbol()
                self._tokenizer.advance()
                self.compileExpressionList()
                self._write_symbol()
            elif self._tokenizer.get_symbol() == "(":
                sanity_check = True
                self._write_symbol()
                self._tokenizer.advance()
                self.compileExpressionList()
                self._write_symbol()

        elif self._tokenizer.get_symbol() == "(":
            self._write_symbol()
            self._tokenizer.advance()
            self.compileExpression()
            self._write_symbol()
        elif self._tokenizer.get_symbol() == "~" or self._tokenizer.get_symbol() == \
                "-":
            self._write_symbol()
            self._tokenizer.advance()
            self.compileTerm()
            sanity_check = False

        if sanity_check:
            self._tokenizer.advance()

        self._indentation -= 1
        self._output.write("  " * self._indentation + "</term>\n")

    def compileExpressionList(self):
        self._output.write("  " * self._indentation + "<expressionList>\n")
        self._indentation += 1

        if self._tokenizer.tokenType() != self._tokenizer.SYMBOL and \
                self._tokenizer.get_symbol() != ")":
            self.compileExpression()
            while self._tokenizer.tokenType() == self._tokenizer.SYMBOL and \
                    self._tokenizer.get_symbol() == ",":
                self._write_symbol()
                self._tokenizer.advance()
                self.compileExpression()
        if self._tokenizer.get_symbol() =="(":
            self.compileExpression()
            while self._tokenizer.tokenType() == self._tokenizer.SYMBOL and \
                    self._tokenizer.get_symbol() == ",":
                self._write_symbol()
                self._tokenizer.advance()
                self.compileExpression()

        self._indentation -= 1
        self._output.write("  " * self._indentation + "</expressionList>\n")

    def _compile_type_and_varName(self):
        if self._tokenizer.tokenType() == self._tokenizer.KEYWORD:
            self._write_keyword()
        elif self._tokenizer.tokenType() == self._tokenizer.IDENTIFIER:
            self._write_identifier()
        self._tokenizer.advance()
        self._write_identifier()
        self._tokenizer.advance()
        while self._tokenizer.get_symbol() == ",":
            self._write_symbol()
            self._tokenizer.advance()
            self._write_identifier()
            self._tokenizer.advance()
        self._write_symbol()
        self._tokenizer.advance()

    def _write_identifier(self):
        self._output.write("  " * self._indentation + "<identifier> " +
                           self._tokenizer.identifier() + " </identifier>\n")

    def _write_keyword(self):
        self._output.write("  " * self._indentation + "<keyword> " +
                           self._tokenizer.get_keyword() + " </keyword>\n")

    def _write_symbol(self):
        string_to_write = self._tokenizer.get_symbol()
        if self._tokenizer.get_symbol() == "<":
            string_to_write = "&lt"
        elif self._tokenizer.get_symbol() == ">":
            string_to_write = "&gt"
        elif self._tokenizer.get_symbol() == "&":
            string_to_write = "&amp"
        self._output.write("  " * self._indentation + "<symbol> " +
                           string_to_write + " </symbol>\n")

    def _write_int_const(self):
        self._output.write("  " * self._indentation + "<integerConstant> " +
                           self._tokenizer.identifier() + " </integerConstant>\n")

    def _write_str_const(self):
        self._output.write("  " * self._indentation + "<stringConstant> " +
                           self._tokenizer.identifier() + " </stringConstant>\n")