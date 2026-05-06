from app import app
from app.models import Department, Personnel
from app import db

with app.app_context():
    print('同步前部门数量:', Department.query.count())
    print('同步前level=2的部门数量:', Department.query.filter_by(level=2).count())
    
    # 从人员表提取二级部门及其对应的部门代码
    dept_level2_map = {}
    personnel = Personnel.query.all()
    for p in personnel:
        if p.dept_level2 and p.dept_code:
            dept_level2_map[p.dept_level2] = p.dept_code
    
    print('\n从人员表提取的二级部门:', len(dept_level2_map))
    for dept_name, dept_code in list(dept_level2_map.items())[:5]:
        print(f'  - {dept_name} (Code: {dept_code})')
    
    # 清除现有部门数据
    print('\n清除现有部门数据...')
    Department.query.delete()
    db.session.commit()
    
    # 创建根部门
    print('创建根部门...')
    root_dept = Department(
        name='总公司',
        code='TOTAL',
        description='公司总部',
        level=1
    )
    db.session.add(root_dept)
    db.session.commit()
    
    # 创建二级部门
    print('创建二级部门...')
    for dept_name, dept_code in dept_level2_map.items():
        dept = Department(
            name=dept_name,
            code=dept_code,
            description=f'{dept_name}',
            level=2,
            parent_id=root_dept.id
        )
        db.session.add(dept)
    
    db.session.commit()
    
    print('\n同步后部门数量:', Department.query.count())
    print('同步后level=2的部门数量:', Department.query.filter_by(level=2).count())
    
    print('\n创建的二级部门:')
    for dept in Department.query.filter_by(level=2).limit(10).all():
        print(f'  - {dept.name} (ID: {dept.id}, Code: {dept.code})')