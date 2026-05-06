"""测试AI数据问答功能"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from app.routes.ai_assistant import generate_sql_v2, execute_sql, get_database_schema, check_if_needs_database_query_v2, smart_retry_query
import requests

# 测试配置 - 请根据你的配置修改
TEST_CONFIG = {
    'provider': 'ollama',
    'api_key': '',
    'model': 'qwen3.5:9B',
    'ollama_api_base': 'http://localhost:11434/v1',
    'openai_api_base': 'https://api.openai.com/v1',
    'minimax_api_key': ''
}

def test_query(question):
    """测试查询"""
    print(f"\n{'='*60}")
    print(f"测试问题: {question}")
    print('='*60)
    
    with app.app_context():
        # 1. 获取数据库Schema
        db_schema = get_database_schema()
        print(f"\n[1] 数据库Schema长度: {len(db_schema)} 字符")
        
        # 2. 检查是否需要查询数据库
        need_query = check_if_needs_database_query_v2(question, db_schema, TEST_CONFIG)
        print(f"\n[2] 是否需要查询数据库: {need_query}")
        
        if not need_query:
            print("  -> 问题不需要查询数据库")
            return
        
        # 3. 生成SQL
        print(f"\n[3] 正在生成SQL...")
        sql = generate_sql_v2(question, db_schema, TEST_CONFIG)
        
        if sql:
            print(f"  生成的SQL: {sql}")
            
            # 4. 执行SQL
            print(f"\n[4] 正在执行SQL...")
            result, error = execute_sql(sql)
            
            if result is not None:
                print(f"  查询成功! 返回 {len(result)} 条记录")
                if result:
                    print(f"  第一条数据: {result[0]}")
                    if len(result) > 1:
                        print(f"  最后一条数据: {result[-1]}")
                else:
                    # 结果为0，尝试智能重试
                    print(f"  结果为0条，尝试智能重试...")
                    retry_sql = smart_retry_query(question, sql, db_schema, TEST_CONFIG)
                    if retry_sql:
                        print(f"  重试SQL: {retry_sql}")
                        result, error = execute_sql(retry_sql)
                        if result and len(result) > 0:
                            print(f"  重试成功! 返回 {len(result)} 条记录")
                            print(f"  第一条数据: {result[0]}")
            else:
                print(f"  查询失败: {error}")
        else:
            print("  无法生成SQL")

def test_direct_sql():
    """直接测试SQL是否正确"""
    print("\n" + "="*60)
    print("直接测试SQL执行")
    print("="*60)
    
    with app.app_context():
        # 测试正确的SQL
        test_sql = "SELECT COUNT(*) as total FROM employees_info WHERE emp_status = '在职'"
        print(f"\n测试SQL: {test_sql}")
        result, error = execute_sql(test_sql)
        if result:
            print(f"成功! 结果: {result}")
        else:
            print(f"失败: {error}")
        
        # 查看employees_info表的数据
        print("\n查看employees_info表前3条数据:")
        result, _ = execute_sql("SELECT emp_id, emp_name, emp_status, dept_full_name FROM employees_info LIMIT 3")
        if result:
            for row in result:
                print(f"  {row}")
        
        # 查看emp_status的可能值
        print("\n查看emp_status的所有可能值:")
        result, _ = execute_sql("SELECT DISTINCT emp_status, COUNT(*) as cnt FROM employees_info GROUP BY emp_status")
        if result:
            for row in result:
                print(f"  {row}")

if __name__ == '__main__':
    # 测试问答
    test_query("刘航是谁")
