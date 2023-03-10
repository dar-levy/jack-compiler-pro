from Patterns import TYPE_TO_SYMBOL


class VMGenerator:
    def __init__(self, vm_file):
        self.vm_file = vm_file
        self.label_count = 0

    def write_function(self, jack_subroutine):
        class_name = jack_subroutine.jack_class.name
        name = jack_subroutine.name
        local_vars = jack_subroutine.var_symbols
        self.vm_file.write(f'function {class_name}.{name} {local_vars}\n')

    def write_if(self, label):
        self.vm_file.write('not\n')
        self.vm_file.write(f'if-goto {label}\n')

    def write_goto(self, label):
        self.vm_file.write(f'goto {label}\n')

    def write_label(self, label):
        self.vm_file.write(f'label {label}\n')

    def write_return(self):
        self.vm_file.write('return\n')

    def write_call(self, class_name, func_name, arg_count):
        self.vm_file.write(f'call {class_name}.{func_name} {arg_count}\n')

    def write_pop_symbol(self, jack_symbol):
        kind = jack_symbol.kind
        offset = jack_symbol.id
        segment = TYPE_TO_SYMBOL[kind]
        self.write_pop(segment, offset)

    def write_push_symbol(self, jack_symbol):
        kind = jack_symbol.kind
        offset = jack_symbol.id
        segment = TYPE_TO_SYMBOL[kind]
        self.write_push(segment, offset)

    def write_int(self, number):
        self.write_push('constant', number)

    def write_string(self, s):
        s = s[1:-1]
        self.write_int(len(s))
        self.write_call('String', 'new', 1)
        for c in s:
            self.write_int(ord(c))
            self.write_call('String', 'appendChar', 2)

    def write_pop(self, segment, offset):
        self.vm_file.write(f'pop {segment} {offset}\n')

    def write_push(self, segment, offset):
        self.vm_file.write(f'push {segment} {offset}\n')

    def write(self, element):
        self.vm_file.write(f'{element}\n')
