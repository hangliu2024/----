import sqlite3
conn = sqlite3.connect('instance/asset_management.db')
cursor = conn.cursor()

# 查看所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print('=== 所有表 ===')
for row in cursor.fetchall():
    print(row[0])

# 检查是否有employees_info表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='employees_info'")
if cursor.fetchone():
    print('\nemployees_info 表存在')
    cursor.execute('PRAGMA table_info(employees_info)')
    cols = cursor.fetchall()
    print('列:', [c[1] for c in cols[:15]])
    
    # 查询080217
    cursor.execute("""
        SELECT emp_id, emp_name, id_number, dept_full_name
        FROM employees_info 
        WHERE emp_id = '080217'
        LIMIT 5
    """)
    rows = cursor.fetchall()
    print('\n=== 工号080217 ===')
    for row in rows:
        print(f'工号: {row[0]}, 姓名: {row[1]}, 身份证: {row[2]}')
else:
    print('\nemployees_info 表不存在')

conn.close()