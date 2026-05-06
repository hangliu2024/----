from app import app, db
from sqlalchemy import text

def create_person_system_permission_matrix():
    with app.app_context():
        conn = db.engine.connect()
        
        try:
            print("重建人员权限矩阵表...")
            
            conn.execute(text("DROP TABLE IF EXISTS person_system_permission_matrix"))
            conn.commit()
            print("已删除旧表（如果存在）")
            
            conn.execute(text("""
                CREATE TABLE person_system_permission_matrix (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    emp_id VARCHAR(20) COMMENT '工号',
                    emp_name VARCHAR(50) COMMENT '姓名',
                    dept_id VARCHAR(20) COMMENT '部门ID',
                    dept_name VARCHAR(100) COMMENT '部门名称',
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
                    UNIQUE KEY unique_emp_system (emp_id, system_name),
                    INDEX idx_emp_id (emp_id),
                    INDEX idx_dept_id (dept_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='人员系统权限矩阵表'
            """))
            conn.commit()
            print("人员系统权限矩阵表创建成功")
            
            result = conn.execute(text("""
                SELECT emp_id, emp_name, dept_code, dept_full_name 
                FROM employees_info 
                WHERE emp_id IS NOT NULL AND emp_id != '' 
                LIMIT 200
            """))
            employees = result.fetchall()
            print(f"从 employees_info 获取到 {len(employees)} 条人员信息")
            
            systems = [
                'OA办公系统', 'ERP企业资源计划', 'CRM客户关系管理', 'HR人力资源系统',
                '财务管理系统', '供应链管理系统', '生产制造系统MES', '资产管理系统',
                '知识管理系统', '项目管理系统', '数据分析平台', '邮件系统',
                '考勤系统', '门禁系统', '视频监控系统', '会议预约系统',
                '预算管理系统', '合同管理系统', '采购管理系统', '销售管理系统'
            ]
            
            if len(employees) == 0:
                print("警告：employees_info 表中没有人员数据，将创建示例数据")
                sample_employees = [
                    ('E001', '张三', 'D001', '研发部'),
                    ('E002', '李四', 'D002', '市场部'),
                    ('E003', '王五', 'D001', '研发部'),
                    ('E004', '赵六', 'D003', '财务部'),
                    ('E005', '钱七', 'D001', '研发部'),
                    ('E006', '孙八', 'D004', '人事部'),
                    ('E007', '周九', 'D002', '市场部'),
                    ('E008', '吴十', 'D005', 'IT部'),
                    ('E009', '郑一', 'D003', '财务部'),
                    ('E010', '陈二', 'D001', '研发部'),
                    ('E011', '刘三', 'D004', '人事部'),
                    ('E012', '杨四', 'D006', '行政部'),
                    ('E013', '黄五', 'D002', '市场部'),
                    ('E014', '林六', 'D005', 'IT部'),
                    ('E015', '徐七', 'D001', '研发部'),
                    ('E016', '何八', 'D007', '采购部'),
                    ('E017', '高九', 'D003', '财务部'),
                    ('E018', '马十', 'D008', '销售部'),
                    ('E019', '朱一', 'D004', '人事部'),
                    ('E020', '许二', 'D005', 'IT部'),
                ]
                employees = sample_employees
            
            permission_count = 0
            for emp in employees:
                emp_id = emp[0]
                emp_name = emp[1]
                dept_id = emp[2] if len(emp) > 2 and emp[2] else 'D000'
                dept_name = emp[3] if len(emp) > 3 and emp[3] else '未分配'
                
                for system in systems:
                    can_view = 1
                    can_add = 1
                    can_edit = 1 if emp_name not in ['保安', '保洁', '园林'] else 0
                    can_delete = 1 if '主管' in emp_name or '经理' in emp_name else 0
                    can_export = 1
                    can_import = 1 if '主管' in emp_name or '经理' in emp_name or 'IT' in dept_name else 0
                    can_approve = 1 if '经理' in emp_name or '主管' in emp_name else 0
                    can_config = 1 if 'IT' in dept_name and ('主管' in emp_name or '经理' in emp_name) else 0
                    
                    if system in ['门禁系统', '视频监控系统']:
                        can_add = 0
                        can_edit = 0
                        can_delete = 0
                        can_approve = 0
                    elif system == '考勤系统':
                        can_add = 0
                        can_edit = 0
                        can_delete = 0
                    
                    conn.execute(text("""
                        INSERT INTO person_system_permission_matrix 
                        (emp_id, emp_name, dept_id, dept_name, system_name, can_view, can_add, can_edit, can_delete, 
                         can_export, can_import, can_approve, can_config, permission_level, description)
                        VALUES (:emp_id, :emp_name, :dept_id, :dept_name, :system_name, :can_view, :can_add, :can_edit, :can_delete,
                                :can_export, :can_import, :can_approve, :can_config, :permission_level, :description)
                    """), {
                        'emp_id': emp_id,
                        'emp_name': emp_name,
                        'dept_id': dept_id,
                        'dept_name': dept_name,
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
                        'description': f'{emp_name}({emp_id}) - {system} 权限配置'
                    })
                    permission_count += 1
            
            conn.commit()
            print(f"成功插入 {permission_count} 条权限配置数据")
            
            result = conn.execute(text("SELECT COUNT(*) as cnt FROM person_system_permission_matrix"))
            count = result.fetchone()[0]
            print(f"表中共有 {count} 条记录")
            
            result = conn.execute(text("SELECT COUNT(DISTINCT emp_id) as cnt FROM person_system_permission_matrix"))
            emp_count = result.fetchone()[0]
            print(f"共 {emp_count} 名人员")
            
        except Exception as e:
            print(f"操作失败: {e}")
            import traceback
            traceback.print_exc()
            conn.rollback()
        finally:
            conn.close()

if __name__ == "__main__":
    create_person_system_permission_matrix()