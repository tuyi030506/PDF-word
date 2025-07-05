# Vercel 部署指南

## 🚀 快速部署到 Vercel

### 前置要求

1. **GitHub 账户**: 确保代码已推送到 GitHub
2. **Vercel 账户**: 在 [vercel.com](https://vercel.com) 注册账户
3. **Vercel CLI** (可选): `npm i -g vercel`

### 部署步骤

#### 方法1: 通过 Vercel Dashboard (推荐)

1. **登录 Vercel**
   - 访问 [vercel.com](https://vercel.com)
   - 使用 GitHub 账户登录

2. **导入项目**
   - 点击 "New Project"
   - 选择你的 GitHub 仓库
   - 选择 "PDF格式转换" 项目

3. **配置项目**
   - **Framework Preset**: 选择 "Other"
   - **Root Directory**: 保持默认 (./)
   - **Build Command**: 留空
   - **Output Directory**: 留空
   - **Install Command**: `pip install -r requirements-vercel.txt`

4. **环境变量** (可选)
   ```
   PYTHONPATH=.
   ```

5. **部署**
   - 点击 "Deploy"
   - 等待部署完成

#### 方法2: 通过 Vercel CLI

```bash
# 安装 Vercel CLI
npm i -g vercel

# 登录 Vercel
vercel login

# 部署项目
vercel --prod
```

### 部署配置说明

#### vercel.json
```json
{
  "version": 2,
  "functions": {
    "api/**/*.py": {
      "runtime": "python3.12",
      "maxDuration": 60
    }
  },
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/index.py"
    },
    {
      "src": "/(.*)",
      "dest": "/api/index.py"
    }
  ],
  "env": {
    "PYTHONPATH": "."
  }
}
```

#### requirements-vercel.txt
```
fastapi>=0.104.0
uvicorn>=0.24.0
python-multipart>=0.0.6
python-docx>=0.8.11
openpyxl>=3.1.2
pandas>=2.1.0
pdf2docx>=0.5.6
tabula-py>=2.8.0
Pillow>=10.0.0
pylovepdf==1.3.2
PyMuPDF>=1.23.0
requests>=2.31.0
pdf2image>=1.16.0
```

### 部署后验证

1. **访问应用**
   - 部署完成后，Vercel 会提供一个域名
   - 例如: `https://your-project.vercel.app`

2. **测试功能**
   ```bash
   # 健康检查
   curl https://your-project.vercel.app/health
   
   # 测试转换
   curl -X POST "https://your-project.vercel.app/api/convert" \
     -F "file=@test.pdf" \
     -F "output_format=docx" \
     -o "output.docx"
   ```

3. **检查日志**
   - 在 Vercel Dashboard 中查看 Function Logs
   - 监控部署状态和错误信息

### Vercel 限制说明

#### Serverless 函数限制
- **执行时间**: 最大 60 秒 (已配置)
- **内存**: 1024MB
- **文件大小**: 最大 10MB
- **并发**: 根据计划限制

#### 优化建议
1. **文件大小**: 建议上传小于 10MB 的 PDF
2. **转换时间**: 复杂文件可能需要 30-45 秒
3. **并发处理**: 避免同时处理多个大文件

### 故障排除

#### 常见问题

1. **部署失败**
   ```bash
   # 检查依赖安装
   pip install -r requirements-vercel.txt
   
   # 检查 Python 版本
   python --version
   ```

2. **函数超时**
   - 减少文件大小
   - 优化转换参数
   - 检查网络连接

3. **内存不足**
   - 使用更小的文件
   - 优化代码内存使用

#### 调试技巧

1. **本地测试**
   ```bash
   # 使用 Vercel 开发环境
   vercel dev
   ```

2. **查看日志**
   ```bash
   # 查看实时日志
   vercel logs
   ```

3. **重新部署**
   ```bash
   # 强制重新部署
   vercel --prod --force
   ```

### 自定义域名

1. **添加域名**
   - 在 Vercel Dashboard 中添加自定义域名
   - 配置 DNS 记录

2. **SSL 证书**
   - Vercel 自动提供 SSL 证书
   - 支持 HTTPS 访问

### 监控和分析

1. **性能监控**
   - 查看 Function 执行时间
   - 监控内存使用情况

2. **错误追踪**
   - 查看错误日志
   - 设置错误通知

3. **使用统计**
   - 查看访问量
   - 分析用户行为

## 🎉 部署完成

部署成功后，你的 PDF 转换服务就可以在全球范围内访问了！

### 访问地址
- **生产环境**: `https://your-project.vercel.app`
- **API 文档**: `https://your-project.vercel.app/docs`
- **健康检查**: `https://your-project.vercel.app/health`

### 下一步
1. 测试所有功能
2. 配置自定义域名
3. 设置监控和告警
4. 优化性能和用户体验 