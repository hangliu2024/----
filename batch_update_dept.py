"""
高效批量更新 - 将 computer_info 表的工号与 employee_info 表关联
"""
from app import app
from sqlalchemy import text

with app.app_context():
    from app import db
    
    print('=' * 80)
    print('部门信息批量更新')
    print('=' * 80)
    
    # 1. 添加部门信息字段
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
            print('  添加字段: {} ({})'.format(col_name, comment))
            try:
                db.session.execute(text('''
                    ALTER TABLE computer_info 
                    ADD COLUMN {} {} NULL
                '''.format(col_name, col_type)))
                db.session.commit()
                print('    [OK] 成功')
            except Exception as e:
                print('    [FAIL] {}'.format(e))
                db.session.rollback()
        else:
            print('  字段 {} 已存在'.format(col_name))
    
    # 2. 获取所有需要更新的记录
    print('\n[2] 获取待更新记录...')
    
    records = db.session.execute(text('''
        SELECT c.id, c.employee_id
        FROM computer_info c
        WHERE c.employee_id IS NOT NULL
          AND (c.dept_code IS NULL OR c.dept_level2 IS NULL)
    ''')).fetchall()
    
    total = len(records)
    print('  待更新记录: {} 条'.format(total))
    
    # 3. 分批更新
    print('\n[3] 分批更新数据...')
    print('-' * 80)
    
    batch_size = 1000
    total_updated = 0
    
    for i in range(0, total, batch_size):
        batch = records[i:i+batch_size]
        
        for record_id, employee_id in batch:
            # 查询对应的员工信息
            emp_info = db.session.execute(text('''
                SELECT dept_code, dept_level2, emp_name
                FROM employees_info
                WHERE emp_id = :emp_id
                LIMIT 1
            '''), {'emp_id': employee_id}).fetchone()
            
            if emp_info:
                try:
                    db.session.execute(text('''
                        UPDATE computer_info
                        SET dept_code = :dept_code,
                            dept_level2 = :dept_level2,
                            emp_name = :emp_name
                        WHERE id = :id
                    '''), {
                        'dept_code': emp_info[0],
                        'dept_level2': emp_info[1],
                        'emp_name': emp_info[2],
                        'id': record_id
                    })
                    total_updated += 1
                except Exception as e:
                    pass
        
        db.session.commit()
        
        # 打印进度
        progress = min(i + batch_size, total)
        percent = progress * 100.0 / total
        print('  进度: {}/{} ({:.1f}%)'.format(progress, total, percent))
    
    print('  [OK] 更新完成! 共更新 {} 条记录'.format(total_updated))
    
    # 4. 验证结果
    print('\n[4] 验证更新结果...')
    
    with_dept = db.session.execute(text('''
        SELECT COUNT(*) FROM computer_info WHERE dept_code IS NOT NULL
    ''')).scalar()
    
    without_dept = db.session.execute(text('''
        SELECT COUNT(*) FROM computer_info 
        WHERE employee_id IS NOT NULL AND dept_code IS NULL
    ''')).scalar()
    
    print('  有部门信息的记录: {}'.format(with_dept))
    print('  无部门信息的记录: {} (无法匹配)'.format(without_dept))
    
    # 5. 显示样例
    print('\n[5] 更新后的数据样例')
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
    print('[OK] 部门信息更新完成!')
    print('=' * 80)