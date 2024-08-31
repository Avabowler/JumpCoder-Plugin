import os, sys
sys.path.append(os.getcwd())
from language_spec.language import LanguageSpec, create_temp_folder
from typing import List, Tuple
import re
from pathlib import Path
import hashlib
from code_eval.safe_subprocess import run
import random
import esprima
import shutil
import json
import subprocess

class JavaScriptSpec(LanguageSpec):

    def __init__(self) -> None:
        self.js_builtins = subprocess.run('node -e "console.log(Object.getOwnPropertyNames(globalThis).join(\',\'))"', capture_output=True, text=True, shell=True).stdout.strip().split(',')
    
    def get_name(self) -> str:
        return "js"

    def infilling_bad_words(self) -> List[str]: 
        return ["//", "/*"]

    def complete_brackets(self, code):
        open_brackets = code.count('{')
        close_brackets = code.count('}')
        missing_brackets = open_brackets - close_brackets

        # Append the missing closing brackets
        for _ in range(open_brackets - close_brackets):
            code += "\n}"
            missing_brackets -= 1

        return code


    def get_num_of_undefined_symbols(self, code_text: str) -> int:
        try:
            parsed_code = esprima.parseScript(self.complete_brackets(code_text))
        except:
            return 0
        defined_identifiers = set(self.js_builtins)
        undefined_identifier = set()

        def traverse(node, parent=None):
            # print(node.type)
            if node.type == 'VariableDeclaration':
                for decl in node.declarations:
                    defined_identifiers.add(decl.id.name)
            elif node.type == 'FunctionDeclaration' or node.type == 'FunctionExpression' or node.type == "ArrowFunctionExpression":
                for param in node.params:
                    defined_identifiers.add(param.name)
                if node.id is not None:
                    defined_identifiers.add(node.id.name)
            elif node.type == 'Identifier' and node.name not in defined_identifiers:
                undefined_identifier.add(node.name)
            if callable(node.items):
                for k, v in node.items():
                    if k == 'property': continue
                    if isinstance(v, list):
                        for child in v:
                            traverse(child, node)
                    elif hasattr(v, "type"):
                        traverse(v, node)

        traverse(parsed_code)
        if len(undefined_identifier) != 0:
            with open("test_debug.log", "a") as f:
                f.write(code_text + f"\n------->\nUndefined: {undefined_identifier}\n======================================\n\n")
            print("Undefined", undefined_identifier)
        return len(undefined_identifier)

    def has_undefined_symbols(self, code_text: str) -> bool:
        return self.get_num_of_undefined_symbols(code_text) > 0

    def is_function(self, code_text: str) -> bool:
        return code_text.strip().startswith("function") or "=>" in code_text
    
    def is_import(self, code_text: str) -> bool:
        return code_text.strip().startswith("require")

    def can_address_undefined_symbols(self, code_text: str, infilling_lines: str, combine_code: str) -> bool:
        previous_num_undefined_symbols = self.get_num_of_undefined_symbols(code_text)
        if previous_num_undefined_symbols == 0:
            return False
        current_num_undefined_symbols = self.get_num_of_undefined_symbols(combine_code)
        return current_num_undefined_symbols < previous_num_undefined_symbols and current_num_undefined_symbols >= 0

    def is_in_comment(self, code_lines: List[str], index: int) -> bool:
        in_block_comment = False
        for i, line in enumerate(code_lines):
            if '/*' in line:
                in_block_comment = True
            if i == index:
                return line.lstrip().startswith("//") or in_block_comment
            if '*/' in line:
                in_block_comment = False
        return False


    def is_illegal_infilling(self, infilling_line: str) -> bool:
        return infilling_line.lstrip().startswith(("for", "if", "while", "else"))
    
    def extract_first_function(self, code_text: str) -> Tuple[List[str], bool]:
        open_brackets = 0
        method_body = []
        in_block_comment = False
        code_after_method = False

        lines = code_text.split('\n')
        for i, line in enumerate(lines):
            # Check for the start or end of a block comment
            if '/*' in line:
                in_block_comment = True
            if '*/' in line:
                in_block_comment = False
                method_body.append(line)
                continue

            if not in_block_comment:
                # Check for the start of the method body
                if '{' in line:
                    open_brackets += line.count('{')
                    if open_brackets == 1 and not method_body:
                        # Start capturing the method body
                        method_body.append(line)
                        continue

                if open_brackets > 0:
                    method_body.append(line)

                # Check for the end of the method body
                if '}' in line:
                    open_brackets -= line.count('}')
                    if open_brackets == 0:
                        break

        # Check if there is code after the method
        if i + 1 < len(lines):
            code_after_method = any(line.strip() for line in lines[i+1:])

        return method_body, code_after_method
    
    def evaluate(self, code_text: str, reference: str) -> Tuple[str, float]:
        with create_temp_folder() as out_dir:
            out_code_file = os.path.join(out_dir, "Problem.js")

            code = code_text
            code = code + "\n" + reference
            with open(out_code_file, "w") as file:
                file.write(code)
            try:
                run_result = run(["node", out_code_file])
                if run_result.exit_code != 0:
                    return "Runtime Error: " + run_result.stderr , -1  
                else:
                    print(run_result.stdout)
                    return "Pass", 0
            except:
                return "Time out", -2

if __name__ == "__main__":

    test_code = """
function foo(eff) {
    var new_text = text.replace(/\s+/g, (match, index, originalText) => {
        Math;
        o;
        return "";
    });
}
"""
    print(JavaScriptSpec().get_num_of_undefined_symbols(test_code))