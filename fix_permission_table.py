"""
修复permission_matrix表缺少description列的问题
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pymysql

# 数据库配置
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://nocobase:nocobase@127.0.0.1:3307/nocobase'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def fix_permission_table():
    with app.app_context():
        try:
            # 检查description列是否存在
            result = db.session.execute(db.text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = 'nocobase' 
                AND TABLE_NAME = 'permission_matrix'
                AND COLUMN_NAME = 'description'
            """))
            
            if result.fetchone() is None:
                print("description列不存在，正在添加...")
                # 添加description列
                db.session.execute(db.text("""
                    ALTER TABLE permission_matrix 
                    ADD COLUMN description TEXT NULL
                """))
                db.session.commit()
                print("✅ 成功添加description列")
            else:
                print("✅ description列已存在，无需修改")
                
        except Exception as e:
            print(f"❌ 错误: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    fix_permission_table()