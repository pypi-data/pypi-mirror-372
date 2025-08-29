# Word文档内容添加 MCP服务

这是一个基于Model Context Protocol (MCP)的Word文档内容添加服务，提供向Word文档添加各种内容元素的功能。

## 功能特性

### 核心功能
- **添加标题** - 向文档添加不同级别的标题
- **添加段落** - 向文档添加文本段落，支持样式设置
- **添加表格** - 向文档添加表格，支持数据填充
- **添加图片** - 向文档添加图片，支持尺寸调整
- **添加分页符** - 向文档添加分页符

### 技术特性
- 基于FastMCP框架构建
- 支持异步操作
- 完整的错误处理和验证
- 文件权限检查
- 图片格式验证
- 自动文件扩展名处理

## 安装要求

- Python 3.10+
- python-docx >= 1.1.0
- fastmcp >= 2.8.1
- Pillow >= 10.0.0 (用于图片处理)

## 安装方法

使用uv安装依赖：

```bash
cd python/Word文档内容添加
uv sync
```

或使用pip安装：

```bash
pip install python-docx fastmcp Pillow
```

## 使用方法

### 启动MCP服务器

```bash
# 使用uv运行
uv run python -m word_document_content_adder.main

# 或直接运行
python -m word_document_content_adder.main
```

### MCP配置

将以下配置添加到您的MCP客户端配置文件中：

```json
{
  "mcpServers": {
    "word-document-content-adder": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/Word文档内容添加",
        "run",
        "python",
        "-m",
        "word_document_content_adder.main"
      ],
      "env": {
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

### 在Claude中使用

配置完成后，在Claude中可以使用以下功能：

1. **添加标题**
   ```
   请向文档 "example.docx" 添加一级标题 "第一章 概述"
   ```

2. **添加段落**
   ```
   请向文档 "example.docx" 添加段落 "这是一个重要的说明文本。"
   ```

   或者指定样式：
   ```
   请向文档 "example.docx" 添加段落 "这是引用文本。"，样式设置为 "Quote"
   ```

3. **添加表格**
   ```
   请向文档 "example.docx" 添加一个3行4列的表格，包含以下数据：
   第一行：姓名、年龄、职位、部门
   第二行：张三、28、工程师、技术部
   第三行：李四、32、经理、销售部
   ```

4. **添加图片**
   ```
   请向文档 "example.docx" 添加图片 "chart.png"，宽度设置为5英寸
   ```

5. **添加分页符**
   ```
   请向文档 "example.docx" 添加一个分页符
   ```

## API参考

### 添加标题
```python
add_heading_tool(filename: str, text: str, level: int = 1)
```
- `filename`: Word文档路径
- `text`: 标题文本
- `level`: 标题级别 (1-9)

### 添加段落
```python
add_paragraph_tool(filename: str, text: str, style: str = "")
```
- `filename`: Word文档路径
- `text`: 段落文本
- `style`: 可选的段落样式名称（留空表示使用默认样式）

### 添加表格
```python
add_table_tool(filename: str, rows: int, cols: int, data: list = [])
```
- `filename`: Word文档路径
- `rows`: 表格行数
- `cols`: 表格列数
- `data`: 可选的二维数组数据（留空表示创建空表格）

### 添加图片
```python
add_picture_tool(filename: str, image_path: str, width: float = 0.0)
```
- `filename`: Word文档路径
- `image_path`: 图片文件路径
- `width`: 可选的图片宽度（英寸，0.0表示使用原始尺寸）

### 添加分页符
```python
add_page_break_tool(filename: str)
```
- `filename`: Word文档路径

## 使用示例

### 添加标题
```python
# 添加一级标题
result = add_heading_tool("document.docx", "第一章 概述", 1)

# 添加二级标题
result = add_heading_tool("document.docx", "1.1 背景", 2)
```

### 添加段落
```python
# 添加普通段落
result = add_paragraph_tool("document.docx", "这是一个段落的内容。")

# 添加带样式的段落
result = add_paragraph_tool("document.docx", "这是引用文本。", "Quote")
```

### 添加表格
```python
# 添加空表格
result = add_table_tool("document.docx", 3, 4)

# 添加带数据的表格
data = [
    ["姓名", "年龄", "职位", "部门"],
    ["张三", "28", "工程师", "技术部"],
    ["李四", "32", "经理", "销售部"]
]
result = add_table_tool("document.docx", 3, 4, data)
```

### 添加图片
```python
# 添加原始尺寸图片
result = add_picture_tool("document.docx", "image.png")

# 添加指定宽度的图片
result = add_picture_tool("document.docx", "image.png", 4.0)
```

### 添加分页符
```python
result = add_page_break_tool("document.docx")
```

## 错误处理

服务提供完整的错误处理：

- 文件不存在检查
- 文件权限验证
- 图片格式验证
- 参数有效性检查
- 详细的错误信息返回

## 支持的图片格式

- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- BMP (.bmp)
- TIFF (.tiff, .tif)

## 注意事项

1. 确保目标Word文档存在且可写
2. 图片文件必须存在且格式受支持
3. 文档不能被其他程序打开
4. 标题级别必须在1-9之间
5. 表格数据应为二维数组格式

## 参数说明

### 可选参数处理
- `style`: 传入空字符串 `""` 表示使用默认样式
- `data`: 传入空数组 `[]` 表示创建空表格
- `width`: 传入 `0.0` 表示使用图片原始尺寸
- 所有可选参数都有合理的默认值，可以省略不填

## 许可证

MIT License

## 作者

Word MCP Services
