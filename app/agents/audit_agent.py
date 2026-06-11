# 稽查助手 Agent - 智能稽查辅助
# 自动分析稽查数据、生成稽查建议、辅助稽查记录填写

import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


# 稽查类型对应的检查清单模板
AUDIT_CHECKLISTS = {
    '安全稽查': {
        'checkpoints': [
            {'item': '涉密人员保密协议签订情况', 'method': '核查涉密人员登记表，确认保密协议签订率', 'risk': 'high'},
            {'item': '涉密电脑安全防护措施', 'method': '检查杀毒软件安装、白名单扫描、USB端口管控', 'risk': 'high'},
            {'item': '保密区域门禁管理', 'method': '核查门禁记录、访客登记、监控覆盖', 'risk': 'high'},
            {'item': '涉密文件流转记录', 'method': '检查电子文档和纸质文档的借阅、复制、销毁记录', 'risk': 'medium'},
            {'item': '保密教育培训开展情况', 'method': '核查培训记录、参训人员覆盖率', 'risk': 'medium'},
            {'item': '离职人员涉密载体清理', 'method': '核查离职人员涉密介质回收、权限注销记录', 'risk': 'high'},
        ],
        'focus': '信息安全保密管理合规性'
    },
    '资产稽查': {
        'checkpoints': [
            {'item': '办公电脑资产台账一致性', 'method': '比对系统记录与实物，核查账实相符率', 'risk': 'high'},
            {'item': '工控机安全防护措施', 'method': '检查杀毒安装、IEP部署、白名单扫描情况', 'risk': 'high'},
            {'item': '未分配使用人的涉密电脑', 'method': '查询无使用人记录的涉密电脑清单', 'risk': 'high'},
            {'item': '资产变更记录完整性', 'method': '核查资产调拨、报废、维修记录', 'risk': 'medium'},
            {'item': 'IP地址分配管理', 'method': '检查IP地址分配记录、MAC地址绑定', 'risk': 'medium'},
            {'item': '操作系统版本合规性', 'method': '统计各操作系统版本，检查是否存在过期系统', 'risk': 'medium'},
        ],
        'focus': '信息资产台账完整性和安全合规'
    },
    '权限稽查': {
        'checkpoints': [
            {'item': '系统权限配置合理性', 'method': '核查人员系统权限矩阵，识别越权配置', 'risk': 'high'},
            {'item': '离职人员账号注销', 'method': '比对离职人员清单与系统活跃账号', 'risk': 'high'},
            {'item': '角色权限最小化原则', 'method': '检查是否存在过度授权的角色配置', 'risk': 'medium'},
            {'item': '数据访问范围控制', 'method': '核查部门数据隔离策略执行情况', 'risk': 'medium'},
            {'item': '管理员账号管理', 'method': '检查管理员账号数量、权限范围、操作审计', 'risk': 'high'},
        ],
        'focus': '系统权限配置安全性和合规性'
    },
    '合规稽查': {
        'checkpoints': [
            {'item': '保密制度执行情况', 'method': '核查各项保密制度的落实记录', 'risk': 'high'},
            {'item': '涉密载体管理规范', 'method': '检查涉密U盘、硬盘的领用、归还、销毁记录', 'risk': 'high'},
            {'item': '保密要害部门管理', 'method': '核查保密区域标识、安防设施、人员出入管理', 'risk': 'high'},
            {'item': '应急响应机制', 'method': '检查应急预案更新、演练开展、应急小组配置', 'risk': 'medium'},
            {'item': '违规事件处置闭环', 'method': '核查违规事件发现、报告、处置、整改闭环', 'risk': 'medium'},
        ],
        'focus': '保密合规制度执行情况'
    }
}


def get_audit_checklist(audit_type):
    """获取指定类型的稽查检查清单"""
    return AUDIT_CHECKLISTS.get(audit_type, AUDIT_CHECKLISTS.get('安全稽查'))


def analyze_audit_task(task, config, call_llm_func):
    """分析稽查任务，生成检查要点和建议
    
    Args:
        task: AuditTask对象
        config: AI配置
        call_llm_func: LLM调用函数
    
    Returns:
        dict: 分析结果
    """
    audit_type = task.task_type
    checklist = get_audit_checklist(audit_type)
    
    # 构建分析prompt
    prompt = f"""你是一个专业的信息安全稽查助手。请分析以下稽查任务，生成详细的检查要点和建议。

<task_info>
任务编号：{task.task_no}
任务标题：{task.task_title}
任务类型：{task.task_type}
任务内容：{task.task_content}
任务要求：{task.task_requirement or '无特殊要求'}
优先级：{task.priority}
被稽查部门：{task.dept_name or '未指定'}
截止时间：{task.deadline.strftime('%Y-%m-%d %H:%M') if task.deadline else '未指定'}
</task_info>

<reference_checklist>
参考检查清单（{audit_type}）：
{json.dumps(checklist['checkpoints'], ensure_ascii=False, indent=2)}
</reference_checklist>

请输出以下内容：

## 1. 稽查重点分析
根据任务内容和类型，分析本次稽查的重点关注领域。

## 2. 详细检查清单
基于参考清单，结合具体任务内容，生成针对性的检查项目清单。

## 3. 稽查方法建议
针对每个检查项目，给出具体的检查方法和步骤。

## 4. 风险预判
预判可能发现的问题和风险点。

## 5. 稽查注意事项
提醒稽查人员需要特别注意的事项。"""

    try:
        messages = [
            {"role": "system", "content": "你是专业的信息安全稽查顾问，具有丰富的稽查经验。请用结构化的方式输出分析结果，使用Markdown格式。"},
            {"role": "user", "content": prompt}
        ]
        result = call_llm_func(config, messages, timeout=120)
        return {
            'success': True,
            'analysis': result,
            'checklist': checklist,
            'audit_type': audit_type
        }
    except Exception as e:
        logger.error(f"Audit task analysis error: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'checklist': checklist,
            'audit_type': audit_type
        }


def generate_audit_suggestions(audit_type, audit_scope, findings, config, call_llm_func):
    """根据稽查发现生成整改建议
    
    Args:
        audit_type: 稽查类型
        audit_scope: 稽查范围
        findings: 稽查发现的问题
        config: AI配置
        call_llm_func: LLM调用函数
    
    Returns:
        dict: 建议结果
    """
    prompt = f"""你是一个专业的信息安全稽查顾问。请根据以下稽查发现，生成详细的整改建议。

<audit_info>
稽查类型：{audit_type}
稽查范围：{audit_scope}
</audit_info>

<findings>
{findings}
</findings>

请输出以下内容：

## 整改建议

针对每个发现的问题，给出：
1. 问题等级（严重/一般/轻微）
2. 整改措施（具体可操作的步骤）
3. 整改时限建议
4. 责任方建议

## 后续跟踪建议

建议的后续跟踪方式和频次。"""

    try:
        messages = [
            {"role": "system", "content": "你是专业的信息安全稽查顾问，擅长制定整改方案。请用Markdown格式输出，确保建议具体可操作。"},
            {"role": "user", "content": prompt}
        ]
        result = call_llm_func(config, messages, timeout=120)
        return {'success': True, 'suggestions': result}
    except Exception as e:
        logger.error(f"Generate audit suggestions error: {str(e)}")
        return {'success': False, 'error': str(e)}


def generate_audit_record_draft(task, findings, config, call_llm_func):
    """辅助生成稽查记录草稿
    
    Args:
        task: AuditTask对象
        findings: 稽查发现
        config: AI配置
        call_llm_func: LLM调用函数
    
    Returns:
        dict: 草稿结果
    """
    prompt = f"""请根据以下信息生成一份稽查记录草稿。

<task_info>
任务编号：{task.task_no}
任务标题：{task.task_title}
任务类型：{task.task_type}
稽查范围：{task.dept_name or '未指定'}
</task_info>

<findings>
{findings}
</findings>

请按以下格式输出：

**稽查类型**：{task.task_type}

**稽查范围**：{task.dept_name or '未指定'}

**稽查内容**：
（概括本次稽查的主要内容）

**稽查结果**：
（详细描述稽查发现）

**发现的问题**：
（列出发现的具体问题，编号列出）

**整改建议**：
（针对每个问题给出整改建议）"""

    try:
        messages = [
            {"role": "system", "content": "你是稽查记录撰写助手，请生成规范、完整的稽查记录草稿。使用正式的公文用语。"},
            {"role": "user", "content": prompt}
        ]
        result = call_llm_func(config, messages, timeout=120)
        return {'success': True, 'draft': result}
    except Exception as e:
        logger.error(f"Generate audit record draft error: {str(e)}")
        return {'success': False, 'error': str(e)}


def analyze_audit_statistics(stats_data, config, call_llm_func):
    """分析稽查统计数据，发现风险趋势
    
    Args:
        stats_data: dict 包含各类统计数据
        config: AI配置
        call_llm_func: LLM调用函数
    
    Returns:
        dict: 分析结果
    """
    prompt = f"""你是一个数据分析专家。请分析以下稽查统计数据，发现风险趋势和规律。

<statistics>
{json.dumps(stats_data, ensure_ascii=False, indent=2)}
</statistics>

请输出以下内容：

## 1. 数据概览
简要总结关键数据指标。

## 2. 趋势分析
分析各维度数据的变化趋势。

## 3. 风险预警
识别需要重点关注的风险领域和部门。

## 4. 改进建议
针对发现的问题，提出系统性改进建议。"""

    try:
        messages = [
            {"role": "system", "content": "你是数据分析专家，擅长从统计数据中发现风险趋势。请用Markdown格式输出。"},
            {"role": "user", "content": prompt}
        ]
        result = call_llm_func(config, messages, timeout=120)
        return {'success': True, 'analysis': result}
    except Exception as e:
        logger.error(f"Audit statistics analysis error: {str(e)}")
        return {'success': False, 'error': str(e)}