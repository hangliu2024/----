#!/bin/bash

# ============================================
# 资产管理系统 - Docker 本机部署脚本
# ============================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 打印标题
print_banner() {
    echo ""
    echo "============================================"
    echo "     资产管理系统 - Docker 本机部署"
    echo "============================================"
    echo ""
}

# 检查 Docker 是否安装
check_docker() {
    log_info "检查 Docker 是否安装..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        log_info "安装 Docker 请参考: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    log_success "Docker 已安装"
    docker --version
}

# 检查 Docker 服务是否运行
check_docker_running() {
    log_info "检查 Docker 服务状态..."
    
    if ! docker info &> /dev/null; then
        log_error "Docker 服务未运行，请启动 Docker"
        log_info "Linux: sudo systemctl start docker"
        log_info "Windows/Mac: 启动 Docker Desktop"
        exit 1
    fi
    
    log_success "Docker 服务正常运行"
}

# 检查端口占用
check_ports() {
    log_info "检查端口占用..."
    
    # 检查 5000 端口
    if netstat -tuln 2>/dev/null | grep -q ":5000 " || ss -tuln 2>/dev/null | grep -q ":5000 "; then
        log_warn "端口 5000 已被占用"
        log_info "可以修改 docker-compose.yml 中的端口映射"
    else
        log_success "端口 5000 可用"
    fi
    
    # 检查 3308 端口（MySQL映射端口）
    if netstat -tuln 2>/dev/null | grep -q ":3308 " || ss -tuln 2>/dev/null | grep -q ":3308 "; then
        log_warn "端口 3308 已被占用"
    else
        log_success "端口 3308 可用"
    fi
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    
    mkdir -p data
    mkdir -p backup
    
    log_success "目录创建完成"
}

# 配置环境变量
setup_env() {
    log_info "配置环境变量..."
    
    # 生成随机密钥
    SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 64 | head -n 1)
    
    # 创建 .env 文件
    cat > .env << EOF
# ============================================
# 资产管理系统 - 环境配置
# ============================================

# Flask 配置
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=${SECRET_KEY}

# 数据库配置
MYSQL_HOST=db
MYSQL_PORT=3306
MYSQL_USER=asset_user
MYSQL_PASSWORD=asset_password_$(date +%s)
MYSQL_DATABASE=asset_management
MYSQL_ROOT_PASSWORD=root_password_$(date +%s)

# AI 配置
AI_PROVIDER=ollama
OLLAMA_API_BASE=http://host.docker.internal:11434/v1
OLLAMA_MODEL=qwen3.5:9B

# API Keys（用于外部API调用）
AI_API_KEYS=["asset-api-key-$(date +%s)"]
EOF
    
    log_success "环境变量配置完成，已保存到 .env 文件"
}

# 构建 Docker 镜像
build_image() {
    log_info "构建 Docker 镜像..."
    
    # 检查是否使用国内镜像源
    if [ "$USE_CN_MIRROR" = "true" ]; then
        log_info "使用国内镜像源加速..."
    fi
    
    docker-compose build --no-cache
    
    log_success "镜像构建完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    docker-compose up -d
    
    log_info "等待服务启动..."
    sleep 10
    
    log_success "服务启动完成"
}

# 检查服务状态
check_status() {
    log_info "检查服务状态..."
    
    docker-compose ps
    
    echo ""
    
    # 检查 Web 服务
    if curl -s http://localhost:5000 > /dev/null 2>&1; then
        log_success "Web 服务正常运行"
    else
        log_warn "Web 服务可能还在启动中，请稍后检查"
    fi
}

# 显示部署信息
show_info() {
    echo ""
    echo "============================================"
    echo "           部署完成！"
    echo "============================================"
    echo ""
    echo "访问地址:"
    echo "  - Web 界面: http://localhost:5000"
    echo "  - API 文档: http://localhost:5000/api/v1/schema"
    echo ""
    echo "数据库连接:"
    echo "  - 主机: localhost"
    echo "  - 端口: 3308"
    echo "  - 用户名: asset_user"
    echo "  - 密码: 查看 .env 文件"
    echo ""
    echo "常用命令:"
    echo "  - 查看日志: docker-compose logs -f"
    echo "  - 停止服务: docker-compose down"
    echo "  - 重启服务: docker-compose restart"
    echo ""
    echo "配置文件: .env"
    echo "============================================"
}

# 主流程
main() {
    print_banner
    
    # 解析参数
    USE_CN_MIRROR="false"
    SKIP_BUILD="false"
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --cn-mirror)
                USE_CN_MIRROR="true"
                shift
                ;;
            --skip-build)
                SKIP_BUILD="true"
                shift
                ;;
            --help)
                echo "用法: ./deploy.sh [选项]"
                echo ""
                echo "选项:"
                echo "  --cn-mirror    使用国内镜像源加速"
                echo "  --skip-build   跳过镜像构建"
                echo "  --help         显示帮助信息"
                exit 0
                ;;
            *)
                log_error "未知参数: $1"
                exit 1
                ;;
        esac
    done
    
    # 执行部署步骤
    check_docker
    check_docker_running
    check_ports
    create_directories
    setup_env
    
    if [ "$SKIP_BUILD" = "false" ]; then
        build_image
    else
        log_warn "跳过镜像构建"
    fi
    
    start_services
    check_status
    show_info
}

# 运行主流程
main "$@"