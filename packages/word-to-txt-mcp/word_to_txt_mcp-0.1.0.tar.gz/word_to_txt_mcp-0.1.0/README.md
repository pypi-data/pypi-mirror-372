# Word to Text MCP Server

一个基于FastMCP的Word文档转文本分析服务器包，提供Word文档处理、文本提取和内容分析功能。

## 功能特性

- 🔄 **Word文档转换**: 支持将.docx和.doc文件转换为纯文本
- 📊 **文档分析**: 提供文档统计、关键词提取、结构分析等功能
- 🚀 **MCP协议**: 基于FastMCP框架，支持多种传输协议
- 🛠️ **易于集成**: 可作为独立服务器运行或集成到其他应用中
- 📋 **表格支持**: 能够提取Word文档中的表格内容

## 安装

### 从PyPI安装

```bash
pip install word-to-txt-mcp
```

### 从源码安装

```bash
git clone https://github.com/yourusername/word-to-txt-mcp.git
cd word-to-txt-mcp
pip install -e .
```

## 快速开始

### 命令行使用

启动MCP服务器：

```bash
# 使用默认配置启动（SSE协议，端口7264）
word-to-txt-mcp

# 指定端口和协议
word-to-txt-mcp --port 8080 --transport sse

# 使用标准输入输出模式
word-to-txt-mcp --transport stdio
```

### 编程接口使用

```python
from word_to_txt_mcp import convert_word_to_text, create_mcp_server

# 直接转换Word文档
text_content = convert_word_to_text("document.docx")
print(text_content)

# 创建并运行MCP服务器
mcp = create_mcp_server("My Document Server")
mcp.run(transport="sse", host="0.0.0.0", port=7264)
```

## API参考

### 核心函数

#### `convert_word_to_text(word_file_path)`

将Word文档转换为文本内容。

**参数:**
- `word_file_path` (str): Word文档的文件路径

**返回值:**
- `str`: 提取的文本内容

**异常:**
- `FileNotFoundError`: 当Word文件不存在时抛出
- `Exception`: 当转换过程中出现错误时抛出

#### `process_word_document(file_path)`

处理Word文档，将其转换为文本并进行基础分析。

**参数:**
- `file_path` (str): Word文档的文件路径

**返回值:**
- `str`: 包含文档内容和基础分析的结果

#### `analyze_document_content(text_content, analysis_type="summary")`

分析文档内容。

**参数:**
- `text_content` (str): 要分析的文本内容
- `analysis_type` (str): 分析类型，可选值：
  - `"summary"`: 文档摘要分析
  - `"keywords"`: 关键词提取
  - `"structure"`: 文档结构分析

**返回值:**
- `str`: 分析结果

### MCP工具

当作为MCP服务器运行时，提供以下工具：

1. **process_word_document**: 处理Word文档并转换为文本
2. **analyze_document_content**: 分析文档内容
3. **echo_tool**: 回显文本（用于测试）

### MCP资源

- `document://help`: 获取帮助信息
- `document://status/{file_path}`: 检查文档状态

### MCP提示

- `analyze_document`: 生成文档分析提示

## 配置选项

### 命令行参数

- `--transport`: 传输协议类型 (stdio, sse, streamable-http)
- `--host`: 服务器主机地址 (默认: 0.0.0.0)
- `--port`: 服务器端口号 (默认: 7264)
- `--name`: 服务器名称
- `--version`: 显示版本信息

## 使用示例

### 基础文档转换

```python
from word_to_txt_mcp import convert_word_to_text

# 转换Word文档
try:
    text = convert_word_to_text("example.docx")
    print("文档内容:")
    print(text)
except FileNotFoundError:
    print("文件不存在")
except Exception as e:
    print(f"转换失败: {e}")
```

### 文档分析

```python
from word_to_txt_mcp import process_word_document, analyze_document_content

# 处理文档并获取分析结果
result = process_word_document("example.docx")
print(result)

# 进行关键词分析
text = convert_word_to_text("example.docx")
keywords = analyze_document_content(text, "keywords")
print(keywords)
```

### 作为MCP服务器

```python
from word_to_txt_mcp import create_mcp_server

# 创建服务器
mcp = create_mcp_server("Document Analysis Server")

# 启动服务器
mcp.run(transport="sse", host="localhost", port=8080)
```

## 支持的文件格式

- `.docx` - Microsoft Word 2007及更新版本
- `.doc` - Microsoft Word 97-2003（需要额外配置）

## 依赖要求

- Python >= 3.8
- fastmcp >= 0.1.0
- python-docx >= 0.8.11

## 开发

### 安装开发依赖

```bash
pip install -e ".[dev]"
```

### 运行测试

```bash
pytest
```

### 代码格式化

```bash
black word_to_txt_mcp/
```

### 类型检查

```bash
mypy word_to_txt_mcp/
```

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎提交Issue和Pull Request！

## 更新日志

### v0.1.0

- 初始版本发布
- 支持Word文档转文本
- 提供基础文档分析功能
- 支持MCP协议
- 命令行工具支持

## 联系方式

- 作者: Your Name
- 邮箱: your.email@example.com
- 项目主页: https://github.com/yourusername/word-to-txt-mcp