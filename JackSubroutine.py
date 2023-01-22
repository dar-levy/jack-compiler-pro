from Patterns import JackSymbol


class JackSubroutine:
    def __init__(self, name, subroutine_type, return_type, jack_class):
        self.name = name
        self.jack_class = jack_class
        self.subroutine_type = subroutine_type
        self.return_type = return_type
        self.symbols = dict()
        self.arg_symbols = 0
        self.var_symbols = 0
        if subroutine_type == 'method':
            self.add_arg('this', self.jack_class.name)

    def add_arg(self, name, var_type):
        self.symbols[name] = JackSymbol('arg', var_type, self.arg_symbols)
        self.arg_symbols += 1

    def add_var(self, name, var_type):
        self.symbols[name] = JackSymbol('var', var_type, self.var_symbols)
        self.var_symbols += 1

    def get_symbol(self, name):
        symbol = self.symbols.get(name)
        if symbol is not None:
            return symbol

        return self.jack_class.get_symbol(name)
