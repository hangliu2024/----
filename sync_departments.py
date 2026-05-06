"""
同步部门数据脚本
从人员表提取二级部门信息，自动创建部门记录
"""
from app import app, db
from app.models import Department, Personnel
from sqlalchemy import text

def sync_departments():
    """从人员表同步二级部门数据"""
    with app.app_context():
        print('开始同步部门数据...')
        print(f'人员表总记录数: {Personnel.query.count()}')
        
        # 从人员表提取二级部门及其对应的部门代码
        dept_level2_map = {}
        personnel_list = Personnel.query.all()
        for p in personnel_list:
            if p.dept_level2 and p.dept_code:
                # 使用字典确保每个部门名称只保存一个部门代码
                if p.dept_level2 not in dept_level2_map:
                    dept_level2_map[p.dept_level2] = p.dept_code
        
        print(f'\n发现 {len(dept_level2_map)} 个不同的二级部门')
        print('\n部门列表:')
        for i, (dept_name, dept_code) in enumerate(dept_level2_map.items(), 1):
            print(f'  {i}. {dept_name} (部门代码: {dept_code})')
        
        # 清除现有部门数据
        print('\n清除现有部门数据...')
        try:
            # 暂时禁用外键约束
            db.session.execute(text('SET FOREIGN_KEY_CHECKS = 0'))
            Department.query.delete()
            db.session.commit()
            # 重新启用外键约束
            db.session.execute(text('SET FOREIGN_KEY_CHECKS = 1'))
            print('现有部门数据已清除')
        except Exception as e:
            print(f'清除部门数据时出错: {e}')
            db.session.rollback()
            return
        
        # 创建根部门
        print('\n创建根部门（总公司）...')
        root_dept = Department(
            name='总公司',
            code='TOTAL',
            description='公司总部',
            level=1
        )
        db.session.add(root_dept)
        db.session.commit()
        print(f'根部门创建成功，ID: {root_dept.id}')
        
        # 创建二级部门
        print('\n创建二级部门...')
        created_count = 0
        for dept_name, dept_code in dept_level2_map.items():
            dept = Department(
                name=dept_name,
                code=dept_code,
                description=f'{dept_name}',
                level=2,
                parent_id=root_dept.id
            )
            db.session.add(dept)
            created_count += 1
        
        try:
            db.session.commit()
            print(f'\n成功创建 {created_count} 个二级部门')
            print('\n同步完成！')
        except Exception as e:
            print(f'\n创建二级部门时出错: {e}')
            db.session.rollback()
            return
        
        # 验证同步结果
        print('\n验证同步结果:')
        total_depts = Department.query.count()
        level2_depts = Department.query.filter_by(level=2).count()
        print(f'  总部门数量: {total_depts}')
        print(f'  二级部门数量: {level2_depts}')
        
        # 显示前10个二级部门
        print('\n前10个二级部门:')
        for dept in Department.query.filter_by(level=2).limit(10).all():
            print(f'  - {dept.name} (ID: {dept.id}, Code: {dept.code})')

if __name__ == '__main__':
    sync_departments()