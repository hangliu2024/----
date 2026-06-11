# 生产环境部署指南

本文档提供资产管理系统的生产环境部署方案。

---

## 目录

1. [部署方式选择](#部署方式选择)
2. [Docker部署（推荐）](#docker部署推荐)
3. [传统部署](#传统部署)
4. [Nginx配置](#nginx配置)
5. [安全加固](#安全加固)
6. [监控与日志](#监控与日志)

---

## 部署方式选择

| 方式 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| Docker | 环境一致、易于扩展 | 需要学习Docker | 推荐，适合大多数场景 |
| 传统部署 | 简单直接 | 环境配置复杂 | 小型部署 |
| Kubernetes | 高可用、自动扩展 | 运维复杂 | 大规模生产环境 |

---

## Docker部署（推荐）

### 1. 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少 2GB 内存
- 至少 10GB 磁盘空间

### 2. 部署步骤

```bash
# 1. 克隆代码
git clone <your-repo-url>
cd 资产管理

# 2. 创建生产环境配置
cp .env .env.production

# 3. 编辑配置文件
# 修改以下关键配置：
```

### 3. 生产环境配置文件

创建 `.env.production`:

```env
# Flask配置
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=your-super-secret-key-change-this-in-production

# 数据库配置
MYSQL_HOST=db
MYSQL_PORT=3306
MYSQL_USER=asset_user
MYSQL_PASSWORD=your-secure-password
MYSQL_DATABASE=asset_management

# AI配置（选择一个）
AI_PROVIDER=ollama
OLLAMA_API_BASE=http://ollama:11434/v1
OLLAMA_MODEL=llama3

# API Key（用于外部调用）
AI_API_KEYS=["your-api-key-1", "your-api-key-2"]
```

### 4. 创建生产环境的 docker-compose

创建 `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  # MySQL数据库
  db:
    image: mysql:8.0
    container_name: asset_mysql
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD:-root_password}
      MYSQL_DATABASE: ${MYSQL_DATABASE:-asset_management}
      MYSQL_USER: ${MYSQL_USER:-asset_user}
      MYSQL_PASSWORD: ${MYSQL_PASSWORD:-your_password}
    volumes:
      - mysql_data:/var/lib/mysql
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "3306:3306"
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - asset_network

  # Web应用
  web:
    image: asset-management:latest
    container_name: asset_web
    restart: always
    build: .
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
      - MYSQL_HOST=db
      - MYSQL_PORT=3306
      - MYSQL_USER=${MYSQL_USER}
      - MYSQL_PASSWORD=${MYSQL_PASSWORD}
      - MYSQL_DATABASE=${MYSQL_DATABASE}
    ports:
      - "5000:5000"
    depends_on:
      db:
        condition: service_healthy
    networks:
      - asset_network

  # Nginx反向代理（可选）
  nginx:
    image: nginx:alpine
    container_name: asset_nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
    networks:
      - asset_network

  # Redis缓存（可选，提升性能）
  redis:
    image: redis:alpine
    container_name: asset_redis
    restart: always
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - asset_network

networks:
  asset_network:
    driver: bridge

volumes:
  mysql_data:
  redis_data:
```

### 5. 启动服务

```bash
# 构建镜像
docker-compose -f docker-compose.prod.yml build

# 启动服务
docker-compose -f docker-compose.prod.yml up -d

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f

# 初始化数据库（首次部署）
docker-compose -f docker-compose.prod.yml exec web python db_init.py
```

---

## 传统部署

### 1. 系统要求

- Ubuntu 20.04+ / CentOS 7+
- Python 3.9+
- MySQL 8.0+
- 2GB+ 内存

### 2. 安装依赖

```bash
# Ubuntu
sudo apt update
sudo apt install python3-pip python3-venv mysql-server nginx -y

# CentOS
sudo yum install python3-pip mysql-server nginx -y
```

### 3. 创建应用用户

```bash
sudo useradd -m -s /bin/bash asset
sudo su - asset
```

### 4. 部署代码

```bash
# 克隆代码
git clone <your-repo> /home/asset/asset-management
cd /home/asset/asset-management

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装 Gunicorn
pip install gunicorn
```

### 5. 配置 Gunicorn

创建 `gunicorn.conf.py`:

```python
# gunicorn.conf.py
import multiprocessing

# 服务器绑定
bind = "127.0.0.1:5000"

# 工作进程数（推荐 2-4 * CPU核心数）
workers = multiprocessing.cpu_count() * 2 + 1

# 每个工作进程的线程数
threads = 2

# 工作模式
worker_class = "sync"

# 超时时间
timeout = 120

# 最大请求数后重启
max_requests = 1000
max_requests_jitter = 100

# 守护进程
daemon = False

# 日志
accesslog = "/home/asset/logs/access.log"
errorlog = "/home/asset/logs/error.log"
loglevel = "info"

# 进程ID文件
pidfile = "/home/asset/gunicorn.pid"
```

### 6. 创建 Systemd 服务

创建 `/etc/systemd/system/asset-management.service`:

```ini
[Unit]
Description=Asset Management System
After=network.target mysql.service

[Service]
User=asset
Group=asset
WorkingDirectory=/home/asset/asset-management
Environment="PATH=/home/asset/asset-management/venv/bin"
Environment="FLASK_ENV=production"
Environment="SECRET_KEY=your-secret-key"
ExecStart=/home/asset/asset-management/venv/bin/gunicorn -c gunicorn.conf.py "app:create_app()"
ExecReload=/bin/kill -s HUP $MAINPID
ExecStop=/bin/kill -s TERM $MAINPID
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

启动服务:

```bash
sudo systemctl daemon-reload
sudo systemctl enable asset-management
sudo systemctl start asset-management
sudo systemctl status asset-management
```

---

## Nginx配置

### 1. 创建 Nginx 配置

创建 `/etc/nginx/sites-available/asset-management`:

```nginx
# HTTP 重定向到 HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS 配置
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL证书（使用 Let's Encrypt）
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # SSL配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1d;

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # 静态文件缓存
    location /static {
        alias /home/asset/asset-management/app/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # 代理到 Gunicorn
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时配置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # 缓冲配置
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }

    # 文件上传限制
    client_max_body_size 50M;

    # 日志
    access_log /var/log/nginx/asset_access.log;
    error_log /var/log/nginx/asset_error.log;
}
```

### 2. 启用配置

```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/asset-management /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重载 Nginx
sudo systemctl reload nginx
```

### 3. 配置 SSL (Let's Encrypt)

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

---

## 安全加固

### 1. 防火墙配置

```bash
# Ubuntu (UFW)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# CentOS (Firewalld)
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 2. MySQL安全配置

```bash
sudo mysql_secure_installation
```

创建专用数据库用户:

```sql
CREATE USER 'asset_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, INDEX ON asset_management.* TO 'asset_user'@'localhost';
FLUSH PRIVILEGES;
```

### 3. 修改默认配置

在 `config.py` 中:

```python
class ProductionConfig:
    DEBUG = False
    TESTING = False
    
    # 安全密钥（从环境变量读取）
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Session安全
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # CSRF保护
    WTF_CSRF_ENABLED = True
    
    # 连接池配置
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'max_overflow': 10,
        'pool_pre_ping': True,
        'pool_recycle': 3600
    }
```

---

## 监控与日志

### 1. 日志配置

创建日志目录:

```bash
sudo mkdir -p /var/log/asset-management
sudo chown asset:asset /var/log/asset-management
```

### 2. 日志轮转

创建 `/etc/logrotate.d/asset-management`:

```
/var/log/asset-management/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 asset asset
    sharedscripts
    postrotate
        systemctl reload asset-management > /dev/null 2>&1 || true
    endscript
}
```

### 3. 监控数据库连接池

访问监控API:

```bash
# 连接池状态
curl http://localhost:5000/api/db/status

# 健康检查
curl http://localhost:5000/api/db/health

# 性能统计
curl http://localhost:5000/api/db/stats
```

### 4. 使用 Prometheus + Grafana (可选)

在 `docker-compose.prod.yml` 中添加:

```yaml
  prometheus:
    image: prom/prometheus
    container_name: asset_prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    container_name: asset_grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

---

## 常用运维命令

```bash
# Docker部署
docker-compose -f docker-compose.prod.yml up -d        # 启动服务
docker-compose -f docker-compose.prod.yml down         # 停止服务
docker-compose -f docker-compose.prod.yml logs -f      # 查看日志
docker-compose -f docker-compose.prod.yml restart web  # 重启Web服务

# 传统部署
sudo systemctl start asset-management     # 启动
sudo systemctl stop asset-management      # 停止
sudo systemctl restart asset-management   # 重启
sudo systemctl status asset-management    # 查看状态

# 数据库备份
docker exec asset_mysql mysqldump -u root -p asset_management > backup.sql
mysqldump -u asset_user -p asset_management > backup.sql

# 数据库恢复
docker exec -i asset_mysql mysql -u root -p asset_management < backup.sql
mysql -u asset_user -p asset_management < backup.sql
```

---

## 性能优化建议

### 1. 数据库优化

```sql
-- 添加必要的索引
CREATE INDEX idx_emp_status ON employees_info(emp_status);
CREATE INDEX idx_emp_name ON employees_info(emp_name);
CREATE INDEX idx_dept_full_name ON employees_info(dept_full_name);
CREATE INDEX idx_computer_emp_name ON computer_info(emp_name);
```

### 2. Gunicorn 配置优化

```python
# 根据服务器配置调整
workers = 4           # 2-4 * CPU核心数
threads = 2           # 每个worker的线程数
worker_class = "sync" # 或使用 "gevent" 提升并发
timeout = 120         # 超时时间
keepalive = 5         # 保持连接时间
```

### 3. 连接池配置

在 `config.py` 中:

```python
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 20,        # 连接池大小
    'max_overflow': 10,     # 最大溢出连接数
    'pool_pre_ping': True,  # 健康检查
    'pool_recycle': 3600,   # 连接回收时间
    'echo': False           # 生产环境关闭SQL日志
}
```

---

## 故障排查

### 常见问题

1. **服务无法启动**
   - 检查端口是否被占用: `netstat -tlnp | grep 5000`
   - 检查日志: `docker-compose logs web` 或 `journalctl -u asset-management`

2. **数据库连接失败**
   - 检查MySQL是否运行: `docker-compose ps` 或 `systemctl status mysql`
   - 检查连接配置是否正确
   - 检查防火墙是否阻止连接

3. **页面加载缓慢**
   - 检查数据库连接池状态: `curl http://localhost:5000/api/db/status`
   - 检查服务器资源使用: `top` 或 `htop`
   - 检查Nginx配置是否正确

4. **AI功能异常**
   - 检查Ollama服务是否运行
   - 检查网络连接是否正常
   - 查看应用日志排查错误

---

## 联系支持

如遇到问题，请查看:
- 项目文档: `项目开发日志.md`
- 部署文档: `DOCKER_DEPLOY.md`
- 或者联系开发团队
