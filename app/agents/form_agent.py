# 智能填表助手 Agent - 自动分析数据并智能填写表单
# 支持人员信息、资产信息、保密管理等表单的自动填充

import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


# 表单模板定义 - 定义各类表单的字段和数据映射
FORM_TEMPLATES = {
    'classified_personnel': {
        'name': '涉密人员登记表',
        'description': '涉密人员基本信息登记表',
        'fields': [
            {'key': 'emp_id', 'label': '工号', 'source': 'employees_info.emp_id', 'required': True},
            {'key': 'emp_name', 'label': '姓名', 'source': 'employees_info.emp_name', 'required': True},
            {'key': 'dept_name', 'label': '所属部门', 'source': 'employees_info.dept_full_name', 'required': True},
            {'key': 'position', 'label': '职务', 'source': 'employees_info.position', 'required': False},
            {'key': 'classification_level', 'label': '涉密等级', 'source': 'auto_suggest', 'required': True},
            {'key': 'training_record', 'label': '培训记录', 'source': 'auto_suggest', 'required': False},
            {'key': 'agreement_type', 'label': '保密协议类型', 'source': 'auto_suggest', 'required': True},
            {'key': 'signing_date', 'label': '签订日期', 'source': 'auto_suggest', 'required': True},
            {'key': 'status', 'label': '状态', 'source': 'auto_suggest', 'required': True},
        ]
    },
    'classified_media': {
        'name': '涉密存储介质登记表',
        'description': '涉密U盘、硬盘等存储介质登记',
        'fields': [
            {'key': 'media_id', 'label': '介质编号', 'source': 'auto_generate', 'required': True},
            {'key': 'media_type', 'label': '介质类型', 'source': 'auto_suggest', 'required': True},
            {'key': 'brand_model', 'label': '品牌型号', 'source': 'auto_suggest', 'required': False},
            {'key': 'serial_no', 'label': '序列号', 'source': 'auto_suggest', 'required': True},
            {'key': 'classification', 'label': '密级', 'source': 'auto_suggest', 'required': True},
            {'key': 'custodian_name', 'label': '保管人', 'source': 'employees_info.emp_name', 'required': True},
            {'key': 'custodian_id', 'label': '保管人工号', 'source': 'employees_info.emp_id', 'required': True},
            {'key': 'dept_name', 'label': '所属部门', 'source': 'employees_info.dept_full_name', 'required': True},
            {'key': 'purpose', 'label': '用途', 'source': 'auto_suggest', 'required': False},
            {'key': 'capacity', 'label': '容量', 'source': 'auto_suggest', 'required': False},
        ]
    },
    'computer_asset': {
        'name': '电脑资产登记表',
        'description': '办公电脑/工控机资产信息登记',
        'fields': [
            {'key': 'computer_name', 'label': '电脑名称', 'source': 'computer_info.computer_name', 'required': True},
            {'key': 'employee_id', 'label': '使用人工号', 'source': 'computer_info.employee_id', 'required': True},
            {'key': 'emp_name', 'label': '使用人', 'source': 'computer_info.emp_name', 'required': True},
            {'key': 'asset_id', 'label': '资产编号', 'source': 'computer_info.asset_id', 'required': True},
            {'key': 'network_address', 'label': 'IP地址', 'source': 'computer_info.network_address', 'required': True},
            {'key': 'operating_system', 'label': '操作系统', 'source': 'computer_info.operating_system', 'required': True},
            {'key': 'ip_mac', 'label': 'MAC地址', 'source': 'computer_info.ip_mac', 'required': True},
            {'key': 'dept_level2', 'label': '所属部门', 'source': 'computer_info.dept_level2', 'required': False},
        ]
    },
    'security_zone': {
        'name': '保密区域登记表',
        'description': '保密要害部门部位登记',
        'fields': [
            {'key': 'zone_id', 'label': '区域编号', 'source': 'auto_generate', 'required': True},
            {'key': 'zone_name', 'label': '区域名称', 'source': 'auto_suggest', 'required': True},
            {'key': 'zone_type', 'label': '区域类型', 'source': 'auto_suggest', 'required': True},
            {'key': 'location', 'label': '位置', 'source': 'auto_suggest', 'required': True},
            {'key': 'manager_name', 'label': '负责人', 'source': 'employees_info.emp_name', 'required': True},
            {'key': 'manager_id', 'label': '负责人工号', 'source': 'employees_info.emp_id', 'required': True},
            {'key': 'dept_name', 'label': '所属部门', 'source': 'employees_info.dept_full_name', 'required': True},
            {'key': 'zone_level', 'label': '区域等级', 'source': 'auto_suggest', 'required': True},
        ]
    },
    'audit_record': {
        'name': '稽查记录表',
        'description': '信息安全稽查记录',
        'fields': [
            {'key': 'audit_type', 'label': '稽查类型', 'source': 'auto_suggest', 'required': True},
            {'key': 'audit_scope', 'label': '稽查范围', 'source': 'auto_suggest', 'required': True},
            {'key': 'audit_content', 'label': '稽查内容', 'source': 'auto_suggest', 'required': True},
            {'key': 'audit_result', 'label': '稽查结果', 'source': 'auto_suggest', 'required': False},
            {'key': 'issue_found', 'label': '发现问题', 'source': 'auto_suggest', 'required': False},
            {'key': 'suggestion', 'label': '整改建议', 'source': 'auto_suggest', 'required': False},
        ]
    }
}


def get_form_templates():
    """获取所有表单模板"""
    return FORM_TEMPLATES


def get_form_template(template_id):
    """获取指定表单模板"""
    return FORM_TEMPLATES.get(template_id)


def auto_fill_from_personnel(emp_id_or_name, db_session, personnel_model, computer_model):
    """根据工号或姓名自动填充数据
    
    Args:
        emp_id_or_name: 工号或姓名
        db_session: 数据库session
        personnel_model: Personnel模型类
        computer_model: ComputerInfo模型类
    
    Returns:
        dict: 填充数据
    """
    # 尝试按工号查询
    person = personnel_model.query.filter_by(emp_id=emp_id_or_name).first()
    if not person:
        # 按姓名查询
        person = personnel_model.query.filter_by(emp_name=emp_id_or_name).first()
    
    if not person:
        return {'success': False, 'error': f'未找到人员：{emp_id_or_name}'}
    
    # 查询关联的电脑信息
    computers = computer_model.query.filter(
        (computer_model.emp_name == person.emp_name) | 
        (computer_model.employee_id == person.emp_id)
    ).all()
    
    result = {
        'success': True,
        'person': {
            'emp_id': person.emp_id,
            'emp_name': person.emp_name,
            'emp_status': person.emp_status,
            'emp_gender': person.emp_gender,
            'dept_full_name': person.dept_full_name,
            'dept_level1': person.dept_level1,
            'dept_level2': person.dept_level2,
            'position': person.position,
            'job_title': person.job_title,
            'job_rank': person.job_rank,
            'phone_number': person.phone_number,
            'hire_date': person.hire_date,
            'emp_type': person.emp_type,
            'highest_education': person.highest_education,
            'school': person.school,
        },
        'computers': []
    }
    
    for comp in computers:
        result['computers'].append({
            'computer_name': comp.computer_name,
            'employee_id': comp.employee_id,
            'asset_id': comp.asset_id,
            'network_address': comp.network_address,
            'operating_system': comp.operating_system,
            'ip_mac': comp.ip_mac,
            'dept_level2': comp.dept_level2,
        })
    
    return result


def validate_form_data(template_id, form_data, config, call_llm_func):
    """智能校验表单数据
    
    Args:
        template_id: 表单模板ID
        form_data: 表单数据
        config: AI配置
        call_llm_func: LLM调用函数
    
    Returns:
        dict: 校验结果
    """
    template = get_form_template(template_id)
    if not template:
        return {'success': False, 'error': f'未知表单模板：{template_id}'}
    
    # 基础校验 - 必填字段
    errors = []
    warnings = []
    
    for field in template['fields']:
        if field['required']:
            value = form_data.get(field['key'], '')
            if not value or str(value).strip() == '':
                errors.append(f"必填字段「{field['label']}」未填写")
    
    # AI深度校验
    prompt = f"""请校验以下表单数据的完整性和合理性。

<template_info>
表单名称：{template['name']}
表单描述：{template['description']}
字段定义：{json.dumps([{'key': f['key'], 'label': f['label'], 'required': f['required']} for f in template['fields']], ensure_ascii=False)}
</template_info>

<form_data>
{json.dumps(form_data, ensure_ascii=False, indent=2)}
</form_data>

请检查以下方面：
1. 必填字段是否完整
2. 数据格式是否正确（如工号格式、日期格式等）
3. 数据逻辑是否合理（如涉密等级与部门类型是否匹配）
4. 是否存在常见的数据录入错误

只输出校验结果，格式如下：
- ✅ 通过项：...
- ⚠️ 警告项：...
- ❌ 错误项：..."""

    try:
        messages = [
            {"role": "system", "content": "你是数据校验专家，请仔细检查表单数据的完整性和合理性。"},
            {"role": "user", "content": prompt}
        ]
        result = call_llm_func(config, messages, timeout=60)
        return {
            'success': True,
            'validation': result,
            'basic_errors': errors,
            'basic_warnings': warnings
        }
    except Exception as e:
        logger.error(f"Form validation error: {str(e)}")
        return {
            'success': True,
            'validation': None,
            'basic_errors': errors,
            'basic_warnings': warnings,
            'ai_error': str(e)
        }


def smart_fill_suggestion(template_id, partial_data, config, call_llm_func):
    """根据部分数据智能推荐填充建议
    
    Args:
        template_id: 表单模板ID
        partial_data: 已填写的部分数据
        config: AI配置
        call_llm_func: LLM调用函数
    
    Returns:
        dict: 填充建议
    """
    template = get_form_template(template_id)
    if not template:
        return {'success': False, 'error': f'未知表单模板：{template_id}'}
    
    prompt = f"""你是一个智能表单填写助手。根据用户已填写的部分数据，推测并建议其他字段的填写内容。

<template_info>
表单名称：{template['name']}
字段定义：{json.dumps([{'key': f['key'], 'label': f['label']} for f in template['fields']], ensure_ascii=False)}
</template_info>

<partial_data>
{json.dumps(partial_data, ensure_ascii=False, indent=2)}
</partial_data>

请根据已有数据，推测未填写字段的建议值。以JSON格式输出建议：

```json
{{
    "suggestions": {{
        "字段key": {{
            "value": "建议值",
            "confidence": "high/medium/low",
            "reason": "推测理由"
        }}
    }}
}}
```"""

    try:
        messages = [
            {"role": "system", "content": "你是智能表单填写助手，善于根据上下文推测字段内容。请以JSON格式输出建议。"},
            {"role": "user", "content": prompt}
        ]
        result = call_llm_func(config, messages, timeout=60)
        
        # 尝试解析JSON
        import re
        json_match = re.search(r'```json\s*(.*?)\s*```', result, re.DOTALL)
        if json_match:
            suggestions = json.loads(json_match.group(1))
            return {'success': True, 'suggestions': suggestions.get('suggestions', {})}
        
        return {'success': True, 'suggestions': {}, 'raw': result}
    except Exception as e:
        logger.error(f"Smart fill suggestion error: {str(e)}")
        return {'success': False, 'error': str(e)}


def batch_generate_form(template_id, records, config, call_llm_func):
    """批量生成表单内容
    
    Args:
        template_id: 表单模板ID
        records: 数据记录列表
        config: AI配置
        call_llm_func: LLM调用函数
    
    Returns:
        dict: 批量生成结果
    """
    template = get_form_template(template_id)
    if not template:
        return {'success': False, 'error': f'未知表单模板：{template_id}'}
    
    prompt = f"""请根据以下数据记录，批量生成{template['name']}的表单内容。

<template_fields>
{json.dumps([{'key': f['key'], 'label': f['label']} for f in template['fields']], ensure_ascii=False)}
</template_fields>

<data_records>
{json.dumps(records[:20], ensure_ascii=False, indent=2)}
</data_records>

请为每条记录生成完整的表单数据，以JSON数组格式输出：

```json
[
    {{
        "record_index": 0,
        "form_data": {{
            "字段key": "值",
            ...
        }}
    }}
]
```"""

    try:
        messages = [
            {"role": "system", "content": f"你是{template['name']}的智能填写助手。请根据提供的数据，批量生成规范的表单内容。"},
            {"role": "user", "content": prompt}
        ]
        result = call_llm_func(config, messages, timeout=180)
        
        # 尝试解析JSON
        import re
        json_match = re.search(r'```json\s*(.*?)\s*```', result, re.DOTALL)
        if json_match:
            forms = json.loads(json_match.group(1))
            return {'success': True, 'forms': forms, 'total': len(forms)}
        
        return {'success': True, 'raw': result}
    except Exception as e:
        logger.error(f"Batch generate form error: {str(e)}")
        return {'success': False, 'error': str(e)}