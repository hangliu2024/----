"""
创建系统管理相关数据库表
"""
import sys
sys.path.insert(0, '.')

from app import app, db
from app.models import User, LoginLog, OperationLog

def create_tables():
    with app.app_context():
        # 创建登录日志表
        print('创建 login_log 表...')
        db.session.execute(db.text('''
            CREATE TABLE IF NOT EXISTS login_log (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                user_id INTEGER NOT NULL,
                username VARCHAR(20),
                login_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                logout_time DATETIME,
                ip_address VARCHAR(50),
                user_agent VARCHAR(255),
                login_type VARCHAR(20) DEFAULT 'login',
                FOREIGN KEY (user_id) REFERENCES user(id)
            )
        '''))
        
        # 创建操作日志表
        print('创建 operation_log 表...')
        db.session.execute(db.text('''
            CREATE TABLE IF NOT EXISTS operation_log (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                user_id INTEGER NOT NULL,
                username VARCHAR(20),
                operation_type VARCHAR(50) NOT NULL,
                module VARCHAR(50),
                description TEXT,
                ip_address VARCHAR(50),
                request_url VARCHAR(255),
                request_method VARCHAR(10),
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user(id)
            )
        '''))
        
        # 检查 user 表是否需要添加新字段
        print('检查 user 表字段...')
        result = db.session.execute(db.text("SHOW COLUMNS FROM user LIKE 'emp_id'"))
        if not result.fetchone():
            print('添加 user 表新字段...')
            db.session.execute(db.text('''
                ALTER TABLE user 
                ADD COLUMN emp_id VARCHAR(20),
                ADD COLUMN phone VARCHAR(20),
                ADD COLUMN real_name VARCHAR(50),
                ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE,
                ADD COLUMN last_login DATETIME,
                ADD COLUMN login_count INTEGER DEFAULT 0,
                ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            '''))
        
        db.session.commit()
        print('数据库表创建/更新完成！')

if __name__ == '__main__':
    create_tables()