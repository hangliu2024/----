"""
检查前20条记录的数据
"""
from app import app
from sqlalchemy import text

with app.app_context():
    from app import db
    
    print('=' * 80)
    print('检查前20条记录')
    print('=' * 80)
    
    samples = db.session.execute(text('''
        SELECT c.id, c.employee_id, c.computer_name, e.emp_id, e.emp_name, e.dept_code, e.dept_level2
        FROM computer_info c
        LEFT JOIN employees_info e ON c.employee_id = e.emp_id
        LIMIT 20
    '''))
    
    print('{:<5} | {:<15} | {:<25} | {:<15} | {:<20}'.format(
        'ID', '工号', '电脑名称', '员工ID', '部门代码'
    ))
    print('-' * 100)
    
    for row in samples:
        print('{:<5} | {:<15} | {:<25} | {:<15} | {:<20}'.format(
            row[0],
            str(row[1])[:14] if row[1] else '[无]',
            str(row[2])[:24] if row[2] else '[无]',
            str(row[3])[:14] if row[3] else '[无]',
            str(row[4])[:19] if row[4] else '[无]'
        ))
    
    print('\n' + '=' * 80)