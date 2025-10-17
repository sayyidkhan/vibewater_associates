#!/usr/bin/env python3
"""
Download GLM-4.6 GGUF model from Hugging Face
"""
import os

# Disable HF transfer to avoid rate limiting
os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "0"

from huggingface_hub import snapshot_download

print("Downloading GLM-4.6 UD-Q2_K_XL (Dynamic 2bit quant)...")
print("This is ~84GB and may take a while...")

snapshot_download(
    repo_id="unsloth/GLM-4.6-GGUF",
    local_dir="unsloth/GLM-4.6-GGUF",
    allow_patterns=["*UD-Q2_K_XL*"],  # Dynamic 2bit quant (recommended)
)

print("\nDownload complete!")
print("Model saved to: unsloth/GLM-4.6-GGUF")
