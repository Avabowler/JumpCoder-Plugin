import os, sys
sys.path.append(os.getcwd())
from language_spec.language import LanguageSpec, create_temp_folder
from typing import List, Tuple
import re
from pathlib import Path
import hashlib
from code_eval.safe_subprocess import run
from tree_sitter import Language, Parser

BUILDIN_SYMBOLS = None

class CSharpScriptSpec(LanguageSpec):

    def __init__(self) -> None:
        global BUILDIN_SYMBOLS
        self.parser = Parser()
        self.parser.set_language(Language("language_spec/lib/cs.so", "c_sharp"))
        if BUILDIN_SYMBOLS is None:
            run(["csc", "language_spec/lib/print_cs_builtin.cs", "/out:language_spec/lib/print_cs_builtin.exe"])
            run(['mono', 'language_spec/lib/print_cs_builtin.exe'])
            BUILDIN_SYMBOLS = open("cs_builtin.log").read().split(",")
            os.remove("cs_builtin.log")
    
    def get_name(self) -> str:
        return "cs"

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
        global BUILDIN_SYMBOLS
        try:
            tree = self.parser.parse(self.complete_brackets(code_text).encode('utf8'))
        except:
            return 0
        defined_identifiers = set(BUILDIN_SYMBOLS)
        undefined_identifier = set()

        def traverse(node, name):
            if node.type == 'identifier':
                parent_type = node.parent.type
                text = node.text.decode('utf8')
                if 'declarat' in parent_type or 'using' in parent_type or 'generic_name' in parent_type or 'parameter' in parent_type or 'qualified_name' in parent_type or ('for_each_statement' in parent_type and name == 'left'):
                    defined_identifiers.add(text)
                elif text not in defined_identifiers:
                    
                    # print(text, parent_type, name)
                    if not (name == 'name' and parent_type == 'member_access_expression'):
                        undefined_identifier.add(text)
            for i in range(node.child_count):
                name = node.field_name_for_child(i)
                child = node.child(i)
                traverse(child, name)
        
        traverse(tree.root_node, None)
        if len(undefined_identifier) != 0:
            with open("test_debug_cs.log", "a") as f:
                f.write(code_text + f"\n------->\nUndefined: {undefined_identifier}\n======================================\n\n")
            print("Undefined", undefined_identifier)
        return len(undefined_identifier)

    def has_undefined_symbols(self, code_text: str) -> bool:
        return self.get_num_of_undefined_symbols(code_text) > 0

    def is_function(self, code_text: str) -> bool:
        code_text = code_text.split("\n")[0]
        return "static" in code_text and ('{') in code_text
    
    def is_import(self, code_text: str) -> bool:
        return code_text.strip().startswith("using")

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
            out_code_file = os.path.join(out_dir, "Problem.cs")

            code = code_text
            code = code + "\n" + reference
            with open(out_code_file, "w") as file:
                file.write(code)
            basename = ".".join(str(out_code_file).split(".")[:-1])
            binaryname = basename + ".exe"
            try:
                run_result = run(["csc", "/d:DEBUG", "-r:System.Numerics.dll", out_code_file, f"/out:{binaryname}"])
                if run_result.exit_code != 0:
                    return "SyntaxError: " + run_result.stderr + " | " + run_result.stdout , -2
                
                output = run(
                    ["mono", binaryname],
                    env={"PATH": os.getenv("PATH"), "MONO_TRACE_LISTENER": "Console.Error"}
                )
                # mono return 0 even when failing
                fail = (
                    "System.Diagnostics.DefaultTraceListener.Fail" in output.stderr
                    or "Unhandled Exception" in output.stderr
                )
                output.exit_code = 1 if fail else 0
                if output.exit_code == 0:
                    return "Pass", 0
                else:
                    return output.stderr, -1
            except:
                import traceback
                traceback.print_exc()
                return "Time out", -2

if __name__ == "__main__":
    test_code = """
class Problem {/*
    static bool IsPrime(long n) {
        if (n < 2) {
            return false;
        }
        for (long i = 2; i * i <= n; i++) {
            if (n % i == 0) {
                return false;
            }
        }
        return true;
    }*/
    // Implement a function that takes an non-negative integer and returns a list of the first n
    // integers that are prime numbers and less than n.
    // for example:
    // >>> CountUpTo((5L))
    // (new List<long>(new long[]{(long)2L, (long)3L}))
    // >>> CountUpTo((11L))
    // (new List<long>(new long[]{(long)2L, (long)3L, (long)5L, (long)7L}))
    // >>> CountUpTo((0L))
    // (new List<long>())
    // >>> CountUpTo((20L))
    // (new List<long>(new long[]{(long)2L, (long)3L, (long)5L, (long)7L, (long)11L, (long)13L, (long)17L, (long)19L}))
    // >>> CountUpTo((1L))
    // (new List<long>())
    // >>> CountUpTo((18L))
    // (new List<long>(new long[]{(long)2L, (long)3L, (long)5L, (long)7L, (long)11L, (long)13L, (long)17L}))
    public static List<long> CountUpTo(long n) {
        List<long> result = new List<long>();
        for (long i = 2; i < n; i++) {
            if (IsPrime(i)) {
                result.Add(i);
            }
        }
        return result;
    }
    static void Main() {
        foreach (var key in dict.Keys) {
            Console.WriteLine(string.Join(", ", CountUpTo(18L)));
        }
    }
}
"""
    print(CSharpScriptSpec().get_num_of_undefined_symbols(test_code))