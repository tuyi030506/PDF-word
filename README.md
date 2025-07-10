# PDF转换工具 - Render版

一个基于FastAPI的PDF转Word/Excel在线转换工具，专门为Render平台优化。

## 🚀 功能特性

- **PDF转Word**: 高质量文档转换
- **PDF转Excel**: 表格数据提取
- **在线使用**: 无需安装，浏览器直接使用
- **快速处理**: 优化算法，处理速度快
- **安全可靠**: 文件处理完自动删除

## 📋 技术栈

- **后端**: FastAPI + Python 3.11
- **PDF处理**: pdf2docx, tabula-py, PyMuPDF
- **文档处理**: python-docx, openpyxl
- **部署**: Render (免费套餐)

## 🌐 在线使用

访问应用主页，上传PDF文件即可开始转换。

## 🔧 本地开发

### 环境要求
- Python 3.11+
- pip

### 安装依赖
```bash
pip install -r requirements.txt
```

### 启动服务
```bash
python start.py
```

访问 http://localhost:8000 即可使用。

## 📊 使用限制

- **文件大小**: 最大10MB
- **处理时间**: 最长30秒
- **并发限制**: 建议同时处理1个请求

## 🔍 API接口

### 健康检查
```
GET /health
```

### 状态查询
```
GET /api/status
```

### 文件转换
```
POST /api/convert
Content-Type: multipart/form-data

参数:
- file: PDF文件
- output_format: docx 或 xlsx
```

## 📝 部署说明

本项目已针对Render平台进行优化，包含以下配置文件：

- `render.yaml`: Render部署配置
- `start.py`: 应用启动脚本
- `requirements.txt`: Python依赖
- `runtime.txt`: Python版本

## 🤝 贡献

欢迎提交Issue和Pull Request！

## �� 许可证

MIT License 