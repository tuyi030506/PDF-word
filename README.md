# PDF 转换工具

这是一个使用 Python 实现的 PDF 转换工具,可以将 PDF 文件转换为 Excel 和 Word 格式。

## 功能特点

- 支持中英文 PDF 文件转换
- 自动识别表格结构
- 保持原有格式和布局
- 支持批量转换
- 提供图像预处理优化识别效果
- 提供 Web 界面和 API 接口

## 环境要求

- Python 3.7+
- Tesseract OCR 引擎
- poppler-utils (用于 PDF 转图像)
- Microsoft Word (用于 PDF 转 Word)

## 安装步骤

1. 安装 Tesseract OCR:
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-chi-sim  # 中文支持

# macOS
brew install tesseract
brew install tesseract-lang  # 语言包
```

2. 安装 poppler-utils:
```bash
# Ubuntu/Debian
sudo apt-get install poppler-utils

# macOS
brew install poppler
```

3. 安装 Python 依赖:
```bash
pip install -r requirements.txt
```

## 使用方法

### 命令行方式

1. 修改 `pdf_to_excel.py` 中的 Tesseract 路径:
```python
pytesseract.pytesseract.tesseract_cmd = r'path_to_tesseract'  # 改为你的 Tesseract 安装路径
```

2. 运行转换:
```bash
python pdf_to_excel.py
```

默认会将 `input.pdf` 转换为 `output.xlsx`。

### Web 界面

1. 启动服务器:
```bash
uvicorn api:app --reload
```

2. 打开浏览器访问 http://localhost:8000

3. 选择要转换的 PDF 文件和目标格式,点击"开始转换"

### API 接口

#### 1. PDF 转 Excel

**请求:**
```http
POST /convert/excel/
Content-Type: multipart/form-data

file: PDF文件
output_format: xlsx (可选)
```

**响应:**
- 成功: 返回转换后的 Excel 文件
- 失败: 返回错误信息

#### 2. PDF 转 Word

**请求:**
```http
POST /convert/word/
Content-Type: multipart/form-data

file: PDF文件
output_format: docx (可选)
```

**响应:**
- 成功: 返回转换后的 Word 文件
- 失败: 返回错误信息

#### 3. 健康检查

**请求:**
```http
GET /health
```

**响应:**
```json
{
    "status": "healthy"
}
```

## 自定义配置

你可以修改以下参数来优化转换效果:

- `horizontal_size` 和 `vertical_size`: 调整表格线检测的粗细
- `lang`: 设置 OCR 识别的语言,默认支持中英文
- 在 `preprocess_image` 方法中调整图像预处理参数

## 注意事项

- 确保 PDF 文件清晰度较高
- 表格线条要清晰可见
- 对于复杂布局的 PDF 可能需要调整参数
- 建议先对小批量文件进行测试
- PDF 转 Word 功能需要安装 Microsoft Word

## API 集成示例

### Python

```python
import requests

def convert_pdf_to_excel(pdf_path, api_url="http://localhost:8000/convert/excel/"):
    with open(pdf_path, "rb") as f:
        files = {"file": f}
        response = requests.post(api_url, files=files)
        
    if response.status_code == 200:
        # 保存转换后的文件
        with open("output.xlsx", "wb") as f:
            f.write(response.content)
        return True
    return False

# 使用示例
convert_pdf_to_excel("input.pdf")
```

### JavaScript

```javascript
async function convertPdfToExcel(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('http://localhost:8000/convert/excel/', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('转换失败');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'converted.xlsx';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();
        
    } catch (error) {
        console.error('转换失败:', error);
    }
}
```

### cURL

```bash
# PDF 转 Excel
curl -X POST -F "file=@input.pdf" http://localhost:8000/convert/excel/ --output output.xlsx

# PDF 转 Word
curl -X POST -F "file=@input.pdf" http://localhost:8000/convert/word/ --output output.docx
```

## 许可证

MIT 