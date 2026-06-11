from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import EmergencyPlan, EmergencyDrill, EmergencyTeam
from datetime import datetime
import json

bp = Blueprint('emergency', __name__, url_prefix='/emergency')

# ==================== 应急管理首页 ====================
@bp.route('/')
@login_required
def index():
    plan_count = EmergencyPlan.query.count()
    drill_count = EmergencyDrill.query.count()
    team_count = EmergencyTeam.query.count()
    recent_drills = EmergencyDrill.query.order_by(EmergencyDrill.created_at.desc()).limit(5).all()
    return render_template('emergency/index.html',
        plan_count=plan_count, drill_count=drill_count, team_count=team_count,
        recent_drills=recent_drills)

# ==================== 应急预案 ====================
@bp.route('/plans')
@login_required
def plans():
    page = request.args.get('page', 1, type=int)
    per_page = 15
    keyword = request.args.get('keyword', '').strip()
    plan_type = request.args.get('plan_type', '').strip()
    status = request.args.get('status', '').strip()
    
    query = EmergencyPlan.query
    if keyword:
        query = query.filter(db.or_(
            EmergencyPlan.plan_no.contains(keyword),
            EmergencyPlan.plan_title.contains(keyword),
            EmergencyPlan.dept_name.contains(keyword)
        ))
    if plan_type:
        query = query.filter(EmergencyPlan.plan_type == plan_type)
    if status:
        query = query.filter(EmergencyPlan.status == status)
    
    query = query.order_by(EmergencyPlan.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('emergency/plans.html',
        items=pagination.items, pagination=pagination,
        keyword=keyword, plan_type=plan_type, status=status)

@bp.route('/plans/add', methods=['GET', 'POST'])
@login_required
def plan_add():
    if request.method == 'POST':
        item = EmergencyPlan(
            plan_no=request.form.get('plan_no', ''),
            plan_title=request.form.get('plan_title', ''),
            plan_type=request.form.get('plan_type', ''),
            plan_level=request.form.get('plan_level', ''),
            applicable_scope=request.form.get('applicable_scope', ''),
            trigger_conditions=request.form.get('trigger_conditions', ''),
            response_procedures=request.form.get('response_procedures', ''),
            resource_requirements=request.form.get('resource_requirements', ''),
            communication_plan=request.form.get('communication_plan', ''),
            recovery_procedures=request.form.get('recovery_procedures', ''),
            dept_name=request.form.get('dept_name', ''),
            responsible_person=request.form.get('responsible_person', ''),
            version=request.form.get('version', '1.0'),
            status=request.form.get('status', 'draft'),
            remark=request.form.get('remark', ''),
            created_by=current_user.id
        )
        db.session.add(item)
        db.session.commit()
        flash('应急预案添加成功！', 'success')
        return redirect(url_for('emergency.plans'))
    return render_template('emergency/plan_form.html', item=None)

@bp.route('/plans/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def plan_edit(id):
    item = EmergencyPlan.query.get_or_404(id)
    if request.method == 'POST':
        item.plan_no = request.form.get('plan_no', item.plan_no)
        item.plan_title = request.form.get('plan_title', item.plan_title)
        item.plan_type = request.form.get('plan_type', item.plan_type)
        item.plan_level = request.form.get('plan_level', item.plan_level)
        item.applicable_scope = request.form.get('applicable_scope', item.applicable_scope)
        item.trigger_conditions = request.form.get('trigger_conditions', item.trigger_conditions)
        item.response_procedures = request.form.get('response_procedures', item.response_procedures)
        item.resource_requirements = request.form.get('resource_requirements', item.resource_requirements)
        item.communication_plan = request.form.get('communication_plan', item.communication_plan)
        item.recovery_procedures = request.form.get('recovery_procedures', item.recovery_procedures)
        item.dept_name = request.form.get('dept_name', item.dept_name)
        item.responsible_person = request.form.get('responsible_person', item.responsible_person)
        item.version = request.form.get('version', item.version)
        item.status = request.form.get('status', item.status)
        item.remark = request.form.get('remark', item.remark)
        item.updated_at = datetime.utcnow()
        db.session.commit()
        flash('应急预案更新成功！', 'success')
        return redirect(url_for('emergency.plans'))
    return render_template('emergency/plan_form.html', item=item)

@bp.route('/plans/delete/<int:id>', methods=['POST'])
@login_required
def plan_delete(id):
    item = EmergencyPlan.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('应急预案已删除！', 'success')
    return redirect(url_for('emergency.plans'))

@bp.route('/plans/export')
@login_required
def plan_export():
    from openpyxl import Workbook
    from io import BytesIO
    items = EmergencyPlan.query.order_by(EmergencyPlan.created_at.desc()).all()
    wb = Workbook()
    ws = wb.active
    ws.title = '应急预案'
    headers = ['预案编号','预案名称','预案类型','预案等级','适用范围','启动条件','责任部门','责任人','版本','状态','备注']
    ws.append(headers)
    for item in items:
        ws.append([item.plan_no, item.plan_title, item.plan_type, item.plan_level,
            item.applicable_scope, item.trigger_conditions, item.dept_name,
            item.responsible_person, item.version, item.status, item.remark])
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    from flask import send_file
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True, download_name='应急预案.xlsx')

# ==================== 应急演练 ====================
@bp.route('/drills')
@login_required
def drills():
    page = request.args.get('page', 1, type=int)
    per_page = 15
    keyword = request.args.get('keyword', '').strip()
    drill_type = request.args.get('drill_type', '').strip()
    status = request.args.get('status', '').strip()
    
    query = EmergencyDrill.query
    if keyword:
        query = query.filter(db.or_(
            EmergencyDrill.drill_no.contains(keyword),
            EmergencyDrill.drill_title.contains(keyword),
            EmergencyDrill.organizer.contains(keyword)
        ))
    if drill_type:
        query = query.filter(EmergencyDrill.drill_type == drill_type)
    if status:
        query = query.filter(EmergencyDrill.status == status)
    
    query = query.order_by(EmergencyDrill.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('emergency/drills.html',
        items=pagination.items, pagination=pagination,
        keyword=keyword, drill_type=drill_type, status=status)

@bp.route('/drills/add', methods=['GET', 'POST'])
@login_required
def drill_add():
    plans = EmergencyPlan.query.filter_by(status='published').order_by(EmergencyPlan.plan_title).all()
    if request.method == 'POST':
        plan_id = request.form.get('plan_id', '') or None
        item = EmergencyDrill(
            drill_no=request.form.get('drill_no', ''),
            drill_title=request.form.get('drill_title', ''),
            plan_id=int(plan_id) if plan_id else None,
            drill_type=request.form.get('drill_type', ''),
            drill_date=request.form.get('drill_date', ''),
            drill_location=request.form.get('drill_location', ''),
            organizer=request.form.get('organizer', ''),
            participants=request.form.get('participants', ''),
            drill_scenario=request.form.get('drill_scenario', ''),
            drill_process=request.form.get('drill_process', ''),
            issues_found=request.form.get('issues_found', ''),
            improvement_measures=request.form.get('improvement_measures', ''),
            overall_evaluation=request.form.get('overall_evaluation', ''),
            status=request.form.get('status', 'planned'),
            remark=request.form.get('remark', ''),
            created_by=current_user.id
        )
        db.session.add(item)
        db.session.commit()
        flash('应急演练添加成功！', 'success')
        return redirect(url_for('emergency.drills'))
    return render_template('emergency/drill_form.html', item=None, plans=plans)

@bp.route('/drills/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def drill_edit(id):
    item = EmergencyDrill.query.get_or_404(id)
    plans = EmergencyPlan.query.filter_by(status='published').order_by(EmergencyPlan.plan_title).all()
    if request.method == 'POST':
        plan_id = request.form.get('plan_id', '') or None
        item.drill_no = request.form.get('drill_no', item.drill_no)
        item.drill_title = request.form.get('drill_title', item.drill_title)
        item.plan_id = int(plan_id) if plan_id else None
        item.drill_type = request.form.get('drill_type', item.drill_type)
        item.drill_date = request.form.get('drill_date', item.drill_date)
        item.drill_location = request.form.get('drill_location', item.drill_location)
        item.organizer = request.form.get('organizer', item.organizer)
        item.participants = request.form.get('participants', item.participants)
        item.drill_scenario = request.form.get('drill_scenario', item.drill_scenario)
        item.drill_process = request.form.get('drill_process', item.drill_process)
        item.issues_found = request.form.get('issues_found', item.issues_found)
        item.improvement_measures = request.form.get('improvement_measures', item.improvement_measures)
        item.overall_evaluation = request.form.get('overall_evaluation', item.overall_evaluation)
        item.status = request.form.get('status', item.status)
        item.remark = request.form.get('remark', item.remark)
        item.updated_at = datetime.utcnow()
        db.session.commit()
        flash('应急演练更新成功！', 'success')
        return redirect(url_for('emergency.drills'))
    return render_template('emergency/drill_form.html', item=item, plans=plans)

@bp.route('/drills/delete/<int:id>', methods=['POST'])
@login_required
def drill_delete(id):
    item = EmergencyDrill.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('应急演练已删除！', 'success')
    return redirect(url_for('emergency.drills'))

# ==================== 应急小组 ====================
@bp.route('/teams')
@login_required
def teams():
    page = request.args.get('page', 1, type=int)
    per_page = 15
    keyword = request.args.get('keyword', '').strip()
    team_type = request.args.get('team_type', '').strip()
    status = request.args.get('status', '').strip()
    
    query = EmergencyTeam.query
    if keyword:
        query = query.filter(db.or_(
            EmergencyTeam.team_no.contains(keyword),
            EmergencyTeam.team_name.contains(keyword),
            EmergencyTeam.leader_name.contains(keyword)
        ))
    if team_type:
        query = query.filter(EmergencyTeam.team_type == team_type)
    if status:
        query = query.filter(EmergencyTeam.status == status)
    
    query = query.order_by(EmergencyTeam.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('emergency/teams.html',
        items=pagination.items, pagination=pagination,
        keyword=keyword, team_type=team_type, status=status)

@bp.route('/teams/add', methods=['GET', 'POST'])
@login_required
def team_add():
    if request.method == 'POST':
        item = EmergencyTeam(
            team_no=request.form.get('team_no', ''),
            team_name=request.form.get('team_name', ''),
            team_type=request.form.get('team_type', ''),
            dept_name=request.form.get('dept_name', ''),
            leader_name=request.form.get('leader_name', ''),
            leader_phone=request.form.get('leader_phone', ''),
            members=request.form.get('members', ''),
            responsibilities=request.form.get('responsibilities', ''),
            response_scope=request.form.get('response_scope', ''),
            contact_info=request.form.get('contact_info', ''),
            status=request.form.get('status', 'active'),
            remark=request.form.get('remark', ''),
            created_by=current_user.id
        )
        db.session.add(item)
        db.session.commit()
        flash('应急小组添加成功！', 'success')
        return redirect(url_for('emergency.teams'))
    return render_template('emergency/team_form.html', item=None)

@bp.route('/teams/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def team_edit(id):
    item = EmergencyTeam.query.get_or_404(id)
    if request.method == 'POST':
        item.team_no = request.form.get('team_no', item.team_no)
        item.team_name = request.form.get('team_name', item.team_name)
        item.team_type = request.form.get('team_type', item.team_type)
        item.dept_name = request.form.get('dept_name', item.dept_name)
        item.leader_name = request.form.get('leader_name', item.leader_name)
        item.leader_phone = request.form.get('leader_phone', item.leader_phone)
        item.members = request.form.get('members', item.members)
        item.responsibilities = request.form.get('responsibilities', item.responsibilities)
        item.response_scope = request.form.get('response_scope', item.response_scope)
        item.contact_info = request.form.get('contact_info', item.contact_info)
        item.status = request.form.get('status', item.status)
        item.remark = request.form.get('remark', item.remark)
        item.updated_at = datetime.utcnow()
        db.session.commit()
        flash('应急小组更新成功！', 'success')
        return redirect(url_for('emergency.teams'))
    return render_template('emergency/team_form.html', item=item)

@bp.route('/teams/delete/<int:id>', methods=['POST'])
@login_required
def team_delete(id):
    item = EmergencyTeam.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('应急小组已删除！', 'success')
    return redirect(url_for('emergency.teams'))