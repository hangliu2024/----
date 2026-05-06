"""
数据库迁移脚本 - 添加部门管理功能
"""
from app import app, db
from app.models import User, Department

def migrate_database():
    """执行数据库迁移"""
    
    with app.app_context():
        # 检查Department表是否存在，不存在则创建
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        if 'department' not in inspector.get_table_names():
            print("创建Department表...")
            Department.__table__.create(db.engine)
            print("Department表创建成功！")
        
        # 添加用户表的字段
        try:
            # 尝试添加department_id字段
            db.session.execute('ALTER TABLE user ADD COLUMN department_id INTEGER')
            print("添加department_id字段成功！")
        except Exception as e:
            if "column 'department_id' already exists" in str(e):
                print("department_id字段已存在，跳过创建")
            else:
                print(f"添加department_id字段失败: {e}")
        
        try:
            # 尝试添加department_access字段
            db.session.execute('ALTER TABLE user ADD COLUMN department_access BOOLEAN DEFAULT FALSE')
            print("添加department_access字段成功！")
        except Exception as e:
            if "column 'department_access' already exists" in str(e):
                print("department_access字段已存在，跳过创建")
            else:
                print(f"添加department_access字段失败: {e}")
        
        db.session.commit()
        
        # 为现有用户设置默认角色
        users = User.query.all()
        for user in users:
            if user.role not in ['admin', 'department_admin', 'user']:
                user.role = 'user'
                user.department_access = False
                print(f"更新用户 {user.username} 的角色为 user")
        
        db.session.commit()
        print("数据库迁移完成！")

if __name__ == '__main__':
    migrate_database()