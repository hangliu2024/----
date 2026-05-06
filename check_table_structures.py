"""
检查 computer_info 和 employee_info 表结构
"""
from app import app
from sqlalchemy import text

with app.app_context():
    from app import db
    
    print('=' * 80)
    print('表结构检查')
    print('=' * 80)
    
    # 1. 检查 computer_info 表结构
    print('\n[1] computer_info 表结构:')
    print('-' * 80)
    comp_columns = db.session.execute(text('DESCRIBE computer_info')).fetchall()
    for col in comp_columns:
        print('  {}: {}'.format(col[0], col[1]))
    
    # 2. 检查 employee_info 表结构
    print('\n[2] employee_info 表结构:')
    print('-' * 80)
    emp_columns = db.session.execute(text('DESCRIBE employees_info')).fetchall()
    
    # 找出部门相关的字段
    dept_fields = []
    for col in emp_columns:
        col_name = col[0]
        col_type = col[1]
        # 检查是否是部门相关字段
        if 'dept' in col_name.lower() or 'department' in col_name.lower():
            dept_fields.append((col_name, col_type))
        print('  {}: {}'.format(col_name, col_type))
    
    # 3. 找出员工ID相关的字段
    print('\n[3] 员工ID相关字段:')
    print('-' * 80)
    for col in emp_columns:
        col_name = col[0]
        if 'emp' in col_name.lower() and 'id' in col_name.lower():
            print('  {}: {}'.format(col_name, col[1]))
    
    # 4. 部门相关字段详情
    print('\n[4] 部门相关字段详情:')
    print('-' * 80)
    for field_name, field_type in dept_fields:
        # 统计非空记录数
        count_result = db.session.execute(text('''
            SELECT COUNT(*)
            FROM employees_info
            WHERE {} IS NOT NULL
        '''.format(field_name))).scalar()
        print('  {}: {} - {} 条记录'.format(field_name, field_type, count_result))
    
    print('\n' + '=' * 80)