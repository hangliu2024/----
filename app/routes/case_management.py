from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import CaseCollection, InvestigationSOP, InvestigationReport
from datetime import datetime
import json

bp = Blueprint('case_management', __name__, url_prefix='/case')

# ==================== 案件管理首页 ====================
@bp.route('/')
@login_required
def index():
    case_count = CaseCollection.query.count()
    sop_count = InvestigationSOP.query.count()
    report_count = InvestigationReport.query.count()
    return render_template('case_management/index.html',
        case_count=case_count, sop_count=sop_count, report_count=report_count)

# ==================== 案例集 ====================
@bp.route('/collections')
@login_required
def collections():
    page = request.args.get('page', 1, type=int)
    per_page = 15
    keyword = request.args.get('keyword', '').strip()
    case_type = request.args.get('case_type', '').strip()
    status = request.args.get('status', '').strip()
    
    query = CaseCollection.query
    if keyword:
        query = query.filter(db.or_(
            CaseCollection.case_no.contains(keyword),
            CaseCollection.case_title.contains(keyword),
            CaseCollection.dept_name.contains(keyword)
        ))
    if case_type:
        query = query.filter(CaseCollection.case_type == case_type)
    if status:
        query = query.filter(CaseCollection.status == status)
    
    query = query.order_by(CaseCollection.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('case_management/collections.html',
        items=pagination.items, pagination=pagination,
        keyword=keyword, case_type=case_type, status=status)

@bp.route('/collections/add', methods=['GET', 'POST'])
@login_required
def collection_add():
    if request.method == 'POST':
        item = CaseCollection(
            case_no=request.form.get('case_no', ''),
            case_title=request.form.get('case_title', ''),
            case_type=request.form.get('case_type', ''),
            case_level=request.form.get('case_level', ''),
            case_source=request.form.get('case_source', ''),
            case_date=request.form.get('case_date', ''),
            dept_name=request.form.get('dept_name', ''),
            description=request.form.get('description', ''),
            cause_analysis=request.form.get('cause_analysis', ''),
            handling_result=request.form.get('handling_result', ''),
            lessons_learned=request.form.get('lessons_learned', ''),
            prevention_measures=request.form.get('prevention_measures', ''),
            status=request.form.get('status', 'draft'),
            remark=request.form.get('remark', ''),
            created_by=current_user.id
        )
        db.session.add(item)
        db.session.commit()
        flash('案例添加成功！', 'success')
        return redirect(url_for('case_management.collections'))
    return render_template('case_management/collection_form.html', item=None)

@bp.route('/collections/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def collection_edit(id):
    item = CaseCollection.query.get_or_404(id)
    if request.method == 'POST':
        item.case_no = request.form.get('case_no', item.case_no)
        item.case_title = request.form.get('case_title', item.case_title)
        item.case_type = request.form.get('case_type', item.case_type)
        item.case_level = request.form.get('case_level', item.case_level)
        item.case_source = request.form.get('case_source', item.case_source)
        item.case_date = request.form.get('case_date', item.case_date)
        item.dept_name = request.form.get('dept_name', item.dept_name)
        item.description = request.form.get('description', item.description)
        item.cause_analysis = request.form.get('cause_analysis', item.cause_analysis)
        item.handling_result = request.form.get('handling_result', item.handling_result)
        item.lessons_learned = request.form.get('lessons_learned', item.lessons_learned)
        item.prevention_measures = request.form.get('prevention_measures', item.prevention_measures)
        item.status = request.form.get('status', item.status)
        item.remark = request.form.get('remark', item.remark)
        item.updated_at = datetime.utcnow()
        db.session.commit()
        flash('案例更新成功！', 'success')
        return redirect(url_for('case_management.collections'))
    return render_template('case_management/collection_form.html', item=item)

@bp.route('/collections/delete/<int:id>', methods=['POST'])
@login_required
def collection_delete(id):
    item = CaseCollection.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('案例已删除！', 'success')
    return redirect(url_for('case_management.collections'))

@bp.route('/collections/export')
@login_required
def collection_export():
    from openpyxl import Workbook
    from io import BytesIO
    items = CaseCollection.query.order_by(CaseCollection.created_at.desc()).all()
    wb = Workbook()
    ws = wb.active
    ws.title = '案例集'
    headers = ['案例编号','案例标题','案例类型','案例等级','案例来源','发生时间','涉及部门','状态','描述','原因分析','处理结果','经验教训','预防措施','备注']
    ws.append(headers)
    for item in items:
        ws.append([item.case_no, item.case_title, item.case_type, item.case_level,
            item.case_source, item.case_date, item.dept_name, item.status,
            item.description, item.cause_analysis, item.handling_result,
            item.lessons_learned, item.prevention_measures, item.remark])
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    from flask import send_file
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True, download_name='案例集.xlsx')

# ==================== 案件调查SOP ====================
@bp.route('/sop')
@login_required
def sop_list():
    page = request.args.get('page', 1, type=int)
    per_page = 15
    keyword = request.args.get('keyword', '').strip()
    sop_type = request.args.get('sop_type', '').strip()
    status = request.args.get('status', '').strip()
    
    query = InvestigationSOP.query
    if keyword:
        query = query.filter(db.or_(
            InvestigationSOP.sop_no.contains(keyword),
            InvestigationSOP.sop_title.contains(keyword),
            InvestigationSOP.applicable_scope.contains(keyword),
            InvestigationSOP.investigation_steps.contains(keyword),
            InvestigationSOP.evidence_requirements.contains(keyword),
            InvestigationSOP.timeline_requirements.contains(keyword),
            InvestigationSOP.approval_process.contains(keyword),
            InvestigationSOP.responsible_role.contains(keyword),
            InvestigationSOP.remark.contains(keyword)
        ))
    if sop_type:
        query = query.filter(InvestigationSOP.sop_type == sop_type)
    if status:
        query = query.filter(InvestigationSOP.status == status)
    
    query = query.order_by(InvestigationSOP.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('case_management/sop_list.html',
        items=pagination.items, pagination=pagination,
        keyword=keyword, sop_type=sop_type, status=status)

@bp.route('/sop/add', methods=['GET', 'POST'])
@login_required
def sop_add():
    if request.method == 'POST':
        item = InvestigationSOP(
            sop_no=request.form.get('sop_no', ''),
            sop_title=request.form.get('sop_title', ''),
            sop_type=request.form.get('sop_type', ''),
            sop_version=request.form.get('sop_version', ''),
            applicable_scope=request.form.get('applicable_scope', ''),
            investigation_steps=request.form.get('investigation_steps', ''),
            evidence_requirements=request.form.get('evidence_requirements', ''),
            timeline_requirements=request.form.get('timeline_requirements', ''),
            responsible_role=request.form.get('responsible_role', ''),
            approval_process=request.form.get('approval_process', ''),
            status=request.form.get('status', 'draft'),
            remark=request.form.get('remark', ''),
            created_by=current_user.id
        )
        db.session.add(item)
        db.session.commit()
        flash('SOP添加成功！', 'success')
        return redirect(url_for('case_management.sop_list'))
    return render_template('case_management/sop_form.html', item=None)

@bp.route('/sop/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def sop_edit(id):
    item = InvestigationSOP.query.get_or_404(id)
    if request.method == 'POST':
        item.sop_no = request.form.get('sop_no', item.sop_no)
        item.sop_title = request.form.get('sop_title', item.sop_title)
        item.sop_type = request.form.get('sop_type', item.sop_type)
        item.sop_version = request.form.get('sop_version', item.sop_version)
        item.applicable_scope = request.form.get('applicable_scope', item.applicable_scope)
        item.investigation_steps = request.form.get('investigation_steps', item.investigation_steps)
        item.evidence_requirements = request.form.get('evidence_requirements', item.evidence_requirements)
        item.timeline_requirements = request.form.get('timeline_requirements', item.timeline_requirements)
        item.responsible_role = request.form.get('responsible_role', item.responsible_role)
        item.approval_process = request.form.get('approval_process', item.approval_process)
        item.status = request.form.get('status', item.status)
        item.remark = request.form.get('remark', item.remark)
        item.updated_at = datetime.utcnow()
        db.session.commit()
        flash('SOP更新成功！', 'success')
        return redirect(url_for('case_management.sop_list'))
    return render_template('case_management/sop_form.html', item=item)

@bp.route('/sop/view/<int:id>')
@login_required
def sop_view(id):
    item = InvestigationSOP.query.get_or_404(id)
    return render_template('case_management/sop_detail.html', item=item)

@bp.route('/sop/delete/<int:id>', methods=['POST'])
@login_required
def sop_delete(id):
    item = InvestigationSOP.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('SOP已删除！', 'success')
    return redirect(url_for('case_management.sop_list'))

# ==================== 调查报告 ====================
@bp.route('/reports')
@login_required
def reports():
    page = request.args.get('page', 1, type=int)
    per_page = 15
    keyword = request.args.get('keyword', '').strip()
    report_type = request.args.get('report_type', '').strip()
    status = request.args.get('status', '').strip()
    
    query = InvestigationReport.query
    if keyword:
        query = query.filter(db.or_(
            InvestigationReport.report_no.contains(keyword),
            InvestigationReport.report_title.contains(keyword),
            InvestigationReport.investigator.contains(keyword)
        ))
    if report_type:
        query = query.filter(InvestigationReport.report_type == report_type)
    if status:
        query = query.filter(InvestigationReport.status == status)
    
    query = query.order_by(InvestigationReport.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    cases = CaseCollection.query.filter_by(status='published').order_by(CaseCollection.case_title).all()
    sops = InvestigationSOP.query.filter_by(status='published').order_by(InvestigationSOP.sop_title).all()
    return render_template('case_management/reports.html',
        items=pagination.items, pagination=pagination,
        keyword=keyword, report_type=report_type, status=status,
        cases=cases, sops=sops)

@bp.route('/reports/add', methods=['GET', 'POST'])
@login_required
def report_add():
    cases = CaseCollection.query.filter_by(status='published').order_by(CaseCollection.case_title).all()
    sops = InvestigationSOP.query.filter_by(status='published').order_by(InvestigationSOP.sop_title).all()
    if request.method == 'POST':
        case_id = request.form.get('case_id', '') or None
        sop_id = request.form.get('sop_id', '') or None
        item = InvestigationReport(
            report_no=request.form.get('report_no', ''),
            report_title=request.form.get('report_title', ''),
            case_id=int(case_id) if case_id else None,
            sop_id=int(sop_id) if sop_id else None,
            report_type=request.form.get('report_type', ''),
            investigation_date=request.form.get('investigation_date', ''),
            investigator=request.form.get('investigator', ''),
            dept_name=request.form.get('dept_name', ''),
            incident_summary=request.form.get('incident_summary', ''),
            investigation_process=request.form.get('investigation_process', ''),
            findings=request.form.get('findings', ''),
            evidence_description=request.form.get('evidence_description', ''),
            conclusion=request.form.get('conclusion', ''),
            suggestions=request.form.get('suggestions', ''),
            status=request.form.get('status', 'draft'),
            remark=request.form.get('remark', ''),
            created_by=current_user.id
        )
        db.session.add(item)
        db.session.commit()
        flash('调查报告添加成功！', 'success')
        return redirect(url_for('case_management.reports'))
    return render_template('case_management/report_form.html', item=None, cases=cases, sops=sops)

@bp.route('/reports/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def report_edit(id):
    item = InvestigationReport.query.get_or_404(id)
    cases = CaseCollection.query.filter_by(status='published').order_by(CaseCollection.case_title).all()
    sops = InvestigationSOP.query.filter_by(status='published').order_by(InvestigationSOP.sop_title).all()
    if request.method == 'POST':
        case_id = request.form.get('case_id', '') or None
        sop_id = request.form.get('sop_id', '') or None
        item.report_no = request.form.get('report_no', item.report_no)
        item.report_title = request.form.get('report_title', item.report_title)
        item.case_id = int(case_id) if case_id else None
        item.sop_id = int(sop_id) if sop_id else None
        item.report_type = request.form.get('report_type', item.report_type)
        item.investigation_date = request.form.get('investigation_date', item.investigation_date)
        item.investigator = request.form.get('investigator', item.investigator)
        item.dept_name = request.form.get('dept_name', item.dept_name)
        item.incident_summary = request.form.get('incident_summary', item.incident_summary)
        item.investigation_process = request.form.get('investigation_process', item.investigation_process)
        item.findings = request.form.get('findings', item.findings)
        item.evidence_description = request.form.get('evidence_description', item.evidence_description)
        item.conclusion = request.form.get('conclusion', item.conclusion)
        item.suggestions = request.form.get('suggestions', item.suggestions)
        item.status = request.form.get('status', item.status)
        item.remark = request.form.get('remark', item.remark)
        item.updated_at = datetime.utcnow()
        db.session.commit()
        flash('调查报告更新成功！', 'success')
        return redirect(url_for('case_management.reports'))
    return render_template('case_management/report_form.html', item=item, cases=cases, sops=sops)

@bp.route('/reports/delete/<int:id>', methods=['POST'])
@login_required
def report_delete(id):
    item = InvestigationReport.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('调查报告已删除！', 'success')
    return redirect(url_for('case_management.reports'))