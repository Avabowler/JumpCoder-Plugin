import os
import subprocess
from pathlib import Path
from typing import List, Tuple
import json
import ast
import builtins
import typing
import socket
import pickle
import bz2
# import torch
from code_eval.execute import check_correctness

SIZE_DATA_LENGTH = 16

def receive(connection: socket.socket) -> dict:
    data_length = int(connection.recv(SIZE_DATA_LENGTH).decode())
    data = connection.recv(data_length)
    return pickle.loads(bz2.decompress(data))

def send(connection: socket.socket, data: dict):
    data = bz2.compress(pickle.dumps(data))
    data_length = str(len(data)).encode().ljust(SIZE_DATA_LENGTH)
    connection.sendall(data_length)
    connection.sendall(data)

def request_api(connection: socket.socket, data: dict) -> dict:
    send(connection, data)
    return receive(connection)

def evaluate_code(
    prompt: str, 
    code_text: str, 
    stop_words: list[str], 
    example: List[str], 
    reference: str
) -> Tuple[str, float]:
    code = code_text
    for _ in range(10):
        try:
            exec(code, {})
            break
        except:
            code = "\n".join(code.split("\n")[:-1])
    try:
        exec(code, {})
    except:
        return "Compile error", -3
    code = code + "\n" + reference
    print("~~~~",code,"~~~")
    result = check_correctness(code, 3, 0, 0)
    if result['passed']:
        return "Pass", 0
    else:
        return result['result'], -1

def evaluate_java_code(
    prompt: str, 
    code_text: str, 
    stop_words: list[str], 
    example: List[str], 
    reference: str
) -> Tuple[str, float]:
    sys_env = os.environ.copy()
    javatuples_path = Path("/home/mouxiangchen/LLM/bigcode-evaluation-harness/datasets/javatuples-1.2.jar")
    out_dir = "/home/mouxiangchen/LLM/JumpCoder"
    sys_env["CLASSPATH"] = f"{javatuples_path}"

    code = code_text
    code = code + "\n" + reference
    with open("Problem.java", "w") as file:
        file.write(code)
    compile_command = "javac Problem.java"
    run_command = f"java -ea -cp {out_dir} Problem"
    # print("test1")
    compile_result = subprocess.run(compile_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=sys_env)
    if compile_result.returncode != 0:
        return "Compile error: " + compile_result.stderr.decode(), -3
    # print("test2")
    try:
        run_result = subprocess.run(run_command,        
                                    shell=True, 
                                    stdin=subprocess.DEVNULL,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, env=sys_env,timeout=30
                                )
        if run_result.returncode != 0:
            return "Runtime Error: " + run_result.stderr.decode() , -1  
        else:
            print(run_result.stdout.decode())
            return "Pass", 0
    except:
        return "Time out", -2

def check_undefined_symbols(code_string):
    try:
        tree = ast.parse(code_string)
    except:
        return set()
    undefined_symbols = set()
    excluded_symbols = set(dir(builtins)).union(['List', 'Tuple', 'Optional', 'Any']) # HumanEval's typing
    class UndefinedSymbolVisitor(ast.NodeVisitor):
        def visit_Name(self, node):
            if isinstance(node.ctx, ast.Load):
                symbol_name = node.id
                if symbol_name not in excluded_symbols:
                    undefined_symbols.add(symbol_name)
        def visit_Assign(self, node):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    excluded_symbols.add(target.id)
            self.generic_visit(node)
        def visit_Import(self, node):
            for alias in node.names:
                excluded_symbols.add(alias.asname or alias.name)
            self.generic_visit(node)
        def visit_ImportFrom(self, node):
            self.visit_Import(node)
        def visit_FunctionDef(self, node):
            try:
                for arg in node.args.args:
                    excluded_symbols.add(arg.arg)
                if node.args.vararg:
                    excluded_symbols.add(node.args.vararg.arg)
                if node.args.kwarg:
                    excluded_symbols.add(node.args.kwarg.arg)
                excluded_symbols.add(node.name)
            except: pass
            self.generic_visit(node)
        def visit_Lambda(self, node):
            self.visit_FunctionDef(node)
        def visit_For(self, node):
            if isinstance(node.target, ast.Name):
                excluded_symbols.add(node.target.id)
            self.generic_visit(node)
        def visit_ListComp(self, node):
            if isinstance(node.elt, ast.Name):
                excluded_symbols.add(node.elt.id)
            self.generic_visit(node)
    visitor = UndefinedSymbolVisitor()
    visitor.visit(tree)
    return undefined_symbols

def debug_assert(condition):
    if not condition:
        print("Assert error! ")
        print("Backtrace:")
        import traceback
        traceback.print_stack()
        breakpoint()


def find_top_k_by_y(a, k):
    """
    Find the top-k elements with the smallest y values in a list of tuples,
    preserving the original order in 'a'.

    Args:
    a (list of tuple): A list of tuples, where each tuple contains two elements (x, y).
    k (int): The number of elements to find.

    Returns:
    list of tuple: A list of the top-k tuples with the smallest y values, in their original order.
    """
    # Extract y values and their indices
    y_values = [(y, index) for index, (x, y) in enumerate(a)]

    # Sort y_values based on y, but keep the original indices
    sorted_y_values = sorted(y_values, key=lambda x: x[0])

    # Get indices of the top-k smallest y values
    top_k_indices = sorted([index for _, index in sorted_y_values[:k]])

    # Get the corresponding elements from 'a' based on these indices
    top_k_elements = [a[index][0] for index in top_k_indices]

    return top_k_elements

# def encode_parallel(prompts, tokenizer, device, eos_token_id):
#     """
#     Manually apply truncation and padding for a list of prompts using a tokenizer.
#     Here, max_length is determined by the longest input_ids generated from the prompts.
#     """
#     tokenized_outputs = [tokenizer.encode_plus(prompt) for prompt in prompts]
    
#     # Find the maximum length among the tokenized prompts
#     max_length = max(len(tokens['input_ids']) for tokens in tokenized_outputs)

#     input_ids = []
#     attention_masks = []

#     for tokens in tokenized_outputs:
#         # Truncate and pad the input_ids
#         input_id = tokens['input_ids'][:max_length]
#         input_id = [eos_token_id] * (max_length - len(input_id)) + input_id

#         # Truncate and pad the attention_mask
#         attention_mask = tokens['attention_mask'][:max_length]
#         attention_mask = [0] * (max_length - len(attention_mask)) + attention_mask

#         # Append to the lists
#         input_ids.append(input_id)
#         attention_masks.append(attention_mask)
#     return torch.tensor(input_ids).to(device), torch.tensor(attention_masks).to(device)


def extract_first_function(code):
    init_indent_count = -1
    lines = []
    has_other_external_code = False
    for cur_line in code.split("\n"):
        if len(cur_line.strip()) == 0: continue
        cur_indent = len(cur_line) - len(cur_line.lstrip())
        if init_indent_count == -1:
            init_indent_count = cur_indent
        elif init_indent_count == cur_indent:
            has_other_external_code = True
            break
        lines.append(cur_line)
    return lines, has_other_external_code

def process_wizard_code(input):
    a = 0
    completion = input
    completion = completion.replace("\r", "")            
    if '```python' in completion: 
        def_line = completion.index('```python')
        completion = completion[def_line:].strip()
        completion = completion.replace('```python', '')
        # print(completion)
        try:
            next_line = completion.index('```')
            completion = completion[:next_line].strip()
        except:
            a += 1
            # print(completion)
            # print("================\n")
        # print(completion)
    if "__name__ == \"__main__\"" in completion:
        next_line = completion.index('if __name__ == "__main__":')
        completion = completion[:next_line].strip()
        # print(completion)
    
    if "# Example usage" in completion:
        # print(completion)
        next_line = completion.index('# Example usage')
        completion = completion[:next_line].strip()
    
    return completion


def process_magic_code(input):
    a = 0
    completion = input
    completion = completion[completion.index('@@ Response'):]
    completion = completion.replace("\r", "")            
    if '```python' in completion: 
        def_line = completion.index('```python')
        completion = completion[def_line:].strip()
        completion = completion.replace('```python', '')
        # print(completion)
        try:
            next_line = completion.index('```')
            completion = completion[:next_line].strip()
        except:
            a += 1
            # print(completion)
            # print("================\n")
        # print(completion)
    if "__name__ == \"__main__\"" in completion:
        next_line = completion.index('if __name__ == "__main__":')
        completion = completion[:next_line].strip()
        # print(completion)
    
    if "# Example usage" in completion:
        # print(completion)
        next_line = completion.index('# Example usage')
        completion = completion[:next_line].strip()
    
    return completion

# signals the start of a document
BOS = "<|endoftext|>"
# signals the end of a generated infill
EOM = "<|endofmask|>"

def make_sentinel_incoder(i):
    # signals (1) a location to insert an infill and (2) the start of the infill generation
    return f"<|mask:{i}|>\n"

def process_incoder_fill(text_list: List[str]):
    new_text_list = []
    for text in text_list:
        parts = text.split("<FILL_ME>")
        prompt = ''
        for sentinel_ix, part in enumerate(parts):
            prompt += part
            if (sentinel_ix < len(parts) - 1):
                prompt += make_sentinel_incoder(sentinel_ix)
        prompt += "\n<|mask:1|><|mask:0|>"
        new_text_list.append(prompt)
    
    return new_text_list

def process_incoder(outputsequences: List[str],multi_bool:bool):
    new_outputsequences = []
    for output_line in outputsequences:
        output_line = output_line.split(BOS)[-1]
        output_line = output_line.split("<|mask:0|>")[-1]
        output_line = output_line.split(EOM)[0]
        if not multi_bool:
            output_line = output_line.split('\n')[0]
        new_outputsequences.append(output_line)
    return new_outputsequences