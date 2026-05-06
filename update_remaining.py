"""
更新剩余记录
"""
from app import app
from sqlalchemy import text

with app.app_context():
    from app import db
    
    print('=' * 80)
    print('更新剩余记录')
    print('=' * 80)
    
    # 获取待更新记录
    records = db.session.execute(text('''
        SELECT c.id, c.employee_id
        FROM computer_info c
        WHERE c.employee_id IS NOT NULL
          AND c.dept_code IS NULL
    ''')).fetchall()
    
    total = len(records)
    print('\n待更新: {} 条'.format(total))
    
    updated = 0
    for i, (record_id, employee_id) in enumerate(records, 1):
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
        
        if i % 500 == 0:
            db.session.commit()
            print('  已更新: {}/{}'.format(i, total))
    
    db.session.commit()
    print('\n[OK] 更新完成! 共更新 {} 条'.format(updated))
    
    # 验证
    final = db.session.execute(text('''
        SELECT COUNT(*) FROM computer_info WHERE employee_id IS NOT NULL AND dept_code IS NOT NULL
    ''')).scalar()
    
    total = db.session.execute(text('''
        SELECT COUNT(*) FROM computer_info WHERE employee_id IS NOT NULL
    ''')).scalar()
    
    print('\n最终统计:')
    print('  总计: {} 条'.format(total))
    print('  已更新: {} 条 ({:.1f}%)'.format(final, final * 100.0 / total))
    
    print('\n' + '=' * 80)
    print('[OK] 全部完成!')
    print('=' * 80)