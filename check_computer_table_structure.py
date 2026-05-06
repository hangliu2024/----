#!/usr/bin/env python3
"""
检查computer_info表的完整结构
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import pymysql
from config import Config

# 使用pymysql直接连接数据库，获取表结构
connection = pymysql.connect(
    host=Config.DB_HOST,
    port=Config.DB_PORT,
    user=Config.DB_USER,
    password=Config.DB_PASSWORD,
    database=Config.DB_DATABASE,
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

try:
    with connection.cursor() as cursor:
        # 获取表结构
        cursor.execute("DESCRIBE computer_info")
        table_structure = cursor.fetchall()
        
        print("✅ computer_info表结构:")
        print("+-----------------+------------------+------+-----+---------+----------------+")
        print("| Field           | Type             | Null | Key | Default | Extra          |")
        print("+-----------------+------------------+------+-----+---------+----------------+")
        for field in table_structure:
            print(f"| {field['Field'].ljust(16)} | {field['Type'].ljust(17)} | {field['Null'].ljust(4)} | {field['Key'].ljust(3)} | {field['Default'] if field['Default'] is not None else 'NULL'.ljust(7)} | {field['Extra'].ljust(15)} |")
        print("+-----------------+------------------+------+-----+---------+----------------+")
        
        # 获取部分数据样本，查看实际内容
        cursor.execute("SELECT * FROM computer_info LIMIT 5")
        sample_data = cursor.fetchall()
        
        print("\n✅ 前5条数据样本:")
        for i, row in enumerate(sample_data):
            print(f"\n记录 {i+1}:")
            for field, value in row.items():
                print(f"  {field}: {value}")
                
finally:
    connection.close()
