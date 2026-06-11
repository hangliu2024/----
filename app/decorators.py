from functools import wraps
from flask import flash, redirect, url_for, request
from flask_login import current_user

def admin_required(f):
    """
    管理员权限装饰器
    只有admin角色的用户才能访问
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('请先登录', 'warning')
            return redirect(url_for('auth.login'))
        
        if current_user.role != 'admin':
            flash('您没有权限访问此页面，需要管理员权限', 'danger')
            return redirect(url_for('assets.dashboard'))
        
        return f(*args, **kwargs)
    
    return decorated_function

def permission_required(module_code, action='view'):
    """基于RBAC的细粒度权限校验装饰器

    用法:
        @permission_required('personnel_list', 'view')
        @permission_required('personnel_add', 'add')
        @permission_required('office_computers', 'edit')

    规则:
        1. admin 角色跳过所有检查
        2. 查 sys_user_role 获取角色
        3. 查 sys_module 获取模块ID
        4. 查 sys_permission 判断操作权限
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('请先登录', 'warning')
            return redirect(url_for('auth.login'))

        if current_user.role == 'admin':
            return f(*args, **kwargs)

        from app.models import SysUserRole, SysModule, SysPermission

        role_ids = [
            r.role_id for r in SysUserRole.query.filter_by(user_id=current_user.id).all()
        ]
        if not role_ids:
            flash('您尚未分配角色，请联系管理员', 'danger')
            return redirect(url_for('assets.dashboard'))

        module = SysModule.query.filter_by(module_code=module_code).first()
        if not module:
            return f(*args, **kwargs)

        perm = SysPermission.query.filter(
            SysPermission.module_id == module.id,
            SysPermission.role_id.in_(role_ids)
        ).first()

        action_field = f'can_{action}'

        if not perm or not getattr(perm, action_field, 0):
            action_names = {
                'view': '查看', 'add': '新增', 'edit': '编辑',
                'delete': '删除', 'export': '导出', 'import': '导入',
                'audit': '审核', 'approve': '审批'
            }
            flash(f'您没有{action_names.get(action, action)}权限', 'danger')
            return redirect(url_for('assets.dashboard'))

        return f(*args, **kwargs)

    return decorated_function

def get_user_permissions():
    """获取当前用户的所有权限字典，使用请求级别缓存减少DB查询
    
    优化说明：
    1. 使用 flask.g 对象存储权限缓存，确保每个请求独立
    2. 避免跨请求共享缓存导致的权限不同步问题
    3. 减少数据库查询次数
    """
    from flask import g
    from flask_login import current_user
    from app import db
    from sqlalchemy import text

    if not current_user.is_authenticated:
        return {}

    if current_user.role == 'admin':
        return {}

    # 使用请求级别的缓存（存储在 g 对象中）
    cache_key = f'_permission_cache_{current_user.id}'
    
    # 检查当前请求是否已缓存
    if hasattr(g, cache_key):
        return getattr(g, cache_key)

    # 查询数据库获取权限
    rows = db.session.execute(text("""
        SELECT m.module_code, p.can_view, p.can_add, p.can_edit, p.can_delete,
               p.can_export, p.can_import, p.can_audit, p.can_approve
        FROM sys_permission p
        JOIN sys_module m ON m.id = p.module_id
        JOIN sys_user_role ur ON ur.role_id = p.role_id
        WHERE ur.user_id = :uid AND m.status = 1
    """), {'uid': current_user.id}).fetchall()

    perms = {}
    for row in rows:
        perms[row[0]] = {
            'view': row[1], 'add': row[2], 'edit': row[3],
            'delete': row[4], 'export': row[5], 'import': row[6],
            'audit': row[7], 'approve': row[8]
        }

    # 存储到请求级别的缓存
    setattr(g, cache_key, perms)
    
    return perms


def clear_permission_cache(user_id=None):
    """清除权限缓存
    
    Args:
        user_id: 指定用户ID，如果为None则清除当前用户缓存
    """
    from flask import g
    from flask_login import current_user
    
    target_id = user_id or (current_user.id if current_user.is_authenticated else None)
    if target_id:
        cache_key = f'_permission_cache_{target_id}'
        if hasattr(g, cache_key):
            delattr(g, cache_key)

def department_permission_required(f):
    """
    部门权限装饰器：
    - admin: 可以查看所有部门数据
    - department_admin: 只能查看和管理自己部门的数据
    - user: 可以查看数据（数据过滤在路由中处理）
    
    注意：此装饰器主要用于验证登录状态，数据过滤逻辑在各个路由中实现
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('请先登录', 'warning')
            return redirect(url_for('auth.login'))
        
        # 如果是管理员，允许访问所有部门数据
        if current_user.role == 'admin':
            return f(*args, **kwargs)
        
        # 如果是部门管理员，检查部门配置
        if current_user.department_access:
            if not current_user.department_id:
                flash('您尚未分配部门，请联系管理员', 'warning')
                return redirect(url_for('assets.dashboard'))
            
            # 检查部门是否存在且激活
            from app.models import Department
            department = Department.query.get(current_user.department_id)
            if not department or not department.is_active:
                flash('您所在的部门不存在或已被禁用', 'warning')
                return redirect(url_for('assets.dashboard'))
            
            return f(*args, **kwargs)
        
        # 普通用户允许访问，数据过滤在路由中处理
        return f(*args, **kwargs)
    
    return decorated_function

def department_data_filter(query, department_id=None):
    """
    根据部门ID过滤数据查询
    - 如果department_id为None，则获取当前用户的部门
    - 如果是管理员，返回所有数据
    - 如果是部门管理员或用户，只返回该部门的数据
    """
    from app.models import Department
    
    # 如果指定了部门ID，使用指定的部门
    if department_id is not None:
        target_department_id = department_id
    else:
        target_department_id = current_user.department_id
    
    # 如果是管理员，返回所有数据
    if current_user.role == 'admin':
        return query
    
    # 如果用户没有部门权限，返回空查询
    if not current_user.department_access or not target_department_id:
        return query.filter(False)
    
    # 获取部门的所有子孙部门（包括部门本身）
    target_department = Department.query.get(target_department_id)
    if not target_department:
        return query.filter(False)
    
    # 获取该部门及其所有子孙部门的部门代码
    department_codes = get_department_codes_recursive(target_department_id)
    
    # 过滤数据：只返回匹配部门代码的资产
    from app.models import Personnel
    return query.filter(Personnel.dept_code.in_(department_codes))

def get_department_codes_recursive(department_id):
    """
    递归获取部门及其所有子孙部门的代码
    """
    from app.models import Department
    
    def get_codes_recursive(current_id):
        department = Department.query.get(current_id)
        if not department:
            return []
        
        codes = [department.code]
        # 递归获取所有子部门的代码
        for sub_dept in department.sub_departments:
            codes.extend(get_codes_recursive(sub_dept.id))
        
        return codes
    
    return get_codes_recursive(department_id)

def can_access_department(department_id):
    """
    检查当前用户是否有权限访问指定部门
    """
    if not current_user.is_authenticated:
        return False
    
    # 管理员可以访问所有部门
    if current_user.role == 'admin':
        return True
    
    # 部门管理员或用户只能访问自己的部门
    if current_user.department_access:
        if current_user.department_id == department_id:
            return True
        
        # 检查是否是上级部门
        target_department = Department.query.get(department_id)
        if target_department:
            user_department = Department.query.get(current_user.department_id)
            if user_department:
                # 检查目标部门是否是用户部门的子部门
                return is_child_department(department_id, current_user.department_id)
    
    return False

def is_child_department(child_id, parent_id):
    """
    检查child_id部门是否是parent_id部门的子部门（包括子孙部门）
    """
    from app.models import Department
    
    child_department = Department.query.get(child_id)
    if not child_department:
        return False
    
    # 向上遍历检查parent_id是否是child或其祖先
    current = child_department
    while current.parent:
        if current.parent.id == parent_id:
            return True
        current = current.parent
    
    return False

def get_user_accessible_departments():
    """
    获取当前用户可以访问的所有部门ID列表
    """
    if not current_user.is_authenticated:
        return []
    
    # 管理员可以访问所有部门
    if current_user.role == 'admin':
        from app.models import Department
        return [dept.id for dept in Department.query.filter_by(is_active=True).all()]
    
    # 部门管理员或用户只能访问自己部门
    if current_user.department_access and current_user.department_id:
        return [current_user.department_id]
    
    return []