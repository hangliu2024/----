from app import app, db
from sqlalchemy import text

def create_person_permission_matrix():
    with app.app_context():
        conn = db.engine.connect()
        
        try:
            print("创建新的人员权限矩阵表...")
            
            conn.execute(text("DROP TABLE IF EXISTS person_permission_matrix"))
            conn.commit()
            print("已删除旧表（如果存在）")
            
            conn.execute(text("""
                CREATE TABLE person_permission_matrix (
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
            print("人员权限矩阵表创建成功")
            
            companies = [
                '华泰科技', '华泰电子', '华泰光电', '华泰机械', '华泰新能源',
                '华泰医疗', '华泰化工', '华泰物流', '华泰金融', '华泰地产',
                '华泰物业', '华泰传媒', '华泰教育', '华泰餐饮', '华泰旅游',
                '华泰保安', '华泰保洁', '华泰园林', '华泰咨询', '华泰重工'
            ]
            
            systems = [
                'OA办公系统', 'ERP企业资源计划', 'CRM客户关系管理', 'HR人力资源系统',
                '财务管理系统', '供应链管理系统', '生产制造系统MES', '资产管理系统',
                '知识管理系统', '项目管理系统', '数据分析平台', '邮件系统',
                '考勤系统', '门禁系统', '视频监控系统', '会议预约系统',
                '预算管理系统', '合同管理系统', '采购管理系统', '销售管理系统'
            ]
            
            permission_data = []
            for company in companies:
                for system in systems:
                    can_view = 1
                    can_add = 1 if company not in ['华泰保安', '华泰保洁', '华泰园林', '华泰咨询'] else 0
                    can_edit = 1 if company not in ['华泰保安', '华泰保洁', '华泰园林', '华泰咨询'] else 0
                    can_delete = 1 if company in ['华泰科技', '华泰电子'] else 0
                    can_export = 1 if company not in ['华泰保安', '华泰保洁'] else 0
                    can_import = 1 if company not in ['华泰保安', '华泰保洁', '华泰园林'] else 0
                    can_approve = 1 if company in ['华泰科技', '华泰电子', '华泰光电', '华泰机械', '华泰金融'] else 0
                    can_config = 1 if company == '华泰科技' else 0
                    
                    if system in ['门禁系统', '视频监控系统']:
                        can_view = 1
                        can_add = 0
                        can_edit = 0
                        can_delete = 0
                        can_approve = 0
                    elif system == '考勤系统':
                        can_view = 1
                        can_add = 0
                        can_edit = 0
                        can_delete = 0
                    
                    permission_data.append({
                        'company_name': company,
                        'system_name': system,
                        'can_view': can_view,
                        'can_add': can_add,
                        'can_edit': can_edit,
                        'can_delete': can_delete,
                        'can_export': can_export,
                        'can_import': can_import,
                        'can_approve': can_approve,
                        'can_config': can_config,
                        'permission_level': 'basic',
                        'description': f'{company} - {system} 权限配置'
                    })
            
            for data in permission_data:
                conn.execute(text("""
                    INSERT INTO person_permission_matrix 
                    (company_name, system_name, can_view, can_add, can_edit, can_delete, 
                     can_export, can_import, can_approve, can_config, permission_level, description)
                    VALUES (:company_name, :system_name, :can_view, :can_add, :can_edit, :can_delete,
                            :can_export, :can_import, :can_approve, :can_config, :permission_level, :description)
                """), data)
            
            conn.commit()
            print(f"成功插入 {len(permission_data)} 条权限配置数据")
            
            result = conn.execute(text("SELECT COUNT(*) as cnt FROM person_permission_matrix"))
            count = result.fetchone()[0]
            print(f"表中共有 {count} 条记录")
            
        except Exception as e:
            print(f"操作失败: {e}")
            import traceback
            traceback.print_exc()
            conn.rollback()
        finally:
            conn.close()

if __name__ == "__main__":
    create_person_permission_matrix()