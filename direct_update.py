"""
直接更新 - 逐条更新避免锁冲突
"""
from app import app
from sqlalchemy import text
import time

with app.app_context():
    from app import db
    
    print('=' * 80)
    print('直接更新部门信息')
    print('=' * 80)
    
    # 1. 添加字段
    print('\n[1] 添加字段...')
    
    columns = db.session.execute(text('DESCRIBE computer_info')).fetchall()
    column_names = [col[0] for col in columns]
    
    for col_name in ['dept_code', 'dept_level2', 'emp_name']:
        if col_name not in column_names:
            print('  添加: {}'.format(col_name))
            db.session.execute(text('ALTER TABLE computer_info ADD COLUMN {} VARCHAR(50)'.format(col_name)))
            db.session.commit()
            time.sleep(0.5)
    
    print('[OK] 字段添加完成')
    
    # 2. 获取待更新记录
    print('\n[2] 获取待更新记录...')
    
    records = db.session.execute(text('''
        SELECT c.id, c.employee_id
        FROM computer_info c
        WHERE c.employee_id IS NOT NULL
          AND c.dept_code IS NULL
    ''')).fetchall()
    
    total = len(records)
    print('  待更新: {} 条'.format(total))
    
    # 3. 逐条更新
    print('\n[3] 开始更新...')
    print('-' * 80)
    
    updated = 0
    failed = 0
    batch = 100
    
    for i, (record_id, employee_id) in enumerate(records, 1):
        try:
            result = db.session.execute(text('''
                SELECT dept_code, dept_level2, emp_name
                FROM employees_info
                WHERE emp_id = :emp_id
                LIMIT 1
            '''), {'emp_id': employee_id}).fetchone()
            
            if result:
                db.session.execute(text('''
                    UPDATE computer_info
                    SET dept_code = :dept_code,
                        dept_level2 = :dept_level2,
                        emp_name = :emp_name
                    WHERE id = :id
                '''), {
                    'dept_code': result[0],
                    'dept_level2': result[1],
                    'emp_name': result[2],
                    'id': record_id
                })
                updated += 1
            
            # 每100条提交一次
            if i % batch == 0:
                db.session.commit()
                print('  进度: {}/{} ({:.1f}%) - 成功: {}'.format(
                    i, total, i * 100.0 / total, updated
                ))
                time.sleep(0.1)
                
        except Exception as e:
            failed += 1
            db.session.rollback()
    
    # 最终提交
    db.session.commit()
    
    print('\n[OK] 更新完成!')
    print('  成功: {} 条'.format(updated))
    print('  失败: {} 条'.format(failed))
    
    # 4. 验证
    print('\n[4] 验证结果...')
    
    result = db.session.execute(text('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN dept_code IS NOT NULL THEN 1 ELSE 0 END) as updated
        FROM computer_info
        WHERE employee_id IS NOT NULL
    ''')).fetchone()
    
    print('  总计: {} 条'.format(result[0]))
    print('  已更新: {} 条 ({:.1f}%)'.format(result[1], result[1] * 100.0 / result[0]))
    
    print('\n' + '=' * 80)
    print('[OK] 完成!')
    print('=' * 80)