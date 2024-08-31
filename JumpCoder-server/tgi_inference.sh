model=/data/CodeLlama-7b-Instruct-hf
# share a volume with the Docker container to avoid downloading weights every run
volume=/data/mouxiangchen/home/models/

CUDA_VISIBLE_DEVICES=0 docker run --gpus all --shm-size 1g -p 8080:80 -v $volume:/data \
    text-generation-inference:2.1.0 --model-id $model --dtype float16 --num-shard 1 --max-batch-total-tokens 2048 \
    --max-batch-prefill-tokens 1024 --max-total-tokens 2048 --max-input-tokens 1024 --cuda-memory-fraction 0.5