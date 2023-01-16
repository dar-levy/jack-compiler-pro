from JackTokenizer import JackTokenizer
import xml.etree.ElementTree as element_tree

OP_LIST = ["+", "-", "*", "/", "&", "|", "<", ">", "="]

class CompilationEngine:
    def __init__(self, input_file_path, output_path):
        self._tokenizer = JackTokenizer(input_file_path)
        self.xml_root = element_tree.Element("class")
        self._output = open(output_path, "w+")
        self.output_file_path = output_path
        self._indentation = 0

    def compile(self):
        self.compile_class()
        element_tree.indent(self.xml_root)
        xml_as_bytes = element_tree.tostring(self.xml_root, short_empty_elements=False)
        with open(self.output_file_path, "wb") as file:
            file.write(xml_as_bytes)
        file.close()

    def compile_class(self):
        current_father = self.xml_root
        if self._tokenizer.hasMoreTokens():
            self._tokenizer.advance()

            self._write_keyword(current_father)

            self._tokenizer.advance()
            self._write_identifier(current_father)

            self._tokenizer.advance()
            self._write_symbol(current_father)

            self._tokenizer.advance()
            self._handle_var_dec(current_father)
            self._handle_sub_routine(current_father)

            self._write_symbol(current_father)

    def _handle_var_dec(self, current_father):
        while self._tokenizer.get_keyword() == "field" or \
                self._tokenizer.get_keyword() == "static":
            self.compile_class_var_dec(current_father)

    def _handle_sub_routine(self, current_father):
        while self._tokenizer.get_keyword() == "constructor" or \
                self._tokenizer.get_keyword() == "function" \
                or self._tokenizer.get_keyword() == "method":
            self.compileSubroutine(current_father)

    def compile_class_var_dec(self, current_father):
        new_father = element_tree.SubElement(current_father, "classVarDec")
        self._write_keyword(new_father)

        self._tokenizer.advance()
        self._compile_type_and_varName(new_father)

    def compileSubroutine(self, current_father):
        new_father = element_tree.SubElement(current_father, "subroutineDec")
        self._write_keyword(new_father)

        self._tokenizer.advance()
        if self._tokenizer.get_token_type() == self._tokenizer.KEYWORD:
            self._write_keyword(new_father)
        elif self._tokenizer.get_token_type() == self._tokenizer.IDENTIFIER:
            self._write_identifier(new_father)

        self._tokenizer.advance()
        self._write_identifier(new_father)

        self._tokenizer.advance()
        self._write_symbol(new_father)

        self._tokenizer.advance()
        self.compileParameterList(new_father)

        self._write_symbol(new_father)

        self._tokenizer.advance()

        self.compile_subroutine_body(new_father)

        self._tokenizer.advance()

    def compile_subroutine_body(self, current_father):
        new_father = element_tree.SubElement(current_father, "subroutineBody")
        self._write_symbol(new_father)

        self._tokenizer.advance()
        while self._tokenizer.get_keyword() == "var":
            self.compileVarDec(new_father)

        self.compileStatements(new_father)

        self._write_symbol(new_father)

    def compileParameterList(self, current_father):
        new_father = element_tree.SubElement(current_father, "parameterList")
        while self._tokenizer.get_token_type() != self._tokenizer.SYMBOL:
            if self._tokenizer.get_token_type() == self._tokenizer.KEYWORD:
                self._write_keyword(new_father)
            elif self._tokenizer.get_token_type() == self._tokenizer.IDENTIFIER:
                self._write_identifier(new_father)
            self._tokenizer.advance()
            self._write_identifier(new_father)
            self._tokenizer.advance()
            if self._tokenizer.get_symbol() == ",":
                self._write_symbol(new_father)
                self._tokenizer.advance()

    def compileVarDec(self, current_father):
        new_father = element_tree.SubElement(current_father, "varDec")
        self._write_keyword(new_father)
        self._tokenizer.advance()
        self._compile_type_and_varName(new_father)

    def compileStatements(self, current_father):
        new_father = element_tree.SubElement(current_father, "statements")
        while self._tokenizer.get_token_type() == self._tokenizer.KEYWORD:
            if self._tokenizer.get_keyword() == "let":
                self.compileLet(new_father)
            elif self._tokenizer.get_keyword() == "if":
                self.compileIf(new_father)
            elif self._tokenizer.get_keyword() == "while":
                self.compileWhile(new_father)
            elif self._tokenizer.get_keyword() == "do":
                self.compileDo(new_father)
            elif self._tokenizer.get_keyword() == "return":
                self.compileReturn(new_father)

    def compileDo(self, current_father):
        new_father = element_tree.SubElement(current_father, "doStatement")
        self._write_keyword(new_father)

        self._tokenizer.advance()

        self._write_identifier(new_father)
        self._tokenizer.advance()
        if self._tokenizer.get_symbol() == ".":
            self._write_symbol(new_father)
            self._tokenizer.advance()
            self._write_identifier(new_father)
            self._tokenizer.advance()

        self._write_symbol(new_father)

        self._tokenizer.advance()
        self.compileExpressionList(new_father)

        self._write_symbol(new_father)

        self._tokenizer.advance()
        self._write_symbol(new_father)

        self._tokenizer.advance()

    def compileLet(self, current_father):
        new_father = element_tree.SubElement(current_father, "letStatement")
        self._write_keyword(new_father)

        self._tokenizer.advance()
        self._write_identifier(new_father)

        self._tokenizer.advance()
        if self._tokenizer.get_symbol() == "[":
            self._write_symbol(new_father)
            self._tokenizer.advance()
            self.compileExpression(new_father)
            self._write_symbol(new_father)
            self._tokenizer.advance()

        self._write_symbol(new_father)

        self._tokenizer.advance()
        self.compileExpression(new_father)
        self._write_symbol(new_father)

        self._tokenizer.advance()

    def compileWhile(self, current_father):
        new_father = element_tree.SubElement(current_father, "whileStatement")
        self._write_keyword(new_father)

        self._tokenizer.advance()
        self._write_symbol(new_father)

        self._tokenizer.advance()
        self.compileExpression(new_father)

        self._write_symbol(new_father)

        self._tokenizer.advance()
        self._write_symbol(new_father)

        self._tokenizer.advance()
        self.compileStatements(new_father)

        self._write_symbol(new_father)
        self._tokenizer.advance()

    def compileReturn(self, current_father):
        new_father = element_tree.SubElement(current_father, "returnStatement")
        self._write_keyword(new_father)

        self._tokenizer.advance()
        if self._tokenizer.get_token_type() != self._tokenizer.SYMBOL and \
                self._tokenizer.get_symbol() != ";":
            self.compileExpression(new_father)

        self._write_symbol(new_father)
        self._tokenizer.advance()

    def compileIf(self, current_father):
        new_father = element_tree.SubElement(current_father, "ifStatement")
        self._write_keyword(new_father)

        self._tokenizer.advance()
        self._write_symbol(new_father)

        self._tokenizer.advance()
        self.compileExpression(new_father)

        self._write_symbol(new_father)

        self._tokenizer.advance()
        self._write_symbol(new_father)

        self._tokenizer.advance()
        self.compileStatements(new_father)

        self._write_symbol(new_father)

        self._tokenizer.advance()
        if self._tokenizer.get_token_type() == self._tokenizer.KEYWORD and \
                self._tokenizer.get_keyword() == "else":
            self._write_keyword(new_father)

            self._tokenizer.advance()
            self._write_symbol(new_father)

            self._tokenizer.advance()
            self.compileStatements(new_father)

            self._write_symbol(new_father)
            self._tokenizer.advance()


    def compileExpression(self, current_father):
        new_father = element_tree.SubElement(current_father, "expression")
        self.compileTerm(new_father)
        while self._tokenizer.get_token_type() == self._tokenizer.SYMBOL and \
                self._tokenizer.get_symbol() in OP_LIST:
            self._write_symbol(new_father)
            self._tokenizer.advance()
            self.compileTerm(new_father)

    def compileTerm(self, current_father):
        sanity_check = True
        new_father = element_tree.SubElement(current_father, "term")
        if self._tokenizer.get_token_type() == self._tokenizer.DIGIT:
            self._write_int_const(new_father)
        elif self._tokenizer.get_token_type() == self._tokenizer.STRING:
            self._write_str_const(new_father)
        elif self._tokenizer.get_token_type() == self._tokenizer.KEYWORD:
            self._write_keyword(new_father)
        elif self._tokenizer.get_token_type() == self._tokenizer.IDENTIFIER:
            self._write_identifier(new_father)


            self._tokenizer.advance()
            sanity_check = False
            if self._tokenizer.get_symbol() == "[":
                sanity_check = True
                self._write_symbol(new_father)
                self._tokenizer.advance()
                self.compileExpression(new_father)
                self._write_symbol(new_father)
            elif self._tokenizer.get_symbol() == ".":
                sanity_check = True
                self._write_symbol(new_father)
                self._tokenizer.advance()
                self._write_identifier(new_father)
                self._tokenizer.advance()
                self._write_symbol(new_father)
                self._tokenizer.advance()
                self.compileExpressionList(new_father)
                self._write_symbol(new_father)
            elif self._tokenizer.get_symbol() == "(":
                sanity_check = True
                self._write_symbol(new_father)
                self._tokenizer.advance()
                self.compileExpressionList(new_father)
                self._write_symbol(new_father)

        elif self._tokenizer.get_symbol() == "(":
            self._write_symbol(new_father)
            self._tokenizer.advance()
            self.compileExpression(new_father)
            self._write_symbol(new_father)
        elif self._tokenizer.get_symbol() == "~" or self._tokenizer.get_symbol() == \
                "-":
            self._write_symbol(new_father)
            self._tokenizer.advance()
            self.compileTerm(new_father)
            sanity_check = False

        if sanity_check:
            self._tokenizer.advance()

    def compileExpressionList(self, current_father):
        new_father = element_tree.SubElement(current_father, "expressionList")
        if self._tokenizer.get_token_type() != self._tokenizer.SYMBOL and \
                self._tokenizer.get_symbol() != ")":
            self.compileExpression(new_father)
            while self._tokenizer.get_token_type() == self._tokenizer.SYMBOL and \
                    self._tokenizer.get_symbol() == ",":
                self._write_symbol(new_father)
                self._tokenizer.advance()
                self.compileExpression(new_father)
        if self._tokenizer.get_symbol() =="(":
            self.compileExpression(new_father)
            while self._tokenizer.get_token_type() == self._tokenizer.SYMBOL and \
                    self._tokenizer.get_symbol() == ",":
                self._write_symbol(new_father)
                self._tokenizer.advance()
                self.compileExpression(new_father)

    def _compile_type_and_varName(self, current_father):
        if self._tokenizer.get_token_type() == self._tokenizer.KEYWORD:
            self._write_keyword(current_father)
        elif self._tokenizer.get_token_type() == self._tokenizer.IDENTIFIER:
            self._write_identifier(current_father)
        self._tokenizer.advance()
        self._write_identifier(current_father)
        self._tokenizer.advance()
        while self._tokenizer.get_symbol() == ",":
            self._write_symbol(current_father)
            self._tokenizer.advance()
            self._write_identifier(current_father)
            self._tokenizer.advance()
        self._write_symbol(current_father)
        self._tokenizer.advance()

    def _write_identifier(self, current_father):
        self._create_element(self._tokenizer.get_identifier(), 'identifier', current_father)

    def _write_keyword(self, current_father):
        self._create_element(self._tokenizer.get_keyword(), 'keyword', current_father)

    def _write_symbol(self, current_father):
        string_to_write = self._tokenizer.get_symbol()
        if self._tokenizer.get_symbol() == "<":
            string_to_write = "&lt;"
        elif self._tokenizer.get_symbol() == ">":
            string_to_write = "&gt;"
        elif self._tokenizer.get_symbol() == "&":
            string_to_write = "&amp;"

        self._create_element(string_to_write, 'symbol', current_father)

    def _write_int_const(self, current_father):
        self._create_element(self._tokenizer.get_identifier(), 'integerConstant', current_father)

    def _write_str_const(self, current_father):
        self._create_element(self._tokenizer.get_identifier(), 'stringConstant', current_father)

    def _create_element(self, element_name, element_type, current_father):
        current_xml_element = element_tree.SubElement(current_father, element_type)
        current_xml_element.text = f' {element_name} '