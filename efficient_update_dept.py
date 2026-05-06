"""
高效更新 - 使用 UPDATE JOIN 关联部门信息
"""
from app import app
from sqlalchemy import text

with app.app_context():
    from app import db
    
    print('=' * 80)
    print('部门信息高效更新')
    print('=' * 80)
    
    # 1. 添加字段
    print('\n[1] 添加部门信息字段...')
    
    columns = db.session.execute(text('DESCRIBE computer_info')).fetchall()
    column_names = [col[0] for col in columns]
    
    new_columns = [
        ('dept_code', 'VARCHAR(50)', '部门代码'),
        ('dept_level2', 'VARCHAR(50)', '二级部门'),
        ('emp_name', 'VARCHAR(50)', '员工姓名')
    ]
    
    for col_name, col_type, comment in new_columns:
        if col_name not in column_names:
            print('  添加字段: {}...'.format(col_name))
            try:
                db.session.execute(text('''
                    ALTER TABLE computer_info 
                    ADD COLUMN {} {} NULL
                '''.format(col_name, col_type)))
                db.session.commit()
                print('    [OK]')
            except Exception as e:
                print('    [FAIL] {}'.format(e))
                db.session.rollback()
        else:
            print('  字段 {} 已存在'.format(col_name))
    
    # 2. 使用高效的 UPDATE JOIN
    print('\n[2] 执行 UPDATE JOIN...')
    print('  (这可能需要几秒钟)')
    
    try:
        # 使用 UPDATE ... JOIN 语法
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
    
    # 3. 统计结果
    print('\n[3] 更新统计...')
    
    with_dept = db.session.execute(text('''
        SELECT COUNT(*) FROM computer_info WHERE dept_code IS NOT NULL
    ''')).scalar()
    
    total = db.session.execute(text('''
        SELECT COUNT(*) FROM computer_info WHERE employee_id IS NOT NULL
    ''')).scalar()
    
    print('  总记录数: {}'.format(total))
    print('  更新成功: {} ({:.1f}%)'.format(with_dept, with_dept * 100.0 / total if total > 0 else 0))
    
    # 4. 显示样例
    print('\n[4] 更新后的数据样例')
    print('-' * 80)
    
    samples = db.session.execute(text('''
        SELECT employee_id, computer_name, dept_code, dept_level2, emp_name
        FROM computer_info
        WHERE dept_code IS NOT NULL
        LIMIT 10
    '''))
    
    print('{:<15} | {:<25} | {:<15} | {:<20} | {:<10}'.format(
        '工号', '电脑名称', '部门代码', '二级部门', '员工姓名'
    ))
    print('-' * 80)
    for row in samples:
        print('{:<15} | {:<25} | {:<15} | {:<20} | {:<10}'.format(
            str(row[0])[:14],
            str(row[1])[:24],
            str(row[2])[:14],
            str(row[3])[:19],
            str(row[4])[:9]
        ))
    
    print('\n' + '=' * 80)
    print('[OK] 完成!')
    print('=' * 80)