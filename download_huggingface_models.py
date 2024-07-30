import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
from huggingface_hub import snapshot_download


# 替换为自己的存储路径
model_path = "/root/storm/models"
snapshot_download( 
            repo_id="sentence-transformers/paraphrase-MiniLM-L6-v2",
            local_dir=model_path,
            max_workers=8)
