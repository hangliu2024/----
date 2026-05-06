"""
系统管理路由 - 用户管理、角色管理、日志管理等
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from sqlalchemy import or_
from app import db, bcrypt
from app.models import User, Department, LoginLog, OperationLog, SysRole, SysUserRole
from app.decorators import admin_required
from functools import wraps

bp = Blueprint('admin', __name__, url_prefix='/admin')


# ==================== 用户管理 ====================

@bp.route('/users')
@login_required
@admin_required
def users():
    """用户列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 15, type=int)
    search = request.args.get('search', '')
    role_filter = request.args.get('role', '')
    status_filter = request.args.get('status', '')
    dept_filter = request.args.get('dept', '')
    
    query = User.query
    
    # 搜索
    if search:
        query = query.filter(
            or_(
                User.username.contains(search),
                User.email.contains(search),
                User.real_name.contains(search),
                User.emp_id.contains(search)
            )
        )
    
    # 角色筛选
    if role_filter:
        query = query.filter(User.role == role_filter)
    
    # 状态筛选
    if status_filter:
        is_active = status_filter == 'active'
        query = query.filter(User.is_active == is_active)
    
    # 部门筛选
    if dept_filter:
        query = query.filter(User.department_id == dept_filter)
    
    # 排序
    query = query.order_by(User.created_at.desc())
    
    # 分页
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    users = pagination.items
    
    # 获取所有部门（用于筛选下拉框）
    departments = Department.query.filter_by(is_active=True).all()
    
    return render_template('admin/users.html', 
                         users=users, 
                         pagination=pagination,
                         departments=departments,
                         search=search,
                         role_filter=role_filter,
                         status_filter=status_filter,
                         dept_filter=dept_filter)


@bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_user():
    """新增用户"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        real_name = request.form.get('real_name')
        emp_id = request.form.get('emp_id')
        phone = request.form.get('phone')
        role = request.form.get('role', 'user')
        department_id = request.form.get('department_id')
        
        # 验证
        if not username or not email or not password:
            flash('用户名、邮箱和密码为必填项', 'danger')
            return redirect(url_for('admin.add_user'))
        
        if password != confirm_password:
            flash('两次密码输入不一致', 'danger')
            return redirect(url_for('admin.add_user'))
        
        # 检查用户名和邮箱是否已存在
        if User.query.filter_by(username=username).first():
            flash('用户名已存在', 'danger')
            return redirect(url_for('admin.add_user'))
        
        if User.query.filter_by(email=email).first():
            flash('邮箱已存在', 'danger')
            return redirect(url_for('admin.add_user'))
        
        # 创建用户
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(
            username=username,
            email=email,
            password=hashed_password,
            real_name=real_name,
            emp_id=emp_id,
            phone=phone,
            role=role,
            department_id=department_id if department_id else None,
            is_active=True
        )
        db.session.add(user)
        db.session.commit()
        
        # 记录操作日志
        log_operation('add', '用户管理', f'新增用户: {username}')
        
        flash('用户创建成功', 'success')
        return redirect(url_for('admin.users'))
    
    # GET请求 - 显示表单
    departments = Department.query.filter_by(is_active=True).all()
    return render_template('admin/user_form.html', user=None, departments=departments)


@bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """编辑用户"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.username = request.form.get('username', user.username)
        user.email = request.form.get('email', user.email)
        user.real_name = request.form.get('real_name')
        user.emp_id = request.form.get('emp_id')
        user.phone = request.form.get('phone')
        user.role = request.form.get('role', user.role)
        department_id = request.form.get('department_id')
        user.department_id = department_id if department_id else None
        user.updated_at = datetime.utcnow()
        
        # 检查用户名和邮箱是否被其他用户占用
        existing_user = User.query.filter(User.username == user.username, User.id != user_id).first()
        if existing_user:
            flash('用户名已存在', 'danger')
            return redirect(url_for('admin.edit_user', user_id=user_id))
        
        existing_email = User.query.filter(User.email == user.email, User.id != user_id).first()
        if existing_email:
            flash('邮箱已存在', 'danger')
            return redirect(url_for('admin.edit_user', user_id=user_id))
        
        db.session.commit()
        
        # 记录操作日志
        log_operation('edit', '用户管理', f'编辑用户: {user.username}')
        
        flash('用户信息已更新', 'success')
        return redirect(url_for('admin.users'))
    
    # GET请求 - 显示表单
    departments = Department.query.filter_by(is_active=True).all()
    return render_template('admin/user_form.html', user=user, departments=departments)


@bp.route('/users/toggle/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def toggle_user(user_id):
    """启用/禁用用户"""
    user = User.query.get_or_404(user_id)
    
    # 不能禁用自己
    if user.id == current_user.id:
        return jsonify({'success': False, 'message': '不能禁用自己的账号'})
    
    user.is_active = not user.is_active
    user.updated_at = datetime.utcnow()
    db.session.commit()
    
    # 记录操作日志
    action = '启用' if user.is_active else '禁用'
    log_operation('edit', '用户管理', f'{action}用户: {user.username}')
    
    return jsonify({
        'success': True, 
        'message': f'用户已{"启用" if user.is_active else "禁用"}',
        'is_active': user.is_active
    })


@bp.route('/users/reset-password/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def reset_password(user_id):
    """重置用户密码"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if not new_password:
            flash('请输入新密码', 'danger')
            return redirect(url_for('admin.reset_password', user_id=user_id))
        
        if new_password != confirm_password:
            flash('两次密码输入不一致', 'danger')
            return redirect(url_for('admin.reset_password', user_id=user_id))
        
        user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        # 记录操作日志
        log_operation('edit', '用户管理', f'重置用户密码: {user.username}')
        
        flash('密码重置成功', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/reset_password.html', user=user)


@bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """删除用户"""
    user = User.query.get_or_404(user_id)
    
    # 不能删除自己
    if user.id == current_user.id:
        return jsonify({'success': False, 'message': '不能删除自己的账号'})
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    # 记录操作日志
    log_operation('delete', '用户管理', f'删除用户: {username}')
    
    return jsonify({'success': True, 'message': '用户已删除'})


# ==================== 登录日志 ====================

@bp.route('/login-logs')
@login_required
@admin_required
def login_logs():
    """登录日志列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    user_id = request.args.get('user_id', '')
    login_type = request.args.get('login_type', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    query = LoginLog.query
    
    # 用户筛选
    if user_id:
        query = query.filter(LoginLog.user_id == user_id)
    
    # 类型筛选
    if login_type:
        query = query.filter(LoginLog.login_type == login_type)
    
    # 日期筛选
    if date_from:
        query = query.filter(LoginLog.login_time >= date_from + ' 00:00:00')
    if date_to:
        query = query.filter(LoginLog.login_time <= date_to + ' 23:59:59')
    
    # 排序
    query = query.order_by(LoginLog.login_time.desc())
    
    # 分页
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    logs = pagination.items
    
    # 获取所有用户（用于筛选）
    users = User.query.all()
    
    return render_template('admin/login_logs.html',
                         logs=logs,
                         pagination=pagination,
                         users=users,
                         user_id=user_id,
                         login_type=login_type,
                         date_from=date_from,
                         date_to=date_to)


# ==================== 操作日志 ====================

@bp.route('/operation-logs')
@login_required
@admin_required
def operation_logs():
    """操作日志列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    user_id = request.args.get('user_id', '')
    operation_type = request.args.get('operation_type', '')
    module = request.args.get('module', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    query = OperationLog.query
    
    # 用户筛选
    if user_id:
        query = query.filter(OperationLog.user_id == user_id)
    
    # 操作类型筛选
    if operation_type:
        query = query.filter(OperationLog.operation_type == operation_type)
    
    # 模块筛选
    if module:
        query = query.filter(OperationLog.module == module)
    
    # 日期筛选
    if date_from:
        query = query.filter(OperationLog.created_at >= date_from + ' 00:00:00')
    if date_to:
        query = query.filter(OperationLog.created_at <= date_to + ' 23:59:59')
    
    # 排序
    query = query.order_by(OperationLog.created_at.desc())
    
    # 分页
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    logs = pagination.items
    
    # 获取所有用户和模块（用于筛选）
    users = User.query.all()
    modules = db.session.query(OperationLog.module).distinct().all()
    modules = [m[0] for m in modules if m[0]]
    
    return render_template('admin/operation_logs.html',
                         logs=logs,
                         pagination=pagination,
                         users=users,
                         modules=modules,
                         user_id=user_id,
                         operation_type=operation_type,
                         module=module,
                         date_from=date_from,
                         date_to=date_to)


# ==================== 辅助函数 ====================

def log_operation(operation_type, module, description):
    """记录操作日志"""
    try:
        log = OperationLog(
            user_id=current_user.id,
            username=current_user.username,
            operation_type=operation_type,
            module=module,
            description=description,
            ip_address=request.remote_addr,
            request_url=request.url,
            request_method=request.method
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f'记录操作日志失败: {e}')