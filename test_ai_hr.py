# -*- coding: utf-8 -*-
"""测试AI问数模块 - 人力资源中心人员结构分析"""
import sys
import os

# 设置控制台编码
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, '.')
os.environ['PYTHONIOENCODING'] = 'utf-8'

from app import app

with app.app_context():
    from app.routes.ai_assistant import (
        get_database_schema, 
        generate_sql_v2, 
        execute_sql, 
        call_llm_api_v2,
        generate_answer_with_data_v2
    )
    
    config = {
        'provider': 'ollama',
        'api_key': '',
        'model': 'qwen3.5:9B',
        'ollama_api_base': 'http://localhost:11434/v1',
        'openai_api_base': '',
        'minimax_api_key': ''
    }
    
    question = '帮我分析一下人力资源中心人员结构'
    db_schema = get_database_schema()
    
    print('=' * 60)
    print(f'问题: {question}')
    print('=' * 60)
    
    # 步骤1: 生成SQL
    print('\n[步骤1] 正在生成SQL...')
    try:
        sql = generate_sql_v2(question, db_schema, config)
        print(f'生成的SQL:\n{sql}')
    except Exception as e:
        print(f'生成SQL失败: {e}')
        sql = None
    
    if sql:
        # 步骤2: 执行SQL
        print('\n[步骤2] 正在执行SQL...')
        try:
            result, error = execute_sql(sql)
            if error:
                print(f'SQL执行错误: {error}')
            else:
                print(f'查询成功，返回 {len(result)} 条记录')
                if result:
                    print(f'前5条数据: {result[:5]}')
        except Exception as e:
            print(f'执行SQL异常: {e}')
            result = None
        
        # 步骤3: 生成回答
        if result:
            print('\n[步骤3] 正在生成回答...')
            try:
                answer = generate_answer_with_data_v2(question, db_schema, sql, result, config)
                print(f'回答:\n{answer}')
            except Exception as e:
                print(f'生成回答失败: {e}')
    
    print('\n' + '=' * 60)
    print('测试完成')