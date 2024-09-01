![](.\assets\sample.gif)

## Requirements

这一插件需要运行JumpCoder_Backend_Server和使用TGI部署相应的代码生成模型。

你可以通过下面方式安装和配置他们。

##### Step 1 部署Text Generation Inference

你可以遵循Hugging Face TGI官方的安装文档[Hugging Face TGI官方的安装文档](https://github.com/huggingface/text-generation-inference/blob/main/README.md)部署TGI。他们提供了docker安装和本地安装两种方式。
安装好TGI后，你可以运行命令部署想要使用的代码生成模型。

注意！！！现在填充模型仅支持**CodeLlama** ，下面是一个部署示例：

```bash
model_path=/data/CodeLlama-7b-Instruct-hf
# share a volume with the Docker container to avoid downloading weights every run
volume=/path/to/directory/of/your/model etc. /data/models/

# 部署生成模型
CUDA_VISIBLE_DEVICES=0 docker run --gpus all --shm-size 1g -p 8080:80 -v $volume:/data \
    text-generation-inference:2.1.0 --model-id $model_path --dtype float16 --num-shard 1 --max-batch-total-tokens 2048 \
    --max-batch-prefill-tokens 1024 --max-total-tokens 2048 --max-input-tokens 1024 --cuda-memory-fraction 0.4
    
# 部署填充模型
CUDA_VISIBLE_DEVICES=0 docker run --gpus all --shm-size 1g -p 8081:80 -v $volume:/data \
    text-generation-inference:2.1.0 --model-id $model_path --dtype float16 --num-shard 1 --max-batch-total-tokens 2048 \
    --max-batch-prefill-tokens 1024 --max-total-tokens 2048 --max-input-tokens 1024 --cuda-memory-fraction 0.4
```

注意这里你可以自己配置TGI部署模型侦听的地址端口。

##### Step 2 启动JumpCoder_Backend_Server

你可以在（）中下载JumpCoder_Backend_Server代码，这是一个基于flask框架实现的简易的后端服务器。你可以按照下面命令安装它。

```bash
conda env create --name JumpCoder_Backend_Server -f environment.yml && conda activate JumpCoder_Backend_Server
```

接下来运行JumpCoder_Backend_Server。注意这里的地址是你在Step 1中部署进行生成或者填充的大模型的地址。

```bash
python run_jumpcoder_server.py --address_infilling 127.0.0.1:8081 --address_generation 127.0.0.1:8080
```

##### Step 3 运行插件



## Extension Settings

* `myExtension.Sidebar`: 提供了JumpCoder的侧边栏搜索框生成功能，你可以点击侧边栏中的JumpCoder图标打开侧边栏，侧边栏中会显示一个搜索框和JumpCoder运行的一些参数，你可以在搜索框中输入你想生成的代码的prompts，点击搜索进行生成。
* `myExtension.processing`: 提供了JumpCoder在代码文件中处理生成代码功能，你可以在文件中拉取选择一部分代码作为prompt，通过点击右键并选择processing进行生成。
