"""
简单的数据库迁移脚本
"""
from app import app, db
from app.models import User, Department
from sqlalchemy import inspect, text

def simple_migrate():
    """执行简单的数据库迁移"""
    with app.app_context():
        inspector = inspect(db.engine)
        
        # 检查Department表是否存在
        if 'department' not in inspector.get_table_names():
            print("创建Department表...")
            Department.__table__.create(db.engine)
            print("Department表创建成功！")
        else:
            print("Department表已存在")
        
        # 检查user表是否有新字段
        try:
            # 检查department_id字段
            columns = [column['name'] for column in inspector.get_columns('user')]
            print(f"User表的现有字段: {columns}")
            
            if 'department_id' not in columns:
                print("添加department_id字段...")
                db.session.execute(text('ALTER TABLE user ADD COLUMN department_id INTEGER'))
                print("department_id字段添加成功！")
            else:
                print("department_id字段已存在")
            
            if 'department_access' not in columns:
                print("添加department_access字段...")
                db.session.execute(text('ALTER TABLE user ADD COLUMN department_access BOOLEAN DEFAULT FALSE'))
                print("department_access字段添加成功！")
            else:
                print("department_access字段已存在")
                
        except Exception as e:
            print(f"添加字段时出错: {e}")
        
        db.session.commit()
        
        # 更新现有用户
        try:
            users = User.query.all()
            for user in users:
                if user.role not in ['admin', 'department_admin', 'user']:
                    user.role = 'user'
                    user.department_access = False
                    print(f"更新用户 {user.username} 的角色为 user")
            
            db.session.commit()
            print("数据库迁移完成！")
            
        except Exception as e:
            print(f"更新用户时出错: {e}")

if __name__ == '__main__':
    simple_migrate()