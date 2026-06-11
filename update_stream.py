import re

path = r'd:\资产管理\app\routes\ai_assistant.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

old_start = "@bp.route('/api/ai/query/stream', methods=['POST'])"
idx = c.find(old_start)
if idx < 0:
    print("Not found")
    exit(1)

next_route = c.find('\n@bp.route', idx + 10)
if next_route < 0:
    next_route = len(c)
old_endpoint = c[idx:next_route]
print(f"Old endpoint length: {len(old_endpoint)}")

new_endpoint = """@bp.route('/api/ai/query/stream', methods=['POST'])
@login_required
def ai_query_stream():
    \"\"\"流式API - 支持两种模式：query(数据问答) / chat(一般对话)\"\"\"
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
                    yield "data: " + json.dumps({'error': '请输入问题'}, ensure_ascii=False) + "\\n\\n"
                    return
                
                if mode == 'chat':
                    yield "data: " + json.dumps({'step': {'step': 1, 'action': '\\u751f\\u6210\\u56de\\u7b54', 'status': 'processing'}}, ensure_ascii=False) + "\\n\\n"
                    chat_prompt = [{'role': 'system', 'content': '\\u4f60\\u662f\\u4e00\\u4e2a\\u53cb\\u597d\\u7684AI\\u52a9\\u624b\\uff0c\\u8bf7\\u7528\\u4e2d\\u6587\\u56de\\u7b54\\u7528\\u6237\\u7684\\u95ee\\u9898\\u3002'}, {'role': 'user', 'content': question}]
                    full_content = ''
                    for chunk in call_llm_api_stream(config, chat_prompt, timeout=120):
                        if chunk['type'] == 'content':
                            full_content += chunk['content']
                            yield "data: " + json.dumps({'content': chunk['content']}, ensure_ascii=False) + "\\n\\n"
                    yield "data: " + json.dumps({'step': {'step': 1, 'action': '\\u751f\\u6210\\u56de\\u7b54', 'status': 'completed'}}, ensure_ascii=False) + "\\n\\n"
                    yield "data: " + json.dumps({'done': True}, ensure_ascii=False) + "\\n\\n"
                    return
                
                db_schema = get_database_schema()
                
                yield "data: " + json.dumps({'step': {'step': 1, 'action': '\\u751f\\u6210SQL', 'status': 'processing'}}, ensure_ascii=False) + "\\n\\n"
                sql_query = generate_sql_v2(question, db_schema, config)
                
                if not sql_query:
                    yield "data: " + json.dumps({'step': {'step': 1, 'action': '\\u751f\\u6210SQL', 'status': 'error', 'result': '\\u65e0\\u6cd5\\u751f\\u6210SQL'}}, ensure_ascii=False) + "\\n\\n"
                    answer = '\\u62b1\\u6b49\\uff0c\\u65e0\\u6cd5\\u7406\\u89e3\\u60a8\\u7684\\u67e5\\u8be2\\u610f\\u56fe\\u3002\\u8bf7\\u6362\\u4e00\\u79cd\\u65b9\\u5f0f\\u63cf\\u8ff0\\u60a8\\u8981\\u67e5\\u4ec0\\u4e48\\u6570\\u636e\\u3002'
                    for char in answer:
                        yield "data: " + json.dumps({'content': char}, ensure_ascii=False) + "\\n\\n"
                    yield "data: " + json.dumps({'done': True}, ensure_ascii=False) + "\\n\\n"
                    return
                
                yield "data: " + json.dumps({'step': {'step': 1, 'action': '\\u751f\\u6210SQL', 'status': 'completed', 'result': sql_query}, 'sql': sql_query}, ensure_ascii=False) + "\\n\\n"
                
                yield "data: " + json.dumps({'step': {'step': 2, 'action': '\\u6267\\u884c\\u67e5\\u8be2', 'status': 'processing'}}, ensure_ascii=False) + "\\n\\n"
                query_result, sql_error = execute_sql(sql_query)
                
                if sql_error and query_result is None:
                    yield "data: " + json.dumps({'step': {'step': 3, 'action': '\\u4fee\\u590dSQL', 'status': 'processing', 'detail': str(sql_error)[:50]}}, ensure_ascii=False) + "\\n\\n"
                    fixed_sql = fix_sql_with_error(sql_query, sql_error, question, db_schema, config)
                    if fixed_sql:
                        sql_query = fixed_sql
                        query_result, sql_error = execute_sql(sql_query)
                        if query_result:
                            yield "data: " + json.dumps({'step': {'step': 3, 'action': '\\u4fee\\u590dSQL', 'status': 'completed', 'result': '\\u4fee\\u590d\\u6210\\u529f'}}, ensure_ascii=False) + "\\n\\n"
                
                if query_result is not None and len(query_result) == 0:
                    yield "data: " + json.dumps({'step': {'step': 4, 'action': '\\u667a\\u80fd\\u91cd\\u8bd5', 'status': 'processing', 'detail': '\\u7ed3\\u679c\\u4e3a0\\uff0c\\u5c1d\\u8bd5\\u66f4\\u5bbd\\u677e\\u5339\\u914d'}}, ensure_ascii=False) + "\\n\\n"
                    retry_sql = smart_retry_query(question, sql_query, db_schema, config)
                    if retry_sql:
                        sql_query = retry_sql
                        query_result, _ = execute_sql(sql_query)
                        if query_result and len(query_result) > 0:
                            yield "data: " + json.dumps({'step': {'step': 4, 'action': '\\u667a\\u80fd\\u91cd\\u8bd5', 'status': 'completed', 'result': '\\u627e\\u5230' + str(len(query_result)) + '\\u6761\\u8bb0\\u5f55'}}, ensure_ascii=False) + "\\n\\n"
                
                if query_result is not None:
                    cnt = len(query_result)
                    yield "data: " + json.dumps({'step': {'step': 2, 'action': '\\u6267\\u884c\\u67e5\\u8be2', 'status': 'completed', 'result': '\\u83b7\\u53d6' + str(cnt) + '\\u6761\\u8bb0\\u5f55'}}, ensure_ascii=False) + "\\n\\n"
                    
                    yield "data: " + json.dumps({'step': {'step': 5, 'action': '\\u751f\\u6210\\u56de\\u7b54', 'status': 'processing'}}, ensure_ascii=False) + "\\n\\n"
                    messages = generate_answer_messages(question, db_schema, sql_query, query_result)
                    full_content = ''
                    for chunk in call_llm_api_stream(config, messages, timeout=120):
                        if chunk['type'] == 'content':
                            full_content += chunk['content']
                            yield "data: " + json.dumps({'content': chunk['content']}, ensure_ascii=False) + "\\n\\n"
                    
                    if not full_content:
                        answer = generate_answer_with_data_v2(question, db_schema, sql_query, query_result, config)
                        for char in answer:
                            yield "data: " + json.dumps({'content': char}, ensure_ascii=False) + "\\n\\n"
                    
                    yield "data: " + json.dumps({'step': {'step': 5, 'action': '\\u751f\\u6210\\u56de\\u7b54', 'status': 'completed'}}, ensure_ascii=False) + "\\n\\n"
                    yield "data: " + json.dumps({'done': True}, ensure_ascii=False) + "\\n\\n"
                else:
                    error_detail = sql_error[:100] if sql_error else '\\u672a\\u77e5\\u9519\\u8bef'
                    yield "data: " + json.dumps({'step': {'step': 2, 'action': '\\u6267\\u884c\\u67e5\\u8be2', 'status': 'error', 'result': '\\u67e5\\u8be2\\u5931\\u8d25: ' + error_detail}}, ensure_ascii=False) + "\\n\\n"
                    answer = '\\u62b1\\u6b49\\uff0c\\u67e5\\u8be2\\u6570\\u636e\\u65f6\\u51fa\\u9519\\u3002\\u8bf7\\u5c1d\\u8bd5\\u6362\\u4e00\\u79cd\\u65b9\\u5f0f\\u63d0\\u95ee\\u3002'
                    for char in answer:
                        yield "data: " + json.dumps({'content': char}, ensure_ascii=False) + "\\n\\n"
                    yield "data: " + json.dumps({'done': True}, ensure_ascii=False) + "\\n\\n"
            
            except Exception as e:
                logger.error(f"Stream error: {str(e)}")
                yield "data: " + json.dumps({'error': str(e)}, ensure_ascii=False) + "\\n\\n"
    
    return Response(generate(), content_type='text/event-stream; charset=utf-8', headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})


"""

c = c[:idx] + new_endpoint + c[idx + len(old_endpoint):]

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print("done")
