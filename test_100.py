"""
测试更新前100条
"""
from app import app
from sqlalchemy import text

with app.app_context():
    from app import db
    
    print('=' * 80)
    print('测试更新100条')
    print('=' * 80)
    
    # 获取前100条需要更新的记录
    records = db.session.execute(text('''
        SELECT c.id, c.employee_id
        FROM computer_info c
        WHERE c.employee_id IS NOT NULL
          AND c.dept_code IS NULL
        LIMIT 100
    ''')).fetchall()
    
    print('\n找到 {} 条待更新记录'.format(len(records)))
    
    updated = 0
    for record_id, employee_id in records:
        result = db.session.execute(text('''
            SELECT dept_code, dept_level2, emp_name
            FROM employees_info
            WHERE emp_id = :emp_id
            LIMIT 1
        '''), {'emp_id': employee_id}).fetchone()
        
        if result:
            db.session.execute(text('''
                UPDATE computer_info
                SET dept_code = :dept_code,
                    dept_level2 = :dept_level2,
                    emp_name = :emp_name
                WHERE id = :id
            '''), {
                'dept_code': result[0],
                'dept_level2': result[1],
                'emp_name': result[2],
                'id': record_id
            })
            updated += 1
    
    db.session.commit()
    print('\n更新了 {} 条记录'.format(updated))
    
    # 显示结果
    samples = db.session.execute(text('''
        SELECT employee_id, dept_code, dept_level2, emp_name
        FROM computer_info
        WHERE dept_code IS NOT NULL
        LIMIT 5
    ''')).fetchall()
    
    print('\n样例数据:')
    for row in samples:
        print('  工号: {:<10} | 部门: {:<15} | 二级: {:<20} | 姓名: {}'.format(
            str(row[0])[:9], str(row[1])[:14], str(row[2])[:19], str(row[3])[:10]
        ))
    
    print('\n[OK] 完成!')
    print('=' * 80)