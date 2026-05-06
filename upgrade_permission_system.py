"""
升级权限矩阵系统为专业的RBAC模型
包括：角色表、功能模块表、权限配置表
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pymysql

# 数据库配置
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://nocobase:nocobase@127.0.0.1:3307/nocobase'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def upgrade_permission_system():
    with app.app_context():
        try:
            print("开始升级权限矩阵系统...")
            
            # 1. 创建角色表 (sys_role)
            print("\n1. 创建角色表 sys_role...")
            db.session.execute(db.text("""
                CREATE TABLE IF NOT EXISTS sys_role (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    role_name VARCHAR(50) NOT NULL COMMENT '角色名称',
                    role_code VARCHAR(50) NOT NULL UNIQUE COMMENT '角色编码',
                    description TEXT COMMENT '角色描述',
                    status TINYINT DEFAULT 1 COMMENT '状态: 1-启用, 0-禁用',
                    sort_order INT DEFAULT 0 COMMENT '排序',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    created_by INT COMMENT '创建人ID'
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色表'
            """))
            db.session.commit()
            print("✅ 角色表创建成功")
            
            # 2. 创建功能模块表 (sys_module)
            print("\n2. 创建功能模块表 sys_module...")
            db.session.execute(db.text("""
                CREATE TABLE IF NOT EXISTS sys_module (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    module_name VARCHAR(50) NOT NULL COMMENT '模块名称',
                    module_code VARCHAR(50) NOT NULL UNIQUE COMMENT '模块编码',
                    parent_id INT DEFAULT 0 COMMENT '父模块ID',
                    module_type VARCHAR(20) DEFAULT 'menu' COMMENT '类型: menu-菜单, button-按钮, api-接口',
                    route_path VARCHAR(200) COMMENT '路由路径',
                    icon VARCHAR(50) COMMENT '图标',
                    sort_order INT DEFAULT 0 COMMENT '排序',
                    status TINYINT DEFAULT 1 COMMENT '状态: 1-启用, 0-禁用',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='功能模块表'
            """))
            db.session.commit()
            print("✅ 功能模块表创建成功")
            
            # 3. 创建权限配置表 (sys_permission)
            print("\n3. 创建权限配置表 sys_permission...")
            db.session.execute(db.text("""
                CREATE TABLE IF NOT EXISTS sys_permission (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    role_id INT NOT NULL COMMENT '角色ID',
                    module_id INT NOT NULL COMMENT '模块ID',
                    can_view TINYINT DEFAULT 0 COMMENT '查看权限',
                    can_add TINYINT DEFAULT 0 COMMENT '新增权限',
                    can_edit TINYINT DEFAULT 0 COMMENT '编辑权限',
                    can_delete TINYINT DEFAULT 0 COMMENT '删除权限',
                    can_export TINYINT DEFAULT 0 COMMENT '导出权限',
                    can_import TINYINT DEFAULT 0 COMMENT '导入权限',
                    can_audit TINYINT DEFAULT 0 COMMENT '审核权限',
                    can_approve TINYINT DEFAULT 0 COMMENT '审批权限',
                    data_scope VARCHAR(20) DEFAULT 'self' COMMENT '数据范围: all-全部, dept-本部门, self-仅本人',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    UNIQUE KEY uk_role_module (role_id, module_id),
                    FOREIGN KEY (role_id) REFERENCES sys_role(id) ON DELETE CASCADE,
                    FOREIGN KEY (module_id) REFERENCES sys_module(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='权限配置表'
            """))
            db.session.commit()
            print("✅ 权限配置表创建成功")
            
            # 4. 创建用户角色关联表 (sys_user_role)
            print("\n4. 创建用户角色关联表 sys_user_role...")
            db.session.execute(db.text("""
                CREATE TABLE IF NOT EXISTS sys_user_role (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    user_id INT NOT NULL COMMENT '用户ID',
                    role_id INT NOT NULL COMMENT '角色ID',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY uk_user_role (user_id, role_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户角色关联表'
            """))
            db.session.commit()
            print("✅ 用户角色关联表创建成功")
            
            # 5. 创建数据权限表 (sys_data_permission)
            print("\n5. 创建数据权限表 sys_data_permission...")
            db.session.execute(db.text("""
                CREATE TABLE IF NOT EXISTS sys_data_permission (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    role_id INT NOT NULL COMMENT '角色ID',
                    dept_id VARCHAR(50) NOT NULL COMMENT '部门ID',
                    permission_type VARCHAR(20) DEFAULT 'view' COMMENT '权限类型: view-查看, edit-编辑, full-完全',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY uk_role_dept (role_id, dept_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='数据权限表'
            """))
            db.session.commit()
            print("✅ 数据权限表创建成功")
            
            # 6. 插入默认角色
            print("\n6. 插入默认角色...")
            db.session.execute(db.text("""
                INSERT IGNORE INTO sys_role (role_name, role_code, description, status, sort_order) VALUES
                ('超级管理员', 'super_admin', '系统超级管理员，拥有所有权限', 1, 1),
                ('系统管理员', 'admin', '系统管理员，拥有大部分管理权限', 1, 2),
                ('部门管理员', 'dept_admin', '部门管理员，管理本部门数据', 1, 3),
                ('资产管理员', 'asset_manager', '负责资产管理相关业务', 1, 4),
                ('人事管理员', 'hr_manager', '负责人员管理相关业务', 1, 5),
                ('保密管理员', 'security_manager', '负责保密管理相关业务', 1, 6),
                ('普通用户', 'user', '普通用户，基础查看权限', 1, 7)
            """))
            db.session.commit()
            print("✅ 默认角色插入成功")
            
            # 7. 插入功能模块
            print("\n7. 插入功能模块...")
            db.session.execute(db.text("""
                INSERT IGNORE INTO sys_module (module_name, module_code, parent_id, module_type, route_path, icon, sort_order, status) VALUES
                -- 一级菜单
                ('首页', 'dashboard', 0, 'menu', '/dashboard', 'bi-house', 1, 1),
                ('人员管理', 'personnel', 0, 'menu', '/personnel', 'bi-people', 2, 1),
                ('资产管理', 'assets', 0, 'menu', '/assets', 'bi-box', 3, 1),
                ('部门管理', 'departments', 0, 'menu', '/departments', 'bi-diagram-3', 4, 1),
                ('保密管理', 'security', 0, 'menu', '/security', 'bi-shield-lock', 5, 1),
                ('AI助手', 'ai_assistant', 0, 'menu', '/ai-assistant', 'bi-robot', 6, 1),
                ('系统设置', 'settings', 0, 'menu', '/settings', 'bi-gear', 7, 1),
                
                -- 人员管理子模块
                ('人员列表', 'personnel_list', 2, 'menu', '/personnel', 'bi-list', 1, 1),
                ('人员新增', 'personnel_add', 2, 'button', '', 'bi-plus', 2, 1),
                ('人员编辑', 'personnel_edit', 2, 'button', '', 'bi-pencil', 3, 1),
                ('人员删除', 'personnel_delete', 2, 'button', '', 'bi-trash', 4, 1),
                ('人员导出', 'personnel_export', 2, 'button', '', 'bi-download', 5, 1),
                
                -- 资产管理子模块
                ('有形资产', 'tangible_assets', 3, 'menu', '/assets/tangible', 'bi-box', 1, 1),
                ('无形资产', 'intangible_assets', 3, 'menu', '/assets/intangible', 'bi-file-earmark', 2, 1),
                ('办公电脑', 'office_computers', 3, 'menu', '/assets/computers', 'bi-pc-display', 3, 1),
                ('工控机', 'industrial_computers', 3, 'menu', '/assets/industrial', 'bi-hdd', 4, 1),
                
                -- 保密管理子模块
                ('权限矩阵', 'permission_matrix', 5, 'menu', '/security/permission', 'bi-grid', 1, 1),
                ('涉密人员', 'classified_personnel', 5, 'menu', '/security/classified-personnel', 'bi-person-lock', 2, 1),
                ('涉密介质', 'classified_media', 5, 'menu', '/security/classified-media', 'bi-usb-drive', 3, 1),
                ('安全区域', 'security_zone', 5, 'menu', '/security/zones', 'bi-geo-alt', 4, 1),
                ('电子文件', 'electronic_docs', 5, 'menu', '/security/electronic-docs', 'bi-file-earmark-lock', 5, 1),
                ('纸质文件', 'paper_docs', 5, 'menu', '/security/paper-docs', 'bi-journal', 6, 1),
                
                -- 系统设置子模块
                ('用户管理', 'user_management', 7, 'menu', '/settings/users', 'bi-person-gear', 1, 1),
                ('角色管理', 'role_management', 7, 'menu', '/settings/roles', 'bi-people-fill', 2, 1),
                ('权限配置', 'permission_config', 7, 'menu', '/settings/permissions', 'bi-key', 3, 1),
                ('AI配置', 'ai_config', 7, 'menu', '/ai-settings', 'bi-robot', 4, 1),
                
                -- 操作日志
                ('操作日志', 'operation_log', 7, 'menu', '/settings/logs', 'bi-clock-history', 5, 1)
            """))
            db.session.commit()
            print("✅ 功能模块插入成功")
            
            # 8. 为超级管理员分配所有权限
            print("\n8. 为超级管理员分配权限...")
            db.session.execute(db.text("""
                INSERT IGNORE INTO sys_permission (role_id, module_id, can_view, can_add, can_edit, can_delete, can_export, can_import, can_audit, can_approve, data_scope)
                SELECT 1, id, 1, 1, 1, 1, 1, 1, 1, 1, 'all'
                FROM sys_module
            """))
            db.session.commit()
            print("✅ 超级管理员权限分配成功")
            
            # 9. 更新旧的permission_matrix表（添加更多字段）
            print("\n9. 更新permission_matrix表结构...")
            
            # 检查并添加新列
            columns_to_add = {
                'permission_code': 'VARCHAR(50) NULL COMMENT "权限编码"',
                'permission_type': 'VARCHAR(20) DEFAULT "view" COMMENT "权限类型"',
                'resource_type': 'VARCHAR(50) NULL COMMENT "资源类型: menu, button, api"',
                'resource_id': 'VARCHAR(100) NULL COMMENT "资源ID"',
                'action_list': 'VARCHAR(200) DEFAULT "view" COMMENT "操作列表: view,add,edit,delete"',
                'condition_expr': 'TEXT NULL COMMENT "权限条件表达式"',
                'status': 'TINYINT DEFAULT 1 COMMENT "状态: 1-启用, 0-禁用"',
                'updated_at': 'DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP',
                'created_by': 'INT NULL COMMENT "创建人ID"'
            }
            
            for col_name, col_def in columns_to_add.items():
                try:
                    db.session.execute(db.text(f"""
                        SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS 
                        WHERE TABLE_SCHEMA = 'nocobase' AND TABLE_NAME = 'permission_matrix' AND COLUMN_NAME = '{col_name}'
                    """))
                    if not db.session.execute(db.text(f"SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'nocobase' AND TABLE_NAME = 'permission_matrix' AND COLUMN_NAME = '{col_name}'")).fetchone():
                        db.session.execute(db.text(f"ALTER TABLE permission_matrix ADD COLUMN {col_name} {col_def}"))
                        db.session.commit()
                        print(f"✅ 添加列 {col_name}")
                except Exception as e:
                    print(f"列 {col_name} 可能已存在: {str(e)}")
            
            print("\n✅ 权限矩阵系统升级完成！")
            print("\n创建的表：")
            print("  - sys_role (角色表)")
            print("  - sys_module (功能模块表)")
            print("  - sys_permission (权限配置表)")
            print("  - sys_user_role (用户角色关联表)")
            print("  - sys_data_permission (数据权限表)")
            print("\n默认角色：超级管理员、系统管理员、部门管理员、资产管理员、人事管理员、保密管理员、普通用户")
            
        except Exception as e:
            print(f"❌ 错误: {str(e)}")
            db.session.rollback()
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    upgrade_permission_system()