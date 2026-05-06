"""
检查更新状态
"""
from app import app
from sqlalchemy import text

with app.app_context():
    from app import db
    
    print('=' * 80)
    print('部门信息更新状态')
    print('=' * 80)
    
    # 统计
    result = db.session.execute(text('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN dept_code IS NOT NULL THEN 1 ELSE 0 END) as updated,
            SUM(CASE WHEN employee_id IS NOT NULL AND dept_code IS NULL THEN 1 ELSE 0 END) as pending
        FROM computer_info
        WHERE employee_id IS NOT NULL
    ''')).fetchone()
    
    print('\n统计:')
    print('  总计: {} 条'.format(result[0]))
    print('  已更新: {} 条 ({:.1f}%)'.format(result[1], result[1] * 100.0 / result[0] if result[0] > 0 else 0))
    print('  待更新: {} 条 ({:.1f}%)'.format(result[2], result[2] * 100.0 / result[0] if result[0] > 0 else 0))
    
    # 样例
    print('\n最新更新的数据:')
    print('-' * 100)
    
    samples = db.session.execute(text('''
        SELECT employee_id, computer_name, dept_code, dept_level2, emp_name
        FROM computer_info
        WHERE dept_code IS NOT NULL
        ORDER BY id DESC
        LIMIT 10
    '''))
    
    print('{:<12} | {:<25} | {:<12} | {:<20} | {}'.format(
        '工号', '电脑名称', '部门代码', '二级部门', '姓名'
    ))
    print('-' * 100)
    
    for row in samples:
        print('{:<12} | {:<25} | {:<12} | {:<20} | {}'.format(
            str(row[0])[:11],
            str(row[1])[:24],
            str(row[2])[:11],
            str(row[3])[:19],
            str(row[4])[:10]
        ))
    
    print('\n' + '=' * 80)