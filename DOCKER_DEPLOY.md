# Docker 部署指南

## 前提条件

- 已安装 Docker Desktop
- 已安装 Docker Compose

## 配置 Docker 镜像加速（国内用户必须）

### Windows Docker Desktop 配置

1. 打开 Docker Desktop
2. 点击右上角齿轮图标 → Settings
3. 选择 Docker Engine
4. 在 JSON 配置中添加镜像加速器：

```json
{
  "registry-mirrors": [
    "https://docker.1ms.run",
    "https://docker.xuanyuan.me"
  ]
}
```

5. 点击 "Apply & Restart"

### 或者使用命令行配置

创建或编辑 `C:\Users\<用户名>\.docker\daemon.json`:

```json
{
  "registry-mirrors": [
    "https://docker.1ms.run",
    "https://docker.xuanyuan.me"
  ]
}
```

然后重启 Docker Desktop。

## 部署步骤

### 1. 构建镜像

```bash
docker-compose -p asset-management build
```

### 2. 启动服务

```bash
docker-compose -p asset-management up -d
```

### 3. 查看日志

```bash
docker-compose -p asset-management logs -f
```

### 4. 停止服务

```bash
docker-compose -p asset-management down
```

## 访问应用

- 应用地址: http://localhost:5000
- 默认管理员账号: admin
- 默认密码: admin123 (需要通过 Flask 生成)

## 数据库配置

数据库连接信息（在 docker-compose.yml 中配置）:

- 主机: db (容器内) 或 localhost (容器外)
- 端口: 3306
- 数据库: asset_management
- 用户名: asset_user
- 密码: asset_password
- Root密码: root_password

## AI 功能配置

AI 功能需要连接宿主机的 Ollama 服务:

- OLLAMA_API_BASE: http://host.docker.internal:11434/v1
- OLLAMA_MODEL: qwen3.5:9B

确保宿主机的 Ollama 服务正在运行。

## 数据持久化

- MySQL 数据: Docker volume `mysql_data`
- 应用数据: `./data` 目录映射

## 生产环境建议

1. 修改 `docker-compose.yml` 中的所有密码
2. 使用环境变量文件 `.env` 管理敏感配置
3. 配置 HTTPS
4. 使用 Nginx 反向代理
5. 配置日志收集

## 故障排除

### 镜像拉取失败

如果仍然无法拉取镜像，可以尝试:

1. 检查网络连接
2. 更换镜像加速器地址
3. 使用 VPN

### 数据库连接失败

1. 检查 MySQL 容器是否正常启动: `docker ps`
2. 查看日志: `docker logs asset-mysql`
3. 确认数据库已初始化完成

### AI 功能不可用

1. 确认宿主机 Ollama 服务运行中: `curl http://localhost:11434/api/tags`
2. 确认模型已下载: `ollama list`