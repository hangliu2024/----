from app import app, db
from sqlalchemy import text

def create_person_permission_matrix():
    with app.app_context():
        conn = db.engine.connect()
        
        try:
            result = conn.execute(text("DESCRIBE permission_matrix"))
            columns = [row[0] for row in result.fetchall()]
            print(f"当前 permission_matrix 表的列: {columns}")
            
            if 'system_name' not in columns:
                print("正在重新设计权限矩阵表...")
                
                conn.execute(text("DROP TABLE IF EXISTS permission_matrix"))
                conn.commit()
                print("已删除旧表")
                
                conn.execute(text("""
                    CREATE TABLE permission_matrix (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        company_name VARCHAR(100) NOT NULL COMMENT '公司名称',
                        system_name VARCHAR(100) NOT NULL COMMENT '系统名称',
                        can_view TINYINT(1) DEFAULT 0 COMMENT '查看权限',
                        can_add TINYINT(1) DEFAULT 0 COMMENT '新增权限',
                        can_edit TINYINT(1) DEFAULT 0 COMMENT '编辑权限',
                        can_delete TINYINT(1) DEFAULT 0 COMMENT '删除权限',
                        can_export TINYINT(1) DEFAULT 0 COMMENT '导出权限',
                        can_import TINYINT(1) DEFAULT 0 COMMENT '导入权限',
                        can_approve TINYINT(1) DEFAULT 0 COMMENT '审批权限',
                        can_config TINYINT(1) DEFAULT 0 COMMENT '配置权限',
                        permission_level VARCHAR(20) DEFAULT 'basic' COMMENT '权限级别',
                        description TEXT COMMENT '说明',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE KEY unique_company_system (company_name, system_name)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='人员权限矩阵表'
                """))
                conn.commit()
                print("新权限矩阵表创建成功")
            else:
                print("表结构已存在")
                
        except Exception as e:
            print(f"操作失败: {e}")
            conn.rollback()
        finally:
            conn.close()

if __name__ == "__main__":
    create_person_permission_matrix()