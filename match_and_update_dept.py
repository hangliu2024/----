"""
将 computer_info 表的工号与 employee_info 表关联，提取部门信息
"""
from app import app
from sqlalchemy import text

with app.app_context():
    from app import db
    
    print('=' * 80)
    print('工号匹配和部门信息提取')
    print('=' * 80)
    
    # 1. 检查匹配情况
    print('\n[1] 检查匹配情况...')
    
    # 检查有多少 computer_info 的 employee_id 能匹配到 employee_info 的 emp_id
    match_count = db.session.execute(text('''
        SELECT COUNT(*)
        FROM computer_info c
        INNER JOIN employees_info e ON c.employee_id = e.emp_id
    ''')).scalar()
    
    total_computer = db.session.execute(text('''
        SELECT COUNT(*) FROM computer_info WHERE employee_id IS NOT NULL
    ''')).scalar()
    
    print('  computer_info 有工号的记录: {}'.format(total_computer))
    print('  能匹配到 employee_info 的记录: {}'.format(match_count))
    print('  匹配率: {:.1f}%'.format(match_count * 100.0 / total_computer if total_computer > 0 else 0))
    
    # 2. 查看一些匹配样例
    print('\n[2] 匹配样例...')
    print('-' * 80)
    samples = db.session.execute(text('''
        SELECT c.employee_id, e.emp_id, e.emp_name, e.dept_level2, e.dept_code
        FROM computer_info c
        INNER JOIN employees_info e ON c.employee_id = e.emp_id
        LIMIT 10
    '''))
    
    print('{:<15} | {:<10} | {:<15} | {:<20} | {:<15}'.format(
        '工号', '员工ID', '员工姓名', '二级部门', '部门代码'
    ))
    print('-' * 80)
    for row in samples:
        print('{:<15} | {:<10} | {:<15} | {:<20} | {:<15}'.format(
            str(row[0])[:14], str(row[1])[:9], str(row[2])[:14], 
            str(row[3])[:19], str(row[4])[:14]
        ))
    
    # 3. 添加部门信息字段到 computer_info 表
    print('\n[3] 添加部门信息字段...')
    
    # 检查是否已存在这些字段
    columns = db.session.execute(text('DESCRIBE computer_info')).fetchall()
    column_names = [col[0] for col in columns]
    
    new_columns = [
        ('dept_code', 'VARCHAR(50)', '部门代码'),
        ('dept_level2', 'VARCHAR(50)', '二级部门'),
        ('emp_name', 'VARCHAR(50)', '员工姓名')
    ]
    
    for col_name, col_type, comment in new_columns:
        if col_name not in column_names:
            print('  添加字段: {} ({})'.format(col_name, comment))
            try:
                db.session.execute(text('''
                    ALTER TABLE computer_info 
                    ADD COLUMN {} {} NULL
                    COMMENT '{}'
                '''.format(col_name, col_type, comment)))
                db.session.commit()
                print('    [OK] 成功添加')
            except Exception as e:
                print('    [FAIL] 失败: {}'.format(e))
                db.session.rollback()
        else:
            print('  字段 {} 已存在，跳过'.format(col_name))
    
    # 4. 更新部门信息
    print('\n[4] 更新部门信息...')
    
    try:
        # 使用 UPDATE ... JOIN 更新数据
        db.session.execute(text('''
            UPDATE computer_info c
            INNER JOIN employees_info e ON c.employee_id = e.emp_id
            SET 
                c.dept_code = e.dept_code,
                c.dept_level2 = e.dept_level2,
                c.emp_name = e.emp_name
        '''))
        db.session.commit()
        print('  [OK] 部门信息更新成功')
    except Exception as e:
        print('  [FAIL] 更新失败: {}'.format(e))
        db.session.rollback()
    
    # 5. 验证更新结果
    print('\n[5] 验证更新结果...')
    print('-' * 80)
    
    updated_count = db.session.execute(text('''
        SELECT COUNT(*)
        FROM computer_info
        WHERE dept_code IS NOT NULL
    ''')).scalar()
    
    print('  更新了 {} 条记录的部门信息'.format(updated_count))
    
    # 显示更新后的样例
    print('\n[6] 更新后的数据样例')
    print('-' * 80)
    samples = db.session.execute(text('''
        SELECT 
            c.employee_id,
            c.computer_name,
            c.dept_code,
            c.dept_level2,
            c.emp_name
        FROM computer_info c
        WHERE c.dept_code IS NOT NULL
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
    print('[OK] 部门信息关联完成！')
    print('=' * 80)