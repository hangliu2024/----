from app import app, db
from sqlalchemy import text

def check_security_data():
    with app.app_context():
        conn = db.engine.connect()
        
        try:
            result = conn.execute(text("SELECT COUNT(*) FROM sys_role WHERE status = 1"))
            role_count = result.fetchone()[0]
            print(f"sys_role 表中有效角色数量: {role_count}")
            
            result = conn.execute(text("SELECT COUNT(*) FROM sys_module WHERE status = 1"))
            module_count = result.fetchone()[0]
            print(f"sys_module 表中有效模块数量: {module_count}")
            
            if role_count == 0:
                print("\n开始创建默认角色...")
                roles_data = [
                    ('超级管理员', 'super_admin', '系统最高权限，拥有所有功能和数据的管理权限', 1, 1),
                    ('系统管理员', 'admin', '负责系统日常管理和维护', 1, 2),
                    ('部门管理员', 'dept_admin', '管理本部门的人员和资产数据', 1, 3),
                    ('资产管理员', 'asset_admin', '负责资产的登记、变更、处置等', 1, 4),
                    ('人事管理员', 'hr_admin', '负责人员信息的维护和管理', 1, 5),
                    ('保密管理员', 'security_admin', '负责涉密资产和人员的管理', 1, 6),
                    ('普通用户', 'user', '仅可查看基本信息，无修改权限', 1, 7),
                ]
                
                for role in roles_data:
                    conn.execute(text("""
                        INSERT INTO sys_role (role_name, role_code, description, status, sort_order)
                        VALUES (:role_name, :role_code, :description, :status, :sort_order)
                    """), {
                        'role_name': role[0],
                        'role_code': role[1],
                        'description': role[2],
                        'status': role[3],
                        'sort_order': role[4]
                    })
                conn.commit()
                print(f"已创建 {len(roles_data)} 个默认角色")
            
            if module_count == 0:
                print("\n开始创建默认模块...")
                modules_data = [
                    ('资产管理', 'asset', 0, 'bi-box-seam', 1),
                    ('  有形资产', 'tangible_asset', 1, 'bi-cpu', 2),
                    ('  无形资产', 'intangible_asset', 1, 'bi-lightning-charge', 3),
                    ('  计算机资产', 'computer_asset', 1, 'bi-pc', 4),
                    ('人员管理', 'personnel', 0, 'bi-people', 5),
                    ('  人员信息', 'personnel_info', 1, 'bi-person-badge', 6),
                    ('  部门管理', 'department', 1, 'bi-diagram-3', 7),
                    ('保密管理', 'security', 0, 'bi-shield-lock', 8),
                    ('  涉密人员', 'classified_personnel', 1, 'bi-person-check', 9),
                    ('  涉密介质', 'classified_media', 1, 'bi-sd-card', 10),
                    ('  安全区域', 'security_zone', 1, 'bi-geo-alt', 11),
                    ('  涉密文件', 'classified_doc', 1, 'bi-file-earmark-lock', 12),
                    ('系统设置', 'system', 0, 'bi-gear', 13),
                    ('  角色管理', 'role_manage', 1, 'bi-person-gear', 14),
                    ('  模块管理', 'module_manage', 1, 'bi-grid-3x3', 15),
                    ('  权限配置', 'permission_config', 1, 'bi-key', 16),
                ]
                
                for mod in modules_data:
                    conn.execute(text("""
                        INSERT INTO sys_module (module_name, module_code, parent_id, icon, sort_order, status)
                        VALUES (:module_name, :module_code, :parent_id, :icon, :sort_order, 1)
                    """), {
                        'module_name': mod[0],
                        'module_code': mod[1],
                        'parent_id': mod[2],
                        'icon': mod[3],
                        'sort_order': mod[4]
                    })
                conn.commit()
                print(f"已创建 {len(modules_data)} 个默认模块")
            
            result = conn.execute(text("SELECT COUNT(*) FROM sys_role WHERE status = 1"))
            role_count = result.fetchone()[0]
            result = conn.execute(text("SELECT COUNT(*) FROM sys_module WHERE status = 1"))
            module_count = result.fetchone()[0]
            print(f"\n最终统计 - 角色: {role_count}, 模块: {module_count}")
            
        except Exception as e:
            print(f"操作失败: {e}")
            import traceback
            traceback.print_exc()
            conn.rollback()
        finally:
            conn.close()

if __name__ == "__main__":
    check_security_data()