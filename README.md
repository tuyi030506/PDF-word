# PDF 转换工具

一个基于 FastAPI 的高质量 PDF 转换工具，支持将 PDF 文件转换为 Word (docx) 和 Excel (xlsx) 格式。

## ✨ 功能特点

- 🚀 **快速转换**: 使用 pdf2docx 和 PyMuPDF 进行高质量转换
- 📄 **格式支持**: PDF → Word (.docx) / Excel (.xlsx)
- 🌐 **Web界面**: 现代化的拖拽上传界面
- 🔌 **API接口**: RESTful API，支持程序化调用
- 🐳 **容器化**: 支持 Docker 部署
- ☁️ **云部署**: 支持 Vercel Serverless 部署
- 📱 **响应式**: 支持移动端和桌面端

## 🛠️ 技术栈

- **后端**: FastAPI + Python 3.9+
- **转换引擎**: pdf2docx + PyMuPDF + pandas
- **前端**: HTML5 + CSS3 + JavaScript
- **部署**: Docker + Vercel

## 📦 安装和运行

### 本地开发

1. **克隆项目**
```bash
git clone <your-repo-url>
cd PDF格式转换
```

2. **创建虚拟环境**
```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# 或
.venv\Scripts\activate  # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **启动服务**
```bash
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

5. **访问应用**
- Web界面: http://localhost:8000
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

### Docker 部署

```bash
# 构建镜像
docker build -t pdf-converter .

# 运行容器
docker run -p 8000:8000 pdf-converter

# 或使用 docker-compose
docker-compose up -d
```

### Vercel 部署

1. **安装 Vercel CLI**
```bash
npm i -g vercel
```

2. **部署到 Vercel**
```bash
vercel --prod
```

## 🔌 API 接口

### 1. 文件转换

**端点**: `POST /api/convert`

**参数**:
- `file`: PDF文件 (multipart/form-data)
- `output_format`: 输出格式 ("docx" 或 "xlsx")

**示例**:
```bash
curl -X POST "http://localhost:8000/api/convert" \
  -F "file=@input.pdf" \
  -F "output_format=docx" \
  -o "output.docx"
```

### 2. 健康检查

**端点**: `GET /health`

**响应**:
```json
{
  "status": "healthy",
  "message": "PDF转换服务运行正常",
  "version": "2.0.0"
}
```

### 3. 系统状态

**端点**: `GET /api/status`

**响应**:
```json
{
  "system": {
    "status": "running",
    "version": "2.0.0",
    "mode": "production"
  },
  "features": {
    "pdf_to_word": "✅ 正常工作",
    "pdf_to_excel": "✅ 正常工作",
    "file_upload": "✅ 正常工作",
    "real_conversion": "✅ 已启用"
  },
  "conversion_engine": "pdf2docx + pandas"
}
```

## 📝 使用示例

### Python 客户端

```python
import requests

def convert_pdf(pdf_path, output_format="docx"):
    url = "http://localhost:8000/api/convert"
    
    with open(pdf_path, "rb") as f:
        files = {"file": f}
        data = {"output_format": output_format}
        
        response = requests.post(url, files=files, data=data)
        
    if response.status_code == 200:
        output_filename = f"output.{output_format}"
        with open(output_filename, "wb") as f:
            f.write(response.content)
        print(f"转换成功: {output_filename}")
        return True
    else:
        print(f"转换失败: {response.json()}")
        return False

# 使用示例
convert_pdf("input.pdf", "docx")
convert_pdf("input.pdf", "xlsx")
```

### JavaScript 客户端

```javascript
async function convertPdf(file, outputFormat = 'docx') {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('output_format', outputFormat);
    
    try {
        const response = await fetch('/api/convert', {
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
        a.download = `converted.${outputFormat}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();
        
    } catch (error) {
        console.error('转换失败:', error);
    }
}
```

## 🔧 配置说明

### 环境变量

创建 `.env` 文件（参考 `env.example`）:

```env
# 服务器配置
HOST=0.0.0.0
PORT=8000
DEBUG=false

# 文件限制
MAX_FILE_SIZE=52428800  # 50MB
ALLOWED_EXTENSIONS=pdf

# 转换配置
CONVERSION_TIMEOUT=300  # 5分钟
```

### 转换参数

可以在代码中调整以下参数：

- **文件大小限制**: 默认50MB
- **转换超时**: 默认5分钟
- **输出质量**: 使用pdf2docx的默认设置

## 📊 性能特点

- **转换速度**: 1MB PDF ≈ 2-5秒
- **内存使用**: 优化内存使用，支持大文件
- **并发处理**: 支持多用户同时转换
- **错误处理**: 完善的错误处理和日志记录

## 🚨 注意事项

1. **文件格式**: 仅支持PDF文件输入
2. **文件大小**: 建议小于50MB，Vercel版本限制10MB
3. **转换质量**: 复杂表格和图片可能影响转换效果
4. **中文支持**: 完全支持中文字符和文件名
5. **临时文件**: 转换完成后自动清理临时文件

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🔗 相关链接

- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [pdf2docx 文档](https://github.com/dothinking/pdf2docx)
- [PyMuPDF 文档](https://pymupdf.readthedocs.io/)
- [Vercel 部署指南](https://vercel.com/docs) 