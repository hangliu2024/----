"""
修复所有安全相关表的缺失列问题
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pymysql

# 数据库配置
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://nocobase:nocobase@127.0.0.1:3307/nocobase'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def fix_tables():
    with app.app_context():
        # 修复 classified_personnel 表
        try:
            print("\n检查 classified_personnel 表...")
            
            # 获取现有列
            result = db.session.execute(db.text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = 'nocobase' 
                AND TABLE_NAME = 'classified_personnel'
            """))
            existing_columns = [row[0] for row in result.fetchall()]
            print(f"现有列: {existing_columns}")
            
            # 需要的列
            required_columns = {
                'emp_id': 'VARCHAR(20) NULL',
                'emp_name': 'VARCHAR(50) NULL',
                'dept_id': 'VARCHAR(20) NULL',
                'dept_name': 'VARCHAR(100) NULL',
                'agreement_type': 'VARCHAR(50) NULL',
                'signing_date': 'VARCHAR(20) NULL',
                'expiration_date': 'VARCHAR(20) NULL',
                'status': 'VARCHAR(20) NULL',
                'remark': 'TEXT NULL',
                'created_at': 'DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP'
            }
            
            for col_name, col_type in required_columns.items():
                if col_name not in existing_columns:
                    print(f"添加列 {col_name}...")
                    db.session.execute(db.text(f"""
                        ALTER TABLE classified_personnel 
                        ADD COLUMN {col_name} {col_type}
                    """))
                    db.session.commit()
                    print(f"✅ 成功添加 {col_name}")
                else:
                    print(f"✅ {col_name} 已存在")
                    
        except Exception as e:
            print(f"❌ 错误: {str(e)}")
            db.session.rollback()
        
        # 修复 classified_media 表
        try:
            print("\n检查 classified_media 表...")
            
            result = db.session.execute(db.text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = 'nocobase' 
                AND TABLE_NAME = 'classified_media'
            """))
            existing_columns = [row[0] for row in result.fetchall()]
            
            required_columns = {
                'media_number': 'VARCHAR(50) NULL',
                'media_type': 'VARCHAR(50) NULL',
                'capacity': 'VARCHAR(20) NULL',
                'dept_id': 'VARCHAR(20) NULL',
                'dept_name': 'VARCHAR(100) NULL',
                'responsible_name': 'VARCHAR(50) NULL',
                'responsible_emp_id': 'VARCHAR(20) NULL',
                'purpose': 'VARCHAR(100) NULL',
                'status': 'VARCHAR(20) NULL',
                'remark': 'TEXT NULL',
                'created_at': 'DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP'
            }
            
            for col_name, col_type in required_columns.items():
                if col_name not in existing_columns:
                    print(f"添加列 {col_name}...")
                    db.session.execute(db.text(f"""
                        ALTER TABLE classified_media 
                        ADD COLUMN {col_name} {col_type}
                    """))
                    db.session.commit()
                    print(f"✅ 成功添加 {col_name}")
                    
        except Exception as e:
            print(f"❌ 错误: {str(e)}")
            db.session.rollback()
        
        # 修复 security_zone 表
        try:
            print("\n检查 security_zone 表...")
            
            result = db.session.execute(db.text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = 'nocobase' 
                AND TABLE_NAME = 'security_zone'
            """))
            existing_columns = [row[0] for row in result.fetchall()]
            
            required_columns = {
                'zone_code': 'VARCHAR(20) NULL',
                'zone_name': 'VARCHAR(100) NULL',
                'zone_level': 'VARCHAR(20) NULL',
                'dept_id': 'VARCHAR(20) NULL',
                'dept_name': 'VARCHAR(100) NULL',
                'responsible_name': 'VARCHAR(50) NULL',
                'responsible_emp_id': 'VARCHAR(20) NULL',
                'location': 'VARCHAR(100) NULL',
                'status': 'VARCHAR(20) NULL',
                'remark': 'TEXT NULL',
                'created_at': 'DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP'
            }
            
            for col_name, col_type in required_columns.items():
                if col_name not in existing_columns:
                    print(f"添加列 {col_name}...")
                    db.session.execute(db.text(f"""
                        ALTER TABLE security_zone 
                        ADD COLUMN {col_name} {col_type}
                    """))
                    db.session.commit()
                    print(f"✅ 成功添加 {col_name}")
                    
        except Exception as e:
            print(f"❌ 错误: {str(e)}")
            db.session.rollback()
        
        # 修复 electronic_document 表
        try:
            print("\n检查 electronic_document 表...")
            
            result = db.session.execute(db.text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = 'nocobase' 
                AND TABLE_NAME = 'electronic_document'
            """))
            existing_columns = [row[0] for row in result.fetchall()]
            
            required_columns = {
                'doc_number': 'VARCHAR(50) NULL',
                'doc_title': 'VARCHAR(200) NULL',
                'doc_level': 'VARCHAR(20) NULL',
                'dept_id': 'VARCHAR(20) NULL',
                'dept_name': 'VARCHAR(100) NULL',
                'responsible_name': 'VARCHAR(50) NULL',
                'responsible_emp_id': 'VARCHAR(20) NULL',
                'file_path': 'VARCHAR(200) NULL',
                'doc_status': 'VARCHAR(20) NULL',
                'remark': 'TEXT NULL',
                'created_at': 'DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP'
            }
            
            for col_name, col_type in required_columns.items():
                if col_name not in existing_columns:
                    print(f"添加列 {col_name}...")
                    db.session.execute(db.text(f"""
                        ALTER TABLE electronic_document 
                        ADD COLUMN {col_name} {col_type}
                    """))
                    db.session.commit()
                    print(f"✅ 成功添加 {col_name}")
                    
        except Exception as e:
            print(f"❌ 错误: {str(e)}")
            db.session.rollback()
        
        # 修复 paper_document 表
        try:
            print("\n检查 paper_document 表...")
            
            result = db.session.execute(db.text("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = 'nocobase' 
                AND TABLE_NAME = 'paper_document'
            """))
            existing_columns = [row[0] for row in result.fetchall()]
            
            required_columns = {
                'doc_number': 'VARCHAR(50) NULL',
                'doc_title': 'VARCHAR(200) NULL',
                'doc_level': 'VARCHAR(20) NULL',
                'dept_id': 'VARCHAR(20) NULL',
                'dept_name': 'VARCHAR(100) NULL',
                'responsible_name': 'VARCHAR(50) NULL',
                'responsible_emp_id': 'VARCHAR(20) NULL',
                'quantity': 'INT NULL',
                'storage_location': 'VARCHAR(100) NULL',
                'doc_status': 'VARCHAR(20) NULL',
                'remark': 'TEXT NULL',
                'created_at': 'DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP'
            }
            
            for col_name, col_type in required_columns.items():
                if col_name not in existing_columns:
                    print(f"添加列 {col_name}...")
                    db.session.execute(db.text(f"""
                        ALTER TABLE paper_document 
                        ADD COLUMN {col_name} {col_type}
                    """))
                    db.session.commit()
                    print(f"✅ 成功添加 {col_name}")
                    
        except Exception as e:
            print(f"❌ 错误: {str(e)}")
            db.session.rollback()
        
        print("\n✅ 所有表修复完成！")

if __name__ == '__main__':
    fix_tables()