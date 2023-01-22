import CompilationTypes
from JackTokenizer import JackTokenizer
import xml.etree.ElementTree as element_tree

OP_LIST = ["+", "-", "*", "/", "&", "|", "<", ">", "="]

class CompilationEngine:
    def __init__(self, input_file_path, output_path):
        self._tokenizer = JackTokenizer(input_file_path)
        self.xml_root = element_tree.Element("class")
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
            class_name = self._tokenizer.get_identifier()
            jack_class = CompilationTypes.JackClass(class_name)

            self._tokenizer.advance()
            self._write_symbol(current_father)

            self._tokenizer.advance()
            self._handle_var_dec(current_father, jack_class)
            self._handle_sub_routine(current_father, jack_class)

            self._write_symbol(current_father)

    def _handle_var_dec(self, current_father, jack_class):
        while self._tokenizer.get_keyword() == "field" or \
                self._tokenizer.get_keyword() == "static":
            self.compile_class_var_dec(current_father, jack_class)

    def _handle_sub_routine(self, current_father, jack_class):
        while self._tokenizer.get_keyword() == "constructor" or \
                self._tokenizer.get_keyword() == "function" \
                or self._tokenizer.get_keyword() == "method":
            self.compile_subroutine(current_father, jack_class)

    def compile_class_var_dec(self, current_father, jack_class):
        new_father = element_tree.SubElement(current_father, "classVarDec")
        self._write_keyword(new_father)
        current_type = self._tokenizer.get_keyword()
        self._tokenizer.advance()
        self._compile_type_and_varName(new_father, jack_class, current_type)

    def compile_subroutine(self, current_father, jack_class):
        new_father = element_tree.SubElement(current_father, "subroutineDec")
        self._write_keyword(new_father)
        subroutine_type = self._tokenizer.get_keyword()
        self._tokenizer.advance()

        return_type = self._tokenizer.get_identifier()
        if self._tokenizer.get_token_type() == self._tokenizer.KEYWORD:
            self._write_keyword(new_father)
        elif self._tokenizer.get_token_type() == self._tokenizer.IDENTIFIER:
            self._write_identifier(new_father)

        self._tokenizer.advance()

        name = self._tokenizer.get_identifier()
        jack_subroutine = CompilationTypes.JackSubroutine(
            name, subroutine_type, return_type, jack_class
        )


        self._write_identifier(new_father)
        self._tokenizer.advance()

        self._write_symbol(new_father)
        self._tokenizer.advance()

        self.compile_parameter_list(new_father, jack_subroutine)

        self._write_symbol(new_father)

        self._tokenizer.advance()

        self.compile_subroutine_body(new_father, jack_subroutine)

        self._tokenizer.advance()

    def compile_subroutine_body(self, current_father, jack_element):
        new_father = element_tree.SubElement(current_father, "subroutineBody")
        self._write_symbol(new_father)

        self._tokenizer.advance()
        while self._tokenizer.get_keyword() == "var":
            self.compile_var_dec(new_father, jack_element)

        self.compile_statements(new_father)

        self._write_symbol(new_father)

    def compile_parameter_list(self, current_father, jack_subroutine):
        new_father = element_tree.SubElement(current_father, "parameterList")
        while self._tokenizer.get_token_type() != self._tokenizer.SYMBOL:
            if self._tokenizer.get_token_type() == self._tokenizer.KEYWORD:
                self._write_keyword(new_father)
            elif self._tokenizer.get_token_type() == self._tokenizer.IDENTIFIER:
                self._write_identifier(new_father)

            parameter_type = self._tokenizer.get_keyword()
            self._tokenizer.advance()

            self._write_identifier(new_father)
            parameter_name = self._tokenizer.get_identifier()
            self._tokenizer.advance()

            jack_subroutine.add_arg(parameter_name, parameter_type)

            if self._tokenizer.get_symbol() == ",":
                self._write_symbol(new_father)
                self._tokenizer.advance()

    def compile_var_dec(self, current_father, jack_element):
        new_father = element_tree.SubElement(current_father, "varDec")
        self._write_keyword(new_father)
        current_type = self._tokenizer.get_keyword()
        self._tokenizer.advance()
        self._compile_type_and_varName(new_father, jack_element, current_type) # TODO: add jack_subroutine

    def compile_statements(self, current_father):
        new_father = element_tree.SubElement(current_father, "statements")
        while self._tokenizer.get_token_type() == self._tokenizer.KEYWORD:
            if self._tokenizer.get_keyword() == "let":
                self.compile_let(new_father)
            elif self._tokenizer.get_keyword() == "if":
                self.compile_if(new_father)
            elif self._tokenizer.get_keyword() == "while":
                self.compile_while(new_father)
            elif self._tokenizer.get_keyword() == "do":
                self.compile_do(new_father)
            elif self._tokenizer.get_keyword() == "return":
                self.compile_return(new_father)

    def compile_do(self, current_father):
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
        self.compile_expression_list(new_father)

        self._write_symbol(new_father)

        self._tokenizer.advance()
        self._write_symbol(new_father)

        self._tokenizer.advance()

    def compile_let(self, current_father):
        new_father = element_tree.SubElement(current_father, "letStatement")
        self._write_keyword(new_father)

        self._tokenizer.advance()
        self._write_identifier(new_father)

        self._tokenizer.advance()
        if self._tokenizer.get_symbol() == "[":
            self._write_symbol(new_father)
            self._tokenizer.advance()
            self.compile_expression(new_father)
            self._write_symbol(new_father)
            self._tokenizer.advance()

        self._write_symbol(new_father)

        self._tokenizer.advance()
        self.compile_expression(new_father)
        self._write_symbol(new_father)

        self._tokenizer.advance()

    def compile_while(self, current_father):
        new_father = element_tree.SubElement(current_father, "whileStatement")
        self._write_keyword(new_father)

        self._tokenizer.advance()
        self._write_symbol(new_father)

        self._tokenizer.advance()
        self.compile_expression(new_father)

        self._write_symbol(new_father)

        self._tokenizer.advance()
        self._write_symbol(new_father)

        self._tokenizer.advance()
        self.compile_statements(new_father)

        self._write_symbol(new_father)
        self._tokenizer.advance()

    def compile_return(self, current_father):
        new_father = element_tree.SubElement(current_father, "returnStatement")
        self._write_keyword(new_father)

        self._tokenizer.advance()
        if self._tokenizer.get_token_type() != self._tokenizer.SYMBOL and \
                self._tokenizer.get_symbol() != ";":
            self.compile_expression(new_father)

        self._write_symbol(new_father)
        self._tokenizer.advance()

    def compile_if(self, current_father):
        new_father = element_tree.SubElement(current_father, "ifStatement")
        self._write_keyword(new_father)

        self._tokenizer.advance()
        self._write_symbol(new_father)

        self._tokenizer.advance()
        self.compile_expression(new_father)

        self._write_symbol(new_father)

        self._tokenizer.advance()
        self._write_symbol(new_father)

        self._tokenizer.advance()
        self.compile_statements(new_father)

        self._write_symbol(new_father)

        self._tokenizer.advance()
        if self._tokenizer.get_token_type() == self._tokenizer.KEYWORD and \
                self._tokenizer.get_keyword() == "else":
            self._write_keyword(new_father)

            self._tokenizer.advance()
            self._write_symbol(new_father)

            self._tokenizer.advance()
            self.compile_statements(new_father)

            self._write_symbol(new_father)
            self._tokenizer.advance()


    def compile_expression(self, current_father):
        new_father = element_tree.SubElement(current_father, "expression")
        self.compile_term(new_father)
        while self._tokenizer.get_token_type() == self._tokenizer.SYMBOL and \
                self._tokenizer.get_symbol() in OP_LIST:
            self._write_symbol(new_father)
            self._tokenizer.advance()
            self.compile_term(new_father)

    def compile_term(self, current_father):
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
                self.compile_expression(new_father)
                self._write_symbol(new_father)
            elif self._tokenizer.get_symbol() == ".":
                sanity_check = True
                self._write_symbol(new_father)
                self._tokenizer.advance()
                self._write_identifier(new_father)
                self._tokenizer.advance()
                self._write_symbol(new_father)
                self._tokenizer.advance()
                self.compile_expression_list(new_father)
                self._write_symbol(new_father)
            elif self._tokenizer.get_symbol() == "(":
                sanity_check = True
                self._write_symbol(new_father)
                self._tokenizer.advance()
                self.compile_expression_list(new_father)
                self._write_symbol(new_father)

        elif self._tokenizer.get_symbol() == "(":
            self._write_symbol(new_father)
            self._tokenizer.advance()
            self.compile_expression(new_father)
            self._write_symbol(new_father)
        elif self._tokenizer.get_symbol() == "~" or self._tokenizer.get_symbol() == \
                "-":
            self._write_symbol(new_father)
            self._tokenizer.advance()
            self.compile_term(new_father)
            sanity_check = False

        if sanity_check:
            self._tokenizer.advance()

    def compile_expression_list(self, current_father):
        new_father = element_tree.SubElement(current_father, "expressionList")
        if self._tokenizer.get_token_type() != self._tokenizer.SYMBOL and \
                self._tokenizer.get_symbol() != ")":
            self.compile_expression(new_father)
            while self._tokenizer.get_token_type() == self._tokenizer.SYMBOL and \
                    self._tokenizer.get_symbol() == ",":
                self._write_symbol(new_father)
                self._tokenizer.advance()
                self.compile_expression(new_father)
        if self._tokenizer.get_symbol() =="(":
            self.compile_expression(new_father)
            while self._tokenizer.get_token_type() == self._tokenizer.SYMBOL and \
                    self._tokenizer.get_symbol() == ",":
                self._write_symbol(new_father)
                self._tokenizer.advance()
                self.compile_expression(new_father)

    def _compile_type_and_varName(self, current_father, jack_element, current_type=None):
        var_type = self._tokenizer.get_token_type()

        if self._tokenizer.get_token_type() == self._tokenizer.KEYWORD:
            self._write_keyword(current_father)
        elif self._tokenizer.get_token_type() == self._tokenizer.IDENTIFIER:
            self._write_identifier(current_father)

        self._tokenizer.advance()
        self._add_jack_element(jack_element, var_type, current_type)
        self._write_identifier(current_father)

        self._tokenizer.advance()
        while self._tokenizer.get_symbol() == ",":
            self._write_symbol(current_father)
            self._tokenizer.advance()
            self._write_identifier(current_father)
            self._add_jack_element(jack_element, var_type, current_type)
            self._tokenizer.advance()

        self._write_symbol(current_father)
        self._tokenizer.advance()

    def _add_jack_element(self, jack_element, var_type, current_type):
        var_name = self._tokenizer.get_identifier()
        if current_type == 'static':
            jack_element.add_static(var_name, var_type)
        elif current_type == 'field':
            jack_element.add_field(var_name, var_type)
        else:
            jack_element.add_var(var_name, var_type)
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