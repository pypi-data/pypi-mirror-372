# SenseSpace DID MCP 部署指南

本文档说明如何将 SenseSpace DID MCP 服务部署到 Google Cloud Run。

## 前置要求

1. **Google Cloud SDK**: 确保已安装并配置 `gcloud` CLI
2. **Docker**: 本地开发时需要（可选）
3. **Google Cloud 项目**: 需要一个有效的 Google Cloud 项目

## 文件说明

### 1. Dockerfile
- 基于 Python 3.11 slim 镜像
- 使用 `uv` 进行依赖管理
- 暴露端口 15925
- 设置环境变量

### 2. cloud-run.yaml
- Cloud Run 服务的 Kubernetes 配置
- 包含资源限制、健康检查、服务账号等配置
- 需要替换 `PROJECT_ID` 为实际项目ID

### 3. deploy.sh
- 使用命令行参数部署的脚本
- 自动创建服务账号和权限
- 构建并推送 Docker 镜像
- 部署到 Cloud Run

### 4. deploy-with-yaml.sh
- 使用 YAML 配置文件部署的脚本
- 提供更细粒度的配置控制
- 自动替换配置文件中的项目ID

## 部署步骤

### 方法一：使用命令行部署脚本

1. **编辑脚本配置**:
   ```bash
   # 编辑 deploy.sh，设置你的项目ID和区域
   vim deploy.sh
   ```
   
   修改以下变量：
   ```bash
   PROJECT_ID="your-project-id"  # 替换为你的项目ID
   REGION="asia-east1"           # 替换为你想要的区域
   ```

2. **运行部署脚本**:
   ```bash
   ./deploy.sh
   ```

### 方法二：使用 YAML 配置部署

1. **编辑脚本配置**:
   ```bash
   # 编辑 deploy-with-yaml.sh，设置你的项目ID和区域
   vim deploy-with-yaml.sh
   ```

2. **运行部署脚本**:
   ```bash
   ./deploy-with-yaml.sh
   ```

### 方法三：手动部署

1. **设置项目**:
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **启用 API**:
   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   ```

3. **构建镜像**:
   ```bash
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/sensespace-did-mcp .
   ```

4. **部署服务**:
   ```bash
   gcloud run deploy sensespace-did-mcp \
     --image gcr.io/YOUR_PROJECT_ID/sensespace-did-mcp \
     --platform managed \
     --region asia-east1 \
     --allow-unauthenticated \
     --port 15925 \
     --memory 2Gi \
     --cpu 2
   ```

## 配置说明

### 资源限制
- **CPU**: 2 核心
- **内存**: 2GB
- **最大实例数**: 10
- **并发数**: 1000
- **超时**: 300秒

### 健康检查
- **存活探针**: 检查 `/mcp` 端点
- **就绪探针**: 检查 `/mcp` 端点
- **初始延迟**: 30秒（存活）/ 5秒（就绪）

### 服务账号
脚本会自动创建 `sensespace-did-sa` 服务账号并授予以下权限：
- `roles/logging.logWriter`
- `roles/monitoring.metricWriter`

## 验证部署

部署完成后，脚本会显示服务URL。你可以通过以下方式验证：

1. **访问 MCP 端点**:
   ```bash
   curl https://your-service-url/mcp
   ```

2. **查看服务状态**:
   ```bash
   gcloud run services describe sensespace-did-mcp --region=asia-east1
   ```

3. **查看日志**:
   ```bash
   gcloud logs read --service=sensespace-did-mcp --limit=50
   ```

## 故障排除

### 常见问题

1. **权限错误**:
   - 确保已启用必要的 API
   - 检查服务账号权限

2. **构建失败**:
   - 检查 Dockerfile 语法
   - 确保所有依赖文件存在

3. **服务启动失败**:
   - 检查端口配置
   - 查看服务日志

### 查看日志
```bash
gcloud logs read --service=sensespace-did-mcp --limit=100
```

### 重新部署
```bash
# 删除现有服务
gcloud run services delete sensespace-did-mcp --region=asia-east1

# 重新运行部署脚本
./deploy.sh
```

## 成本优化

- 设置 `min-instances=0` 以在无流量时缩放到零
- 调整 `max-instances` 以控制最大成本
- 监控 Cloud Run 的使用情况

## 安全建议

- 考虑启用身份验证（移除 `--allow-unauthenticated`）
- 使用 VPC 连接器限制网络访问
- 定期更新依赖包
- 监控异常访问模式

