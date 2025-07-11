#!/bin/bash

# Render 部署脚本
echo "🚀 开始部署到 Render..."

# 检查Git状态
if [ -n "$(git status --porcelain)" ]; then
    echo "📝 检测到未提交的更改，正在提交..."
    git add .
    git commit -m "优化Render部署配置 - $(date)"
fi

# 推送到GitHub
echo "📤 推送到GitHub..."
git push origin main

echo "✅ 部署完成！"
echo "🌐 请访问 Render Dashboard 查看部署状态"
echo "📋 部署地址: https://your-app-name.onrender.com/"
echo "🔍 健康检查: https://your-app-name.onrender.com/health" 