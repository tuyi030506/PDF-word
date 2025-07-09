# Render 部署指南

## 📋 部署前准备

### 1. 确保代码已推送到 GitHub
```bash
git add .
git commit -m "准备 Render 部署"
git push origin main
```

### 2. 检查文件结构
确保以下文件存在：
- ✅ `api/index.py` - FastAPI 应用入口
- ✅ `requirements-render.txt` - 依赖文件
- ✅ `runtime.txt` - Python 版本
- ✅ `render.yaml` - Render 配置（可选）

## 🚀 Render 部署步骤

### 第一步：注册 Render
1. 访问 [render.com](https://render.com)
2. 点击 "Get Started"
3. 选择 "Continue with GitHub"
4. 授权 GitHub 账户

### 第二步：创建 Web Service
1. 在 Render Dashboard 点击 "New +"
2. 选择 "Web Service"
3. 选择 "Connect a repository"
4. 选择你的 GitHub 仓库

### 第三步：配置部署设置
```
Name: pdf-converter (或你喜欢的名字)
Environment: Python 3
Region: 选择离你最近的地区
Branch: main
Root Directory: ./ (留空)
Build Command: pip install -r requirements-render.txt
Start Command: uvicorn api.index:app --host 0.0.0.0 --port $PORT
```

### 第四步：高级设置（可选）
- **Auto-Deploy**: 保持开启（每次 push 自动部署）
- **Health Check Path**: `/health`

### 第五步：创建服务
点击 "Create Web Service"

## 🔧 部署配置说明

### 启动命令
```bash
uvicorn api.index:app --host 0.0.0.0 --port $PORT
```
- `--host 0.0.0.0`: 允许外部访问
- `--port $PORT`: 使用 Render 分配的端口

### 依赖文件
使用 `requirements-render.txt` 而不是 `requirements-vercel.txt`，因为：
- 固定版本号，避免兼容性问题
- 包含 `uvicorn[standard]` 以获得更好的性能

### 健康检查
应用提供 `/health` 端点用于 Render 健康检查

## 🌐 部署完成后

### 访问地址
- **应用主页**: `https://your-app-name.onrender.com/`
- **API 端点**: `https://your-app-name.onrender.com/api/`
- **健康检查**: `https://your-app-name.onrender.com/health`

### 功能测试
1. 访问主页，应该看到 PDF 转换界面
2. 上传小文件测试转换功能
3. 检查 `/health` 端点返回正常状态

## 📊 免费套餐限制

- **休眠**: 15分钟无请求后自动休眠
- **唤醒**: 首次请求可能需要几秒钟
- **资源**: 0.1 vCPU, 512MB RAM
- **带宽**: 100GB/月

## 🔍 故障排除

### 常见问题

1. **构建失败**
   - 检查 `requirements-render.txt` 中的依赖版本
   - 查看构建日志中的错误信息

2. **启动失败**
   - 确认 `api/index.py` 中的 FastAPI 应用正确
   - 检查启动命令是否正确

3. **应用无响应**
   - 检查健康检查端点 `/health`
   - 查看应用日志

### 查看日志
在 Render Dashboard 中：
1. 选择你的 Web Service
2. 点击 "Logs" 标签
3. 查看实时日志和错误信息

## 🔄 更新部署

每次推送到 GitHub 主分支，Render 会自动重新部署。

## 📞 支持

如果遇到问题：
1. 查看 Render 文档
2. 检查应用日志
3. 确认代码在本地运行正常 