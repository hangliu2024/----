"""
验证 ComputerInfo 模型的字段
"""
from app import app
from app.models import ComputerInfo
from sqlalchemy import text

with app.app_context():
    from app import db
    
    print('=' * 80)
    print('验证 ComputerInfo 模型字段')
    print('=' * 80)
    
    # 1. 检查模型定义
    print('\n[1] 模型字段定义:')
    print('-' * 80)
    for col in ComputerInfo.__table__.columns:
        print('  {}: {}'.format(col.name, col.type))
    
    # 2. 检查数据库实际数据
    print('\n[2] 数据库实际数据:')
    print('-' * 80)
    
    result = db.session.execute(text('DESCRIBE computer_info')).fetchall()
    print('数据库字段:')
    for col in result:
        print('  {}: {}'.format(col[0], col[1]))
    
    # 3. 查看样例数据
    print('\n[3] 样例数据:')
    print('-' * 80)
    
    samples = ComputerInfo.query.filter(
        ComputerInfo.dept_code.isnot(None)
    ).limit(5).all()
    
    print('{:<6} | {:<25} | {:<12} | {:<20} | {:<10}'.format(
        'ID', '电脑名称', '部门代码', '二级部门', '员工姓名'
    ))
    print('-' * 80)
    
    for comp in samples:
        print('{:<6} | {:<25} | {:<12} | {:<20} | {:<10}'.format(
            comp.id,
            comp.computer_name[:24] if comp.computer_name else '[无]',
            comp.dept_code[:11] if comp.dept_code else '[无]',
            comp.dept_level2[:19] if comp.dept_level2 else '[无]',
            comp.emp_name[:9] if comp.emp_name else '[无]'
        ))
    
    # 4. 统计
    print('\n[4] 统计信息:')
    print('-' * 80)
    
    total = ComputerInfo.query.filter(ComputerInfo.employee_id.isnot(None)).count()
    with_dept = ComputerInfo.query.filter(
        ComputerInfo.employee_id.isnot(None),
        ComputerInfo.dept_code.isnot(None)
    ).count()
    
    print('  有工号的记录: {} 条'.format(total))
    print('  有部门信息的记录: {} 条 ({:.1f}%)'.format(with_dept, with_dept * 100.0 / total if total > 0 else 0))
    
    print('\n' + '=' * 80)
    print('[OK] 验证完成!')
    print('=' * 80)