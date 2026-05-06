from app import app, db
from sqlalchemy import inspect

with app.app_context():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print('=== 数据库表结构 ===\n')
    for t in sorted(tables):
        print(f'表名: {t}')
        columns = inspector.get_columns(t)
        for col in columns:
            nullable = '可空' if col['nullable'] else '非空'
            default = f", 默认:{col.get('default')}" if col.get('default') else ''
            print(f"  - {col['name']}: {col['type']} ({nullable}{default})")
        print()
        
    # 查看一些示例数据
    print('\n=== 示例数据 ===\n')
    
    # employees_info表
    try:
        result = db.session.execute(db.text('SELECT * FROM employees_info LIMIT 2'))
        rows = result.fetchall()
        if rows:
            print('employees_info 示例:')
            for row in rows:
                print(f'  {dict(row._mapping)}')
    except Exception as e:
        print(f'employees_info 查询失败: {e}')
    
    # computer_info表
    try:
        result = db.session.execute(db.text('SELECT * FROM computer_info LIMIT 2'))
        rows = result.fetchall()
        if rows:
            print('\ncomputer_info 示例:')
            for row in rows:
                print(f'  {dict(row._mapping)}')
    except Exception as e:
        print(f'computer_info 查询失败: {e}')
    
    # departments表
    try:
        result = db.session.execute(db.text('SELECT * FROM departments LIMIT 3'))
        rows = result.fetchall()
        if rows:
            print('\ndepartments 示例:')
            for row in rows:
                print(f'  {dict(row._mapping)}')
    except Exception as e:
        print(f'departments 查询失败: {e}')