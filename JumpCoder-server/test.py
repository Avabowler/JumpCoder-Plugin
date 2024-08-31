from text_generation import Client
import torch
from transformers import AutoTokenizer,AutoModelForCausalLM

tokenizer = AutoTokenizer.from_pretrained("/data/mouxiangchen/home/models/CodeLlama-7b-hf")
model = AutoModelForCausalLM.from_pretrained("/data/mouxiangchen/home/models/CodeLlama-7b-hf", device_map="cuda")
input = """<PRE>  <SUF>
        for j in range(i + 1, len(numbers)):
            if abs(numbers[i] - numbers[j]) < threshold:
                return True
    return False <MID>"""
input = """<PRE>  <SUF>
from typing import List, Tuple


def sum_product(numbers: List[int]) -> Tuple[int, int]:
    \"\"\" For a given list of integers, return a tuple consisting of a sum and a product of all the integers in a list.
    Empty sum should be equal to 0 and empty product should be equal to 1.
    >>> sum_product([])
    (0, 1)
    >>> sum_product([1, 2, 3, 4])
    (10, 24)
    \"\"\"
    return sum(numbers), reduce(lambda x, y: x * y, numbers, 1) <MID>"""
# input = """<FILL_ME>
# from typing import List, Tuple


# def sum_product(numbers: List[int]) -> Tuple[int, int]:
#     \"\"\" For a given list of integers, return a tuple consisting of a sum and a product of all the integers in a list.
#     Empty sum should be equal to 0 and empty product should be equal to 1.
#     >>> sum_product([])
#     (0, 1)
#     >>> sum_product([1, 2, 3, 4])
#     (10, 24)
#     \"\"\"
#     return sum(numbers), reduce(lambda x, y: x * y, numbers, 1)"""
input_ids = tokenizer.encode(input,return_tensors="pt").to('cuda')
print(input_ids)
output = model.generate(input_ids,max_new_tokens = 128)
print(tokenizer.batch_decode(output))

client = Client("http://127.0.0.1:8080")
# input = """<FILL_ME>
#         for j in range(i + 1, len(numbers)):
#             if abs(numbers[i] - numbers[j]) < threshold:
#                 return True
#     return False
# """
print(client.generate(input, max_new_tokens=128,decoder_input_details=True))

# text = ""
# for response in client.generate_stream(input,max_new_tokens=128):
#     if not response.token.special:
#         text += response.token.text
# print(text)