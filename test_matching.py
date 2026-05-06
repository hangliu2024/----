"""
测试工号匹配 - 快速检查匹配情况
"""
from app import app
from sqlalchemy import text

with app.app_context():
    from app import db
    
    print('=' * 80)
    print('工号匹配测试')
    print('=' * 80)
    
    # 1. 统计总览
    print('\n[1] 数据总览')
    
    total_computer = db.session.execute(text('''
        SELECT COUNT(*) FROM computer_info WHERE employee_id IS NOT NULL
    ''')).scalar()
    
    total_employee = db.session.execute(text('''
        SELECT COUNT(*) FROM employees_info WHERE emp_id IS NOT NULL
    ''')).scalar()
    
    print('  computer_info 有工号的记录: {}'.format(total_computer))
    print('  employees_info 有员工ID的记录: {}'.format(total_employee))
    
    # 2. 匹配测试（前20条）
    print('\n[2] 匹配测试（前20条）')
    print('-' * 80)
    
    samples = db.session.execute(text('''
        SELECT 
            c.id,
            c.employee_id,
            e.emp_id,
            e.emp_name,
            e.dept_code,
            e.dept_level2
        FROM computer_info c
        LEFT JOIN employees_info e ON c.employee_id = e.emp_id
        WHERE c.employee_id IS NOT NULL
        LIMIT 20
    '''))
    
    matched = 0
    unmatched = 0
    
    print('{:<5} | {:<12} | {:<12} | {:<10} | {:<15} | {}'.format(
        'ID', '工号', '员工ID', '姓名', '部门代码', '状态'
    ))
    print('-' * 80)
    
    for row in samples:
        emp_id = row[2]
        status = '匹配' if emp_id else '未匹配'
        if emp_id:
            matched += 1
        else:
            unmatched += 1
            
        print('{:<5} | {:<12} | {:<12} | {:<10} | {:<15} | {}'.format(
            row[0],
            str(row[1])[:11],
            str(emp_id if emp_id else '-')[:11],
            str(row[3] if row[3] else '-')[:9],
            str(row[4] if row[4] else '-')[:14],
            status
        ))
    
    print('\n  匹配: {} 条'.format(matched))
    print('  未匹配: {} 条'.format(unmatched))
    
    # 3. 统计总体匹配率
    print('\n[3] 总体匹配统计')
    
    result = db.session.execute(text('''
        SELECT 
            SUM(CASE WHEN e.emp_id IS NOT NULL THEN 1 ELSE 0 END) as matched,
            SUM(CASE WHEN e.emp_id IS NULL THEN 1 ELSE 0 END) as unmatched
        FROM computer_info c
        LEFT JOIN employees_info e ON c.employee_id = e.emp_id
        WHERE c.employee_id IS NOT NULL
    ''')).fetchone()
    
    print('  匹配: {} 条 ({:.1f}%)'.format(
        result[0], result[0] * 100.0 / total_computer if total_computer > 0 else 0
    ))
    print('  未匹配: {} 条 ({:.1f}%)'.format(
        result[1], result[1] * 100.0 / total_computer if total_computer > 0 else 0
    ))
    
    print('\n' + '=' * 80)
    print('测试完成!')
    print('=' * 80)