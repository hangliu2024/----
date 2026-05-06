"""
检查包含EVE和LUBAN的employee_id数据
"""
from app import app
from sqlalchemy import text

with app.app_context():
    from app import db
    
    print('=' * 80)
    print('检查包含 EVE 和 LUBAN 的 employee_id 数据')
    print('=' * 80)
    
    # 1. 查找包含 EVE 的数据
    print('\n[1] 包含 EVE 的 employee_id (前20条):')
    print('-' * 80)
    
    eve_data = db.session.execute(text('''
        SELECT id, employee_id, last_login_user
        FROM computer_info
        WHERE employee_id LIKE '%EVE%' 
           OR employee_id LIKE '%eve%'
           OR employee_id LIKE '%Eve%'
        LIMIT 20
    '''))
    
    eve_count = 0
    for row in eve_data:
        print('ID: {:>6} | 工号: {:<30} | 原始: {}'.format(
            row[0], row[1], row[2]
        ))
        eve_count += 1
    
    # 统计包含 EVE 的总数
    eve_total = db.session.execute(text('''
        SELECT COUNT(*)
        FROM computer_info
        WHERE employee_id LIKE '%EVE%' 
           OR employee_id LIKE '%eve%'
           OR employee_id LIKE '%Eve%'
    ''')).scalar()
    
    print('\n包含 EVE 的总记录数: {}'.format(eve_total))
    
    # 2. 查找包含 LUBAN 的数据
    print('\n[2] 包含 LUBAN 的 employee_id (前20条):')
    print('-' * 80)
    
    luban_data = db.session.execute(text('''
        SELECT id, employee_id, last_login_user
        FROM computer_info
        WHERE employee_id LIKE '%LUBAN%' 
           OR employee_id LIKE '%luban%'
           OR employee_id LIKE '%Luban%'
        LIMIT 20
    '''))
    
    luban_count = 0
    for row in luban_data:
        print('ID: {:>6} | 工号: {:<30} | 原始: {}'.format(
            row[0], row[1], row[2]
        ))
        luban_count += 1
    
    # 统计包含 LUBAN 的总数
    luban_total = db.session.execute(text('''
        SELECT COUNT(*)
        FROM computer_info
        WHERE employee_id LIKE '%LUBAN%' 
           OR employee_id LIKE '%luban%'
           OR employee_id LIKE '%Luban%'
    ''')).scalar()
    
    print('\n包含 LUBAN 的总记录数: {}'.format(luban_total))
    
    print('\n' + '=' * 80)
    print('问题确认: 共有 {} 条数据需要重新清洗'.format(eve_total + luban_total))
    print('=' * 80)