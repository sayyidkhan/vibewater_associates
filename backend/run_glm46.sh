#!/bin/bash
# Run GLM-4.6 with llama.cpp
# This script uses the recommended settings from Unsloth documentation

export LLAMA_CACHE="unsloth/GLM-4.6-GGUF"

llama-cli \
  --model unsloth/GLM-4.6-GGUF/UD-Q2_K_XL/GLM-4.6-UD-Q2_K_XL-00001-of-00003.gguf \
  --n-gpu-layers 99 \
  --jinja \
  --ctx-size 16384 \
  --flash-attn on \
  --temp 1.0 \
  --top-p 0.95 \
  --top-k 40 \
  -ot ".ffn_.*_exps.=CPU"

# Note: The -ot flag offloads MoE layers to CPU to save GPU memory
# Adjust based on your GPU capacity:
# - More GPU memory: -ot ".ffn_(up)_exps.=CPU"
# - Medium GPU memory: -ot ".ffn_(up|down)_exps.=CPU"
# - Less GPU memory: -ot ".ffn_.*_exps.=CPU" (current setting)
