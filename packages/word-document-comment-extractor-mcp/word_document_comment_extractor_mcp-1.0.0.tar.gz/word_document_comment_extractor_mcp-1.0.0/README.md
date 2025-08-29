# Word文档评论提取 MCP服务

这是一个基于Model Context Protocol (MCP)的Word文档评论提取服务，提供从Word文档中提取和分析评论的功能。

## 功能特性

### 核心功能
- **提取所有评论** - 从Word文档中提取所有评论及其元数据
- **按作者筛选评论** - 提取指定作者的所有评论
- **按段落提取评论** - 提取特定段落的相关评论

### 技术特性
- 基于FastMCP框架构建
- 支持异步操作
- 完整的错误处理和验证
- JSON格式输出，便于处理
- 支持表格内评论检测
- 智能XML解析和备用方案
- 详细的评论元数据提取

## 安装要求

- Python 3.10+
- python-docx >= 1.1.0
- fastmcp >= 2.8.1

## 安装方法

使用uv安装依赖：

```bash
cd python/Word文档评论提取
uv sync
```

或使用pip安装：

```bash
pip install python-docx fastmcp
```

## 使用方法

### 启动MCP服务器

```bash
# 使用uv运行
uv run python -m word_document_comment_extractor.main

# 或直接运行
python -m word_document_comment_extractor.main
```

### MCP配置

将以下配置添加到您的MCP客户端配置文件中：

```json
{
  "mcpServers": {
    "word-document-comment-extractor": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/Word文档评论提取",
        "run",
        "python",
        "-m",
        "word_document_comment_extractor.main"
      ],
      "env": {
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

## API参考

### 提取所有评论
```python
get_all_comments_tool(filename: str)
```
- `filename`: Word文档路径

返回JSON格式：
```json
{
  "success": true,
  "comments": [
    {
      "id": "comment_1",
      "comment_id": "1",
      "author": "张三",
      "initials": "ZS",
      "date": "2024-01-15T10:30:00",
      "text": "这里需要修改",
      "paragraph_index": 2,
      "in_table": false,
      "reference_text": "相关文本内容..."
    }
  ],
  "total_comments": 1
}
```

### 按作者提取评论
```python
get_comments_by_author_tool(filename: str, author: str)
```
- `filename`: Word文档路径
- `author`: 作者姓名（不区分大小写）

### 按段落提取评论
```python
get_comments_for_paragraph_tool(filename: str, paragraph_index: int)
```
- `filename`: Word文档路径
- `paragraph_index`: 段落索引（从0开始）

## 使用示例

### 提取所有评论
```python
# 获取文档中的所有评论
result = get_all_comments_tool("document.docx")
```

### 按作者筛选评论
```python
# 获取张三的所有评论
result = get_comments_by_author_tool("document.docx", "张三")

# 不区分大小写
result = get_comments_by_author_tool("document.docx", "zhang san")
```

### 按段落提取评论
```python
# 获取第一个段落的评论
result = get_comments_for_paragraph_tool("document.docx", 0)

# 获取第五个段落的评论
result = get_comments_for_paragraph_tool("document.docx", 4)
```

## 评论数据结构

每个评论包含以下字段：

- `id`: 唯一标识符
- `comment_id`: Word文档中的评论ID
- `author`: 评论作者
- `initials`: 作者缩写
- `date`: 评论日期（ISO格式）
- `text`: 评论内容
- `paragraph_index`: 关联的段落索引
- `in_table`: 是否在表格中
- `reference_text`: 被评论的文本片段

## 错误处理

服务提供完整的错误处理：

- 文件存在性检查
- 段落索引有效性验证
- 作者名称验证
- XML解析错误处理
- 详细的错误信息返回

## 技术实现

### 评论提取策略
1. **主要方法**: 通过文档关系访问评论部分
2. **备用方法**: 扫描段落XML查找评论引用
3. **智能解析**: 处理不同版本的Word文档格式

### 支持的评论类型
- 段落评论
- 表格内评论
- 文本范围评论
- 嵌套评论结构

## 限制说明

1. 某些复杂的评论格式可能无法完全解析
2. 评论的精确位置信息依赖于Word文档的内部结构
3. 加密或受保护的文档可能无法访问评论
4. 非标准格式的评论可能显示为占位符

## 注意事项

1. 确保Word文档存在且可读
2. 段落索引从0开始计算
3. 作者名称匹配不区分大小写
4. 返回结果为JSON格式字符串
5. 大型文档的评论提取可能需要较长时间

## 许可证

MIT License

## 作者

Word MCP Services
