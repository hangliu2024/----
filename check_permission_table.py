from app import app, db
from sqlalchemy import text

def check_and_fix_permission_matrix():
    with app.app_context():
        conn = db.engine.connect()
        
        try:
            result = conn.execute(text("DESCRIBE permission_matrix"))
            columns = [row[0] for row in result.fetchall()]
            print(f"当前 permission_matrix 表的列: {columns}")
            
            if 'permission_level' not in columns:
                print("缺少 permission_level 列，正在添加...")
                conn.execute(text("ALTER TABLE permission_matrix ADD COLUMN permission_level VARCHAR(20) DEFAULT 'basic'"))
                conn.commit()
                print("已成功添加 permission_level 列")
            else:
                print("permission_level 列已存在")
                
        except Exception as e:
            print(f"操作失败: {e}")
            conn.rollback()
        finally:
            conn.close()

if __name__ == "__main__":
    check_and_fix_permission_matrix()