"""直接测试AI问答功能 - 绕过登录直接测试核心逻辑"""
import sys
import os
sys.path.insert(0, '.')

# 设置环境
os.environ.setdefault('FLASK_APP', 'run.py')

from app import app, db
import requests
import logging

logging.basicConfig(level=logging.INFO)

def test_ai_query():
    with app.app_context():
        question = "080217的电脑名是啥"
        
        # 获取配置
        config = {
            'provider': app.config.get('AI_PROVIDER', 'ollama'),
            'api_key': '',
            'model': app.config.get('OLLAMA_MODEL', 'llama3'),
            'ollama_api_base': app.config.get('OLLAMA_API_BASE', 'http://localhost:11434/v1'),
            'openai_api_base': 'https://api.openai.com/v1',
            'minimax_api_key': ''
        }
        
        print(f'=== AI问答测试 ===')
        print(f'问题: {question}')
        print(f'LLM提供商: {config["provider"]}')
        print(f'模型: {config["model"]}')
        print()
        
        # 检查Ollama是否可用
        try:
            resp = requests.get(f'{config["ollama_api_base"].rstrip("/v1")}/api/tags', timeout=5)
            if resp.status_code == 200:
                models = resp.json().get('models', [])
                print(f'可用的Ollama模型: {[m["name"] for m in models]}')
            else:
                print('Ollama服务可能未启动')
        except Exception as e:
            print(f'无法连接到Ollama: {e}')
            return
        
        print()
        
        # 导入AI助手函数
        from app.routes.ai_assistant import (
            check_if_needs_database_query_v2,
            generate_sql_v2,
            execute_sql,
            generate_answer_with_data_v2,
            get_database_schema
        )
        
        # 获取数据库Schema
        db_schema = get_database_schema()
        
        # 步骤1: 意图识别
        print('步骤1: 意图识别...')
        need_query = check_if_needs_database_query_v2(question, db_schema, config)
        print(f'  结果: {"需要查询数据库" if need_query else "普通对话"}')
        
        if need_query:
            # 步骤2: 生成SQL
            print('\n步骤2: 生成SQL...')
            sql = generate_sql_v2(question, db_schema, config)
            print(f'  SQL: {sql}')
            
            if sql:
                # 步骤3: 执行查询
                print('\n步骤3: 执行查询...')
                result, error = execute_sql(sql)
                
                if result:
                    print(f'  获取到 {len(result)} 条记录')
                    if result:
                        print(f'  数据: {result[:3]}')
                    
                    # 步骤4: 生成回答
                    print('\n步骤4: 生成回答...')
                    answer = generate_answer_with_data_v2(question, db_schema, sql, result, config)
                    print(f'\n=== 最终回答 ===')
                    print(answer)
                else:
                    print(f'  查询出错: {error}')
            else:
                print('  无法生成SQL')
        else:
            print('\n这是普通对话，不需要查询数据库')

if __name__ == '__main__':
    test_ai_query()