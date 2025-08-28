#!/bin/bash

# 本地测试脚本

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_message "开始本地测试..."

# 1. 构建本地Docker镜像
print_message "构建本地Docker镜像..."
docker build -t sensespace-did-mcp:local .

# 2. 运行容器
print_message "启动本地容器..."
docker run -d --name sensespace-did-test -p 15925:15925 sensespace-did-mcp:local

# 3. 等待服务启动
print_message "等待服务启动..."
sleep 10

# 4. 测试服务
print_message "测试MCP端点..."
if curl -s "http://localhost:15925/mcp" > /dev/null; then
    print_message "✅ 本地服务运行正常！"
    print_message "MCP端点: http://localhost:15925/mcp"
else
    print_warning "⚠️  服务可能还在启动中，请稍后重试"
fi

# 5. 显示容器日志
print_message "显示容器日志..."
docker logs sensespace-did-test

print_message "本地测试完成！"
print_message "要停止容器，请运行: docker stop sensespace-did-test && docker rm sensespace-did-test"

