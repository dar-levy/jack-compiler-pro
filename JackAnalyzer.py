import sys
import os
from os import path
from CompilationEngine import CompilationEngine
from JackTokenizer import JackTokenizer
class JackAnalyzer:
    def __init__(self, directory_path):
        self.directory_path = directory_path
        self.input_path = path.dirname(directory_path) if path.isfile(directory_path) else directory_path

    def analyze(self):
        if path.isfile(self.directory_path): self._read_file()
        else: self._read_directory()

    def _read_file(self):
        if self.directory_path.endswith(".jack"):
            input_file_path = self.directory_path
            output_xml_path = f"{self.directory_path.split('.')[0]}.xml"
            output_vm_path = f"{self.directory_path.split('.')[0]}.vm"
            with open(output_vm_path, 'w') as vm_file:
                tokenizer = JackTokenizer(input_file_path)
                current_code = CompilationEngine(tokenizer, vm_file)
                current_code.compile()
    def _read_directory(self):
        for file_name in os.listdir(self.input_path):
            if file_name.endswith(".jack"):
                input_file_path = f"{self.input_path}/{file_name.split('.')[0]}.jack"
                output_file_path = f"{self.input_path}/{file_name.split('.')[0]}.xml"
                current_code = CompilationEngine(input_file_path, output_file_path)
                current_code.compile()

# The main program:
if __name__ == "__main__":
    jack_analyzer = JackAnalyzer(sys.argv[1])
    jack_analyzer.analyze()