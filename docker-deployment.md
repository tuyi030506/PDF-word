# PDF转换工具 - 云部署指南

## 🐳 Docker部署（推荐）

### 1. 创建Dockerfile
```dockerfile
FROM python:3.9-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要目录
RUN mkdir -p converted_files static logs

# 暴露端口
EXPOSE 3001

# 启动命令
CMD ["python", "server_final.py"]
```

### 2. 创建docker-compose.yml
```yaml
version: '3.8'
services:
  pdf-converter:
    build: .
    ports:
      - "3001:3001"
    volumes:
      - ./converted_files:/app/converted_files
      - ./logs:/app/logs
    environment:
      - ENVIRONMENT=production
    restart: unless-stopped
```

### 3. 部署命令
```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f
```

## ☁️ 云平台部署选项

### A. 阿里云/腾讯云 ECS
**配置要求：**
- CPU: 2核心以上
- 内存: 4GB以上
- 存储: 20GB以上
- 带宽: 5Mbps以上

**月成本：** 约￥100-200/月

### B. Vercel/Netlify (免费)
**限制：**
- 函数执行时间限制（10-60秒）
- 内存限制（1GB）
- 适合小文件转换

### C. Railway/Render (便宜)
**优势：**
- 自动部署
- 免费额度
- 简单配置

**月成本：** $5-20/月

### D. AWS/Google Cloud
**优势：**
- 高可用性
- 自动扩缩容
- 企业级服务

**月成本：** $20-100/月

## 🛡️ 生产环境优化

### 1. 性能优化
```python
# 并发限制
import asyncio
semaphore = asyncio.Semaphore(5)  # 最多5个并发转换

# 内存优化
import gc
gc.collect()  # 转换后清理内存

# 文件清理
import schedule
schedule.every(1).hours.do(cleanup_old_files)
```

### 2. 安全增强
```python
# 文件大小限制
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# 速率限制
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@app.post("/api/convert")
@limiter.limit("10/minute")  # 每分钟最多10次
async def convert_pdf():
    pass
```

### 3. 监控告警
```python
# 健康检查增强
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "disk_usage": check_disk_space(),
        "memory_usage": check_memory(),
        "active_conversions": get_active_count()
    }
```

## 📊 部署成本估算

| 方案 | 月成本 | 适用场景 |
|------|--------|----------|
| 个人VPS | ￥50-100 | 个人/小团队使用 |
| 云服务器 | ￥100-300 | 中小企业 |
| 企业云 | ￥500+ | 大企业/高并发 |

## 🚀 快速部署步骤

### 1. 准备服务器
```bash
# 安装Docker
curl -fsSL https://get.docker.com | sh

# 安装docker-compose
sudo apt install docker-compose
```

### 2. 上传代码
```bash
# 克隆/上传项目到服务器
git clone your-repo
cd pdf-converter
```

### 3. 启动服务
```bash
# 构建并启动
docker-compose up -d

# 配置反向代理 (nginx)
sudo apt install nginx
# 配置SSL证书 (Let's Encrypt)
sudo apt install certbot
```

### 4. 域名绑定
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:3001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📈 商业化考虑

### 收费模式选项：
1. **免费 + 广告** - 个人用户免费使用
2. **按次收费** - ￥0.1-1/次转换
3. **订阅制** - ￥10-50/月无限制
4. **API调用** - 对开发者提供API接口

### 技术栈升级：
1. **用户系统** - 注册/登录/会员
2. **支付集成** - 微信/支付宝
3. **使用统计** - 转换次数/成功率
4. **CDN加速** - 文件上传下载加速 