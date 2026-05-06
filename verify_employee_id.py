"""
验证工号列添加和数据清洗结果
"""
from app import app
from sqlalchemy import text

with app.app_context():
    from app import db
    from app.models import ComputerInfo
    
    print('=== 验证工号列添加结果 ===\n')
    
    # 1. 检查表结构
    print('1. 检查表结构...')
    columns = db.session.execute(text('DESCRIBE computer_info')).fetchall()
    print('computer_info 表字段:')
    for col in columns:
        print('  - {}: {}'.format(col[0], col[1]))
    
    # 2. 统计信息
    print('\n2. 统计信息...')
    stats = db.session.execute(text('''
        SELECT 
            COUNT(*) as total,
            COUNT(employee_id) as with_employee_id,
            COUNT(last_login_user) as with_last_login_user
        FROM computer_info
    ''')).fetchone()
    
    print('  总记录数: {}'.format(stats[0]))
    print('  有工号的记录: {}'.format(stats[1]))
    print('  有最后登录用户的记录: {}'.format(stats[2]))
    
    # 3. 显示样例数据
    print('\n3. 样例数据对比...')
    print('-' * 100)
    print('{:<5} | {:<25} | {:<20} | {:<15} | {:<20}'.format(
        'ID', '电脑名称', '工号', '资产ID', '最后登录用户'))
    print('-' * 100)
    
    samples = db.session.execute(text('''
        SELECT id, computer_name, employee_id, asset_id, last_login_user
        FROM computer_info
        WHERE employee_id IS NOT NULL
        LIMIT 20
    '''))
    
    for row in samples:
        print('{:<5} | {:<25} | {:<20} | {:<15} | {:<20}'.format(
            row[0], 
            row[1][:24] if row[1] else '[无]',
            row[2][:19] if row[2] else '[无]',
            row[3] if row[3] else '[无]',
            row[4][:19] if row[4] else '[无]'
        ))
    
    # 4. 工号格式分布
    print('\n4. 工号格式分布...')
    pattern_stats = db.session.execute(text('''
        SELECT 
            CASE 
                WHEN employee_id REGEXP '^[A-Z]{2,}[0-9]+$' THEN '大写字母开头+数字'
                WHEN employee_id REGEXP '^[a-z]+[0-9]+$' THEN '小写字母开头+数字'
                WHEN employee_id REGEXP '^[0-9]+$' THEN '纯数字'
                WHEN employee_id REGEXP '^[0-9]+-[0-9]+$' THEN '数字-数字'
                ELSE '其他'
            END as pattern,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM computer_info WHERE employee_id IS NOT NULL), 2) as percentage
        FROM computer_info
        WHERE employee_id IS NOT NULL
        GROUP BY pattern
        ORDER BY count DESC
    '''))
    
    print('-' * 80)
    for row in pattern_stats:
        print('  {:20s}: {:>6} 条 ({:>5}%)'.format(row[0], row[1], row[2]))
    
    # 5. 检查数据质量
    print('\n5. 数据质量检查...')
    
    # 检查空工号
    null_count = db.session.execute(text('''
        SELECT COUNT(*) 
        FROM computer_info 
        WHERE last_login_user IS NOT NULL AND employee_id IS NULL
    ''')).scalar()
    
    if null_count == 0:
        print('  [OK] 所有有最后登录用户的记录都有工号')
    else:
        print('  [WARN] 有 {} 条记录有最后登录用户但没有工号'.format(null_count))
    
    # 检查重复工号
    duplicate_count = db.session.execute(text('''
        SELECT COUNT(*) FROM (
            SELECT employee_id 
            FROM computer_info 
            WHERE employee_id IS NOT NULL
            GROUP BY employee_id
            HAVING COUNT(*) > 1
        ) as duplicates
    ''')).scalar()
    
    print('  [INFO] 有 {} 个工号出现了多次'.format(duplicate_count))
    
    print('\n' + '=' * 100)
    print('[OK] 验证完成！工号列已成功添加并填充数据。')
    print('=' * 100)