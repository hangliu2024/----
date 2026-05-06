"""
最终清理 - 处理残留的 EVE 和无效数据
"""
from app import app
from sqlalchemy import text
import re

with app.app_context():
    from app import db
    
    print('=' * 80)
    print('最终清理残留数据')
    print('=' * 80)
    
    # 1. 处理所有包含 EVE 或 LUBAN 的记录
    print('\n[1] 处理包含 EVE 的记录...')
    
    # 获取所有包含 EVE 的记录
    eve_records = db.session.execute(text('''
        SELECT id, last_login_user 
        FROM computer_info 
        WHERE last_login_user LIKE '%EVE%' 
           OR last_login_user LIKE '%eve%'
           OR last_login_user LIKE '%Eve%'
    '''))
    
    eve_count = 0
    for row in eve_records:
        record_id = row[0]
        last_login_user = row[1]
        
        # 去除所有 EVE（不区分大小写）
        cleaned = re.sub(r'EVE', '', last_login_user, flags=re.IGNORECASE)
        # 去除所有 LUBAN（不区分大小写）
        cleaned = re.sub(r'LUBAN', '', cleaned, flags=re.IGNORECASE)
        # 去除所有特殊字符，只保留字母和数字
        cleaned = re.sub(r'[^a-zA-Z0-9]', '', cleaned)
        
        # 如果清洗后太短，标记为无工号
        if len(cleaned) < 3 or cleaned.upper() == 'EVE':
            cleaned = None
        
        # 更新数据库
        try:
            db.session.execute(text('''
                UPDATE computer_info 
                SET employee_id = :employee_id 
                WHERE id = :id
            '''), {'employee_id': cleaned, 'id': record_id})
            eve_count += 1
        except Exception as e:
            print('更新记录 {} 失败: {}'.format(record_id, e))
    
    db.session.commit()
    print('  处理了 {} 条包含 EVE 的记录'.format(eve_count))
    
    # 2. 验证结果
    print('\n[2] 验证清洗结果...')
    
    # 检查还有多少包含 EVE 的
    eve_count_after = db.session.execute(text('''
        SELECT COUNT(*)
        FROM computer_info
        WHERE employee_id LIKE '%EVE%' 
           OR employee_id LIKE '%eve%'
    ''')).scalar()
    
    print('  包含 EVE 的记录数: {} (之前: 77)'.format(eve_count_after))
    
    if eve_count_after == 0:
        print('  [OK] 所有 EVE 已成功去除！')
    else:
        print('  [WARN] 仍有残留')
    
    # 3. 最终统计
    print('\n[3] 最终统计...')
    stats = db.session.execute(text('''
        SELECT 
            COUNT(*) as total,
            COUNT(employee_id) as with_employee_id,
            COUNT(CASE WHEN employee_id IS NOT NULL THEN 1 END) as not_null_count
        FROM computer_info
    ''')).fetchone()
    
    print('  总记录数: {:>6}'.format(stats[0]))
    print('  有工号的记录: {:>6}'.format(stats[1]))
    
    # 4. 显示样例
    print('\n[4] 最终数据样例')
    print('-' * 80)
    samples = db.session.execute(text('''
        SELECT id, employee_id, last_login_user
        FROM computer_info
        ORDER BY id
        LIMIT 20
    '''))
    
    print('{:<6} | {:<25} | {:<25}'.format('ID', '工号', '原始'))
    print('-' * 80)
    for row in samples:
        employee_id = row[1] if row[1] else '[无工号]'
        print('{:<6} | {:<25} | {:<25}'.format(
            row[0], employee_id[:24], row[2][:24]
        ))
    
    print('\n' + '=' * 80)
    print('[OK] 数据清理完成！')
    print('=' * 80)