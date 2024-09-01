<video src="./assets/sample.mp4"></video>


### Requirements

This plugin requires the JumpCoder_Backend_Server to be running and the corresponding code generation model to be deployed using Text Generation Inference (TGI).

Here’s how you can install and configure them:

#### Step 1: Deploy Text Generation Inference (TGI)

You can follow the [official Hugging Face TGI installation guide](https://github.com/huggingface/text-generation-inference/blob/main/README.md) to set up TGI. They offer two methods: installing via Docker or locally. Once TGI is installed, you can run the following command to deploy the desired code generation model.

**Note:** Currently, the infilling model only supports **CodeLlama**. Here's an example of how to deploy it:

```bash
model_path=/data/CodeLlama-7b-Instruct-hf
# Share a volume with the Docker container to avoid downloading weights every run
volume=/path/to/directory/of/your/model etc. /data/models/

# Deploy the generation model
CUDA_VISIBLE_DEVICES=0 docker run --gpus all --shm-size 1g -p 8080:80 -v $volume:/data \
    text-generation-inference:2.1.0 --model-id $model_path --dtype float16 --num-shard 1 --max-batch-total-tokens 2048 \
    --max-batch-prefill-tokens 1024 --max-total-tokens 2048 --max-input-tokens 1024 --cuda-memory-fraction 0.4
    
# Deploy the infilling model
CUDA_VISIBLE_DEVICES=0 docker run --gpus all --shm-size 1g -p 8081:80 -v $volume:/data \
    text-generation-inference:2.1.0 --model-id $model_path --dtype float16 --num-shard 1 --max-batch-total-tokens 2048 \
    --max-batch-prefill-tokens 1024 --max-total-tokens 2048 --max-input-tokens 1024 --cuda-memory-fraction 0.4
```

You can customize the address and port where the TGI models are deployed.

#### Step 2: Start JumpCoder_Backend_Server

You can download the JumpCoder_Backend_Server code from [JumpCoder-Plugin/JumpCoder-server](https://github.com/Avabowler/JumpCoder-Plugin/tree/main/JumpCoder-server). This is a simple backend server built using the Flask framework. To install it, use the following commands:

```bash
conda env create --name JumpCoder_Backend_Server -f environment.yml && conda activate JumpCoder_Backend_Server
```

Next, run JumpCoder_Backend_Server. Note that the addresses used here should match the addresses of the generation or infilling models deployed in Step 1. JumpCoder_Backend_Server runs by default on port 127.0.0.1:5000, but you can adjust this if needed.

```bash
python run_jumpcoder_server.py --address_infilling 127.0.0.1:8081 --address_generation 127.0.0.1:8080
```

#### Step 3: Run the Plugin

You can configure the plugin to use your custom JumpCoder_Backend_Server address to utilize JumpCoder.

### Extension Settings

- `myExtension.Sidebar`: Provides a sidebar search box feature for JumpCoder. You can open the sidebar by clicking the JumpCoder icon, where a search box and some parameters for JumpCoder will be displayed. You can input your code generation prompts in the search box and click search to generate code.
- `myExtension.processing`: Offers a feature to generate code within code files using JumpCoder. You can select a portion of the code in the file as a prompt, then right-click and choose "processing" to generate code.