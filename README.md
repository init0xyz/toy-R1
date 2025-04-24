# toy-R1
Using Qwen2.5-1.5B to achieve aha moment with OpenRLHF

Log: [Training Log on Wandb](https://wandb.ai/init0xyz/toys_r1/runs/zumy5524?nw=nwuserinit0xyz)

## Install Dependencies 🖇️
```bash
conda create -n openrlhf python=3.10
conda activate openrlhf
pip install openrlhf vllm==0.8.3
```

## Construct Training Data
```bash
python countdown_dataset.py
```

Data Sample:
```json
{
    "target": 36,
    "nums": [
        79,
        17,
        60
    ],
    "data_source": "countdown",
    "prompt": "<|im_start|>system\nYou are a helpful assistant. You first thinks about the reasoning process in the mind and then provides the user with the answer.<|im_end|>\n<|im_start|>user\n Using the numbers [79, 17, 60], create an equation that equals 36. You can use basic arithmetic operations (+, -, *, /) and each number can only be used once. Show your work in <think> </think> tags. And return the final answer in <answer> </answer> tags, for example <answer> (1 + 2) / 3 </answer>.<|im_end|>\n<|im_start|>assistant\nLet me solve this step by step.\n<think>",
    "ability": "math",
    "groud_truth": "{'target': 36, 'numbers': [79, 17, 60]}",
    "extra_info": {
        "index": 0,
        "split": "test"
    }
},
```

## Training
All the experiments are conducted on a server equipped with 4x Nvidia 3090.
```bash
ray start --head --node-ip-address 0.0.0.0 --num-gpus 3 ## start ray cluster
bash train_reinforce_qwen_ray.sh
```

## Acknowledgement
- [Tinyzero](https://github.com/Jiayi-Pan/TinyZero)