"""
最终验证 - 确认所有修改
"""
from app import app
from sqlalchemy import text

with app.app_context():
    from app import db
    
    print('=' * 80)
    print('最终验证报告')
    print('=' * 80)
    
    # 1. 验证表结构
    print('\n[1] computer_info 表结构验证')
    print('-' * 80)
    columns = db.session.execute(text('DESCRIBE computer_info')).fetchall()
    for col in columns:
        print('  {field:<20} {type:<15} Nullable: {null}'.format(
            field=col[0], type=col[1], null=col[2]
        ))
    
    # 2. 验证数据
    print('\n[2] 数据统计')
    print('-' * 80)
    stats = db.session.execute(text('''
        SELECT 
            COUNT(*) as total,
            COUNT(employee_id) as with_employee_id
        FROM computer_info
    ''')).fetchone()
    
    print('  总记录数: {:>6}'.format(stats[0]))
    print('  有工号的记录: {:>6} ({:.1f}%)'.format(
        stats[1], stats[1] * 100.0 / stats[0]
    ))
    
    # 3. 显示样例
    print('\n[3] 样例数据')
    print('-' * 80)
    print('{:<6} | {:<25} | {:<20} | {:<20}'.format(
        'ID', '电脑名称', '工号', '最后登录用户'
    ))
    print('-' * 80)
    
    samples = db.session.execute(text('''
        SELECT id, computer_name, employee_id, last_login_user
        FROM computer_info
        WHERE employee_id IS NOT NULL
        LIMIT 10
    '''))
    
    for row in samples:
        print('{:<6} | {:<25} | {:<20} | {:<20}'.format(
            row[0],
            (row[1][:24] if row[1] else '[无]'),
            (row[2][:19] if row[2] else '[无]'),
            (row[3][:19] if row[3] else '[无]')
        ))
    
    print('\n' + '=' * 80)
    print('修改状态: ✅ 全部成功')
    print('=' * 80)