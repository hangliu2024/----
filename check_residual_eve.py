"""
检查残留的 EVE 数据
"""
from app import app
from sqlalchemy import text

with app.app_context():
    from app import db
    
    print('=' * 80)
    print('检查残留的包含 EVE 的数据')
    print('=' * 80)
    
    # 查找所有包含 EVE 的数据
    residual_data = db.session.execute(text('''
        SELECT id, employee_id, last_login_user
        FROM computer_info
        WHERE employee_id LIKE '%EVE%' 
           OR employee_id LIKE '%eve%'
    '''))
    
    count = 0
    for row in residual_data:
        print('ID: {:>6} | 工号: {:<30} | 原始: {}'.format(
            row[0], row[1], row[2]
        ))
        count += 1
    
    print('\n总共 {} 条残留数据'.format(count))
    print('=' * 80)