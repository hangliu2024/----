"""调试AI查询问题"""
from app import app, db
from sqlalchemy import text
import requests
import json
import os

# 读取AI配置
def get_ai_config():
    config = {}
    env_file = os.path.join(os.path.dirname(__file__), 'app', '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    parts = line.split('=', 1)
                    if len(parts) == 2:
                        config[parts[0].strip()] = parts[1].strip()
    return config

# 测试数据库中是否存在正确的数据
print("=== 测试数据库 ===")
with app.app_context():
    # 测试查询
    result = db.session.execute(text("""
        SELECT COUNT(*) as cnt 
        FROM employees_info 
        WHERE emp_status = '在职' 
        AND dept_full_name LIKE '%人力资源%' 
        AND dept_full_name LIKE '%保卫部%'
    """))
    for row in result:
        print(f"人力资源中心保卫部人数: {row[0]}")
    
    # 查看实际的部门名称
    result2 = db.session.execute(text("""
        SELECT DISTINCT dept_full_name 
        FROM employees_info 
        WHERE emp_status = '在职' 
        AND dept_full_name LIKE '%人力资源%' 
        AND dept_full_name LIKE '%保卫%'
    """))
    print("\n匹配的部门:")
    for row in result2:
        print(f"  - {row[0]}")

# 测试AI配置
print("\n=== AI配置 ===")
ai_config = get_ai_config()
print(f"Provider: {ai_config.get('AI_PROVIDER', 'ollama')}")
print(f"Model: {ai_config.get('OLLAMA_MODEL', 'not set')}")
print(f"API Base: {ai_config.get('OLLAMA_API_BASE', 'not set')}")

# 测试Ollama连接
print("\n=== 测试Ollama连接 ===")
try:
    response = requests.get(f"{ai_config.get('OLLAMA_API_BASE', 'http://localhost:11434/v1').rstrip('/v1')}/api/tags", timeout=5)
    if response.status_code == 200:
        models = response.json().get('models', [])
        print(f"可用模型: {[m['name'] for m in models]}")
    else:
        print(f"Ollama返回状态码: {response.status_code}")
except Exception as e:
    print(f"Ollama连接失败: {e}")

# 测试生成SQL
print("\n=== 测试SQL生成 ===")
question = "人力资源保卫部有几个人"
provider = ai_config.get('AI_PROVIDER', 'ollama')
model = ai_config.get('OLLAMA_MODEL', 'llama3')
api_base = ai_config.get('OLLAMA_API_BASE', 'http://localhost:11434/v1')

prompt = f"""你是一个SQL专家。根据问题生成MySQL查询语句。

表: employees_info
重要字段:
- emp_status: 员工状态 ('在职' 或 '离职')
- dept_full_name: 部门全称 (如 '集团总部/人力资源中心/保卫部')

规则:
1. 员工状态必须是 '在职'
2. 部门名称用 LIKE 模糊匹配
3. 当用户说"人力资源保卫部"时，拆分成: LIKE '%人力资源%' AND LIKE '%保卫部%'

问题: {question}

只返回SQL语句，用```sql包裹。"""

try:
    response = requests.post(
        f"{api_base.rstrip('/')}/chat/completions",
        json={"model": model, "messages": [{"role": "user", "content": prompt}], "stream": False},
        timeout=60
    )
    if response.status_code == 200:
        content = response.json()['choices'][0]['message']['content']
        print(f"AI生成的回答:\n{content}")
        
        # 提取SQL
        import re
        sql_match = re.search(r'```sql\s*(.*?)\s*```', content, re.DOTALL | re.IGNORECASE)
        if sql_match:
            sql = sql_match.group(1).strip()
            print(f"\n提取的SQL: {sql}")
            
            # 执行SQL
            print("\n=== 执行SQL ===")
            with app.app_context():
                result = db.session.execute(text(sql))
                rows = [dict(zip(result.keys(), row)) for row in result.fetchmany(100)]
                print(f"查询结果: {len(rows)} 条记录")
                if rows:
                    print(f"数据: {rows}")
    else:
        print(f"AI请求失败: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"AI请求出错: {e}")