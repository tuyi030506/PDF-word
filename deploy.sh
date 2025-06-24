#!/bin/bash

# PDF转换工具 - 一键部署脚本
# 支持: Ubuntu/Debian/CentOS

set -e

echo "🚀 PDF转换工具 - 一键部署脚本"
echo "=================================="

# 检测操作系统
if [ -f /etc/debian_version ]; then
    OS="debian"
    echo "检测到 Debian/Ubuntu 系统"
elif [ -f /etc/redhat-release ]; then
    OS="centos"
    echo "检测到 CentOS/RHEL 系统"
else
    echo "❌ 不支持的操作系统"
    exit 1
fi

# 安装Docker
echo "📦 安装Docker..."
if ! command -v docker &> /dev/null; then
    if [ "$OS" = "debian" ]; then
        sudo apt-get update
        sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
        echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        sudo apt-get update
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io
    else
        sudo yum install -y yum-utils
        sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
        sudo yum install -y docker-ce docker-ce-cli containerd.io
    fi
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker $USER
    echo "✅ Docker安装完成"
else
    echo "✅ Docker已存在"
fi

# 安装Docker Compose
echo "📦 安装Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.12.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose安装完成"
else
    echo "✅ Docker Compose已存在"
fi

# 创建项目目录
echo "📁 创建项目目录..."
PROJECT_DIR="/opt/pdf-converter"
sudo mkdir -p $PROJECT_DIR
sudo chown $USER:$USER $PROJECT_DIR
cd $PROJECT_DIR

# 下载项目文件（假设已上传）
echo "📥 准备项目文件..."
if [ ! -f "server_final.py" ]; then
    echo "❌ 请先上传项目文件到当前目录"
    echo "📍 当前目录: $(pwd)"
    echo "📋 需要的文件: server_final.py, requirements.txt, Dockerfile, docker-compose.yml"
    exit 1
fi

# 创建必要目录
mkdir -p converted_files logs static

# 设置防火墙
echo "🔥 配置防火墙..."
if command -v ufw &> /dev/null; then
    sudo ufw allow 3001/tcp
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
elif command -v firewall-cmd &> /dev/null; then
    sudo firewall-cmd --permanent --add-port=3001/tcp
    sudo firewall-cmd --permanent --add-port=80/tcp
    sudo firewall-cmd --permanent --add-port=443/tcp
    sudo firewall-cmd --reload
fi

# 构建并启动服务
echo "🐳 构建并启动Docker容器..."
docker-compose down --remove-orphans
docker-compose up -d --build

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 30

# 检查服务状态
echo "🔍 检查服务状态..."
if curl -f http://localhost:3001/health > /dev/null 2>&1; then
    echo "✅ 服务启动成功！"
    echo "🌐 访问地址: http://$(curl -s ifconfig.me):3001"
    echo "🏥 健康检查: http://$(curl -s ifconfig.me):3001/health"
else
    echo "❌ 服务启动失败，查看日志:"
    docker-compose logs --tail=50
    exit 1
fi

# 设置开机自启
echo "🔄 设置开机自启..."
cat > /etc/systemd/system/pdf-converter.service << EOF
[Unit]
Description=PDF Converter Service
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$PROJECT_DIR
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable pdf-converter.service
echo "✅ 开机自启设置完成"

# 显示部署信息
echo ""
echo "🎉 部署完成！"
echo "=================================="
echo "📍 服务地址: http://$(curl -s ifconfig.me):3001"
echo "🏥 健康检查: http://$(curl -s ifconfig.me):3001/health" 
echo "📁 文件目录: $PROJECT_DIR/converted_files"
echo "📄 日志目录: $PROJECT_DIR/logs"
echo ""
echo "🔧 管理命令:"
echo "  启动服务: cd $PROJECT_DIR && docker-compose up -d"
echo "  停止服务: cd $PROJECT_DIR && docker-compose down"
echo "  查看日志: cd $PROJECT_DIR && docker-compose logs -f"
echo "  重启服务: cd $PROJECT_DIR && docker-compose restart"
echo ""
echo "📊 监控命令:"
echo "  容器状态: docker ps"
echo "  资源使用: docker stats"
echo "  磁盘空间: df -h"
echo ""
echo "�� 下一步: 配置域名和SSL证书" 