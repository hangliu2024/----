#!/usr/bin/env python3
"""
检查tangible_asset表的结构和数据
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import app, db
from app.models import TangibleAsset

with app.app_context():
    try:
        # 使用SQLAlchemy获取表结构
        table = TangibleAsset.__table__
        print("✅ TangibleAsset模型定义的表结构:")
        print(f"表名: {table.name}")
        print("字段:")
        for column in table.columns:
            print(f"  - {column.name}: {column.type} (nullable: {column.nullable})")
        
        # 获取部分数据样本
        print("\n✅ 前5条数据样本:")
        tangible_assets = TangibleAsset.query.limit(5).all()
        for i, asset in enumerate(tangible_assets):
            print(f"\n记录 {i+1}:")
            print(f"  id: {asset.id}")
            print(f"  name: {asset.name}")
            print(f"  category: {asset.category}")
            print(f"  value: {asset.value}")
            print(f"  purchase_date: {asset.purchase_date}")
            print(f"  location: {asset.location}")
            print(f"  status: {asset.status}")
            print(f"  assigned_to: {asset.assigned_to}")
            print(f"  description: {asset.description}")
        
    except Exception as e:
        print(f"❌ 检查时出错：{e}")
