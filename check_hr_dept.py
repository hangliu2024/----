"""检查人力资源保卫部相关数据"""
from app import app, db

with app.app_context():
    # 查找包含'人力资源'的部门
    print('=== 包含"人力资源"的部门 ===')
    result = db.session.execute(db.text("""
        SELECT DISTINCT dept_full_name, company_dept, first_level_dept_abbr 
        FROM employees_info 
        WHERE dept_full_name LIKE '%人力资源%' OR company_dept LIKE '%人力资源%'
        LIMIT 20
    """))
    for row in result:
        print(f'  dept_full_name: {row[0]}')
        print(f'  company_dept: {row[1]}')
        print(f'  first_level_dept_abbr: {row[2]}')
        print()
    
    # 查找包含'保卫'的部门
    print('\n=== 包含"保卫"的部门 ===')
    result = db.session.execute(db.text("""
        SELECT DISTINCT dept_full_name, company_dept 
        FROM employees_info 
        WHERE dept_full_name LIKE '%保卫%' OR company_dept LIKE '%保卫%'
        LIMIT 20
    """))
    for row in result:
        print(f'  dept_full_name: {row[0]}')
        print(f'  company_dept: {row[1]}')
        print()