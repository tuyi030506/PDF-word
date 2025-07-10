# Render 部署指南 (优化版)

## 📋 部署前准备

### 1. 确保代码已推送到 GitHub
```bash
git add .
git commit -m "优化Render部署配置"
git push origin main
```

### 2. 检查文件结构
确保以下文件存在：
- ✅ `api/render_app.py` - Render优化版FastAPI应用
- ✅ `start.py` - 启动脚本
- ✅ `requirements-render.txt` - 简化依赖文件
- ✅ `runtime.txt` - Python版本
- ✅ `render.yaml` - Render配置

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
Start Command: python start.py
```

### 第四步：高级设置
- **Auto-Deploy**: 保持开启（每次 push 自动部署）
- **Health Check Path**: `/health`

### 第五步：创建服务
点击 "Create Web Service"

## 🔧 优化配置说明

### 启动命令
```bash
python start.py
```
- 使用专门的启动脚本
- 自动检测PORT环境变量
- 单worker模式，适合免费套餐

### 依赖文件
使用 `requirements-render.txt`：
- 移除了可能导致冲突的包
- 使用稳定版本号
- 只包含核心功能依赖

### 应用文件
使用 `api/render_app.py`：
- 简化版本，减少内存使用
- 移除复杂功能，提高稳定性
- 优化错误处理

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
- **构建时间**: 最长10分钟

## 🔍 故障排除

### 常见问题及解决方案

1. **构建失败 - 依赖冲突**
   ```
   错误: Could not find a version that satisfies the requirement
   解决: 使用 requirements-render.txt 中的固定版本
   ```

2. **构建失败 - 内存不足**
   ```
   错误: MemoryError during pip install
   解决: 已简化依赖，移除大型包
   ```

3. **启动失败 - 端口问题**
   ```
   错误: Address already in use
   解决: 使用 $PORT 环境变量
   ```

4. **启动失败 - 模块导入错误**
   ```
   错误: ModuleNotFoundError
   解决: 检查 requirements-render.txt 是否包含所有依赖
   ```

5. **应用无响应 - 健康检查失败**
   ```
   错误: Health check failed
   解决: 确保 /health 端点正常工作
   ```

### 查看日志
在 Render Dashboard 中：
1. 选择你的 Web Service
2. 点击 "Logs" 标签
3. 查看实时日志和错误信息

### 调试步骤
1. **检查构建日志**
   - 查看依赖安装是否成功
   - 确认Python版本正确

2. **检查启动日志**
   - 确认应用正常启动
   - 查看端口绑定情况

3. **检查运行日志**
   - 测试健康检查端点
   - 查看API请求日志

## 🔄 更新部署

每次推送到 GitHub 主分支，Render 会自动重新部署。

## 📞 支持

如果遇到问题：
1. 查看 Render 文档: https://render.com/docs
2. 检查应用日志
3. 确认代码在本地运行正常
4. 尝试简化配置

## 🎯 优化建议

1. **文件大小限制**: 建议用户上传小于5MB的文件
2. **处理时间**: 复杂PDF可能需要较长时间
3. **并发限制**: 免费套餐建议同时处理1个请求
4. **错误处理**: 应用会返回详细的错误信息 