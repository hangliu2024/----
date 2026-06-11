from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models import AuditTask, AuditTaskFeedback, AuditRecord, User, Department
from app.decorators import admin_required

audit_bp = Blueprint('audit', __name__, url_prefix='/audit')

def _is_admin():
    return current_user.role == 'admin'

# 稽查任务列表（管理员视图）
@audit_bp.route('/tasks')
@login_required
def task_list():
    """稽查任务列表"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    task_type = request.args.get('type', '')
    
    query = AuditTask.query
    
    if not _is_admin():
        query = query.filter_by(assignee_id=current_user.id)
    
    if status:
        query = query.filter_by(status=status)
    if task_type:
        query = query.filter_by(task_type=task_type)
    
    tasks = query.order_by(AuditTask.created_at.desc()).paginate(page=page, per_page=20)
    
    return render_template('audit/task_list.html', tasks=tasks, status=status, task_type=task_type)

# 创建稽查任务
@audit_bp.route('/tasks/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_task():
    """创建稽查任务"""
    if request.method == 'POST':
        # 生成任务编号
        today = datetime.now().strftime('%Y%m%d')
        count = AuditTask.query.filter(AuditTask.task_no.like(f'AT{today}%')).count() + 1
        task_no = f'AT{today}{count:04d}'
        
        task = AuditTask(
            task_no=task_no,
            task_title=request.form.get('task_title'),
            task_type=request.form.get('task_type'),
            task_content=request.form.get('task_content'),
            task_requirement=request.form.get('task_requirement'),
            priority=request.form.get('priority', 'normal'),
            assignee_id=request.form.get('assignee_id', type=int),
            assigner_id=current_user.id,
            dept_id=request.form.get('dept_id', type=int),
            dept_name=request.form.get('dept_name'),
            deadline=datetime.strptime(request.form.get('deadline'), '%Y-%m-%d %H:%M') if request.form.get('deadline') else None,
            status='pending'
        )
        
        db.session.add(task)
        db.session.commit()
        
        flash(f'稽查任务 {task_no} 创建成功！', 'success')
        return redirect(url_for('audit.task_list'))
    
    # 获取用户列表用于选择被分配人
    users = User.query.filter_by(role='user').all()
    departments = Department.query.filter_by(is_active=True).all()
    
    return render_template('audit/task_form.html', users=users, departments=departments)

# 任务详情
@audit_bp.route('/tasks/<int:task_id>')
@login_required
def task_detail(task_id):
    """任务详情"""
    task = AuditTask.query.get_or_404(task_id)
    
    # 权限检查：管理员或被分配人可以查看
    if not _is_admin() and task.assignee_id != current_user.id:
        flash('您没有权限查看此任务', 'danger')
        return redirect(url_for('audit.task_list'))
    
    return render_template('audit/task_detail.html', task=task)

# 开始执行任务
@audit_bp.route('/tasks/<int:task_id>/start', methods=['POST'])
@login_required
def start_task(task_id):
    """开始执行任务"""
    task = AuditTask.query.get_or_404(task_id)
    
    if task.assignee_id != current_user.id:
        return jsonify({'success': False, 'message': '您没有权限操作此任务'}), 403
    
    if task.status != 'pending':
        return jsonify({'success': False, 'message': '任务状态不正确'}), 400
    
    task.status = 'in_progress'
    task.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'success': True, 'message': '任务已开始执行'})

# 提交任务反馈
@audit_bp.route('/tasks/<int:task_id>/feedback', methods=['POST'])
@login_required
def submit_feedback(task_id):
    """提交任务反馈"""
    task = AuditTask.query.get_or_404(task_id)
    
    if task.assignee_id != current_user.id:
        return jsonify({'success': False, 'message': '您没有权限操作此任务'}), 403
    
    feedback = AuditTaskFeedback(
        task_id=task_id,
        feedback_content=request.form.get('feedback_content'),
        feedback_type=request.form.get('feedback_type', 'report'),
        feedback_by=current_user.id
    )
    
    db.session.add(feedback)
    
    # 如果是完成报告，更新任务状态
    if request.form.get('mark_complete') == 'true':
        task.status = 'completed'
        task.completed_at = datetime.utcnow()
    
    task.updated_at = datetime.utcnow()
    db.session.commit()
    
    flash('反馈提交成功！', 'success')
    return redirect(url_for('audit.task_detail', task_id=task_id))

# 关闭任务
@audit_bp.route('/tasks/<int:task_id>/close', methods=['POST'])
@login_required
@admin_required
def close_task(task_id):
    """关闭任务"""
    task = AuditTask.query.get_or_404(task_id)
    
    task.status = 'closed'
    task.updated_at = datetime.utcnow()
    db.session.commit()
    
    flash('任务已关闭', 'success')
    return redirect(url_for('audit.task_detail', task_id=task_id))

# 我的任务（用户视图）
@audit_bp.route('/my-tasks')
@login_required
def my_tasks():
    """我的任务"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    
    query = AuditTask.query.filter_by(assignee_id=current_user.id)
    
    if status:
        query = query.filter_by(status=status)
    
    tasks = query.order_by(AuditTask.created_at.desc()).paginate(page=page, per_page=20)
    
    return render_template('audit/my_tasks.html', tasks=tasks, status=status)

# 稽查记录列表
@audit_bp.route('/records')
@login_required
def record_list():
    """稽查记录列表"""
    page = request.args.get('page', 1, type=int)
    
    query = AuditRecord.query
    
    # 非管理员只能看到自己的记录
    if not _is_admin():
        query = query.filter_by(audit_by=current_user.id)
    
    records = query.order_by(AuditRecord.created_at.desc()).paginate(page=page, per_page=20)
    
    return render_template('audit/record_list.html', records=records)

# 创建稽查记录
@audit_bp.route('/records/create', methods=['GET', 'POST'])
@login_required
def create_record():
    """创建稽查记录"""
    if request.method == 'POST':
        record = AuditRecord(
            task_id=request.form.get('task_id', type=int),
            audit_type=request.form.get('audit_type'),
            audit_scope=request.form.get('audit_scope'),
            audit_content=request.form.get('audit_content'),
            audit_result=request.form.get('audit_result'),
            issue_found=request.form.get('issue_found'),
            suggestion=request.form.get('suggestion'),
            audit_by=current_user.id,
            audit_date=datetime.strptime(request.form.get('audit_date'), '%Y-%m-%d') if request.form.get('audit_date') else datetime.utcnow(),
            status='draft'
        )
        
        db.session.add(record)
        db.session.commit()
        
        flash('稽查记录创建成功！', 'success')
        return redirect(url_for('audit.record_list'))
    
    # 获取关联的任务
    tasks = AuditTask.query.filter_by(assignee_id=current_user.id, status='in_progress').all()
    
    return render_template('audit/record_form.html', tasks=tasks)

# 任务统计
@audit_bp.route('/statistics')
@login_required
@admin_required
def statistics():
    """任务统计"""
    # 总任务数
    total_tasks = AuditTask.query.count()
    
    # 各状态任务数
    pending_count = AuditTask.query.filter_by(status='pending').count()
    in_progress_count = AuditTask.query.filter_by(status='in_progress').count()
    completed_count = AuditTask.query.filter_by(status='completed').count()
    closed_count = AuditTask.query.filter_by(status='closed').count()
    
    # 各类型任务数
    type_stats = db.session.query(
        AuditTask.task_type,
        db.func.count(AuditTask.id)
    ).group_by(AuditTask.task_type).all()
    
    # 逾期任务
    overdue_tasks = AuditTask.query.filter(
        AuditTask.deadline < datetime.utcnow(),
        AuditTask.status.in_(['pending', 'in_progress'])
    ).all()
    
    return render_template('audit/statistics.html',
        total_tasks=total_tasks,
        pending_count=pending_count,
        in_progress_count=in_progress_count,
        completed_count=completed_count,
        closed_count=closed_count,
        type_stats=type_stats,
        overdue_tasks=overdue_tasks
    )