import gradio as gr
from flask import Flask, request, jsonify
import requests

#连接flusk后端进行处理

#输入文本处理程序
def code_generate(prompts, k_positions, threshold_improvement,similar_threshold, do_sample, temperature):
    print(f"generate Loginfo:\n    prompts: {prompts}\n    k_positions: {k_positions}\n    threshold_improvement: {threshold_improvement}\n\
    similar_threshold: {similar_threshold}\n    do_sample: {do_sample}\n    temperature:{temperature}")
    
    response = requests.post("http://127.0.0.1:5000/api/generate", json={"prompts": prompts,"k_positions": k_positions, "threshold_improvement": threshold_improvement,"similar_threshold":similar_threshold})
    result = response.json()["generate_outputs"]
    return result

#fn,inputs,outputs都是必填函数
demo = gr.Interface(fn=code_generate,
inputs=["text", gr.Slider(0, 10, 5, step=1),gr.Slider(0.5, 1, 0.85, step=0.05), gr.Slider(0, 1, 0.3, step=0.1), gr.Checkbox(), gr.Slider(0, 1, 0.1, step=0.1)],
outputs="text")

demo.launch()

