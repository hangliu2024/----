"""
创建示例数据
"""
from app import app, db, bcrypt
from app.models import User, Department

def create_sample_data():
    """创建示例数据"""
    with app.app_context():
        # 先检查部门是否存在
        if Department.query.count() == 0:
            print("创建部门数据...")
            
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
                ('技术研发部', 'TECH', '技术研发部门', 1),
                ('人力资源部', 'HR', '人力资源管理部门', 1),
                ('财务部', 'FINANCE', '财务管理部门', 1),
                ('市场部', 'MKT', '市场营销部门', 1),
                ('运营部', 'OPS', '运营管理部门', 1),
            ]
            
            # 提交一级部门，以便二级部门可以引用
            db.session.commit()
            
            for name, code, desc, level in depts:
                dept = Department(
                    name=name,
                    code=code,
                    description=desc,
                    level=level,
                    parent_id=root_dept.id
                )
                db.session.add(dept)
            
            db.session.commit()
            print("部门数据创建成功！")
        else:
            print("部门数据已存在")
        
        # 创建用户数据
        print("重新创建用户数据...")
        # 删除现有用户数据
        db.session.query(User).delete()
        db.session.commit()
        
        # 获取技术研发部门
        tech_dept = Department.query.filter_by(code='TECH').first()
        
        admin = User(
            username='admin',
            email='admin@example.com',
            password=bcrypt.generate_password_hash('admin123').decode('utf-8'),
            role='admin'
        )
        db.session.add(admin)
        
        tech_admin = User(
            username='tech_admin',
            email='tech_admin@example.com',
            password=bcrypt.generate_password_hash('tech123').decode('utf-8'),
            role='department_admin',
            department_id=tech_dept.id if tech_dept else None,
            department_access=True
        )
        db.session.add(tech_admin)
        
        user1 = User(
            username='user1',
            email='user1@example.com',
            password=bcrypt.generate_password_hash('user123').decode('utf-8'),
            role='user',
            department_id=tech_dept.id if tech_dept else None,
            department_access=True
        )
        db.session.add(user1)
        
        user2 = User(
            username='user2',
            email='user2@example.com',
            password=bcrypt.generate_password_hash('user123').decode('utf-8'),
            role='user',
            department_access=False
        )
        db.session.add(user2)
        
        db.session.commit()
        print("用户数据创建成功！")
        print("管理员: admin@example.com / admin123")
        print("技术部管理员: tech_admin@example.com / tech123")
        print("普通用户: user1@example.com / user123, user2@example.com / user123")

if __name__ == '__main__':
    create_sample_data()