u
import sqlite3

conn = sqlite3.connect('instance/asset_management.db')
cursor = conn.cursor()

# 将personnel表重命名为employees_info
try:
    cursor.execute('ALTER TABLE personnel RENAME TO employees_info')
    conn.commit()
    print('已将 personnel 表重命名为 employees_info')
except Exception as e:
    print(f'重命名失败: {e}')

# 验证
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print('当前表:', [r[0] for r in cursor.fetchall()])

conn.close()