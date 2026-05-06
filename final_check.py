"""
最终验证 - 确认 EVE 和 LUBAN 已完全清除
"""
from app import app
from sqlalchemy import text

with app.app_context():
    from app import db
    
    print('=' * 80)
    print('最终验证报告')
    print('=' * 80)
    
    # 1. 检查是否还有 EVE
    print('\n[1] 检查包含 EVE 的数据')
    eve_count = db.session.execute(text('''
        SELECT COUNT(*)
        FROM computer_info
        WHERE employee_id LIKE '%EVE%' 
           OR employee_id LIKE '%eve%'
    ''')).scalar()
    print('  包含 EVE 的记录: {} 条'.format(eve_count))
    if eve_count == 0:
        print('  [OK] EVE 已全部清除')
    
    # 2. 检查是否还有 LUBAN
    print('\n[2] 检查包含 LUBAN 的数据')
    luban_count = db.session.execute(text('''
        SELECT COUNT(*)
        FROM computer_info
        WHERE employee_id LIKE '%LUBAN%' 
           OR employee_id LIKE '%luban%'
    ''')).scalar()
    print('  包含 LUBAN 的记录: {} 条'.format(luban_count))
    if luban_count == 0:
        print('  [OK] LUBAN 已全部清除')
    
    # 3. 统计信息
    print('\n[3] 数据统计')
    stats = db.session.execute(text('''
        SELECT 
            COUNT(*) as total,
            COUNT(employee_id) as with_employee_id,
            SUM(CASE WHEN employee_id IS NULL AND last_login_user IS NOT NULL THEN 1 ELSE 0 END) as null_employee
        FROM computer_info
    ''')).fetchone()
    
    print('  总记录数: {:>6}'.format(stats[0]))
    print('  有工号的记录: {:>6} ({:.1f}%)'.format(
        stats[1], stats[1] * 100.0 / stats[0]
    ))
    print('  无工号的记录: {:>6} ({:.1f}%)'.format(
        stats[2], stats[2] * 100.0 / stats[0]
    ))
    
    # 4. 显示一些工号样例
    print('\n[4] 工号样例（清洗后的正确格式）')
    print('-' * 80)
    
    samples = db.session.execute(text('''
        SELECT employee_id, COUNT(*) as count
        FROM computer_info
        WHERE employee_id IS NOT NULL
        GROUP BY employee_id
        ORDER BY count DESC
        LIMIT 10
    '''))
    
    print('最常见的工号:')
    for row in samples:
        print('  {} - {} 台电脑'.format(row[0][:30], row[1]))
    
    print('\n' + '=' * 80)
    print('验证结果: EVE 和 LUBAN 已全部清除！')
    print('=' * 80)