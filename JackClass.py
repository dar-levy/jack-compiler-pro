from Patterns import JackSymbol

class JackClass:
	def __init__(self, name):
		self.name = name
		self.symbols = dict()
		self.static_symbols = 0
		self.field_symbols = 0

	def add_field(self, name, var_type):
		self.symbols[name] = JackSymbol('field', var_type, self.field_symbols)
		self.field_symbols += 1

	def add_static(self, name, var_type):
		self.symbols[name] = JackSymbol('static', var_type, self.static_symbols)
		self.static_symbols += 1

	def get_symbol(self, name):
		return self.symbols.get(name)
