from app import app, db
from app.models import User, Department, Personnel

def create_sample_departments():
    """创建示例部门数据"""
    
    with app.app_context():
        # 清空现有数据（可选）
        db.session.query(User).delete()
        db.session.query(Department).delete()
        
        # 创建根部门
        root_dept = Department(
            name='总公司',
            code='TOTAL',
            description='公司总部',
            level=1
        )
        db.session.add(root_dept)
        
        # 创建一级部门
        depts = [
            ('技术研发部', 'TECH', '技术研发部门', 1, root_dept.id),
            ('人力资源部', 'HR', '人力资源管理部门', 1, root_dept.id),
            ('财务部', 'FINANCE', '财务管理部门', 1, root_dept.id),
            ('市场部', 'MKT', '市场营销部门', 1, root_dept.id),
            ('运营部', 'OPS', '运营管理部门', 1, root_dept.id),
        ]
        
        for name, code, desc, level, parent_id in depts:
            dept = Department(
                name=name,
                code=code,
                description=desc,
                level=level,
                parent_id=parent_id
            )
            db.session.add(dept)
        
        # 创建二级部门
        tech_depts = [
            ('前端开发组', 'FRONTEND', '前端开发团队', 2, 2),
            ('后端开发组', 'BACKEND', '后端开发团队', 2, 2),
            ('测试组', 'QA', '质量保证团队', 2, 2),
            ('运维组2', 'OPS_TECH', '系统运维团队', 2, 2),
        ]
        
        for name, code, desc, level, parent_id in tech_depts:
            dept = Department(
                name=name,
                code=code,
                description=desc,
                level=level,
                parent_id=parent_id
            )
            db.session.add(dept)
        
        # 创建管理员用户
        admin = User(
            username='admin',
            email='admin@example.com',
            password='admin123',
            role='admin'
        )
        db.session.add(admin)
        
        # 创建部门管理员用户
        tech_admin = User(
            username='tech_admin',
            email='tech_admin@example.com',
            password='tech123',
            role='department_admin',
            department_id=2,  # 技术研发部
            department_access=True
        )
        db.session.add(tech_admin)
        
        # 创建普通用户
        user1 = User(
            username='user1',
            email='user1@example.com',
            password='user123',
            role='user',
            department_id=3,  # 人力资源部
            department_access=True
        )
        db.session.add(user1)
        
        # 创建普通用户
        user2 = User(
            username='user2',
            email='user2@example.com',
            password='user123',
            role='user',
            department_access=False  # 不限制部门访问
        )
        db.session.add(user2)
        
        db.session.commit()
        print("示例部门和用户数据创建成功！")
        print("管理员: admin / admin123")
        print("技术部管理员: tech_admin / tech123")
        print("普通用户: user1 / user123, user2 / user123")

if __name__ == '__main__':
    create_sample_departments()