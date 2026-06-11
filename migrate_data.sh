#!/bin/bash

# ============================================
# 数据迁移脚本 - 从本地MySQL迁移到Docker MySQL
# ============================================

echo "============================================"
echo "     数据迁移：本地MySQL -> Docker MySQL"
echo "============================================"
echo ""

# 本地MySQL配置
LOCAL_HOST="127.0.0.1"
LOCAL_PORT="3307"
LOCAL_USER="nocobase"
LOCAL_PASS="nocobase"
LOCAL_DB="nocobase"

# Docker MySQL配置
DOCKER_CONTAINER="asset-mysql"
DOCKER_USER="nocobase"
DOCKER_PASS="nocobase"
DOCKER_DB="nocobase"

# 备份文件名
BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"

echo "步骤 1: 从本地MySQL导出数据..."
echo "  主机: $LOCAL_HOST:$LOCAL_PORT"
echo "  数据库: $LOCAL_DB"
echo ""

# 检查mysqldump是否可用
if ! command -v mysqldump &> /dev/null; then
    echo "错误: mysqldump 未安装"
    echo "请安装 MySQL 客户端工具"
    exit 1
fi

# 导出数据
mysqldump -h $LOCAL_HOST -P $LOCAL_PORT -u $LOCAL_USER -p$LOCAL_PASS $LOCAL_DB > $BACKUP_FILE

if [ $? -ne 0 ]; then
    echo "错误: 数据导出失败"
    exit 1
fi

echo "数据导出成功: $BACKUP_FILE"
echo ""

echo "步骤 2: 导入数据到Docker MySQL..."
echo "  容器: $DOCKER_CONTAINER"
echo "  数据库: $DOCKER_DB"
echo ""

# 导入数据
docker exec -i $DOCKER_CONTAINER mysql -u $DOCKER_USER -p$DOCKER_PASS $DOCKER_DB < $BACKUP_FILE

if [ $? -ne 0 ]; then
    echo "错误: 数据导入失败"
    exit 1
fi

echo "数据导入成功！"
echo ""

# 清理
echo "清理临时文件..."
rm -f $BACKUP_FILE

echo ""
echo "============================================"
echo "           数据迁移完成！"
echo "============================================"