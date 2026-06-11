# AI Agents 路由 - Agent调度和管理
# 提供Agent仪表盘、稽查助手、填表助手等页面和API

from flask import Blueprint, render_template, request, jsonify, current_app, Response
from flask_login import login_required, current_user
from app import db
from app.models import AuditTask, AuditRecord, Personnel, ComputerInfo, ClassifiedPersonnel, ClassifiedMedia
from app.agents.registry import AgentRegistry
from app.agents.audit_agent import (
    get_audit_checklist, analyze_audit_task, generate_audit_suggestions,
    generate_audit_record_draft, analyze_audit_statistics, AUDIT_CHECKLISTS
)
from app.agents.form_agent import (
    get_form_templates, get_form_template, auto_fill_from_personnel,
    validate_form_data, smart_fill_suggestion, batch_generate_form
)
from app.routes.ai_assistant import call_llm_api_v2, call_llm_api_stream
import json
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('ai_agents', __name__, url_prefix='/ai-agents')


def _get_ai_config():
    """获取AI配置"""
    provider = current_app.config.get('AI_PROVIDER', 'ollama')
    return {
        'provider': provider,
        'api_key': current_app.config.get('MINIMAX_API_KEY') if provider == 'minimax' else current_app.config.get('OPENAI_API_KEY') if provider == 'openai' else '',
        'model': current_app.config.get('OLLAMA_MODEL') if provider == 'ollama' else current_app.config.get('OPENAI_MODEL', 'gpt-4o') if provider == 'openai' else current_app.config.get('MINIMAX_MODEL') if provider == 'minimax' else 'llama3',
        'ollama_api_base': current_app.config.get('OLLAMA_API_BASE', 'http://localhost:11434/v1'),
        'openai_api_base': current_app.config.get('OPENAI_API_BASE', 'https://api.openai.com/v1'),
        'minimax_api_key': current_app.config.get('MINIMAX_API_KEY', '')
    }


# ========== Agent 仪表盘 ==========

@bp.route('/')
@login_required
def index():
    """Agent仪表盘 - 展示所有可用的AI Agent"""
    agents = AgentRegistry.get_enabled()
    return render_template('ai_agents/index.html', agents=agents)


# ========== 稽查助手 ==========

@bp.route('/audit')
@login_required
def audit_agent():
    """稽查助手页面"""
    # 获取用户的稽查任务
    if current_user.role == 'admin':
        tasks = AuditTask.query.order_by(AuditTask.created_at.desc()).limit(20).all()
    else:
        tasks = AuditTask.query.filter_by(assignee_id=current_user.id).order_by(AuditTask.created_at.desc()).limit(20).all()
    
    audit_types = list(AUDIT_CHECKLISTS.keys())
    return render_template('ai_agents/audit_agent.html', tasks=tasks, audit_types=audit_types)


@bp.route('/audit/analyze-task', methods=['POST'])
@login_required
def audit_analyze_task():
    """分析稽查任务，生成检查要点"""
    data = request.get_json()
    task_id = data.get('task_id')
    
    if not task_id:
        return jsonify({'success': False, 'error': '请指定稽查任务'})
    
    task = AuditTask.query.get(task_id)
    if not task:
        return jsonify({'success': False, 'error': '未找到指定任务'})
    
    config = _get_ai_config()
    result = analyze_audit_task(task, config, call_llm_api_v2)
    return jsonify(result)


@bp.route('/audit/checklist', methods=['POST'])
@login_required
def audit_get_checklist():
    """获取稽查检查清单"""
    data = request.get_json()
    audit_type = data.get('audit_type', '安全稽查')
    checklist = get_audit_checklist(audit_type)
    return jsonify({'success': True, 'checklist': checklist})


@bp.route('/audit/suggest', methods=['POST'])
@login_required
def audit_suggest():
    """根据稽查发现生成整改建议"""
    data = request.get_json()
    audit_type = data.get('audit_type', '')
    audit_scope = data.get('audit_scope', '')
    findings = data.get('findings', '')
    
    if not findings:
        return jsonify({'success': False, 'error': '请输入稽查发现'})
    
    config = _get_ai_config()
    result = generate_audit_suggestions(audit_type, audit_scope, findings, config, call_llm_api_v2)
    return jsonify(result)


@bp.route('/audit/generate-draft', methods=['POST'])
@login_required
def audit_generate_draft():
    """生成稽查记录草稿"""
    data = request.get_json()
    task_id = data.get('task_id')
    findings = data.get('findings', '')
    
    task = AuditTask.query.get(task_id) if task_id else None
    if not task:
        return jsonify({'success': False, 'error': '未找到指定任务'})
    
    if not findings:
        return jsonify({'success': False, 'error': '请输入稽查发现'})
    
    config = _get_ai_config()
    result = generate_audit_record_draft(task, findings, config, call_llm_api_v2)
    return jsonify(result)


@bp.route('/audit/analyze-stream', methods=['POST'])
@login_required
def audit_analyze_stream():
    """流式分析稽查任务"""
    data = request.get_json()
    task_id = data.get('task_id')
    action = data.get('action', 'analyze')  # analyze / suggest / draft
    findings = data.get('findings', '')
    
    task = AuditTask.query.get(task_id) if task_id else None
    if not task and action != 'suggest':
        return jsonify({'success': False, 'error': '未找到指定任务'})
    
    config = _get_ai_config()
    app_instance = current_app._get_current_object()
    
    def generate():
        with app_instance.app_context():
            try:
                if action == 'analyze':
                    audit_type = task.task_type
                    checklist = get_audit_checklist(audit_type)
                    prompt = f"""你是一个专业的信息安全稽查助手。请分析以下稽查任务，生成详细的检查要点和建议。

<task_info>
任务编号：{task.task_no}
任务标题：{task.task_title}
任务类型：{task.task_type}
任务内容：{task.task_content}
任务要求：{task.task_requirement or '无特殊要求'}
被稽查部门：{task.dept_name or '未指定'}
</task_info>

<reference_checklist>
参考检查清单：{json.dumps(checklist['checkpoints'], ensure_ascii=False, indent=2)}
</reference_checklist>

请生成：1.稽查重点分析 2.详细检查清单 3.稽查方法建议 4.风险预判 5.注意事项"""
                    
                    messages = [
                        {"role": "system", "content": "你是专业的信息安全稽查顾问，请用Markdown格式输出分析结果。"},
                        {"role": "user", "content": prompt}
                    ]
                elif action == 'suggest':
                    prompt = f"""你是一个专业的信息安全稽查顾问。请根据以下稽查发现，生成详细的整改建议。

稽查类型：{data.get('audit_type', '')}
稽查范围：{data.get('audit_scope', '')}
发现的问题：{findings}

请给出：1.问题等级 2.整改措施 3.整改时限 4.责任方建议"""
                    messages = [
                        {"role": "system", "content": "你是专业的信息安全稽查顾问，擅长制定整改方案。请用Markdown格式输出。"},
                        {"role": "user", "content": prompt}
                    ]
                elif action == 'draft':
                    prompt = f"""请根据以下信息生成一份稽查记录草稿。

任务编号：{task.task_no}
任务标题：{task.task_title}
任务类型：{task.task_type}
稽查范围：{task.dept_name or '未指定'}
稽查发现：{findings}

请按格式输出：稽查类型、稽查范围、稽查内容、稽查结果、发现的问题、整改建议。"""
                    messages = [
                        {"role": "system", "content": "你是稽查记录撰写助手，请用正式公文用语生成规范草稿。"},
                        {"role": "user", "content": prompt}
                    ]
                else:
                    yield "data: " + json.dumps({'error': '未知操作'}, ensure_ascii=False) + "\n\n"
                    return
                
                for chunk in call_llm_api_stream(config, messages, timeout=120):
                    if chunk['type'] == 'content':
                        yield "data: " + json.dumps({'content': chunk['content']}, ensure_ascii=False) + "\n\n"
                    elif chunk['type'] == 'error':
                        yield "data: " + json.dumps({'error': chunk['content']}, ensure_ascii=False) + "\n\n"
                
                yield "data: " + json.dumps({'done': True}, ensure_ascii=False) + "\n\n"
            except Exception as e:
                logger.error(f"Audit stream error: {str(e)}")
                yield "data: " + json.dumps({'error': str(e)}, ensure_ascii=False) + "\n\n"
    
    return Response(generate(), mimetype='text/event-stream')


# ========== 智能填表助手 ==========

@bp.route('/form')
@login_required
def form_agent():
    """智能填表助手页面"""
    templates = get_form_templates()
    return render_template('ai_agents/form_agent.html', templates=templates)


@bp.route('/form/auto-fill', methods=['POST'])
@login_required
def form_auto_fill():
    """根据工号/姓名自动填充数据"""
    data = request.get_json()
    emp_id_or_name = data.get('emp_id_or_name', '').strip()
    template_id = data.get('template_id', '')
    
    if not emp_id_or_name:
        return jsonify({'success': False, 'error': '请输入工号或姓名'})
    
    result = auto_fill_from_personnel(emp_id_or_name, db.session, Personnel, ComputerInfo)
    
    # 如果指定了模板，按模板格式组织数据
    if result['success'] and template_id:
        template = get_form_template(template_id)
        if template:
            form_data = {}
            person = result['person']
            for field in template['fields']:
                source = field['source']
                if source.startswith('employees_info.'):
                    col = source.split('.')[1]
                    form_data[field['key']] = person.get(col, '')
                elif source.startswith('computer_info.') and result['computers']:
                    col = source.split('.')[1]
                    form_data[field['key']] = result['computers'][0].get(col, '')
            result['form_data'] = form_data
    
    return jsonify(result)


@bp.route('/form/validate', methods=['POST'])
@login_required
def form_validate():
    """校验表单数据"""
    data = request.get_json()
    template_id = data.get('template_id', '')
    form_data = data.get('form_data', {})
    
    if not template_id:
        return jsonify({'success': False, 'error': '请指定表单模板'})
    
    config = _get_ai_config()
    result = validate_form_data(template_id, form_data, config, call_llm_api_v2)
    return jsonify(result)


@bp.route('/form/smart-fill', methods=['POST'])
@login_required
def form_smart_fill():
    """智能填充建议"""
    data = request.get_json()
    template_id = data.get('template_id', '')
    partial_data = data.get('partial_data', {})
    
    if not template_id:
        return jsonify({'success': False, 'error': '请指定表单模板'})
    
    config = _get_ai_config()
    result = smart_fill_suggestion(template_id, partial_data, config, call_llm_api_v2)
    return jsonify(result)


@bp.route('/form/batch-generate', methods=['POST'])
@login_required
def form_batch_generate():
    """批量生成表单"""
    data = request.get_json()
    template_id = data.get('template_id', '')
    
    if not template_id:
        return jsonify({'success': False, 'error': '请指定表单模板'})
    
    # 根据模板类型获取数据
    records = []
    if template_id == 'classified_personnel':
        # 获取在职涉密人员候选
        records = []
        personnel_list = Personnel.query.filter_by(emp_status='在职').limit(20).all()
        for p in personnel_list:
            records.append({
                'emp_id': p.emp_id,
                'emp_name': p.emp_name,
                'dept_full_name': p.dept_full_name,
                'position': p.position
            })
    elif template_id == 'computer_asset':
        computers = ComputerInfo.query.limit(20).all()
        for c in computers:
            records.append({
                'computer_name': c.computer_name,
                'employee_id': c.employee_id,
                'emp_name': c.emp_name,
                'asset_id': c.asset_id,
                'network_address': c.network_address,
                'operating_system': c.operating_system
            })
    
    if not records:
        return jsonify({'success': False, 'error': '没有可用的数据记录'})
    
    config = _get_ai_config()
    result = batch_generate_form(template_id, records, config, call_llm_api_v2)
    return jsonify(result)


@bp.route('/form/smart-fill-stream', methods=['POST'])
@login_required
def form_smart_fill_stream():
    """流式智能填充建议"""
    data = request.get_json()
    template_id = data.get('template_id', '')
    partial_data = data.get('partial_data', {})
    user_question = data.get('question', '')
    
    if not template_id:
        return jsonify({'success': False, 'error': '请指定表单模板'})
    
    template = get_form_template(template_id)
    if not template:
        return jsonify({'success': False, 'error': '未知表单模板'})
    
    config = _get_ai_config()
    app_instance = current_app._get_current_object()
    
    def generate():
        with app_instance.app_context():
            try:
                if user_question:
                    prompt = f"""你是智能填表助手。用户正在填写「{template['name']}」，有以下问题：

已填写的数据：{json.dumps(partial_data, ensure_ascii=False)}

用户问题：{user_question}

请帮助用户解答问题，并给出填写建议。用Markdown格式回复。"""
                else:
                    prompt = f"""你是智能填表助手。用户正在填写「{template['name']}」。

已填写的数据：{json.dumps(partial_data, ensure_ascii=False)}

字段定义：{json.dumps([{{'key': f['key'], 'label': f['label']}} for f in template['fields']], ensure_ascii=False)}

请分析已填写数据，推荐未填写字段的建议值和理由。用Markdown格式回复。"""
                
                messages = [
                    {"role": "system", "content": f"你是{template['name']}的智能填写助手，请用中文回答。"},
                    {"role": "user", "content": prompt}
                ]
                
                for chunk in call_llm_api_stream(config, messages, timeout=120):
                    if chunk['type'] == 'content':
                        yield "data: " + json.dumps({'content': chunk['content']}, ensure_ascii=False) + "\n\n"
                    elif chunk['type'] == 'error':
                        yield "data: " + json.dumps({'error': chunk['content']}, ensure_ascii=False) + "\n\n"
                
                yield "data: " + json.dumps({'done': True}, ensure_ascii=False) + "\n\n"
            except Exception as e:
                logger.error(f"Form smart fill stream error: {str(e)}")
                yield "data: " + json.dumps({'error': str(e)}, ensure_ascii=False) + "\n\n"
    
    return Response(generate(), mimetype='text/event-stream')


# ========== 报告生成助手 ==========

@bp.route('/report')
@login_required
def report_agent():
    """报告生成助手页面"""
    return render_template('ai_agents/report_agent.html')


@bp.route('/report/generate', methods=['POST'])
@login_required
def report_generate():
    """生成报告"""
    data = request.get_json()
    report_type = data.get('report_type', '')
    dept_name = data.get('dept_name', '')
    extra_context = data.get('extra_context', '')
    
    config = _get_ai_config()
    
    # 根据报告类型收集数据
    stats = {}
    if report_type == 'personnel':
        if dept_name:
            total = Personnel.query.filter(Personnel.dept_full_name.like(f'%{dept_name}%'), Personnel.emp_status == '在职').count()
            left = Personnel.query.filter(Personnel.dept_full_name.like(f'%{dept_name}%'), Personnel.emp_status == '离职').count()
        else:
            total = Personnel.query.filter_by(emp_status='在职').count()
            left = Personnel.query.filter_by(emp_status='离职').count()
        stats = {'type': '人员统计', 'dept': dept_name or '全部', 'active_count': total, 'left_count': left}
    elif report_type == 'asset':
        total_computers = ComputerInfo.query.count()
        no_user = ComputerInfo.query.filter((ComputerInfo.emp_name == None) | (ComputerInfo.emp_name == '')).count()
        stats = {'type': '资产统计', 'total_computers': total_computers, 'no_user_computers': no_user}
    elif report_type == 'audit':
        total_tasks = AuditTask.query.count()
        pending = AuditTask.query.filter_by(status='pending').count()
        completed = AuditTask.query.filter_by(status='completed').count()
        stats = {'type': '稽查统计', 'total_tasks': total_tasks, 'pending': pending, 'completed': completed}
    elif report_type == 'security':
        classified_p = ClassifiedPersonnel.query.count()
        classified_m = ClassifiedMedia.query.count()
        stats = {'type': '保密统计', 'classified_personnel': classified_p, 'classified_media': classified_m}
    
    prompt = f"""请根据以下数据生成一份专业的{report_type}报告。

<statistics>
{json.dumps(stats, ensure_ascii=False, indent=2)}
</statistics>

{f'<extra_context>{extra_context}</extra_context>' if extra_context else ''}

请生成包含以下部分的报告：
1. 概述
2. 数据分析
3. 问题与风险
4. 改进建议
5. 总结

请使用正式的公文用语，Markdown格式输出。"""

    app_instance = current_app._get_current_object()
    
    def generate():
        with app_instance.app_context():
            try:
                messages = [
                    {"role": "system", "content": "你是专业的报告撰写助手，请生成结构清晰、数据翔实的分析报告。"},
                    {"role": "user", "content": prompt}
                ]
                for chunk in call_llm_api_stream(config, messages, timeout=180):
                    if chunk['type'] == 'content':
                        yield "data: " + json.dumps({'content': chunk['content']}, ensure_ascii=False) + "\n\n"
                    elif chunk['type'] == 'error':
                        yield "data: " + json.dumps({'error': chunk['content']}, ensure_ascii=False) + "\n\n"
                yield "data: " + json.dumps({'done': True}, ensure_ascii=False) + "\n\n"
            except Exception as e:
                yield "data: " + json.dumps({'error': str(e)}, ensure_ascii=False) + "\n\n"
    
    return Response(generate(), mimetype='text/event-stream')


# ========== 风险分析助手 ==========

@bp.route('/risk')
@login_required
def risk_agent():
    """风险分析助手页面"""
    return render_template('ai_agents/risk_agent.html')


@bp.route('/risk/analyze', methods=['POST'])
@login_required
def risk_analyze():
    """风险分析"""
    data = request.get_json()
    risk_type = data.get('risk_type', 'all')
    
    config = _get_ai_config()
    
    # 收集风险数据
    risk_data = {}
    
    if risk_type in ['all', 'resignation']:
        # 离职人员涉密资产清理风险
        left_with_computer = db.session.query(Personnel, ComputerInfo).join(
            ComputerInfo, Personnel.emp_name == ComputerInfo.emp_name
        ).filter(Personnel.emp_status == '离职').limit(50).all()
        risk_data['resignation_risk'] = {
            'description': '离职人员涉密电脑未清理',
            'count': len(left_with_computer),
            'details': [{'name': p.emp_name, 'emp_id': p.emp_id, 'computer': c.computer_name, 'ip': c.network_address} for p, c in left_with_computer[:10]]
        }
    
    if risk_type in ['all', 'unassigned']:
        # 未分配使用人的涉密电脑
        unassigned = ComputerInfo.query.filter(
            (ComputerInfo.emp_name == None) | (ComputerInfo.emp_name == '')
        ).limit(50).all()
        risk_data['unassigned_risk'] = {
            'description': '未分配使用人的电脑',
            'count': len(unassigned),
            'details': [{'computer_name': c.computer_name, 'ip': c.network_address, 'os': c.operating_system} for c in unassigned[:10]]
        }
    
    if risk_type in ['all', 'permission']:
        # 权限配置风险（简化）
        risk_data['permission_risk'] = {
            'description': '系统权限配置审计',
            'note': '建议定期检查人员系统权限矩阵'
        }
    
    prompt = f"""你是一个信息安全风险分析专家。请分析以下风险数据，给出专业的风险评估和处置建议。

<risk_data>
{json.dumps(risk_data, ensure_ascii=False, indent=2)}
</risk_data>

请输出：
1. 风险概览 - 各类风险等级评估
2. 详细分析 - 每个风险点的具体分析
3. 处置建议 - 具体可操作的处置步骤
4. 优先级排序 - 建议的处置优先级
5. 预防措施 - 防止再次发生的预防措施

用Markdown格式输出。"""

    app_instance = current_app._get_current_object()
    
    def generate():
        with app_instance.app_context():
            try:
                messages = [
                    {"role": "system", "content": "你是信息安全风险分析专家，请给出专业、可操作的风险评估和处置建议。"},
                    {"role": "user", "content": prompt}
                ]
                for chunk in call_llm_api_stream(config, messages, timeout=180):
                    if chunk['type'] == 'content':
                        yield "data: " + json.dumps({'content': chunk['content']}, ensure_ascii=False) + "\n\n"
                    elif chunk['type'] == 'error':
                        yield "data: " + json.dumps({'error': chunk['content']}, ensure_ascii=False) + "\n\n"
                yield "data: " + json.dumps({'done': True}, ensure_ascii=False) + "\n\n"
            except Exception as e:
                yield "data: " + json.dumps({'error': str(e)}, ensure_ascii=False) + "\n\n"
    
    return Response(generate(), mimetype='text/event-stream')