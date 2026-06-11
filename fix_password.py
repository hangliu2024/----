"""强制重置所有用户密码为bcrypt格式"""
from app import app, db, bcrypt
from app.models import User

with app.app_context():
    users = User.query.all()
    print(f"找到 {len(users)} 个用户")
    
    for user in users:
        new_password = "Admin123!"
        new_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        user.password = new_hash
        db.session.add(user)
        print(f"  [RESET] {user.email} - 密码已重置为: {new_password}")

    db.session.commit()
    
    print("\n验证所有用户密码:")
    for user in User.query.all():
        try:
            result = bcrypt.check_password_hash(user.password, "Admin123!")
            print(f"  [{'OK' if result else 'FAIL'}] {user.email} - {'验证通过' if result else '验证失败'}")
        except Exception as e:
            print(f"  [ERROR] {user.email} - {e}")
    
    print("\n所有用户密码已修复完成！")
