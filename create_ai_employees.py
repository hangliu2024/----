"""
创建AI员工相关数据库表
"""
import sqlite3
import os

def create_ai_employees_tables():
    db_path = os.path.join('instance', 'asset_management.db')
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建AI员工表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) UNIQUE NOT NULL,
            nickname VARCHAR(100) NOT NULL,
            position VARCHAR(100),
            avatar VARCHAR(200),
            bio TEXT,
            about TEXT,
            greeting TEXT,
            model_settings TEXT,
            skill_settings TEXT,
            data_source_settings TEXT,
            allowed_tables TEXT,
            allowed_actions TEXT,
            enabled BOOLEAN DEFAULT 1,
            is_builtin BOOLEAN DEFAULT 0,
            sort_order INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建AI会话表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id VARCHAR(50) UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            ai_employee_id INTEGER NOT NULL,
            title VARCHAR(200),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES user(id),
            FOREIGN KEY (ai_employee_id) REFERENCES ai_employees(id)
        )
    ''')
    
    # 创建AI消息表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            role VARCHAR(20) NOT NULL,
            content TEXT,
            metadata TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES ai_conversations(id)
        )
    ''')
    
    # 插入内置AI员工
    builtin_employees = [
        ('data_analyst', '数据分析师', '高级数据分析师', 
         '你是一个专业的数据分析师，擅长SQL查询和数据分析。你可以帮助用户查询和分析资产管理系统中的数据，包括员工信息、资产信息等。',
         '你好！我是数据分析师，可以帮助你查询和分析数据。请问有什么可以帮你的？',
         '["employees_info", "computer_info", "tangible_asset", "intangible_asset", "department"]'),
        
        ('hr_assistant', '人事助手', '人力资源管理助手',
         '你是一个人事管理助手，熟悉人力资源管理流程。你可以帮助用户查询员工信息、统计分析人力资源数据。',
         '你好！我是人事助手，可以帮助你查询员工信息和人力资源相关数据。请问有什么可以帮你的？',
         '["employees_info", "department"]'),
        
        ('it_support', 'IT支持', 'IT资产管理专员',
         '你是一个IT资产管理人员，负责管理公司的计算机和网络设备资产。你可以帮助用户查询IT设备信息、分析设备使用情况。',
         '你好！我是IT支持，可以帮助你查询计算机资产和网络设备信息。请问有什么可以帮你的？',
         '["computer_info"]'),
        
        ('asset_manager', '资产管理员', '固定资产管理专员',
         '你是一个资产管理专员，负责管理公司的固定资产和无形资产。你可以帮助用户查询资产信息、分析资产状况。',
         '你好！我是资产管理员，可以帮助你查询固定资产和无形资产信息。请问有什么可以帮你的？',
         '["tangible_asset", "intangible_asset"]')
    ]
    
    for emp in builtin_employees:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO ai_employees 
                (username, nickname, position, about, greeting, allowed_tables, is_builtin, enabled)
                VALUES (?, ?, ?, ?, ?, ?, 1, 1)
            ''', emp)
        except Exception as e:
            print(f"插入员工失败: {e}")
    
    conn.commit()
    conn.close()
    
    print("AI员工表创建成功！")
    print("已创建以下内置AI员工：")
    for emp in builtin_employees:
        print(f"  - {emp[1]} ({emp[0]})")

if __name__ == '__main__':
    create_ai_employees_tables()