#!/usr/bin/env python3
"""
检查人员表中emp_status字段的不同值
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import app, db
from app.models import Personnel

with app.app_context():
    try:
        # 查询所有不同的emp_status值及其数量
        print("✅ 员工状态分布:")
        
        # 获取所有人员记录
        all_personnel = Personnel.query.all()
        
        # 统计状态分布
        status_counts = {}
        for person in all_personnel:
            status = person.emp_status or '未设置'
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # 打印结果
        for status, count in status_counts.items():
            print(f"  - {status}: {count} 人")
        
        print(f"\n✅ 总人数: {len(all_personnel)} 人")
        
    except Exception as e:
        print(f"❌ 检查时出错：{e}")
