"""
最小化测试 - 只更新10条记录
"""
from app import app
from sqlalchemy import text

with app.app_context():
    from app import db
    
    print('=' * 80)
    print('最小化测试 - 更新10条记录')
    print('=' * 80)
    
    # 检查字段
    columns = db.session.execute(text('DESCRIBE computer_info')).fetchall()
    column_names = [col[0] for col in columns]
    
    for col_name in ['dept_code', 'dept_level2', 'emp_name']:
        if col_name not in column_names:
            print('添加字段: {}'.format(col_name))
            db.session.execute(text('ALTER TABLE computer_info ADD COLUMN {} VARCHAR(50)'.format(col_name)))
            db.session.commit()
    
    # 只更新前10条
    print('\n更新前10条...')
    count = 0
    for i in range(1, 11):
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
            print('  更新 ID {} 成功'.format(result[0]))
    
    db.session.commit()
    print('\n更新了 {} 条记录'.format(count))
    
    # 显示结果
    print('\n结果:')
    samples = db.session.execute(text('''
        SELECT employee_id, dept_code, dept_level2, emp_name
        FROM computer_info
        WHERE dept_code IS NOT NULL
        LIMIT 5
    '''))
    
    for row in samples:
        print('  工号: {:<10} | 部门代码: {:<10} | 二级部门: {:<15} | 姓名: {}'.format(
            str(row[0])[:9],
            str(row[1])[:9],
            str(row[2])[:14],
            str(row[3])[:10]
        ))
    
    print('\n[OK] 完成!')
    print('=' * 80)