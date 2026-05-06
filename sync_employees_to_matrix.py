from app import app, db
from sqlalchemy import text

def sync_employees():
    with app.app_context():
        conn = db.engine.connect()
        
        try:
            print("开始同步员工到权限矩阵表...")
            
            result = conn.execute(text("""
                SELECT DISTINCT emp_id, emp_name, dept_code, dept_full_name 
                FROM employees_info 
                WHERE emp_id IS NOT NULL AND emp_id != '' AND emp_id != 'emp_id'
            """))
            employees = result.fetchall()
            total_emp = len(employees)
            print(f"从 employees_info 获取到 {total_emp} 名员工")
            
            conn.execute(text("DELETE FROM person_system_permission_matrix"))
            conn.commit()
            print("已清空旧数据")
            
            systems = [
                'OA办公系统', 'ERP企业资源计划', 'CRM客户关系管理', 'HR人力资源系统',
                '财务管理系统', '供应链管理系统', '生产制造系统MES', '资产管理系统',
                '知识管理系统', '项目管理系统', '数据分析平台', '邮件系统',
                '考勤系统', '门禁系统', '视频监控系统', '会议预约系统',
                '预算管理系统', '合同管理系统', '采购管理系统', '销售管理系统'
            ]
            
            batch = []
            batch_size = 500
            total_inserted = 0
            
            for emp in employees:
                emp_id = emp[0]
                emp_name = emp[1] or ''
                dept_id = emp[2] or ''
                dept_name = emp[3] or ''
                
                if not emp_id or emp_id == 'emp_id':
                    continue
                
                for system in systems:
                    batch.append({
                        'emp_id': emp_id,
                        'emp_name': emp_name,
                        'dept_id': dept_id,
                        'dept_name': dept_name,
                        'system_name': system,
                        'can_view': 1,
                        'can_add': 0,
                        'can_edit': 0,
                        'can_delete': 0,
                        'can_export': 0,
                        'can_import': 0,
                        'can_approve': 0,
                        'can_config': 0,
                        'permission_level': 'basic'
                    })
                
                if len(batch) >= batch_size:
                    conn.execute(text("""
                        INSERT INTO person_system_permission_matrix 
                        (emp_id, emp_name, dept_id, dept_name, system_name, can_view, can_add, can_edit, can_delete, 
                         can_export, can_import, can_approve, can_config, permission_level)
                        VALUES (:emp_id, :emp_name, :dept_id, :dept_name, :system_name, :can_view, :can_add, :can_edit, :can_delete, 
                                :can_export, :can_import, :can_approve, :can_config, :permission_level)
                    """), batch)
                    conn.commit()
                    total_inserted += len(batch)
                    print(f"已插入 {total_inserted} 条记录...")
                    batch = []
            
            if batch:
                conn.execute(text("""
                    INSERT INTO person_system_permission_matrix 
                    (emp_id, emp_name, dept_id, dept_name, system_name, can_view, can_add, can_edit, can_delete, 
                     can_export, can_import, can_approve, can_config, permission_level)
                    VALUES (:emp_id, :emp_name, :dept_id, :dept_name, :system_name, :can_view, :can_add, :can_edit, :can_delete, 
                            :can_export, :can_import, :can_approve, :can_config, :permission_level)
                """), batch)
                conn.commit()
                total_inserted += len(batch)
                print(f"已插入最后 {len(batch)} 条记录...")
            
            result = conn.execute(text("SELECT COUNT(*) as cnt FROM person_system_permission_matrix"))
            total = result.fetchone()[0]
            result = conn.execute(text("SELECT COUNT(DISTINCT emp_id) as cnt FROM person_system_permission_matrix"))
            emp_count = result.fetchone()[0]
            print(f"完成！权限矩阵表中共 {total} 条记录，{emp_count} 名员工")
            
        except Exception as e:
            print(f"操作失败: {e}")
            import traceback
            traceback.print_exc()
            conn.rollback()
        finally:
            conn.close()

if __name__ == "__main__":
    sync_employees()