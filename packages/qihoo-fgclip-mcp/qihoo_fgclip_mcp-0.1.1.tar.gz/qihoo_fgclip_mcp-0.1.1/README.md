# qihoo-fgclip-mcp

MCP (Model Context Protocol) Server for 360 Research embedding services.

## 功能特性

这个MCP服务器提供了以下工具：

- **text_embedding**: 为文本生成嵌入向量
- **image_embedding**: 为图像生成嵌入向量  
- **embedding**: 通用的文本或图像嵌入向量生成工具

## 安装

```bash
# 使用uv安装依赖
uv sync
```

## 配置

设置环境变量：

```bash
export MCP_API_KEY="your_360_research_api_key"
export MCP_API_BASE_URL="https://api.research.360.cn/models/interface"
```

## 使用方法

### 作为MCP服务器运行

```bash
# 使用stdio传输（推荐用于uvx）
python main.py --transport stdio

# 使用HTTP传输
python main.py --transport http --host 0.0.0.0 --port 8000
```

### 作为可执行脚本运行

```bash
# 安装后可以直接运行
qihoo-fgclip-mcp --transport stdio
```

## 工具说明

### text_embedding

为文本生成嵌入向量。

参数：
- `texts`: 要嵌入的文本字符串列表
- `model`: 使用的模型（默认: "fg-clip"）
- `embedding_types`: 返回的嵌入类型（默认: ["float"]）
- `truncate`: 截断策略（"start", "end", "none"，默认: "start"）

### image_embedding

为图像生成嵌入向量。

参数：
- `images`: 图像URL或base64编码图像的列表
- `model`: 使用的模型（默认: "fg-clip"）
- `embedding_types`: 返回的嵌入类型（默认: ["float"]）

### embedding

通用的文本或图像嵌入向量生成工具。

参数：
- `inputs`: 文本字符串或图像URL/base64的列表
- `input_type`: 输入类型（"text" 或 "image"）
- `model`: 使用的模型（默认: "fg-clip"）
- `embedding_types`: 返回的嵌入类型（默认: ["float"]）
- `truncate`: 截断策略（仅用于文本，默认: "start"）

## 开发

```bash
# 安装开发依赖
uv sync --dev

# 运行测试
python -m pytest
```

## 许可证

MIT License
