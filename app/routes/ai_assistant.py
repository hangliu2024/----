from flask import Blueprint, render_template, request, jsonify, current_app, Response
from flask_login import login_required, current_user
from app import db
from app.models import Personnel, ComputerInfo, Department, User, ChatSession, ChatMessage
from datetime import datetime
import re
import requests
import json
import logging
import functools

logger = logging.getLogger(__name__)

bp = Blueprint('ai_assistant', __name__)


# API Key认证装饰器
def api_key_required(f):
    """API Key认证装饰器，用于外部程序调用"""
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        
        valid_api_keys = current_app.config.get('AI_API_KEYS', [])
        
        if not valid_api_keys:
            return jsonify({
                'success': False,
                'error': 'AI API未配置密钥，请联系管理员在.env中设置AI_API_KEYS'
            }), 401
        
        if not api_key or api_key not in valid_api_keys:
            return jsonify({
                'success': False,
                'error': '无效的API Key，请在请求头中提供有效的X-API-Key'
            }), 401
        
        return f(*args, **kwargs)
    # 标记为CSRF豁免，因为API路由使用API Key认证，不需要CSRF token
    decorated_function._csrf_exempt = True
    return decorated_function

@bp.route('/ai-assistant')
@login_required
def ai_assistant():
    current_time = datetime.now().strftime('%H:%M')
    return render_template('ai_assistant/ai_assistant.html', current_time=current_time)

def call_llm_api_v2(config, messages, timeout=300):
    """不依赖current_app的LLM API调用"""
    provider = config['provider']
    api_key = config['api_key']
    model = config['model']
    
    logger.info(f"Calling LLM API - Provider: {provider}, Model: {model}")
    
    if provider == 'ollama':
        api_base = config['ollama_api_base']
        url = f"{api_base.rstrip('/')}/chat/completions"
        payload = {"model": model, "messages": messages, "stream": False}
        try:
            response = requests.post(url, json=payload, timeout=timeout)
            if response.status_code == 200:
                response_json = response.json()
                message = response_json.get('choices', [{}])[0].get('message', {})
                content = message.get('content', '')
                thinking = message.get('reasoning', '') or message.get('thinking', '') or message.get('reasoning_content', '')
                if thinking and content:
                    return f"思考过程:\n{thinking}\n\n回答:\n{content}"
                return content
            raise Exception(f"Ollama API返回 {response.status_code}")
        except requests.exceptions.Timeout:
            raise Exception("Ollama请求超时")
    elif provider == 'openai':
        api_base = config['openai_api_base']
        url = f"{api_base.rstrip('/')}/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {"model": model, "messages": messages}
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=timeout)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            raise Exception(f"OpenAI API返回 {response.status_code}")
        except requests.exceptions.Timeout:
            raise Exception("OpenAI请求超时")
    else:
        url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
        headers = {"Authorization": f"Bearer {config['minimax_api_key']}", "Content-Type": "application/json"}
        payload = {"model": model, "messages": messages}
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=timeout)
            if response.status_code == 200:
                response_json = response.json()
                if 'choices' in response_json:
                    return response_json['choices'][0]['message']['content']
            raise Exception(f"MiniMax API返回 {response.status_code}")
        except requests.exceptions.Timeout:
            raise Exception("MiniMax请求超时")


def call_llm_api_stream(config, messages, timeout=300):
    """流式调用LLM API，逐token返回内容
    
    Yields:
        dict: {'type': 'thinking', 'content': '...'} for thinking/reasoning content
              {'type': 'content', 'content': '...'} for answer content
              {'type': 'error', 'content': '...'} for errors
    """
    provider = config['provider']
    api_key = config['api_key']
    model = config['model']
    
    logger.info(f"Calling LLM API (stream) - Provider: {provider}, Model: {model}")
    
    if provider == 'ollama':
        api_base = config['ollama_api_base']
        url = f"{api_base.rstrip('/')}/chat/completions"
        payload = {"model": model, "messages": messages, "stream": True}
        try:
            response = requests.post(url, json=payload, timeout=timeout, stream=True)
            response.encoding = 'utf-8'
            if response.status_code == 200:
                for line in response.iter_lines(decode_unicode=True):
                    if not line or not line.startswith('data: '):
                        continue
                    data_str = line[6:].strip()
                    if data_str == '[DONE]':
                        break
                    try:
                        chunk = json.loads(data_str)
                        delta = chunk.get('choices', [{}])[0].get('delta', {})
                        # Ollama的qwen3.5等推理模型用"reasoning"字段返回思考内容
                        thinking_content = delta.get('reasoning', '') or delta.get('thinking', '') or delta.get('reasoning_content', '')
                        if thinking_content:
                            yield {'type': 'thinking', 'content': thinking_content}
                        content = delta.get('content', '')
                        if content:
                            yield {'type': 'content', 'content': content}
                    except json.JSONDecodeError:
                        continue
            else:
                yield {'type': 'error', 'content': f'Ollama API返回 {response.status_code}'}
        except requests.exceptions.Timeout:
            yield {'type': 'error', 'content': 'Ollama请求超时'}
        except Exception as e:
            yield {'type': 'error', 'content': str(e)}
    elif provider == 'openai':
        api_base = config['openai_api_base']
        url = f"{api_base.rstrip('/')}/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {"model": model, "messages": messages, "stream": True}
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=timeout, stream=True)
            response.encoding = 'utf-8'
            if response.status_code == 200:
                for line in response.iter_lines(decode_unicode=True):
                    if not line or not line.startswith('data: '):
                        continue
                    data_str = line[6:].strip()
                    if data_str == '[DONE]':
                        break
                    try:
                        chunk = json.loads(data_str)
                        delta = chunk.get('choices', [{}])[0].get('delta', {})
                        thinking_content = delta.get('reasoning_content', '') or delta.get('thinking', '')
                        if thinking_content:
                            yield {'type': 'thinking', 'content': thinking_content}
                        content = delta.get('content', '')
                        if content:
                            yield {'type': 'content', 'content': content}
                    except json.JSONDecodeError:
                        continue
            else:
                yield {'type': 'error', 'content': f'OpenAI API返回 {response.status_code}'}
        except requests.exceptions.Timeout:
            yield {'type': 'error', 'content': 'OpenAI请求超时'}
        except Exception as e:
            yield {'type': 'error', 'content': str(e)}
    else:
        url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
        headers = {"Authorization": f"Bearer {config['minimax_api_key']}", "Content-Type": "application/json"}
        payload = {"model": model, "messages": messages, "stream": True}
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=timeout, stream=True)
            response.encoding = 'utf-8'
            if response.status_code == 200:
                for line in response.iter_lines(decode_unicode=True):
                    if not line or not line.startswith('data: '):
                        continue
                    data_str = line[6:].strip()
                    if data_str == '[DONE]':
                        break
                    try:
                        chunk = json.loads(data_str)
                        delta = chunk.get('choices', [{}])[0].get('delta', {})
                        content = delta.get('content', '')
                        if content:
                            yield {'type': 'content', 'content': content}
                    except json.JSONDecodeError:
                        continue
            else:
                yield {'type': 'error', 'content': f'MiniMax API返回 {response.status_code}'}
        except requests.exceptions.Timeout:
            yield {'type': 'error', 'content': 'MiniMax请求超时'}
        except Exception as e:
            yield {'type': 'error', 'content': str(e)}


def is_obviously_non_db_query(question):
    """快速关键词判断：明显不需要查数据库的问题直接跳过意图识别，省2-10秒"""
    non_db_keywords = [
        '写', '作文', '故事', '笑话', '诗', '歌词', '小说', '文章', '演讲稿',
        '总结', '概括', '翻译', '解释', '什么是', '为什么', '怎么', '如何',
        '帮我', '你能', '请问', '你好', '早上好', '下午好', '晚上好',
        '天气', '今天', '推荐', '建议', '想法', '看法', '观点',
        '对比', '区别', '意义', '影响', '原因', '方法',
        '谢谢', '感谢', '再见', '拜拜', '哈哈', '嗯嗯',
        '汇报', '材料', '报告', '方案', '计划', 'PPT', 'ppt',
        '流程', '步骤', '模板', '格式', '范文', '示例'
    ]
    # 检查是否包含明显的数据库查询关键词
    db_keywords = [
        '查询', '查找', '搜索', '列出', '统计', '多少', '几个', '人数',
        '工号', 'IP', '电话', '部门', '员工', '电脑', '在职', '离职',
        '资产', '姓名', '职位', '职级', '入职', '操作系统',
        '住址', '地址', '家庭住址', '居住地', '户籍', '身份证地址'
    ]
    has_db_keyword = any(kw in question for kw in db_keywords)
    has_non_db_keyword = any(kw in question for kw in non_db_keywords)
    
    # 如果有数据库关键词，不做跳过（让LLM判断）
    if has_db_keyword:
        return False
    # 如果有非数据库关键词，直接跳过
    if has_non_db_keyword:
        return True
    return False


def check_if_needs_database_query_v2(question, db_schema, config):
    prompt = f"""判断用户问题是否需要查询数据库来回答。

用户问题：{question}

以下类型的问题必须回答"是"（需要查询数据库）：
- 列出、查找、查询、搜索任何人员、部门、电脑等信息
- 统计数量（多少人、多少台电脑等）
- 查询某个人的信息（电话、部门、职位、住址、地址等）
- 查询某个部门的员工列表
- 涉及工号、IP地址、资产编号等具体数据
- 任何关于"经理"、"主管"、"工程师"等职位的人员查询
- 查询某人的家庭住址、现居住地、户籍所在地、身份证地址等地址信息

以下类型回答"否"（普通闲聊）：
- 问候语（你好、早上好等）
- 闲聊（今天天气怎么样等）
- 关于系统本身的使用问题

只回答一个字：是或否。"""

    try:
        messages = [
            {"role": "system", "content": "你是一个分类器，只回答是或否。涉及任何人员、部门、电脑、资产数据查询的都回答是。"},
            {"role": "user", "content": prompt}
        ]
        result = call_llm_api_v2(config, messages, timeout=30)
        logger.info(f"Intent check: {result}")
        return result.strip() in ['是', 'yes', 'y', 'true', '1']
    except Exception as e:
        logger.error(f"Intent detection error: {str(e)}")
        return True

def generate_sql_v2(question, db_schema, config):
    """参考NocoBase的结构化SQL生成Prompt"""
    prompt = f"""<task>
你是一个专业的SQL生成助手。根据用户的问题和数据库结构，生成准确的SQL查询语句。
</task>

{db_schema}

<instructions>
1. 仔细分析用户问题，理解查询意图
2. 根据上面的表结构选择正确的表和字段
3. 参考few_shot_examples中的示例格式
4. 生成标准的MySQL SELECT语句
5. 只返回SQL语句，用```sql代码块包裹

特别注意：
- 当用户说的部门名称可能是简称时，要拆分成多个LIKE条件
- 例如："人力资源保卫部" 应该理解为 "人力资源中心" + "保卫部"
- 使用 LIKE '%人力资源%' AND LIKE '%保卫部%' 这样的组合条件
</instructions>

<user_question>
{question}
</user_question>

<output_format>
```sql
你的SQL语句
```
</output_format>"""
    
    try:
        messages = [
            {
                "role": "system", 
                "content": """你是一个SQL专家。请遵循以下规则：
1. 员工状态字段 emp_status 取值必须是 '在职' 或 '离职'
2. 部门名称查询用 LIKE 模糊匹配，如 dept_full_name LIKE '%关键词%'
3. 当用户说的部门名称可能是简称时，拆分成多个LIKE条件
   例如："人力资源保卫部" 应该用 LIKE '%人力资源%' AND LIKE '%保卫部%'
4. 统计数量用 COUNT(*)
5. 只生成SELECT查询语句，不要生成INSERT/UPDATE/DELETE
6. 返回的SQL要用```sql代码块包裹"""
            },
            {"role": "user", "content": prompt}
        ]
        content = call_llm_api_v2(config, messages, timeout=180)
        logger.info(f"LLM response for SQL: {content[:500]}...")
        
        sql_match = re.search(r'```sql\s*(.*?)\s*```', content, re.DOTALL | re.IGNORECASE)
        if sql_match:
            sql = sql_match.group(1).strip()
            if sql.upper().startswith('SELECT'):
                return sql
        
        sql_match = re.search(r'(SELECT\s+.*?(?:;|$))', content, re.DOTALL | re.IGNORECASE)
        if sql_match:
            sql = sql_match.group(1).strip().rstrip(';')
            if sql.upper().startswith('SELECT'):
                return sql
        
        logger.error(f"Could not extract SQL from response: {content}")
        return None
    except Exception as e:
        logger.error(f"SQL generation error: {str(e)}")
        return None

def smart_retry_query(question, sql, db_schema, config):
    """当查询结果为0时，智能重试：拆分关键词重新生成SQL"""
    logger.info(f"Smart retry for question: {question}")
    
    prompt = f"""<task>
上一次查询返回0条结果，可能是因为部门名称匹配不正确。请重新分析并生成更准确的SQL。
</task>

<original_question>
{question}
</original_question>

<original_sql>
{sql}
</original_sql>

{db_schema}

<instructions>
1. 分析用户问题中的关键词
2. 数据库中的部门路径格式是：集团总部/人力资源中心/保卫部
3. 当用户说"人力资源保卫部"时，应该拆分成：
   LIKE '%人力资源%' AND LIKE '%保卫部%'
4. 尝试使用更宽松的匹配条件
5. 只返回SQL语句，用```sql代码块包裹
</instructions>"""
    
    try:
        messages = [
            {
                "role": "system", 
                "content": "你是SQL专家。当查询结果为空时，尝试拆分部门名称关键词，使用多个LIKE条件。"
            },
            {"role": "user", "content": prompt}
        ]
        content = call_llm_api_v2(config, messages, timeout=60)
        
        sql_match = re.search(r'```sql\s*(.*?)\s*```', content, re.DOTALL | re.IGNORECASE)
        if sql_match:
            new_sql = sql_match.group(1).strip()
            if new_sql.upper().startswith('SELECT'):
                logger.info(f"Retry SQL: {new_sql}")
                return new_sql
        
        sql_match = re.search(r'(SELECT\s+.*?(?:;|$))', content, re.DOTALL | re.IGNORECASE)
        if sql_match:
            new_sql = sql_match.group(1).strip().rstrip(';')
            if new_sql.upper().startswith('SELECT'):
                logger.info(f"Retry SQL: {new_sql}")
                return new_sql
        
        return None
    except Exception as e:
        logger.error(f"Smart retry error: {str(e)}")
        return None

def execute_sql(sql):
    """执行SQL并返回结果（仅限只读查询）"""
    sql_upper = sql.strip().upper()
    if not sql_upper.startswith('SELECT') and not sql_upper.startswith('SHOW') and not sql_upper.startswith('DESCRIBE') and not sql_upper.startswith('EXPLAIN'):
        return None, "仅允许执行 SELECT/SHOW/DESCRIBE 只读查询"
    
    dangerous = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE', 'GRANT', 'REVOKE',
                 'REPLACE', 'RENAME', 'LOAD', 'INTO OUTFILE', 'INTO DUMPFILE', 'LOCK', 'UNLOCK']
    for keyword in dangerous:
        if re.search(r'\b' + keyword + r'\b', sql_upper):
            return None, f"禁止执行 {keyword} 操作，仅允许 SELECT/SHOW/DESCRIBE 只读查询"
    
    try:
        logger.info(f"Executing SQL: {sql}")
        result = db.session.execute(db.text(sql))
        columns = result.keys()
        rows = [dict(zip(columns, row)) for row in result.fetchmany(100)]
        logger.info(f"SQL executed successfully, got {len(rows)} rows")
        return rows, None
    except Exception as e:
        error_msg = str(e)
        logger.error(f"SQL execution error: {error_msg}")
        return None, error_msg

def fix_sql_with_error(sql, error_msg, question, db_schema, config):
    """当SQL执行失败时，让LLM修复SQL"""
    prompt = f"""<task>
生成的SQL执行出错，请根据错误信息修复SQL。
</task>

<original_sql>
{sql}
</original_sql>

<error_message>
{error_msg}
</error_message>

<user_question>
{question}
</user_question>

{db_schema}

<instructions>
1. 分析错误原因
2. 根据错误信息修复SQL语法或表名/字段名
3. 只返回修复后的SQL，用```sql代码块包裹
</instructions>"""
    
    try:
        messages = [
            {
                "role": "system", 
                "content": "你是SQL专家，请修复错误的SQL语句。只返回修复后的SQL。"
            },
            {"role": "user", "content": prompt}
        ]
        content = call_llm_api_v2(config, messages, timeout=30)
        
        sql_match = re.search(r'```sql\s*(.*?)\s*```', content, re.DOTALL | re.IGNORECASE)
        if sql_match:
            fixed_sql = sql_match.group(1).strip()
            if fixed_sql.upper().startswith('SELECT'):
                logger.info(f"Fixed SQL: {fixed_sql}")
                return fixed_sql
        
        sql_match = re.search(r'(SELECT\s+.*?(?:;|$))', content, re.DOTALL | re.IGNORECASE)
        if sql_match:
            fixed_sql = sql_match.group(1).strip().rstrip(';')
            if fixed_sql.upper().startswith('SELECT'):
                logger.info(f"Fixed SQL: {fixed_sql}")
                return fixed_sql
        
        return None
    except Exception as e:
        logger.error(f"SQL fix error: {str(e)}")
        return None

def generate_answer_with_data_v2(question, db_schema, sql, data, config):
    """根据查询结果生成回答（非流式）"""
    if len(data) > 1 and any('emp_name' in row or 'emp_id' in row for row in data):
        prompt = f"""根据查询结果回答用户问题。

问题：{question}
查询结果：共{len(data)}条记录
{json.dumps(data[:10], ensure_ascii=False, indent=2)}

重要提示：
1. 查询到多条记录，可能是同名人员
2. **必须使用Markdown表格格式**展示每个人的信息
3. 表格列应包括：工号、姓名、部门、状态、电话等可用字段
4. 如果有在职和离职的区别，在表格后添加提示说明
5. 不要遗漏任何人

输出格式示例：
| 工号 | 姓名 | 部门 | 状态 | 电话 |
|------|------|------|------|------|
| 001 | 张三 | 人力资源部 | 在职 | 138xxxx |
| 002 | 张三 | 财务部 | 离职 | 139xxxx |

提示：以上记录中X条为在职，Y条为已离职。"""
    elif len(data) == 1:
        prompt = f"""根据查询结果回答用户问题。

问题：{question}
查询结果：
{json.dumps(data[0], ensure_ascii=False, indent=2)}

请用Markdown表格格式展示这条记录的信息。"""
    else:
        prompt = f"""根据查询结果回答。

问题：{question}
结果（{len(data)}条）：{data[:10]}

用中文简洁回答，如果是统计数据直接给出数字，如果是列表数据用Markdown表格展示。"""
    
    try:
        messages = [
            {"role": "system", "content": "你是数据分析师，请清晰、准确地展示查询结果。重要：多条记录必须用Markdown表格格式展示。"},
            {"role": "user", "content": prompt}
        ]
        return call_llm_api_v2(config, messages, timeout=60)
    except Exception as e:
        return f"生成回答出错: {str(e)}"


def generate_answer_messages(question, db_schema, sql, data):
    """构造用于流式生成回答的messages列表"""
    if len(data) > 1 and any('emp_name' in row or 'emp_id' in row for row in data):
        prompt = f"""根据查询结果回答用户问题。

问题：{question}
查询结果：共{len(data)}条记录
{json.dumps(data[:10], ensure_ascii=False, indent=2)}

重要提示：
1. 查询到多条记录，可能是同名人员
2. **必须使用Markdown表格格式**展示每个人的信息
3. 表格列应包括：工号、姓名、部门、状态、电话等可用字段
4. 如果有在职和离职的区别，在表格后添加提示说明
5. 不要遗漏任何人

输出格式示例：
| 工号 | 姓名 | 部门 | 状态 | 电话 |
|------|------|------|------|------|
| 001 | 张三 | 人力资源部 | 在职 | 138xxxx |
| 002 | 张三 | 财务部 | 离职 | 139xxxx |

提示：以上记录中X条为在职，Y条为已离职。"""
    elif len(data) == 1:
        prompt = f"""根据查询结果回答用户问题。

问题：{question}
查询结果：
{json.dumps(data[0], ensure_ascii=False, indent=2)}

请用Markdown表格格式展示这条记录的信息。"""
    else:
        prompt = f"""根据查询结果回答。

问题：{question}
结果（{len(data)}条）：{data[:10]}

用中文简洁回答，如果是统计数据直接给出数字，如果是列表数据用Markdown表格展示。"""
    
    return [
        {"role": "system", "content": "你是数据分析师，请清晰、准确地展示查询结果。重要：多条记录必须用Markdown表格格式展示。"},
        {"role": "user", "content": prompt}
    ]


def direct_answer_v2(question, config):
    prompt = question
    
    try:
        messages = [
            {"role": "system", "content": "你是友好的AI助手，请根据用户的问题给出完整、详细的回答。如果用户要求写长文，请完整输出，不要截断。"},
            {"role": "user", "content": prompt}
        ]
        return call_llm_api_v2(config, messages, timeout=60)
    except Exception as e:
        return f"生成回答出错: {str(e)}"


def direct_answer_messages(question):
    """构造用于流式直接回答的messages列表"""
    return [
        {"role": "system", "content": "你是友好的AI助手，请根据用户的问题给出完整、详细的回答。如果用户要求写长文，请完整输出，不要截断。"},
        {"role": "user", "content": question}
    ]


def get_ai_config():
    """获取AI配置（用于异步任务中不依赖current_app）"""
    return {
        'provider': 'ollama',
        'api_key': '',
        'model': 'llama3',
        'ollama_api_base': 'http://localhost:11434/v1',
        'openai_api_base': 'https://api.openai.com/v1',
        'minimax_api_key': ''
    }


def get_database_schema():
    """参考NocoBase做法：详细的数据库Schema描述 + Few-shot示例"""
    return """
<database_schema>
## 表结构

### employees_info (员工信息表) - 约93163条记录
主要字段：
- emp_id: 工号 (如 '000001', '100001')
- emp_name: 姓名 (如 '张三', '李四')
- id_number: 身份证号 (如 '411325198805186015')
- emp_status: 员工状态 (取值: '在职', '离职')
- emp_gender: 性别 (取值: '男', '女')
- emp_type: 员工类型 (取值: '正式工', '派遣工', '实习生')
- company_dept: 公司部门 (如 '惠州亿纬锂能股份有限公司', '湖北亿纬动力有限公司')
- dept_full_name: 部门全称 (如 '集团总部/人力资源中心/保卫部', '集团总部/总裁办公室')
- dept_level1: 一级部门 (如 '集团总部', '研究院')
- dept_level2: 二级部门 (如 '人力资源中心', '总裁办公室')
- leaf_dept: 末级部门
- first_level_dept_abbr: 一级部门简称 (如 '人力资源中心', '研究院')
- position: 职位 (如 '总裁', '工程师')
- job_title: 职称
- job_rank: 职级 (如 'E24', 'P5')
- hire_date: 入职日期
- age: 年龄
- phone_number: 电话号码
- emergency_contact_name: 紧急联系人姓名
- emergency_contact_phone: 紧急联系人电话
- current_residence: 现居住地/家庭住址 (如 '广东省佛山市南海区狮山镇...')
- registered_residence: 户籍所在地 (如 '广东省佛山市南海区')
- id_address: 身份证地址 (如 '广东省佛山市南海区狮山镇...')
- highest_education: 最高学历
- school: 毕业院校

部门层级示例：
- 集团总部/人力资源中心/保卫部
- 集团总部/人力资源中心/薪酬管理部
- 湖北亿纬动力/人力资源中心/HR服务中心
- 集团总部/安环中心/应急准备中心/应急保卫部

### computer_info (电脑信息表) - 办公电脑资产管理
主要字段：
- id: 主键ID (自增整数)
- computer_name: 电脑名称 (如 '9030-30000487(高红福)'，格式通常为 '型号-资产编号(使用人)')
- employee_id: 使用人工号 (如 '132091', '018251'，注意：部分记录错误地填入了登录用户名如'Administrator'等，约15424条是正确工号)
- emp_name: 使用人姓名 (如 '高红福', '张三')
- asset_id: 资产ID (资产编号)
- network_address: IP地址/网络地址 (如 '10.2.59.32', '192.168.1.100')
- ip_mac: MAC地址信息 (物理地址，如 '00:1A:2B:3C:4D:5E')
- operating_system: 操作系统 (如 'Windows 10', 'Windows 11', 'Windows 7')
- last_login_user: 最后登录用户名 (通常是域账号或系统登录名，如 'jy050', 'admin')
- dept_code: 部门代码 (此字段大部分为空)
- dept_level2: 二级部门名称 (如 '人力资源中心', '财务部')

电脑信息示例：
- 电脑名称: '9030-30000487(高红福)' 表示9030型号，资产编号30000487，使用人高红福
- IP地址: 10.x.x.x 为内网地址段
- 操作系统: 大部分为 Windows 10/11

## 表关联
- employees_info.emp_id = computer_info.employee_id (员工工号关联电脑使用人工号，约15456条匹配)
- employees_info.emp_name = computer_info.emp_name (员工姓名关联电脑使用人姓名字段，约39847条匹配)
- 部门关联需要通过 employees_info 表进行 JOIN 查询

## 重要规则
1. 员工状态字段 emp_status 取值必须是 '在职' 或 '离职'，不是'在册'
2. 部门名称查询用 LIKE 模糊匹配，如 dept_full_name LIKE '%关键词%'
3. 当用户问"XX部门有多少人"时，需要同时匹配部门路径中的各个部分
4. 统计数量用 COUNT(*)，分组用 GROUP BY
5. 排序用 ORDER BY ... DESC/ASC
6. 限制结果用 LIMIT
7. 查询电脑时，使用人姓名在 emp_name 字段查找，工号在 employee_id 字段查找
8. IP地址查询使用 network_address 字段
9. employee_id 字段主要存储工号，但部分数据可能不标准（如填入了登录用户名）
</database_schema>

<few_shot_examples>
## 员工信息相关示例

问题: 有多少在职员工？
SQL: SELECT COUNT(*) as total FROM employees_info WHERE emp_status = '在职'

问题: 人力资源中心有多少人？
SQL: SELECT COUNT(*) as total FROM employees_info WHERE emp_status = '在职' AND dept_full_name LIKE '%人力资源中心%'

问题: 人力资源中心的保卫部有多少人？
SQL: SELECT COUNT(*) as total FROM employees_info WHERE emp_status = '在职' AND dept_full_name LIKE '%人力资源中心%保卫部%'

问题: 统计各部门人数
SQL: SELECT dept_level2 as department, COUNT(*) as count FROM employees_info WHERE emp_status = '在职' GROUP BY dept_level2 ORDER BY count DESC

问题: 查询职级E24以上的员工
SQL: SELECT emp_id, emp_name, job_rank, dept_full_name FROM employees_info WHERE emp_status = '在职' AND job_rank LIKE 'E%' ORDER BY job_rank

问题: 最近入职的10个员工
SQL: SELECT emp_id, emp_name, hire_date, dept_full_name FROM employees_info WHERE emp_status = '在职' ORDER BY hire_date DESC LIMIT 10

问题: 安环中心的应急保卫部有多少人？
SQL: SELECT COUNT(*) as total FROM employees_info WHERE emp_status = '在职' AND dept_full_name LIKE '%安环中心%保卫部%'

问题: 查询袁文杰的电话号码
SQL: SELECT emp_id, emp_name, phone_number, dept_full_name, emp_status FROM employees_info WHERE emp_name = '袁文杰'

问题: 查询张三的员工信息
SQL: SELECT emp_id, emp_name, phone_number, dept_full_name, emp_status, position, job_rank FROM employees_info WHERE emp_name = '张三'

问题: 查询在职的张三的信息
SQL: SELECT emp_id, emp_name, phone_number, dept_full_name, position FROM employees_info WHERE emp_name = '张三' AND emp_status = '在职'

问题: 查询张三的紧急联系人
SQL: SELECT emp_id, emp_name, emergency_contact_name, emergency_contact_phone, dept_full_name, emp_status FROM employees_info WHERE emp_name = '张三'

问题: 刘航的紧急联系人是谁
SQL: SELECT emp_id, emp_name, emergency_contact_name, emergency_contact_phone, dept_full_name, emp_status FROM employees_info WHERE emp_name = '刘航'

问题: 查询张三的家庭住址
SQL: SELECT emp_id, emp_name, current_residence, registered_residence, id_address, dept_full_name, emp_status FROM employees_info WHERE emp_name = '张三'

问题: 覃家明的住址是什么
SQL: SELECT emp_id, emp_name, current_residence as 现居住地, registered_residence as 户籍所在地, id_address as 身份证地址, dept_full_name, emp_status FROM employees_info WHERE emp_name = '覃家明'

问题: 查询张三的身份证地址
SQL: SELECT emp_id, emp_name, id_address, dept_full_name, emp_status FROM employees_info WHERE emp_name = '张三'

## 电脑信息相关示例

问题: 有多少台电脑？
SQL: SELECT COUNT(*) as total FROM computer_info

问题: 查询张三使用的电脑
SQL: SELECT * FROM computer_info WHERE emp_name = '张三' OR last_login_user = '张三'

问题: 统计各操作系统数量
SQL: SELECT operating_system, COUNT(*) as count FROM computer_info GROUP BY operating_system ORDER BY count DESC

问题: 查询IP地址为10.2.59.32的电脑信息
SQL: SELECT * FROM computer_info WHERE network_address = '10.2.59.32'

问题: 查询人力资源中心的电脑
SQL: SELECT * FROM computer_info WHERE dept_level2 LIKE '%人力资源%'

问题: 统计各部门电脑数量
SQL: SELECT dept_level2 as department, COUNT(*) as count FROM computer_info GROUP BY dept_level2 ORDER BY count DESC

问题: 查询使用Windows 10的电脑数量
SQL: SELECT COUNT(*) as total FROM computer_info WHERE operating_system LIKE '%Windows 10%'

问题: 查询电脑名称包含9030的电脑
SQL: SELECT * FROM computer_info WHERE computer_name LIKE '%9030%'

问题: 查询某员工(工号100001)使用的电脑
SQL: SELECT * FROM computer_info WHERE employee_id = '100001'

问题: 统计各操作系统的电脑数量并排序
SQL: SELECT operating_system, COUNT(*) as count FROM computer_info GROUP BY operating_system ORDER BY count DESC

问题: 查询没有绑定使用人的电脑
SQL: SELECT * FROM computer_info WHERE emp_name IS NULL OR emp_name = ''

问题: 查询最近登录用户为zhangsan的电脑
SQL: SELECT * FROM computer_info WHERE last_login_user = 'zhangsan'

## 员工与电脑关联查询示例

问题: 查询人力资源中心员工使用的电脑
SQL: SELECT c.* FROM computer_info c INNER JOIN employees_info e ON c.emp_name = e.emp_name WHERE e.dept_full_name LIKE '%人力资源中心%' AND e.emp_status = '在职'

问题: 统计在职员工中有多少人分配了电脑
SQL: SELECT COUNT(DISTINCT c.emp_name) as count FROM computer_info c INNER JOIN employees_info e ON c.emp_name = e.emp_name WHERE e.emp_status = '在职'

问题: 查询张三的员工信息和电脑信息
SQL: SELECT e.emp_id, e.emp_name, e.dept_full_name, c.computer_name, c.network_address, c.operating_system FROM employees_info e LEFT JOIN computer_info c ON e.emp_name = c.emp_name WHERE e.emp_name = '张三' AND e.emp_status = '在职'
</few_shot_examples>
"""

@bp.route('/ai_assistant/chat', methods=['POST'])
@login_required
def chat():
    """简单的聊天API（非流式）"""
    logger.info("=== AI Chat API Called ===")
    try:
        data = request.get_json()
        question = data.get('message', '').strip()
        
        if not question:
            return jsonify({'success': False, 'error': '请输入问题'})
        
        provider = current_app.config.get('AI_PROVIDER', 'ollama')
        
        config = {
            'provider': provider,
            'api_key': current_app.config.get('MINIMAX_API_KEY') if provider == 'minimax' else current_app.config.get('OPENAI_API_KEY') if provider == 'openai' else '',
            'model': current_app.config.get('OLLAMA_MODEL') if provider == 'ollama' else current_app.config.get('OPENAI_MODEL', 'gpt-4o') if provider == 'openai' else current_app.config.get('MINIMAX_MODEL') if provider == 'minimax' else 'llama3',
            'ollama_api_base': current_app.config.get('OLLAMA_API_BASE', 'http://localhost:11434/v1'),
            'openai_api_base': current_app.config.get('OPENAI_API_BASE', 'https://api.openai.com/v1'),
            'minimax_api_key': current_app.config.get('MINIMAX_API_KEY', '')
        }
        
        db_schema = get_database_schema()
        need_query = check_if_needs_database_query_v2(question, db_schema, config)
        
        response_text = ""
        sql_query = None
        query_result = None
        thinking_steps = []
        
        thinking_steps.append({
            'step': '意图识别',
            'status': 'completed',
            'result': '需要查询数据库' if need_query else '普通对话'
        })
        
        if need_query:
            thinking_steps.append({
                'step': '生成SQL',
                'status': 'processing'
            })
            
            sql_query = generate_sql_v2(question, db_schema, config)
            
            if sql_query:
                thinking_steps[-1]['status'] = 'completed'
                thinking_steps[-1]['result'] = sql_query
                
                thinking_steps.append({
                    'step': '执行查询',
                    'status': 'processing'
                })
                
                query_result, sql_error = execute_sql(sql_query)
                
                if sql_error and query_result is None:
                    thinking_steps.append({
                        'step': '修复SQL',
                        'status': 'processing',
                        'detail': f'错误: {sql_error}'
                    })
                    fixed_sql = fix_sql_with_error(sql_query, sql_error, question, db_schema, config)
                    if fixed_sql:
                        sql_query = fixed_sql
                        query_result, sql_error = execute_sql(sql_query)
                        if query_result:
                            thinking_steps[-1]['status'] = 'completed'
                            thinking_steps[-1]['result'] = 'SQL修复成功'
                
                if query_result is not None and len(query_result) == 0:
                    thinking_steps.append({
                        'step': '智能重试',
                        'status': 'processing',
                        'detail': '查询结果为0，尝试更宽松的匹配'
                    })
                    retry_sql = smart_retry_query(question, sql_query, db_schema, config)
                    if retry_sql:
                        sql_query = retry_sql
                        query_result, _ = execute_sql(sql_query)
                        if query_result and len(query_result) > 0:
                            thinking_steps[-1]['status'] = 'completed'
                            thinking_steps[-1]['result'] = f'重试成功，找到{len(query_result)}条记录'
                
                if query_result is not None:
                    thinking_steps[2]['status'] = 'completed'
                    thinking_steps[2]['result'] = f'获取到 {len(query_result)} 条记录'
                    
                    thinking_steps.append({
                        'step': '生成回答',
                        'status': 'completed'
                    })
                    
                    response_text = generate_answer_with_data_v2(question, db_schema, sql_query, query_result, config)
                else:
                    thinking_steps[2]['status'] = 'error'
                    thinking_steps[2]['result'] = '查询执行失败'
                    response_text = f"抱歉，查询数据时出错。请尝试换一种方式提问。"
            else:
                thinking_steps[-1]['status'] = 'error'
                thinking_steps[-1]['result'] = '无法生成SQL'
                response_text = "抱歉，无法理解您的问题并生成查询。请换一种方式提问。"
        else:
            thinking_steps.append({
                'step': '生成回答',
                'status': 'completed'
            })
            response_text = direct_answer_v2(question, config)
        
        return jsonify({
            'success': True,
            'response': response_text,
            'sql': sql_query,
            'data_count': len(query_result) if query_result else 0,
            'thinking_steps': thinking_steps
        })
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})


@bp.route('/api/ai/query/stream', methods=['POST'])
@login_required
def ai_query_stream():
    """流式API - 支持两种模式：query(数据问答) / chat(一般对话)"""
    data = request.get_json()
    question = data.get('question', '').strip()
    mode = data.get('mode', 'query')
    provider = data.get('provider', '') or current_app.config.get('AI_PROVIDER', 'ollama')
    
    config = {
        'provider': provider,
        'api_key': current_app.config.get('MINIMAX_API_KEY') if provider == 'minimax' else current_app.config.get('OPENAI_API_KEY') if provider == 'openai' else '',
        'model': current_app.config.get('OLLAMA_MODEL') if provider == 'ollama' else current_app.config.get('OPENAI_MODEL', 'gpt-4o') if provider == 'openai' else current_app.config.get('MINIMAX_MODEL') if provider == 'minimax' else 'llama3',
        'ollama_api_base': current_app.config.get('OLLAMA_API_BASE', 'http://localhost:11434/v1'),
        'openai_api_base': current_app.config.get('OPENAI_API_BASE', 'https://api.openai.com/v1'),
        'minimax_api_key': current_app.config.get('MINIMAX_API_KEY', '')
    }
    
    app_instance = current_app._get_current_object()
    
    def generate():
        with app_instance.app_context():
            try:
                if not question:
                    yield "data: " + json.dumps({'error': '请输入问题'}, ensure_ascii=False) + "\n\n"
                    return
                
                if mode == 'chat':
                    yield "data: " + json.dumps({'step': {'step': 1, 'action': '\u751f\u6210\u56de\u7b54', 'status': 'processing'}}, ensure_ascii=False) + "\n\n"
                    chat_prompt = [{'role': 'system', 'content': '\u4f60\u662f\u4e00\u4e2a\u53cb\u597d\u7684AI\u52a9\u624b\uff0c\u8bf7\u7528\u4e2d\u6587\u56de\u7b54\u7528\u6237\u7684\u95ee\u9898\u3002'}, {'role': 'user', 'content': question}]
                    full_content = ''
                    for chunk in call_llm_api_stream(config, chat_prompt, timeout=120):
                        if chunk['type'] == 'content':
                            full_content += chunk['content']
                            yield "data: " + json.dumps({'content': chunk['content']}, ensure_ascii=False) + "\n\n"
                    yield "data: " + json.dumps({'step': {'step': 1, 'action': '\u751f\u6210\u56de\u7b54', 'status': 'completed'}}, ensure_ascii=False) + "\n\n"
                    yield "data: " + json.dumps({'done': True}, ensure_ascii=False) + "\n\n"
                    return
                
                db_schema = get_database_schema()
                
                yield "data: " + json.dumps({'step': {'step': 1, 'action': '\u751f\u6210SQL', 'status': 'processing'}}, ensure_ascii=False) + "\n\n"
                sql_query = generate_sql_v2(question, db_schema, config)
                
                if not sql_query:
                    yield "data: " + json.dumps({'step': {'step': 1, 'action': '\u751f\u6210SQL', 'status': 'error', 'result': '\u65e0\u6cd5\u751f\u6210SQL'}}, ensure_ascii=False) + "\n\n"
                    answer = '\u62b1\u6b49\uff0c\u65e0\u6cd5\u7406\u89e3\u60a8\u7684\u67e5\u8be2\u610f\u56fe\u3002\u8bf7\u6362\u4e00\u79cd\u65b9\u5f0f\u63cf\u8ff0\u60a8\u8981\u67e5\u4ec0\u4e48\u6570\u636e\u3002'
                    for char in answer:
                        yield "data: " + json.dumps({'content': char}, ensure_ascii=False) + "\n\n"
                    yield "data: " + json.dumps({'done': True}, ensure_ascii=False) + "\n\n"
                    return
                
                yield "data: " + json.dumps({'step': {'step': 1, 'action': '\u751f\u6210SQL', 'status': 'completed', 'result': sql_query}, 'sql': sql_query}, ensure_ascii=False) + "\n\n"
                
                yield "data: " + json.dumps({'step': {'step': 2, 'action': '\u6267\u884c\u67e5\u8be2', 'status': 'processing'}}, ensure_ascii=False) + "\n\n"
                query_result, sql_error = execute_sql(sql_query)
                
                if sql_error and query_result is None:
                    yield "data: " + json.dumps({'step': {'step': 3, 'action': '\u4fee\u590dSQL', 'status': 'processing', 'detail': str(sql_error)[:50]}}, ensure_ascii=False) + "\n\n"
                    fixed_sql = fix_sql_with_error(sql_query, sql_error, question, db_schema, config)
                    if fixed_sql:
                        sql_query = fixed_sql
                        query_result, sql_error = execute_sql(sql_query)
                        if query_result:
                            yield "data: " + json.dumps({'step': {'step': 3, 'action': '\u4fee\u590dSQL', 'status': 'completed', 'result': '\u4fee\u590d\u6210\u529f'}}, ensure_ascii=False) + "\n\n"
                
                if query_result is not None and len(query_result) == 0:
                    yield "data: " + json.dumps({'step': {'step': 4, 'action': '\u667a\u80fd\u91cd\u8bd5', 'status': 'processing', 'detail': '\u7ed3\u679c\u4e3a0\uff0c\u5c1d\u8bd5\u66f4\u5bbd\u677e\u5339\u914d'}}, ensure_ascii=False) + "\n\n"
                    retry_sql = smart_retry_query(question, sql_query, db_schema, config)
                    if retry_sql:
                        sql_query = retry_sql
                        query_result, _ = execute_sql(sql_query)
                        if query_result and len(query_result) > 0:
                            yield "data: " + json.dumps({'step': {'step': 4, 'action': '\u667a\u80fd\u91cd\u8bd5', 'status': 'completed', 'result': '\u627e\u5230' + str(len(query_result)) + '\u6761\u8bb0\u5f55'}}, ensure_ascii=False) + "\n\n"
                
                if query_result is not None:
                    cnt = len(query_result)
                    yield "data: " + json.dumps({'step': {'step': 2, 'action': '\u6267\u884c\u67e5\u8be2', 'status': 'completed', 'result': '\u83b7\u53d6' + str(cnt) + '\u6761\u8bb0\u5f55'}}, ensure_ascii=False) + "\n\n"
                    
                    yield "data: " + json.dumps({'step': {'step': 5, 'action': '\u751f\u6210\u56de\u7b54', 'status': 'processing'}}, ensure_ascii=False) + "\n\n"
                    messages = generate_answer_messages(question, db_schema, sql_query, query_result)
                    full_content = ''
                    for chunk in call_llm_api_stream(config, messages, timeout=120):
                        if chunk['type'] == 'content':
                            full_content += chunk['content']
                            yield "data: " + json.dumps({'content': chunk['content']}, ensure_ascii=False) + "\n\n"
                    
                    if not full_content:
                        answer = generate_answer_with_data_v2(question, db_schema, sql_query, query_result, config)
                        for char in answer:
                            yield "data: " + json.dumps({'content': char}, ensure_ascii=False) + "\n\n"
                    
                    yield "data: " + json.dumps({'step': {'step': 5, 'action': '\u751f\u6210\u56de\u7b54', 'status': 'completed'}}, ensure_ascii=False) + "\n\n"
                    yield "data: " + json.dumps({'done': True}, ensure_ascii=False) + "\n\n"
                else:
                    error_detail = sql_error[:100] if sql_error else '\u672a\u77e5\u9519\u8bef'
                    yield "data: " + json.dumps({'step': {'step': 2, 'action': '\u6267\u884c\u67e5\u8be2', 'status': 'error', 'result': '\u67e5\u8be2\u5931\u8d25: ' + error_detail}}, ensure_ascii=False) + "\n\n"
                    answer = '\u62b1\u6b49\uff0c\u67e5\u8be2\u6570\u636e\u65f6\u51fa\u9519\u3002\u8bf7\u5c1d\u8bd5\u6362\u4e00\u79cd\u65b9\u5f0f\u63d0\u95ee\u3002'
                    for char in answer:
                        yield "data: " + json.dumps({'content': char}, ensure_ascii=False) + "\n\n"
                    yield "data: " + json.dumps({'done': True}, ensure_ascii=False) + "\n\n"
            
            except Exception as e:
                logger.error(f"Stream error: {str(e)}")
                yield "data: " + json.dumps({'error': str(e)}, ensure_ascii=False) + "\n\n"
    
    return Response(generate(), content_type='text/event-stream; charset=utf-8', headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})



@bp.route('/api/v1/query', methods=['POST'])
@api_key_required
def api_query():
    """
    外部API接口 - 查询数据
    
    请求示例:
    curl -X POST http://localhost:5000/api/v1/query \
         -H "Content-Type: application/json" \
         -H "X-API-Key: asset-ai-api-key-2024" \
         -d '{"question": "袁文杰的电话号码"}'
    
    返回格式:
    {
        "success": true,
        "question": "袁文杰的电话号码",
        "answer": "查询结果如下...",
        "sql": "SELECT ...",
        "data": [...],
        "data_count": 4,
        "thinking_steps": [...]
    }
    """
    logger.info("=== External API Query Called ===")
    
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({
                'success': False,
                'error': '请提供question参数'
            }), 400
        
        provider = current_app.config.get('AI_PROVIDER', 'ollama')
        
        config = {
            'provider': provider,
            'api_key': current_app.config.get('MINIMAX_API_KEY') if provider == 'minimax' else current_app.config.get('OPENAI_API_KEY') if provider == 'openai' else '',
            'model': current_app.config.get('OLLAMA_MODEL') if provider == 'ollama' else current_app.config.get('OPENAI_MODEL', 'gpt-4o') if provider == 'openai' else current_app.config.get('MINIMAX_MODEL') if provider == 'minimax' else 'llama3',
            'ollama_api_base': current_app.config.get('OLLAMA_API_BASE', 'http://localhost:11434/v1'),
            'openai_api_base': current_app.config.get('OPENAI_API_BASE', 'https://api.openai.com/v1'),
            'minimax_api_key': current_app.config.get('MINIMAX_API_KEY', '')
        }
        
        db_schema = get_database_schema()
        need_query = check_if_needs_database_query_v2(question, db_schema, config)
        
        thinking_steps = [{
            'step': '意图识别',
            'status': 'completed',
            'result': '需要查询数据库' if need_query else '普通对话'
        }]
        
        sql_query = None
        query_result = None
        answer = ""
        
        if need_query:
            thinking_steps.append({'step': '生成SQL', 'status': 'processing'})
            sql_query = generate_sql_v2(question, db_schema, config)
            
            if sql_query:
                thinking_steps[-1]['status'] = 'completed'
                thinking_steps[-1]['result'] = sql_query
                
                thinking_steps.append({'step': '执行查询', 'status': 'processing'})
                query_result, sql_error = execute_sql(sql_query)
                
                if sql_error and query_result is None:
                    thinking_steps.append({
                        'step': '修复SQL',
                        'status': 'processing',
                        'detail': f'错误: {sql_error}'
                    })
                    fixed_sql = fix_sql_with_error(sql_query, sql_error, question, db_schema, config)
                    if fixed_sql:
                        sql_query = fixed_sql
                        query_result, sql_error = execute_sql(sql_query)
                        if query_result:
                            thinking_steps[-1]['status'] = 'completed'
                            thinking_steps[-1]['result'] = 'SQL修复成功'
                
                if query_result is not None and len(query_result) == 0:
                    thinking_steps.append({
                        'step': '智能重试',
                        'status': 'processing',
                        'detail': '查询结果为0，尝试更宽松的匹配'
                    })
                    retry_sql = smart_retry_query(question, sql_query, db_schema, config)
                    if retry_sql:
                        sql_query = retry_sql
                        query_result, _ = execute_sql(sql_query)
                        if query_result and len(query_result) > 0:
                            thinking_steps[-1]['status'] = 'completed'
                            thinking_steps[-1]['result'] = f'重试成功，找到{len(query_result)}条记录'
                
                if query_result is not None:
                    thinking_steps[-2]['status'] = 'completed'
                    thinking_steps[-2]['result'] = f'获取到 {len(query_result)} 条记录'
                    
                    thinking_steps.append({'step': '生成回答', 'status': 'completed'})
                    answer = generate_answer_with_data_v2(question, db_schema, sql_query, query_result, config)
                else:
                    thinking_steps[-2]['status'] = 'error'
                    thinking_steps[-2]['result'] = '查询执行失败'
                    answer = f"抱歉，查询数据时出错。请尝试换一种方式提问。"
            else:
                thinking_steps[-1]['status'] = 'error'
                thinking_steps[-1]['result'] = '无法生成SQL'
                answer = "抱歉，无法理解您的问题并生成查询。请换一种方式提问。"
        else:
            thinking_steps.append({'step': '生成回答', 'status': 'completed'})
            answer = direct_answer_v2(question, config)
        
        return jsonify({
            'success': True,
            'question': question,
            'answer': answer,
            'sql': sql_query,
            'data': query_result,
            'data_count': len(query_result) if query_result else 0,
            'thinking_steps': thinking_steps
        })
        
    except Exception as e:
        logger.error(f"API Query error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/api/v1/query/raw', methods=['POST'])
@api_key_required
def api_query_raw():
    """
    外部API接口 - 仅返回原始数据（不生成自然语言回答）
    """
    logger.info("=== External API Query Raw Called ===")
    
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({
                'success': False,
                'error': '请提供question参数'
            }), 400
        
        provider = current_app.config.get('AI_PROVIDER', 'ollama')
        
        config = {
            'provider': provider,
            'api_key': current_app.config.get('MINIMAX_API_KEY') if provider == 'minimax' else current_app.config.get('OPENAI_API_KEY') if provider == 'openai' else '',
            'model': current_app.config.get('OLLAMA_MODEL') if provider == 'ollama' else current_app.config.get('OPENAI_MODEL', 'gpt-4o') if provider == 'openai' else current_app.config.get('MINIMAX_MODEL') if provider == 'minimax' else 'llama3',
            'ollama_api_base': current_app.config.get('OLLAMA_API_BASE', 'http://localhost:11434/v1'),
            'openai_api_base': current_app.config.get('OPENAI_API_BASE', 'https://api.openai.com/v1'),
            'minimax_api_key': current_app.config.get('MINIMAX_API_KEY', '')
        }
        
        db_schema = get_database_schema()
        sql_query = generate_sql_v2(question, db_schema, config)
        
        if not sql_query:
            return jsonify({
                'success': False,
                'error': '无法生成SQL查询语句'
            })
        
        query_result, sql_error = execute_sql(sql_query)
        
        if query_result is None:
            fixed_sql = fix_sql_with_error(sql_query, sql_error, question, db_schema, config)
            if fixed_sql:
                sql_query = fixed_sql
                query_result, _ = execute_sql(sql_query)
        
        if query_result is None:
            return jsonify({
                'success': False,
                'error': f'查询执行失败: {sql_error}'
            })
        
        if len(query_result) == 0:
            retry_sql = smart_retry_query(question, sql_query, db_schema, config)
            if retry_sql:
                sql_query = retry_sql
                query_result, _ = execute_sql(sql_query)
        
        return jsonify({
            'success': True,
            'question': question,
            'sql': sql_query,
            'data': query_result,
            'data_count': len(query_result) if query_result else 0
        })
        
    except Exception as e:
        logger.error(f"API Query Raw error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/api/ai/sessions', methods=['GET'])
@login_required
def get_chat_sessions():
    """获取用户的对话历史列表"""
    sessions = ChatSession.query.filter_by(user_id=current_user.id).order_by(ChatSession.updated_at.desc()).limit(20).all()
    return jsonify([{
        'id': s.id,
        'title': s.title,
        'created_at': s.created_at.strftime('%Y-%m-%d %H:%M'),
        'message_count': s.messages.count()
    } for s in sessions])


@bp.route('/api/ai/sessions', methods=['POST'])
@login_required
def create_chat_session():
    """创建新对话"""
    data = request.get_json() or {}
    session = ChatSession(
        user_id=current_user.id,
        title=data.get('title', '新对话')
    )
    db.session.add(session)
    db.session.commit()
    return jsonify({'success': True, 'id': session.id})


@bp.route('/api/ai/sessions/<int:session_id>/messages', methods=['GET'])
@login_required
def get_chat_messages(session_id):
    """获取对话的消息列表"""
    messages = ChatMessage.query.filter_by(session_id=session_id).order_by(ChatMessage.created_at).all()
    return jsonify([{
        'id': m.id,
        'role': m.role,
        'content': m.content,
        'has_sql': m.has_sql,
        'sql_query': m.sql_query,
        'created_at': m.created_at.strftime('%H:%M')
    } for m in messages])


@bp.route('/api/ai/messages', methods=['POST'])
@login_required
def save_chat_message():
    """保存一条消息"""
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'no data'}), 400
    
    session_id = data.get('session_id')
    role = data.get('role')
    content = data.get('content', '')
    
    # 如果没有session_id，创建新会话
    if not session_id:
        session = ChatSession(user_id=current_user.id)
        db.session.add(session)
        db.session.flush()
        session_id = session.id
    
    message = ChatMessage(
        session_id=session_id,
        role=role,
        content=content,
        has_sql=data.get('has_sql', False),
        sql_query=data.get('sql_query'),
        has_result=data.get('has_result', False),
        result_summary=data.get('result_summary')
    )
    db.session.add(message)
    
    # 更新会话标题（从第一条用户消息提取）
    session = ChatSession.query.get(session_id)
    if session and session.title == '新对话' and role == 'user' and len(content) > 2:
        session.title = content[:30] + ('...' if len(content) > 30 else '')
    if session:
        session.updated_at = datetime.utcnow()
    
    db.session.commit()
    return jsonify({'success': True, 'session_id': session_id, 'message_id': message.id})


@bp.route('/api/ai/messages/batch', methods=['POST'])
@login_required
def save_chat_messages_batch():
    """批量保存消息（用于页面关闭前保存所有消息）"""
    data = request.get_json()
    if not data or 'messages' not in data:
        return jsonify({'success': False, 'error': 'no messages'}), 400
    
    session_id = data.get('session_id')
    messages = data['messages']
    
    # 创建或获取会话
    if not session_id:
        session = ChatSession(user_id=current_user.id)
        title = ''
        for msg in messages:
            if msg.get('role') == 'user' and len(msg.get('content', '')) > 2:
                title = msg['content'][:30]
                break
        session.title = title or '新对话'
        db.session.add(session)
        db.session.flush()
        session_id = session.id
        session.updated_at = datetime.utcnow()
    else:
        session = ChatSession.query.get(session_id)
        if session:
            if session.title == '新对话':
                for msg in messages:
                    if msg.get('role') == 'user' and len(msg.get('content', '')) > 2:
                        session.title = msg['content'][:30]
                        break
            session.updated_at = datetime.utcnow()
    
    # 只保存还没有保存的消息（通过内容+角色去重）
    existing = set()
    if session_id:
        for m in ChatMessage.query.filter_by(session_id=session_id).all():
            existing.add((m.role, m.content[:100]))
    
    for msg in messages:
        key = (msg.get('role', ''), msg.get('content', '')[:100])
        if key not in existing:
            chat_msg = ChatMessage(
                session_id=session_id,
                role=msg.get('role', ''),
                content=msg.get('content', ''),
                has_sql=msg.get('has_sql', False),
                sql_query=msg.get('sql_query'),
            )
            db.session.add(chat_msg)
            existing.add(key)
    
    db.session.commit()
    return jsonify({'success': True, 'session_id': session_id})