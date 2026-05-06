#!/usr/bin/env python3
"""
数据库初始化脚本：创建computer_info表
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import app, db
from app.models import ComputerInfo

with app.app_context():
    try:
        # 创建表（如果不存在）
        db.create_all()
        print("✅ computer_info表创建成功！")
        print("表结构：")
        print("- id: 主键，自增整数")
        print("- asset_id: 外键，关联tangible_asset表的id")
        print("- network_address: 网络地址")
        print("- ip_mac: IP/MAC地址")
        print("- operating_system: 操作系统")
        print("- last_login_user: 最后登录用户")
    except Exception as e:
        print(f"❌ 创建表时出错：{e}")
        print("请确保数据库连接正确，并且tangible_asset表已存在。")
