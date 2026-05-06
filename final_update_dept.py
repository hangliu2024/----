"""
最终更新 - 将部门信息写入 computer_info 表
"""
from app import app
from sqlalchemy import text

with app.app_context():
    from app import db
    
    print('=' * 80)
    print('部门信息更新')
    print('=' * 80)
    
    # 1. 添加字段
    print('\n[1] 添加部门信息字段...')
    
    columns = db.session.execute(text('DESCRIBE computer_info')).fetchall()
    column_names = [col[0] for col in columns]
    
    new_columns = [
        ('dept_code', 'VARCHAR(50)'),
        ('dept_level2', 'VARCHAR(50)'),
        ('emp_name', 'VARCHAR(50)')
    ]
    
    for col_name, col_type in new_columns:
        if col_name not in column_names:
            print('  添加字段: {}...'.format(col_name))
            try:
                db.session.execute(text('ALTER TABLE computer_info ADD COLUMN {} {}'.format(col_name, col_type)))
                db.session.commit()
                print('    [OK]')
            except Exception as e:
                print('    [FAIL]')
                db.session.rollback()
        else:
            print('  字段 {} 已存在'.format(col_name))
    
    # 2. 执行 UPDATE JOIN
    print('\n[2] 执行更新...')
    
    try:
        db.session.execute(text('''
            UPDATE computer_info c
            INNER JOIN employees_info e ON c.employee_id = e.emp_id
            SET 
                c.dept_code = e.dept_code,
                c.dept_level2 = e.dept_level2,
                c.emp_name = e.emp_name
        '''))
        db.session.commit()
        print('  [OK] 更新成功!')
    except Exception as e:
        print('  [FAIL] {}'.format(e))
        db.session.rollback()
        exit(1)
    
    # 3. 统计结果
    print('\n[3] 更新结果...')
    
    with_dept = int(db.session.execute(text('SELECT COUNT(*) FROM computer_info WHERE dept_code IS NOT NULL')).scalar())
    total = int(db.session.execute(text('SELECT COUNT(*) FROM computer_info WHERE employee_id IS NOT NULL')).scalar())
    
    print('  更新成功: {}/{} ({:.1f}%)'.format(with_dept, total, with_dept * 100.0 / total))
    
    # 4. 显示样例
    print('\n[4] 更新后的数据')
    print('-' * 80)
    
    samples = db.session.execute(text('''
        SELECT employee_id, computer_name, dept_code, dept_level2, emp_name
        FROM computer_info
        WHERE dept_code IS NOT NULL
        LIMIT 10
    '''))
    
    print('{:<12} | {:<25} | {:<12} | {:<20} | {}'.format(
        '工号', '电脑名称', '部门代码', '二级部门', '姓名'
    ))
    print('-' * 80)
    
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