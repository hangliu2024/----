from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Department, User, Personnel
from app.forms import DepartmentForm, UserDepartmentForm
from sqlalchemy import text

bp = Blueprint('departments', __name__)

@bp.route('/manage', methods=['GET', 'POST'])
@login_required
def manage_departments():
    """管理部门"""
    if current_user.role != 'admin':
        flash('您没有权限访问此页面', 'danger')
        return redirect(url_for('assets.dashboard'))

    dept_level2_map = {}
    rows = db.session.execute(text(
        "SELECT DISTINCT dept_level2, dept_code FROM employees_info WHERE dept_level2 IS NOT NULL AND dept_code IS NOT NULL"
    )).fetchall()
    for row in rows:
        dept_level2_map[row[0]] = row[1]
    
    # 同步部门数据
    if request.method == 'POST':
        db.session.execute(text('SET FOREIGN_KEY_CHECKS = 0'))
        # 删除所有部门
        Department.query.delete()
        db.session.commit()
        # 重新启用外键约束
        db.session.execute(text('SET FOREIGN_KEY_CHECKS = 1'))
        
        # 创建根部门
        root_dept = Department(
            name='总公司',
            code='TOTAL',
            description='公司总部',
            level=1
        )
        db.session.add(root_dept)
        db.session.commit()
        
        # 创建二级部门
        for dept_name, dept_code in dept_level2_map.items():
            dept = Department(
                name=dept_name,
                code=dept_code,
                description=f'{dept_name}',
                level=2,
                parent_id=root_dept.id
            )
            db.session.add(dept)
        
        db.session.commit()
        flash('部门数据已从人员表同步', 'success')
        return redirect(url_for('departments.manage_departments'))
    
    departments = Department.query.all()
    return render_template('departments/manage.html', departments=departments, dept_level2_map=dept_level2_map)

@bp.route('/user/<int:user_id>/departments', methods=['GET', 'POST'])
@login_required
def manage_user_departments(user_id):
    """管理用户的部门权限"""
    if current_user.role != 'admin':
        flash('您没有权限访问此页面', 'danger')
        return redirect(url_for('assets.dashboard'))
    
    user = User.query.get_or_404(user_id)
    departments = Department.query.filter_by(level=2).all()  # 只显示二级部门
    
    if request.method == 'POST':
        department_id = request.form.get('department_id')
        department_access = 'department_access' in request.form
        
        user.department_id = department_id if department_id else None
        user.department_access = department_access
        db.session.commit()
        
        flash('用户部门权限已更新', 'success')
        return redirect(url_for('departments.manage_users'))
    
    return render_template('departments/user_departments.html', user=user, departments=departments)

@bp.route('/users')
@login_required
def manage_users():
    """管理用户列表"""
    if current_user.role != 'admin':
        flash('您没有权限访问此页面', 'danger')
        return redirect(url_for('assets.dashboard'))
    
    users = User.query.all()
    return render_template('departments/manage_users.html', users=users)
