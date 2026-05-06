"""
正确更新 - 使用正确的列名
"""
from app import app
from sqlalchemy import text

with app.app_context():
    from app import db
    
    print('=' * 80)
    print('部门信息更新')
    print('=' * 80)
    
    # 检查字段
    columns = db.session.execute(text('DESCRIBE computer_info')).fetchall()
    column_names = [col[0] for col in columns]
    
    # 添加字段
    for col_name in ['dept_code', 'dept_level2', 'emp_name']:
        if col_name not in column_names:
            print('添加字段: {}'.format(col_name))
            db.session.execute(text('ALTER TABLE computer_info ADD COLUMN {} VARCHAR(50)'.format(col_name)))
            db.session.commit()
    
    # 检查数据结构
    print('\n检查数据...')
    sample = db.session.execute(text('''
        SELECT c.id, c.employee_id, e.dept_code, e.dept_level2, e.emp_name
        FROM computer_info c
        INNER JOIN employees_info e ON c.employee_id = e.emp_id
        WHERE c.id = 194
    ''')).fetchone()
    
    if sample:
        print('测试数据:')
        print('  ID: {}'.format(sample[0]))
        print('  工号: {}'.format(sample[1]))
        print('  部门代码: {}'.format(sample[2]))
        print('  二级部门: {}'.format(sample[3]))
        print('  姓名: {}'.format(sample[4]))
        
        # 更新这条记录
        print('\n更新记录 194...')
        db.session.execute(text('''
            UPDATE computer_info
            SET dept_code = :dept_code,
                dept_level2 = :dept_level2,
                emp_name = :emp_name
            WHERE id = 194
        '''), {
            'dept_code': sample[2],
            'dept_level2': sample[3],
            'emp_name': sample[4]
        })
        db.session.commit()
        print('[OK] 更新成功')
        
        # 验证
        print('\n验证更新结果...')
        result = db.session.execute(text('''
            SELECT employee_id, dept_code, dept_level2, emp_name
            FROM computer_info
            WHERE id = 194
        ''')).fetchone()
        
        if result:
            print('  工号: {}'.format(result[0]))
            print('  部门代码: {}'.format(result[1]))
            print('  二级部门: {}'.format(result[2]))
            print('  姓名: {}'.format(result[3]))
    
    print('\n' + '=' * 80)
    print('[OK] 测试完成')
    print('=' * 80)