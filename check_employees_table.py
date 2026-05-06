import sqlite3
import os

db_path = 'instance/asset_management.db'
print(f'数据库文件存在: {os.path.exists(db_path)}')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 列出所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cursor.fetchall()
print('\n所有表:')
for t in tables:
    print(f'  - {t[0]}')

# 检查是否有employees_info
table_names = [t[0] for t in tables]
print(f'\nemployees_info 在表中: {"employees_info" in table_names}')

# 如果存在，查询080217
if 'employees_info' in table_names:
    cursor.execute("SELECT emp_id, emp_name, id_number FROM employees_info WHERE emp_id = '080217' LIMIT 5")
    rows = cursor.fetchall()
    print('\n工号080217的员工:')
    for row in rows:
        print(f'  工号: {row[0]}, 姓名: {row[1]}, 身份证: {row[2]}')

conn.close()