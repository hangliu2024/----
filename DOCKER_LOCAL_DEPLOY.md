# Docker 本机部署详细指南

本文档提供资产管理系统在本地使用 Docker 部署的完整步骤。

---

## 一、前置要求

### 1. 硬件要求

| 项目 | 最低要求 | 推荐配置 |
|------|----------|----------|
| CPU | 2核 | 4核+ |
| 内存 | 4GB | 8GB+ |
| 磁盘 | 20GB | 50GB+ |

### 2. 软件要求

- **Docker**: 20.10+
- **Docker Compose**: 2.0+

### 3. 安装 Docker

#### Windows

1. 下载 [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop)
2. 安装并启动 Docker Desktop
3. 验证安装:
   ```cmd
   docker --version
   docker-compose --version
   ```

#### macOS

1. 下载 [Docker Desktop for Mac](https://www.docker.com/products/docker-desktop)
2. 安装并启动 Docker Desktop
3. 验证安装:
   ```bash
   docker --version
   docker-compose --version
   ```

#### Linux (Ubuntu)

```bash
# 安装 Docker
curl -fsSL https://get.docker.com | bash

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 将当前用户添加到 docker 组
sudo usermod -aG docker $USER

# 验证安装
docker --version
docker-compose --version
```

---

## 二、快速部署（推荐）

### 方法一：使用部署脚本（Linux/macOS）

```bash
# 1. 进入项目目录
cd d:/资产管理

# 2. 添加执行权限
chmod +x deploy.sh

# 3. 运行部署脚本
./deploy.sh

# 或者使用国内镜像加速
./deploy.sh --cn-mirror
```

### 方法二：手动部署（Windows/通用）

#### 步骤 1: 创建环境配置文件

在项目根目录创建 `.env` 文件:

```env
# Flask 配置
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=your-super-secret-key-change-this

# 数据库配置
MYSQL_HOST=db
MYSQL_PORT=3306
MYSQL_USER=asset_user
MYSQL_PASSWORD=your-secure-password
MYSQL_DATABASE=asset_management
MYSQL_ROOT_PASSWORD=your-root-password

# AI 配置
AI_PROVIDER=ollama
OLLAMA_API_BASE=http://host.docker.internal:11434/v1
OLLAMA_MODEL=qwen3.5:9B

# API Keys
AI_API_KEYS=["your-api-key"]
```

#### 步骤 2: 构建并启动服务

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

#### 步骤 3: 验证部署

```bash
# 检查服务状态
docker-compose ps

# 测试访问
curl http://localhost:5000
```

---

## 三、详细配置说明

### 1. 目录结构

```
d:/资产管理/
├── app/                    # 应用代码
├── data/                   # 数据目录（自动创建）
├── backup/                 # 备份目录（自动创建）
├── docker-compose.yml      # Docker Compose 配置
├── Dockerfile              # Docker 镜像构建文件
├── .env                    # 环境变量配置
├── .dockerignore           # Docker 忽略文件
├── init.sql                # 数据库初始化脚本
├── requirements.txt        # Python 依赖
└── deploy.sh               # 部署脚本
```

### 2. 端口说明

| 服务 | 容器端口 | 主机端口 | 说明 |
|------|----------|----------|------|
| Web | 5000 | 5000 | Web 应用 |
| MySQL | 3306 | 3308 | 数据库（避免与本地MySQL冲突） |

**修改端口映射**:

如果端口冲突，可以修改 `docker-compose.yml`:

```yaml
services:
  web:
    ports:
      - "8080:5000"  # 将 5000 改为 8080
```

### 3. 数据持久化

Docker 会创建一个名为 `mysql_data` 的 volume 来持久化数据库数据。

**查看 volumes**:
```bash
docker volume ls
```

**备份数据**:
```bash
# 导出数据库
docker exec asset-mysql mysqldump -u root -p asset_management > backup.sql
```

**恢复数据**:
```bash
# 导入数据库
docker exec -i asset-mysql mysql -u root -p asset_management < backup.sql
```

---

## 四、AI 功能配置

### 方案一：使用本地 Ollama（推荐）

1. **安装 Ollama**

   访问 [ollama.com](https://ollama.com) 下载安装

2. **启动 Ollama 服务**
   ```bash
   # Linux
   ollama serve

   # Windows/Mac: Ollama 会自动启动
   ```

3. **下载模型**
   ```bash
   ollama pull qwen2.5:7b
   # 或
   ollama pull llama3
   ```

4. **修改配置**

   `.env` 文件:
   ```env
   AI_PROVIDER=ollama
   OLLAMA_API_BASE=http://host.docker.internal:11434/v1
   OLLAMA_MODEL=qwen2.5:7b
   ```

### 方案二：使用 OpenAI API

`.env` 文件:
```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-api-key
OPENAI_MODEL=gpt-4o
```

### 方案三：使用 MiniMax API

`.env` 文件:
```env
AI_PROVIDER=minimax
MINIMAX_API_KEY=your-api-key
MINIMAX_MODEL=abab6.5-chat
```

---

## 五、常用操作命令

### 服务管理

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f web
docker-compose logs -f db
```

### 进入容器

```bash
# 进入 Web 容器
docker exec -it asset-management bash

# 进入 MySQL 容器
docker exec -it asset-mysql bash

# 连接 MySQL
docker exec -it asset-mysql mysql -u root -p
```

### 更新部署

```bash
# 拉取最新代码
git pull

# 重新构建镜像
docker-compose build --no-cache

# 重启服务
docker-compose down && docker-compose up -d
```

### 清理资源

```bash
# 停止并删除容器（保留数据）
docker-compose down

# 停止并删除容器和数据
docker-compose down -v

# 删除所有未使用的镜像
docker image prune -a

# 完全清理
docker system prune -a
```

---

## 六、故障排查

### 1. 服务无法启动

**检查日志**:
```bash
docker-compose logs web
docker-compose logs db
```

**常见原因**:
- 端口被占用 → 修改端口映射
- 内存不足 → 增加 Docker 内存限制
- 镜像拉取失败 → 检查网络或使用国内镜像

### 2. 数据库连接失败

**检查数据库状态**:
```bash
docker-compose ps db
docker exec asset-mysql mysqladmin ping -h localhost
```

**解决方案**:
```bash
# 重启数据库
docker-compose restart db

# 查看数据库日志
docker-compose logs db
```

### 3. AI 功能不工作

**检查 Ollama 服务**:
```bash
# 测试 Ollama 是否运行
curl http://localhost:11434/api/tags

# 查看 Ollama 日志
ollama logs
```

**解决方案**:
- 确保 Ollama 服务已启动
- 确保模型已下载
- 检查 `OLLAMA_API_BASE` 配置

### 4. 镜像构建失败

**检查网络**:
```bash
# 测试网络连接
ping mirrors.aliyun.com
```

**使用国内镜像源**:
- Dockerfile 已配置阿里云镜像源
- requirements.txt 使用阿里云 PyPI 镜像

### 5. 数据丢失

**恢复数据**:
```bash
# 从备份恢复
docker exec -i asset-mysql mysql -u root -p asset_management < backup.sql
```

---

## 七、性能优化

### 1. Docker 配置优化

编辑 Docker Desktop 设置:
- Memory: 4GB+
- CPU: 2+
- Swap: 2GB

### 2. 数据库优化

```sql
-- 添加索引
CREATE INDEX idx_emp_status ON employees_info(emp_status);
CREATE INDEX idx_emp_name ON employees_info(emp_name);
CREATE INDEX idx_dept_full_name ON employees_info(dept_full_name);
```

### 3. 应用优化

修改 `docker-compose.yml`:
```yaml
services:
  web:
    environment:
      - SQLALCHEMY_ENGINE_OPTIONS={"pool_size": 20, "max_overflow": 10}
```

---

## 八、安全建议

1. **修改默认密码**
   - 修改 `.env` 中的所有密码
   - 使用强密码

2. **限制网络访问**
   - 不要将数据库端口暴露到公网
   - 使用防火墙限制访问

3. **定期备份**
   ```bash
   # 创建备份脚本
   docker exec asset-mysql mysqldump -u root -p asset_management > backup_$(date +%Y%m%d).sql
   ```

4. **更新依赖**
   ```bash
   # 更新 Python 依赖
   pip install --upgrade -r requirements.txt
   
   # 重新构建镜像
   docker-compose build --no-cache
   ```

---

## 九、监控与日志

### 1. 查看实时日志

```bash
# 所有服务
docker-compose logs -f

# 特定服务
docker-compose logs -f web
```

### 2. 数据库监控 API

```bash
# 连接池状态
curl http://localhost:5000/api/db/status

# 健康检查
curl http://localhost:5000/api/db/health
```

### 3. 容器资源监控

```bash
# 查看资源使用
docker stats

# 查看特定容器
docker stats asset-management asset-mysql
```

---

## 十、附录

### Windows PowerShell 命令

```powershell
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### Linux/Systemd 服务（可选）

创建 `/etc/systemd/system/asset-management.service`:

```ini
[Unit]
Description=Asset Management Docker Services
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/path/to/资产管理
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
User=root

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable asset-management
sudo systemctl start asset-management
```

---

## 联系支持

如遇到问题，请提供以下信息:
1. 操作系统版本
2. Docker 版本 (`docker --version`)
3. 错误日志 (`docker-compose logs`)

---

**部署成功后访问**: http://localhost:5000