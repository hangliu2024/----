import requests, re, time, json

base = 'http://10.5.192.253:5001'
s = requests.Session()

print("=" * 60)
print("测试AI问答功能")
print("=" * 60)

# Step 1: Login
print("\n1. 登录...")
r = s.get(f'{base}/login')
token = None
m = re.search(r'<input[^>]*id="csrf_token"[^>]*value="([^"]+)"', r.text)
if m:
    token = m.group(1)

r = s.post(f'{base}/login', data={
    'csrf_token': token,
    'email': 'admin@example.com',
    'password': 'Admin123!',
}, allow_redirects=True)

if 'dashboard' in r.url:
    print("   ✅ 登录成功!")
else:
    print("   ❌ 登录失败!")
    exit(1)

# Step 2: Test AI chat API
print("\n2. 测试AI问答: 帮我列出行政中心厂务工程部所有经理")
question = "帮我列出行政中心厂务工程部所有经理"

start_time = time.time()
try:
    r = s.post(f'{base}/ai_assistant/chat', 
        json={'message': question},
        headers={'Content-Type': 'application/json'},
        timeout=300)
    elapsed = time.time() - start_time
    print(f"   状态码: {r.status_code}, 耗时: {elapsed:.1f}秒")
    
    if r.status_code == 200:
        result = r.json()
        print(f"   success: {result.get('success')}")
        print(f"   SQL: {result.get('sql', 'N/A')}")
        print(f"   数据条数: {result.get('data_count', 0)}")
        
        # Print thinking steps
        steps = result.get('thinking_steps', [])
        print(f"\n   思考步骤:")
        for step in steps:
            status_icon = '✅' if step.get('status') == 'completed' else '❌' if step.get('status') == 'error' else '⏳'
            result_text = step.get('result', '')
            if result_text and len(str(result_text)) > 100:
                result_text = str(result_text)[:100] + '...'
            print(f"     {status_icon} {step.get('step', '?')}: {result_text}")
        
        # Print answer
        response_text = result.get('response', '')
        if response_text:
            print(f"\n   AI回答:")
            print("   " + "-" * 50)
            for line in response_text.split('\n'):
                print(f"   {line}")
            print("   " + "-" * 50)
        else:
            print(f"\n   ❌ 无回答内容")
            print(f"   error: {result.get('error', 'N/A')}")
    else:
        print(f"   ❌ 请求失败: {r.status_code}")
        print(f"   响应: {r.text[:500]}")
except requests.exceptions.Timeout:
    print(f"   ❌ 请求超时 (超过300秒)")
except Exception as e:
    print(f"   ❌ 请求异常: {e}")

print("\n" + "=" * 60)
print("测试完成!")
print("=" * 60)