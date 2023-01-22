kind_to_segment = {'static': 'static',
                   'field': 'this',
                   'arg': 'argument',
                   'var': 'local'}

class VMWriter:
	def __init__(self, vm_file):
		self.vm_file = vm_file
		self.label_count = 0

	def write_if(self, label):
		self.vm_file.write('not\n')
		self.vm_file.write('if-goto {}\n'.format(label))

	def write_goto(self, label):
		self.vm_file.write('goto {}\n'.format(label))

	def write_label(self, label):
		self.vm_file.write('label {}\n'.format(label))

	def write_function(self, jack_subroutine):
		class_name = jack_subroutine.jack_class.name
		name = jack_subroutine.name
		local_vars = jack_subroutine.var_symbols
		subroutine_type = jack_subroutine.subroutine_type

		self.vm_file.write('function {}.{} {}\n'.format(class_name, name, local_vars))

	def write_return(self):
		self.vm_file.write('return\n')

	def write_call(self, class_name, func_name, arg_count):
		self.vm_file.write('call {0}.{1} {2}\n'.format(
				class_name, func_name, arg_count
			))

	def write_pop_symbol(self, jack_symbol):
		kind = jack_symbol.kind
		offset = jack_symbol.id

		segment = kind_to_segment[kind]
		self.write_pop(segment, offset)

	def write_push_symbol(self, jack_symbol):
		kind = jack_symbol.kind
		offset = jack_symbol.id

		segment = kind_to_segment[kind]
		self.write_push(segment, offset)

	def write_pop(self, segment, offset):
		self.vm_file.write('pop {0} {1}\n'.format(segment, offset))

	def write_push(self, segment, offset):
		self.vm_file.write('push {0} {1}\n'.format(segment, offset))

	def write(self, action):
		self.vm_file.write('{}\n'.format(action))

	def write_int(self, n):
		self.write_push('constant', n)

	def write_string(self, s):
		s = s[1:-1]
		self.write_int(len(s))
		self.write_call('String', 'new', 1)
		for c in s:
			self.write_int(ord(c))
			self.write_call('String','appendChar', 2)