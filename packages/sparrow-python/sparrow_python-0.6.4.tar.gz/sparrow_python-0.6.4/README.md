# sparrow-python

[![image](https://img.shields.io/badge/Pypi-0.1.7-green.svg)](https://pypi.org/project/sparrow-python)
[![image](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/)
[![image](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## 快速命令索引

### 🎯 常用命令速查
```bash
# 查看表格数据
spr table_viewer data.csv

# 图像批量处理  
spr mllm_call_images ./photos
spr download_images "关键词" --num_images=100

# 视频处理
spr video_dedup video.mp4
spr frames_to_video frames_dir

# 文件操作
spr pack folder_name        # 压缩
spr split large_file.dat    # 分割大文件
spr kill 8080              # 杀死端口进程

# 项目工具
spr create my_project      # 创建项目
spr clone repo_url         # 克隆仓库
spr gen_key project_name   # 生成SSH密钥

# 服务启动
spr start_server           # 多进程服务器
spr reminder              # 提醒服务
```

### 📖 详细命令说明
所有命令都支持 `sp`、`spr`、`sparrow` 三种调用方式。
使用 `spr <command> --help` 查看具体参数说明。

---

## TODO
- [ ] 多模态图像预处理 考虑使用多进程
- [ ] 找一个可以优雅绘制流程图、示意图的工具，如ppt？
- [ ]  实现一个优雅的TextSplitter

- [ ] prompt调试页面
- [ ] 相关配置指定支持：prompt后端地址；模型参数配置；
- [ ] 
- [ ] 添加测试按钮，模型选项，模型配置
- [ ] 原生git下载支持
- [ ]
- [X] streamlit 多模态chat input: https://github.com/streamlit/streamlit/issues/7409
- [ ] https://github.com/hiyouga/LLaMA-Factory/blob/main/src/llamafactory/chat/vllm_engine.py#L99

识别下面链接的滚动截图：
https://sjh.baidu.com/site/dzfmws.cn/da721a31-476d-42ed-aad1-81c2dc3a66a3



vllm 异步推理示例：

new 实例(from deepwiki)  
```python
import asyncio  
from fastapi import FastAPI, Request  
from fastapi.responses import JSONResponse, StreamingResponse  
from vllm.engine.arg_utils import AsyncEngineArgs  
from vllm.engine.async_llm_engine import AsyncLLMEngine  
from vllm.sampling_params import SamplingParams  
from vllm.utils import random_uuid  
import json  
  
app = FastAPI()  
engine = None  
  
async def init_engine():  
    """初始化 vLLM 引擎"""  
    global engine  
    # 配置引擎参数  
    engine_args = AsyncEngineArgs(  
        model="your-model-name",  # 替换为您的模型  
        tensor_parallel_size=1,   # 根据您的GPU数量调整  
        dtype="auto",  
        max_model_len=2048,  
    )  
    engine = AsyncLLMEngine.from_engine_args(engine_args)  
  
@app.on_event("startup")  
async def startup_event():  
    await init_engine()  
  
@app.post("/generate")  
async def generate(request: Request):  
    """生成文本的端点"""  
    request_dict = await request.json()  
    prompt = request_dict.get("prompt")  
    stream = request_dict.get("stream", False)  
      
    # 创建采样参数  
    sampling_params = SamplingParams(  
        temperature=request_dict.get("temperature", 0.7),  
        max_tokens=request_dict.get("max_tokens", 100),  
        top_p=request_dict.get("top_p", 1.0),  
    )  
      
    request_id = random_uuid()  
    results_generator = engine.generate(prompt, sampling_params, request_id)  
      
    if stream:  
        # 流式响应  
        async def stream_results():  
            async for request_output in results_generator:  
                text_outputs = [output.text for output in request_output.outputs]  
                ret = {"text": text_outputs}
                yield f"data: {json.dumps(ret)}\n\n"  
          
        return StreamingResponse(stream_results(), media_type="text/plain")  
    else:  
        # 非流式响应  
        final_output = None  
        async for request_output in results_generator:  
            final_output = request_output  
          
        text_outputs = [output.text for output in final_output.outputs]  
        return JSONResponse({"text": text_outputs})  
  
if __name__ == "__main__":  
    import uvicorn  
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

```python
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import uvicorn
from vllm.engine.arg_utils import AsyncEngineArgs
from vllm.engine.async_llm_engine import AsyncLLMEngine
from vllm.sampling_params import SamplingParams
import torch

# Define request data model
class RequestData(BaseModel):
    prompts: List[str]
    max_tokens: int = 2048
    temperature: float = 0.7

# Initialize FastAPI app
app = FastAPI()

# Determine device
device = "cuda" if torch.cuda.is_available() else "cpu"

# Initialize AsyncLLMEngine
engine_args = AsyncEngineArgs(
    model="your-model-name",  # Replace with your model name
    dtype="bfloat16",
    gpu_memory_utilization=0.8,
    max_model_len=4096,
    trust_remote_code=True
)
llm_engine = AsyncLLMEngine.from_engine_args(engine_args)

# Define the inference endpoint
@app.post("/predict")
async def generate_text(data: RequestData):
    sampling_params = SamplingParams(
        max_tokens=data.max_tokens,
        temperature=data.temperature
    )
    request_id = "unique_request_id"  # Generate a unique request ID
    results_generator = llm_engine.generate(data.prompts, sampling_params, request_id)
  
    final_output = None
    async for request_output in results_generator:
        final_output = request_output
  
    assert final_output is not None
    text_outputs = [output.text for output in final_output.outputs]
    return {"responses": text_outputs}

# Run the server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

```



## 待添加脚本

## Install

```bash
pip install sparrow-python
# Or dev version
pip install sparrow-python[dev]
# Or
pip install -e .
# Or
pip install -e .[dev]
```

## Usage

### Multiprocessing SyncManager

Open server first:

```bash
$ spr start-server
```

The defualt port `50001`.

(Process1) productor:

```python
from sparrow.multiprocess.client import Client

client = Client(port=50001)
client.update_dict({'a': 1, 'b': 2})
```

(Process2) consumer:

```python
from sparrow.multiprocess.client import Client

client = Client(port=50001)
print(client.get_dict_data())

>> > {'a': 1, 'b': 2}
```

### 常用工具

#### 数据处理与查看
- **表格查看器**
```bash
# 基本用法
spr table_viewer sample_products.csv --port 8081

# 指定图像列并设置端口
spr table_viewer "products.xlsx" --image_columns="product_image,thumbnail" --port=9090

# 指定工作表
spr table_viewer "report.xlsx" --sheet_name="Sheet2"
```

- **文本去重**
```bash
# 使用编辑距离去重
spr deduplicate input.txt output.txt --method=edit --threshold=0.8

# 使用ROUGE相似度去重
spr deduplicate data.csv clean.csv --method=rouge --target_col=content
```

- **文件压缩与解压**
支持格式："zip", "tar", "gztar", "bztar", "xztar"
```bash
# 压缩文件/文件夹
spr pack pack_dir

# 解压文件
spr unpack filename extract_dir
```

- **大文件分割与合并**
```bash
# 分割大文件 (默认1GB块)
spr split large_file.dat

# 合并分割文件
spr merge large_file.dat
```

#### 项目管理
- **项目脚手架**
```bash
spr create awesome-project
```

- **Git仓库克隆**
```bash
# 基本克隆
spr clone https://github.com/user/repo.git

# 指定分支和保存路径
spr clone https://github.com/user/repo.git --branch=dev --save_path=./my_project
```

- **自动Git提交监控**
```bash
spr auto_commit --interval=60
```

- **SSH密钥生成**
```bash
spr gen_key project_name --email=your@email.com
```

- **配置管理**
```bash
# 初始化配置文件
spr init_config

# 查看当前配置
spr get_config

# 查看特定配置项
spr get_config mllm.model
```

#### 系统工具
- **端口进程管理**
```bash
# 杀死指定端口进程
spr kill 8080

# 获取本机IP
spr get_ip
spr get_ip --env=outer  # 获取外网IP
```

- **Docker管理**
```bash
# 保存所有Docker镜像
spr save_docker_images

# 加载Docker镜像
spr load_docker_images

# Docker GPU状态监控
spr docker_gpu_stat
```

#### 多媒体处理
- **视频帧去重**
```bash
# 基本去重 (默认phash算法)
spr video_dedup video.mp4

# 自定义参数
spr video_dedup video.mp4 --method=dhash --threshold=5 --step=2 --workers=4
```

- **图像帧转视频**
```bash
# 将帧目录转换为视频
spr frames_to_video frames_dir --fps=24

# 一站式：去重+生成视频
spr dedup_and_create_video video.mp4 --video_fps=15
```

- **视频字幕处理**
```bash
# 自动生成字幕（转录+翻译）
spr subtitles video.mp4

# 翻译现有字幕
spr translate_subt subtitles.srt

# 合并双语字幕
spr merge_subtitles en.srt zh.srt
```

#### 图像下载与处理
- **批量图像下载**
```bash
# 单关键词下载
spr download_images "猫咪" --num_images=100

# 多关键词，多搜索引擎
spr download_images "猫咪,狗狗" --engines="bing,google,baidu" --save_dir="animals"
```

#### 大模型与AI
- **批量图像识别（表格）**
```bash
# 基本用法
spr mllm_call_table images.xlsx --image_col=图片路径

# 自定义模型和提示词
spr mllm_call_table data.csv \
    --model="gpt-4o-mini" \
    --text_prompt="详细描述这张图片" \
    --output_file="results.csv"
```

- **批量图像识别（文件夹）**
```bash
# 处理文件夹中所有图片
spr mllm_call_images ./photos --recursive=True

# 指定文件类型和数量限制
spr mllm_call_images ./images \
    --extensions=".jpg,.png" \
    --max_num=50 \
    --output_file="analysis.csv"
```

#### 网络与API
- **异步HTTP请求**
```bash
# POST请求
spr post "https://api.example.com" '{"key": "value"}' --concurrent=10

# GET请求
spr get_url "https://api.example.com" --concurrent=5
```

- **文件传输**
```bash
# P2P文件传输 (基于croc)
spr send file.txt
spr recv  # 在另一台机器上接收

# 云存储传输
spr send2 file.txt workspace_name
spr recv2 file.txt workspace_name
```

#### 数据库与服务
- **启动多进程同步服务器**
```bash
spr start_server --port=50001
```

- **Milvus向量数据库**
```bash
# 启动Milvus服务
spr milvus start

# 停止Milvus服务
spr milvus stop
```

- **数据存储 (FlaxKV)**
```bash
# 存储文件到指定空间
spr set mykey /path/to/file.txt

# 获取存储的数据
spr get mykey

# 查看所有存储的键
spr keys

# 清理过期数据
spr clean
```

#### 开发工具
- **软件安装**
```bash
# 安装Node.js (通过NVM)
spr install_node --version=18

# 安装/卸载Neovim
spr install_nvim --version=0.9.2
spr uninstall_nvim
```

- **定时器工具**
```bash
spr timer --dt=0.5  # 0.5秒间隔定时器
```

- **性能测试**
```bash
# 测试PyTorch环境
spr test_torch
```

#### 高级功能
- **提醒服务**
```bash
# 启动Web提醒服务
spr reminder --port=8000
```

### Some useful functions

> `sparrow.relp`
> Relative path, which is used to read or save files more easily.

> `sparrow.performance.MeasureTime`
> For measuring time (including gpu time)

> `sparrow.performance.get_process_memory`
> Get the memory size occupied by the process

> `sparrow.performance.get_virtual_memory`
> Get virtual machine memory information

> `sparrow.add_env_path`
> Add python environment variable (use relative file path)
