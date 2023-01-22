import VMGenerator
import CompilationTypes
import xml.etree.ElementTree as element_tree

OP_LIST = ["+", "-", "*", "/", "&", "|", "<", ">", "="]

binary_op_actions = {'+': 'add',
                     '-': 'sub',
                     '*': 'call Math.multiply 2',
                     '/': 'call Math.divide 2',
                     '&': 'and',
                     '|': 'or',
                     '<': 'lt',
                     '>': 'gt',
                     '=': 'eq'}


label_count = 0

class CompilationEngine:
    def __init__(self,tokenizer, vm_file):
        self.xml_root = element_tree.Element("class")
        self.vm_writer = VMGenerator.VMGenerator(vm_file)
        self._tokenizer = tokenizer

    @staticmethod
    def get_label():
        global label_count

        label = 'L{}'.format(label_count)
        label_count += 1

        return label

    def compile(self):
        self.compile_class()
        element_tree.indent(self.xml_root)
        xml_as_bytes = element_tree.tostring(self.xml_root, short_empty_elements=False)
        # with open(self.output_file_path, "wb") as file:
        #     file.write(xml_as_bytes)
        # file.close()

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

        self.vm_writer.write_function(jack_element)

        if jack_element.subroutine_type == 'constructor':
            field_count = jack_element.jack_class.field_symbols
            self.vm_writer.write_push('constant', field_count)
            self.vm_writer.write_call('Memory', 'alloc', 1)
            # Set 'this' in the function to allow it to return it
            self.vm_writer.write_pop('pointer', 0)
        elif jack_element.subroutine_type == 'method':
            self.vm_writer.write_push('argument', 0)
            self.vm_writer.write_pop('pointer', 0)

        self.compile_statements(new_father, jack_element)

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

    def compile_statements(self, current_father, jack_element):
        new_father = element_tree.SubElement(current_father, "statements")
        while self._tokenizer.get_token_type() == self._tokenizer.KEYWORD:
            if self._tokenizer.get_keyword() == "let":
                self.compile_let(new_father, jack_element)
            elif self._tokenizer.get_keyword() == "if":
                self.compile_if(new_father, jack_element)
            elif self._tokenizer.get_keyword() == "while":
                self.compile_while(new_father, jack_element)
            elif self._tokenizer.get_keyword() == "do":
                self.compile_do(new_father, jack_element)
            elif self._tokenizer.get_keyword() == "return":
                self.compile_return(new_father, jack_element)

    def compile_do(self, current_father, jack_subroutine):
        new_father = element_tree.SubElement(current_father, "doStatement")
        self._write_keyword(new_father)
        self._tokenizer.advance()

        self.compile_term(new_father, jack_subroutine)

        self.vm_writer.write_pop('temp', 0)
        self._write_symbol(new_father)
        self._tokenizer.advance()


    def compile_let(self, current_father, jack_subroutine):
        new_father = element_tree.SubElement(current_father, "letStatement")
        self._write_keyword(new_father)
        self._tokenizer.advance()

        var_name = self._tokenizer.get_symbol()
        jack_symbol = jack_subroutine.get_symbol(var_name)

        self._write_identifier(new_father)
        self._tokenizer.advance()

        if self._tokenizer.get_symbol() == "[":
            self._write_symbol(new_father)
            self._tokenizer.advance()

            self.compile_expression(new_father, jack_subroutine)

            self._write_symbol(new_father)
            self._tokenizer.advance()

            self._write_symbol(new_father)
            self._tokenizer.advance()

            self.vm_writer.write_push_symbol(jack_symbol)
            self.vm_writer.write('add')

            self.compile_expression(new_father, jack_subroutine)

            self.vm_writer.write_pop('temp', 0)
            self.vm_writer.write_pop('pointer', 1)
            self.vm_writer.write_push('temp', 0)
            self.vm_writer.write_pop('that', 0)
        else:
            self._write_symbol(new_father)
            self._tokenizer.advance()
            self.compile_expression(new_father, jack_subroutine)
            self.vm_writer.write_pop_symbol(jack_symbol)

        self._write_symbol(new_father)
        self._tokenizer.advance()

    def compile_while(self, current_father, jack_subroutine):
        new_father = element_tree.SubElement(current_father, "whileStatement")
        self._write_keyword(new_father)
        self._tokenizer.advance()

        self._write_symbol(new_father)
        self._tokenizer.advance()

        while_label = CompilationEngine.get_label()
        false_label = CompilationEngine.get_label()

        self.vm_writer.write_label(while_label)
        self.compile_expression(new_father, jack_subroutine)

        self._write_symbol(new_father)
        self._tokenizer.advance()

        self._write_symbol(new_father)
        self._tokenizer.advance()

        self.vm_writer.write_if(false_label)

        self.compile_statements(new_father, jack_subroutine)

        self.vm_writer.write_goto(while_label)
        self.vm_writer.write_label(false_label)

        self._write_symbol(new_father)
        self._tokenizer.advance()

    def compile_return(self, current_father, jack_subroutine):
        new_father = element_tree.SubElement(current_father, "returnStatement")
        self._write_keyword(new_father)
        self._tokenizer.advance()

        if self._tokenizer.get_token_type() != self._tokenizer.SYMBOL and \
                self._tokenizer.get_symbol() != ";":
            self.compile_expression(new_father, jack_subroutine)
        else:
            self.vm_writer.write_int(0)

        self.vm_writer.write_return()

        self._write_symbol(new_father)
        self._tokenizer.advance()

    def compile_if(self, current_father, jack_subroutine):
        new_father = element_tree.SubElement(current_father, "ifStatement")
        self._write_keyword(new_father)

        self._tokenizer.advance()
        self._write_symbol(new_father)

        self._tokenizer.advance()
        self.compile_expression(new_father, jack_subroutine)

        self._write_symbol(new_father)
        self._tokenizer.advance()

        self._write_symbol(new_father)
        self._tokenizer.advance()

        false_label = CompilationEngine.get_label()
        end_label = CompilationEngine.get_label()

        self.vm_writer.write_if(false_label)

        self.compile_statements(new_father, jack_subroutine)

        self.vm_writer.write_goto(end_label)
        self.vm_writer.write_label(false_label)

        self._write_symbol(new_father)
        self._tokenizer.advance()

        if self._tokenizer.get_token_type() == self._tokenizer.KEYWORD and \
                self._tokenizer.get_keyword() == "else":
            self._write_keyword(new_father)
            self._tokenizer.advance()

            self._write_symbol(new_father)
            self._tokenizer.advance()

            self.compile_statements(new_father, jack_subroutine)

            self._write_symbol(new_father)
            self._tokenizer.advance()

        self.vm_writer.write_label(end_label)

    def compile_expression(self, current_father, jack_subroutine):
        new_father = element_tree.SubElement(current_father, "expression")
        self.compile_term(new_father, jack_subroutine)
        while self._tokenizer.get_token_type() == self._tokenizer.SYMBOL and \
                self._tokenizer.get_symbol() in OP_LIST:
            binary_op = self._tokenizer.get_symbol()
            self._write_symbol(new_father)
            self._tokenizer.advance()
            self.compile_term(new_father, jack_subroutine)
            self.vm_writer.write(binary_op_actions[binary_op])

    def compile_term(self, current_father, jack_subroutine):
        sanity_check = True
        new_father = element_tree.SubElement(current_father, "term") if current_father.tag != "doStatement" else current_father
        if self._tokenizer.get_token_type() == self._tokenizer.DIGIT:
            self._write_int_const(new_father)
        elif self._tokenizer.get_token_type() == self._tokenizer.STRING:
            self._write_str_const(new_father)
        elif self._tokenizer.get_token_type() == self._tokenizer.KEYWORD:
            self._write_keyword(new_father)
            if self._tokenizer.get_identifier() == 'this':
                self.vm_writer.write_push('pointer', 0)
            else:
                self.vm_writer.write_int(0) # null / false
                if self._tokenizer.get_identifier() == 'true':
                    self.vm_writer.write('not')
        elif self._tokenizer.get_token_type() == self._tokenizer.IDENTIFIER:
            self._write_identifier(new_father)
            token_value = self._tokenizer.get_identifier()
            token_var = jack_subroutine.get_symbol(self._tokenizer.get_identifier())
            self._tokenizer.advance()

            function_name = token_value
            function_class = jack_subroutine.jack_class.name
            arg_count = 0

            sanity_check = False

            if self._tokenizer.get_symbol() == "[":
                sanity_check = True
                self._write_symbol(new_father)
                self._tokenizer.advance()

                self.compile_expression(new_father, jack_subroutine)
                self.vm_writer.write_push_symbol(token_var)
                self.vm_writer.write('add')
                # rebase 'that' to point to var+index
                self.vm_writer.write_pop('pointer', 1)
                self.vm_writer.write_push('that', 0)

                self._write_symbol(new_father)
            elif self._tokenizer.get_symbol() == ".":
                sanity_check = True

                self._write_symbol(new_father)
                self._tokenizer.advance()
                function_object = jack_subroutine.get_symbol(token_value)

                self._write_identifier(new_father)
                function_name = self._tokenizer.get_identifier()
                self._tokenizer.advance()

                if function_object:
                    function_class = token_var.type  # Use the class of the object
                    arg_count = 1  # Add 'this' to args
                    self.vm_writer.write_push_symbol(token_var)  # push "this"
                else:
                    function_class = token_value

                self._write_symbol(new_father)
                self._tokenizer.advance()

                arg_count += self.compile_expression_list(new_father, jack_subroutine)
                self.vm_writer.write_call(function_class, function_name, arg_count)

                self._write_symbol(new_father)
            elif self._tokenizer.get_symbol() == "(":
                sanity_check = True
                arg_count = 1
                self.vm_writer.write_push('pointer', 0)

                self._write_symbol(new_father)
                self._tokenizer.advance()
                arg_count += self.compile_expression_list(new_father, jack_subroutine)
                self.vm_writer.write_call(function_class, function_name, arg_count)

                self._write_symbol(new_father)
            elif token_var:
                self.vm_writer.write_push_symbol(token_var)

        elif self._tokenizer.get_symbol() == "(": # TODO: Debug to see when you enter here
            self._write_symbol(new_father)
            self._tokenizer.advance()
            self.compile_expression(new_father, jack_subroutine)
            self._write_symbol(new_father)
        elif self._tokenizer.get_symbol() == "~":
            self._write_symbol(new_father)
            self._tokenizer.advance()
            self.compile_term(new_father, jack_subroutine)
            self.vm_writer.write('not')
            sanity_check = False
        elif self._tokenizer.get_symbol() == "-":
            self._write_symbol(new_father)
            self._tokenizer.advance()
            self.compile_term(new_father, jack_subroutine)
            self.vm_writer.write('neg')
            sanity_check = False

        if sanity_check:
            self._tokenizer.advance()


    def compile_expression_list(self, current_father, jack_subroutine):
        count = 0
        new_father = element_tree.SubElement(current_father, "expressionList")
        if self._tokenizer.get_token_type() != self._tokenizer.SYMBOL and \
                self._tokenizer.get_symbol() != ")":
            count += 1
            self.compile_expression(new_father, jack_subroutine)
            while self._tokenizer.get_token_type() == self._tokenizer.SYMBOL and \
                    self._tokenizer.get_symbol() == ",":
                self._write_symbol(new_father)
                self._tokenizer.advance()
                self.compile_expression(new_father, jack_subroutine)
                count += 1
        if self._tokenizer.get_symbol() == "(":
            self.compile_expression(new_father, jack_subroutine)
            count += 1
            while self._tokenizer.get_token_type() == self._tokenizer.SYMBOL and \
                    self._tokenizer.get_symbol() == ",":
                self._write_symbol(new_father)
                self._tokenizer.advance()
                self.compile_expression(new_father, jack_subroutine)
                count += 1

        return count

    def _compile_type_and_varName(self, current_father, jack_element, current_type=None):
        var_type = self._tokenizer.get_identifier()

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
        self.vm_writer.write_int(self._tokenizer.get_identifier())

    def _write_str_const(self, current_father):
        self._create_element(self._tokenizer.get_identifier(), 'stringConstant', current_father)
        self.vm_writer.write_string(self._tokenizer.get_identifier())

    def _create_element(self, element_name, element_type, current_father):
        current_xml_element = element_tree.SubElement(current_father, element_type)
        current_xml_element.text = f' {element_name} '