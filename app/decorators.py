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

def department_permission_required(f):
    """
    部门权限装饰器：
    - admin: 可以查看所有部门数据
    - department_admin: 只能查看和管理自己部门的数据
    - user: 只能查看自己部门的数据（如果有部门关联）
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('请先登录', 'warning')
            return redirect(url_for('auth.login'))
        
        # 如果是管理员，允许访问所有部门数据
        if current_user.role == 'admin':
            return f(*args, **kwargs)
        
        # 如果是部门管理员或用户，需要检查部门权限
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
        
        # 默认情况，不允许访问
        flash('您没有权限访问此页面', 'danger')
        return redirect(url_for('assets.dashboard'))
    
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