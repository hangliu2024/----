"""
创建稽查管理相关数据库表
"""
import sys
sys.path.insert(0, '.')

from app import app, db

with app.app_context():
    print('正在创建稽查管理相关数据表...')
    
    # 创建稽查任务表
    db.session.execute(db.text('''
        CREATE TABLE IF NOT EXISTS audit_task (
            id INT AUTO_INCREMENT PRIMARY KEY,
            task_no VARCHAR(50) NOT NULL UNIQUE,
            task_title VARCHAR(200) NOT NULL,
            task_type VARCHAR(50) NOT NULL,
            task_content TEXT NOT NULL,
            task_requirement TEXT,
            priority VARCHAR(20) DEFAULT 'normal',
            assignee_id INT NOT NULL,
            assigner_id INT NOT NULL,
            dept_id INT,
            dept_name VARCHAR(100),
            deadline DATETIME,
            status VARCHAR(20) DEFAULT 'pending',
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            completed_at DATETIME,
            FOREIGN KEY (assignee_id) REFERENCES user(id),
            FOREIGN KEY (assigner_id) REFERENCES user(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    '''))
    
    # 创建稽查任务反馈表
    db.session.execute(db.text('''
        CREATE TABLE IF NOT EXISTS audit_task_feedback (
            id INT AUTO_INCREMENT PRIMARY KEY,
            task_id INT NOT NULL,
            feedback_content TEXT NOT NULL,
            feedback_type VARCHAR(20) DEFAULT 'report',
            attachment_path VARCHAR(500),
            feedback_by INT NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES audit_task(id),
            FOREIGN KEY (feedback_by) REFERENCES user(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    '''))
    
    # 创建稽查记录表
    db.session.execute(db.text('''
        CREATE TABLE IF NOT EXISTS audit_record (
            id INT AUTO_INCREMENT PRIMARY KEY,
            task_id INT,
            audit_type VARCHAR(50) NOT NULL,
            audit_scope VARCHAR(100),
            audit_content TEXT NOT NULL,
            audit_result TEXT,
            issue_found TEXT,
            suggestion TEXT,
            audit_by INT NOT NULL,
            audit_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(20) DEFAULT 'draft',
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES audit_task(id),
            FOREIGN KEY (audit_by) REFERENCES user(id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    '''))
    
    db.session.commit()
    print('稽查管理数据表创建完成！')
    
    # 验证表是否创建成功
    result = db.session.execute(db.text('SHOW TABLES LIKE "audit_%"'))
    tables = list(result)
    print(f'已创建的稽查管理表: {[t[0] for t in tables]}')