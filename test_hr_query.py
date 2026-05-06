from app import app, db
from sqlalchemy import text

with app.app_context():
    # 检查人力资源相关的部门
    result = db.session.execute(text("""
        SELECT dept_full_name, COUNT(*) as cnt 
        FROM employees_info 
        WHERE emp_status = '在职' 
        AND (dept_full_name LIKE '%人力资源%' OR dept_full_name LIKE '%保卫%')
        GROUP BY dept_full_name
        ORDER BY cnt DESC
        LIMIT 20
    """))
    print('=== 人力资源和保卫相关部门 ===')
    for row in result:
        print(f'{row[0]}: {row[1]}人')
    
    # 检查保卫部
    result2 = db.session.execute(text("""
        SELECT dept_full_name, COUNT(*) as cnt 
        FROM employees_info 
        WHERE emp_status = '在职' 
        AND dept_full_name LIKE '%保卫部%'
        GROUP BY dept_full_name
        ORDER BY cnt DESC
        LIMIT 10
    """))
    print('\n=== 保卫部 ===')
    for row in result2:
        print(f'{row[0]}: {row[1]}人')
    
    # 测试组合查询
    result3 = db.session.execute(text("""
        SELECT COUNT(*) as cnt 
        FROM employees_info 
        WHERE emp_status = '在职' 
        AND dept_full_name LIKE '%人力资源%' 
        AND dept_full_name LIKE '%保卫部%'
    """))
    print('\n=== 人力资源中心保卫部人数 ===')
    for row in result3:
        print(f'人数: {row[0]}')