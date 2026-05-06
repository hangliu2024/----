# 初始化数据库
from app import app, db
from app.models import User, Personnel

# 在应用程序上下文中运行数据库操作
with app.app_context():
    try:
        # 创建所有表，但Personnel表由于指定了__tablename__且已经存在，不会被重新创建
        db.create_all()
        print("All tables created successfully!")
    except Exception as e:
        print(f"Failed to create tables: {str(e)}")