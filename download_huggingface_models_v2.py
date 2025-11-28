#!/bin/bash

PYTHON_EXECUTOR="/usr/bin/python3"

if [ ! -f "$PYTHON_EXECUTOR" ]; then
    exit 1
fi


"$PYTHON_EXECUTOR" -c "import huggingface_hub" 2>/dev/null
if [ $? -ne 0 ]; then
    
    "$PYTHON_EXECUTOR" -m pip install --break-system-packages huggingface_hub
    if [ $? -ne 0 ]; then
        VENV_DIR=$(mktemp -d)
        "$PYTHON_EXECUTOR" -m venv "$VENV_DIR/venv"
        source "$VENV_DIR/venv/bin/activate"
        
        pip install huggingface_hub
        if [ $? -ne 0 ]; then
            rm -rf "$VENV_DIR"
            exit 1
        fi
        
        PYTHON_EXECUTOR="$VENV_DIR/venv/bin/python3"
    fi
    
fi

TEMP_SCRIPT=$(mktemp)
cat > "$TEMP_SCRIPT" << 'PYTHON_EOF'
#!/usr/bin/env python3
import os
import argparse
import sys

# 设置镜像源
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

def download_model(repo_id, local_dir, max_workers):
    try:
        from huggingface_hub import snapshot_download
        print(f"开始下载模型: {repo_id}")
        print(f"存储路径: {local_dir}")
        print(f"工作线程数: {max_workers}")
        
        snapshot_download(
            repo_id=repo_id,
            local_dir=local_dir,
            max_workers=max_workers
        )
        print(f"模型下载完成: {repo_id} -> {local_dir}")
        
    except ImportError:
        print("错误: 请先安装 huggingface_hub: pip install huggingface-hub")
        sys.exit(1)
    except Exception as e:
        print(f"下载过程中发生错误: {str(e)}")
        sys.exit(1)

def main():
    # 获取当前用户名
    current_user = os.getenv('USER') or 'unknown'
    
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(
        prog="hfd",
        description="Hugging Face模型下载工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f'''
使用示例:
  hfd -m "sentence-transformers/paraphrase-MiniLM-L6-v2" -p /data/{current_user}/models -t 8
  hfd -m "sentence-transformers/paraphrase-MiniLM-L6-v2" -p ./models
        '''
    )
    
    # 添加命令行参数
    parser.add_argument(
        '-m', '--model',
        type=str,
        required=True,
        help='模型仓库ID (例如: "sentence-transformers/paraphrase-MiniLM-L6-v2")'
    )
    
    parser.add_argument(
        '-p', '--path',
        type=str,
        default=f'/data/{current_user}/models',  
        help=f'本地存储路径 (默认: /data/{current_user}/models)'
    )
    
    parser.add_argument(
        '-t', '--threads',
        type=int,
        default=4,
        help='最大工作线程数 (默认: 4)'
    )
    
    # 解析参数
    args = parser.parse_args()
    
    # 确保存储路径存在
    os.makedirs(args.path, exist_ok=True)
    
    # 下载模型
    download_model(args.model, args.path, args.threads)

if __name__ == "__main__":
    main()
PYTHON_EOF

echo "开始执行模型下载..."
"$PYTHON_EXECUTOR" "$TEMP_SCRIPT" "$@"

exit_code=$?
rm -f "$TEMP_SCRIPT"

if [ ! -z "$VENV_DIR" ] && [ -d "$VENV_DIR" ]; then
    rm -rf "$VENV_DIR"
fi

exit $exit_code
