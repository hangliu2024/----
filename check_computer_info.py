#!/usr/bin/env python3
"""
检查computer_info表的结构和数据
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import app, db
from app.models import ComputerInfo, TangibleAsset

with app.app_context():
    try:
        # 检查表结构
        print("✅ 检查表结构:")
        table = ComputerInfo.__table__
        print(f"表名: {table.name}")
        print("列名:")
        for column in table.columns:
            print(f"  - {column.name}: {column.type}")
        
        # 检查数据
        print("\n✅ 检查数据:")
        computer_infos = ComputerInfo.query.all()
        if computer_infos:
            print(f"共找到 {len(computer_infos)} 条计算机信息记录")
            print("前5条记录:")
            for i, comp_info in enumerate(computer_infos[:5]):
                print(f"\n记录 {i+1}:")
                print(f"  id: {comp_info.id}")
                print(f"  asset_id: {comp_info.asset_id}")
                print(f"  network_address: {comp_info.network_address}")
                print(f"  ip_mac: {comp_info.ip_mac}")
                print(f"  operating_system: {comp_info.operating_system}")
                print(f"  last_login_user: {comp_info.last_login_user}")
                
                # 检查关联的资产
                asset = TangibleAsset.query.get(comp_info.asset_id)
                if asset:
                    print(f"  关联资产: {asset.name} (类别: {asset.category})")
                else:
                    print(f"  关联资产: 未找到 (asset_id: {comp_info.asset_id})")
        else:
            print("未找到计算机信息记录")
            
    except Exception as e:
        print(f"❌ 检查时出错：{e}")
