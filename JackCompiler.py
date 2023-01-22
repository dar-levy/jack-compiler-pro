import os
import sys
from os import path
from CompilationEngine import CompilationEngine
from JackTokenizer import JackTokenizer


class JackCompiler:
    def __init__(self, directory_path):
        self.directory_path = directory_path
        self.input_path = path.dirname(directory_path) if path.isfile(directory_path) else directory_path

    def compile(self):
        if path.isfile(self.directory_path):
            self._read_file()
        else:
            self._read_directory()

    def _read_file(self):
        if self.directory_path.endswith(".jack"):
            input_file_path = self.directory_path
            output_xml_path = f"{self.directory_path.split('.')[0]}.xml"
            output_vm_path = f"{self.directory_path.split('.')[0]}.vm"
            with open(output_vm_path, 'w') as vm_file:
                tokenizer = JackTokenizer(input_file_path)
                current_code = CompilationEngine(tokenizer, output_xml_path, vm_file)
                current_code.compile()

            vm_file.close()

    def _read_directory(self):
        for file_name in os.listdir(self.input_path):
            if file_name.endswith(".jack"):
                input_file_path = f"{self.input_path}/{file_name.split('.')[0]}.jack"
                output_xml_path = f"{self.input_path}/{file_name.split('.')[0]}.xml"
                output_vm_path = f"{self.input_path}/{file_name.split('.')[0]}.vm"
                with open(output_vm_path, 'w') as vm_file:
                    tokenizer = JackTokenizer(input_file_path)
                    current_code = CompilationEngine(tokenizer, output_xml_path, vm_file)
                    current_code.compile()

                vm_file.close()


# The main program:
if __name__ == "__main__":
    jack_compiler = JackCompiler(sys.argv[1])
    jack_compiler.compile()
