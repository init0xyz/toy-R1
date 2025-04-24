set -x

# reinforce++

ray job submit --address="http://127.0.0.1:8265" \
   --runtime-env-json='{"working_dir": "/data1/laiyilong/OpenRLHF/tinyzero"}' \
   -- python3 -m openrlhf.cli.train_ppo_ray \
   --ref_num_nodes 1 \
   --ref_num_gpus_per_node 2 \
   --actor_num_nodes 1 \
   --actor_num_gpus_per_node 2 \
   --vllm_num_engines 1 \
   --vllm_tensor_parallel_size 1 \
   --critic_num_nodes=0 \
   --critic_num_gpus_per_node=0 \
   --pretrain /data1/laiyilong/Qwen2.5-1.5B-Instruct \
   --remote_rm_url /data1/laiyilong/OpenRLHF/tinyzero/countdown_reward_fn.py \
   --save_path /data1/laiyilong/OpenRLHF/checkpoint/qwen-1.5b-rlhf \
   --micro_train_batch_size 4 \
   --train_batch_size 120 \
   --micro_rollout_batch_size 8 \
   --rollout_batch_size 256 \
   --n_samples_per_prompt 4 \
   --max_epochs 1 \
   --prompt_max_len 1024 \
   --max_samples 1000000 \
   --generate_max_len 768 \
   --advantage_estimator reinforce \
   --zero_stage 2 \
   --bf16 \
   --actor_learning_rate 1e-6 \
   --init_kl_coef 1e-3 \
   --prompt_data /data1/laiyilong/OpenRLHF/data/countdown/train.json \
   --eval_dataset /data1/laiyilong/OpenRLHF/data/countdown/test.json \
   --input_key prompt \
   --label_key groud_truth \
   --normalize_reward \
   --gradient_checkpointing \
   --save_steps 100 \
   --eval_steps 100 \
   --vllm_gpu_memory_utilization 0.9 \
   --colocate_actor_ref \
   --packing_samples \
   --adam_offload \
   --disable_ds_ckpt \
   --save_hf_ckpt \
   --vllm_sync_backend nccl \
   --ckpt_path /data1/laiyilong/OpenRLHF/ckpt/checkpoints_rlhf_qwen1.5b \
   --use_wandb WANDB_TOKEN \
   --wandb_project toys_r1 \
   --wandb_run_name qwen2.5-1.5b-countdown-reinforce-v3 \

# You could also try
#   --use_kl_loss \
#   --kl_estimator k3 | k2 \

# also supports --advantage_estimator rloo | reinforce_baseline
