"""
快速更新前1000条记录
"""
from app import app
from sqlalchemy import text

with app.app_context():
    from app import db
    
    print('=' * 80)
    print('快速更新前1000条记录')
    print('=' * 80)
    
    # 1. 添加字段
    print('\n[1] 检查字段...')
    
    columns = db.session.execute(text('DESCRIBE computer_info')).fetchall()
    column_names = [col[0] for col in columns]
    
    for col_name in ['dept_code', 'dept_level2', 'emp_name']:
        if col_name not in column_names:
            print('  添加字段: {}'.format(col_name))
            try:
                db.session.execute(text('ALTER TABLE computer_info ADD COLUMN {} VARCHAR(50)'.format(col_name)))
                db.session.commit()
                print('    [OK]')
            except:
                db.session.rollback()
    
    # 2. 限制更新前1000条
    print('\n[2] 更新前1000条记录...')
    
    count = 0
    for i in range(1, 1001):
        result = db.session.execute(text('''
            SELECT c.id, e.dept_code, e.dept_level2, e.emp_name
            FROM computer_info c
            INNER JOIN employees_info e ON c.employee_id = e.emp_id
            WHERE c.id = :id
        '''), {'id': i}).fetchone()
        
        if result:
            db.session.execute(text('''
                UPDATE computer_info
                SET dept_code = :dept_code,
                    dept_level2 = :dept_level2,
                    emp_name = :emp_name
                WHERE id = :id
            '''), {
                'dept_code': result[1],
                'dept_level2': result[2],
                'emp_name': result[3],
                'id': result[0]
            })
            count += 1
    
    db.session.commit()
    print('  [OK] 更新了 {} 条记录'.format(count))
    
    # 3. 显示结果
    print('\n[3] 更新结果')
    print('-' * 80)
    
    samples = db.session.execute(text('''
        SELECT employee_id, computer_name, dept_code, dept_level2, emp_name
        FROM computer_info
        WHERE dept_code IS NOT NULL
        LIMIT 10
    '''))
    
    for row in samples:
        print('{:<12} | {:<25} | {:<12} | {:<20} | {}'.format(
            str(row[0])[:11],
            str(row[1])[:24],
            str(row[2])[:11],
            str(row[3])[:19],
            str(row[4])[:10]
        ))
    
    print('\n' + '=' * 80)
    print('[OK] 完成!')
    print('=' * 80)