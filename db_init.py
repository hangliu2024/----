# 初始化数据库
from app import app, db, bcrypt
from app.models import User, Personnel

# 在应用程序上下文中运行数据库操作
with app.app_context():
    try:
        # 创建所有表
        db.create_all()
        print("All tables created successfully!")
    except Exception as e:
        print(f"Failed to create tables: {str(e)}")

    # 创建默认管理员账户（如果不存在）
    try:
        admin = User.query.filter_by(email='admin@example.com').first()
        if not admin:
            hashed_password = bcrypt.generate_password_hash('Admin123!').decode('utf-8')
            admin = User(
                username='admin',
                email='admin@example.com',
                password=hashed_password,
                role='admin',
                is_active=True
            )
            db.session.add(admin)
            db.session.commit()
            print("Default admin created: admin@example.com / Admin123!")
        else:
            print(f"Admin user already exists: {admin.email}")
    except Exception as e:
        print(f"Failed to create admin user: {str(e)}")
