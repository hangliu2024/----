import requests, re, time

base = 'http://10.5.192.253:5001'
s = requests.Session()

print("=" * 60)
print("测试登录 10.5.192.253:5001")
print("=" * 60)

# Wait for server to be ready
print("\n等待服务启动...")
for i in range(10):
    try:
        r = requests.get(f'{base}/login', timeout=5)
        if r.status_code == 200:
            print(f"   服务已就绪! (尝试{i+1}次)")
            break
    except:
        time.sleep(2)
        print(f"   等待中... (尝试{i+1}次)")
else:
    print("   ❌ 服务无法访问!")
    exit(1)

# Step 1: Get login page
print("\n1. 获取登录页面...")
r = s.get(f'{base}/login')
print(f"   状态码: {r.status_code}")

# Check cookie Secure flag
for cookie in s.cookies:
    print(f"   Cookie: {cookie.name} Secure={cookie.secure}")

# Extract CSRF token
token = None
m = re.search(r'<input[^>]*id="csrf_token"[^>]*value="([^"]+)"', r.text)
if m:
    token = m.group(1)
    print(f"   CSRF令牌: {token[:40]}...")

if not token:
    m = re.search(r'<meta\s+name="csrf-token"\s+content="([^"]+)"', r.text)
    if m:
        token = m.group(1)
        print(f"   CSRF令牌(meta): {token[:40]}...")

if not token:
    print("   ❌ 未找到CSRF令牌!")
    exit(1)

# Step 2: Login
print("\n2. 登录测试 (admin@example.com / Admin123!)...")
r = s.post(f'{base}/login', data={
    'csrf_token': token,
    'email': 'admin@example.com',
    'password': 'Admin123!',
}, allow_redirects=True)

print(f"   状态码: {r.status_code}")
print(f"   最终URL: {r.url}")
if r.history:
    print(f"   重定向链: {' -> '.join([str(h.status_code) for h in r.history])}")

if 'dashboard' in r.url:
    print("   ✅ 登录成功!")
elif 'login' in r.url:
    print("   ❌ 登录失败!")
    # Check for flash messages
    if '会话已过期' in r.text:
        print("   原因: CSRF验证失败 (会话已过期)")
    if '登录失败' in r.text:
        print("   原因: 邮箱或密码错误")
    if '锁定' in r.text:
        print("   原因: IP被锁定")
    if '禁用' in r.text:
        print("   原因: 账号被禁用")
else:
    print(f"   ⚠️ 未知状态: {r.url}")

# Step 3: Test dashboard
print("\n3. 测试仪表板访问...")
r = s.get(f'{base}/dashboard', allow_redirects=False)
print(f"   状态码: {r.status_code}")
if r.status_code == 200:
    if '仪表板' in r.text or 'dashboard' in r.text.lower():
        print("   ✅ 仪表板正常!")
    else:
        print("   ⚠️ 仪表板内容异常")
elif r.status_code == 302:
    print(f"   ❌ 被重定向 (未认证)")
else:
    print(f"   ❌ 状态码: {r.status_code}")

# Step 4: Test key pages
print("\n4. 测试其他页面...")
test_pages = [
    ('/office_computers', '办公电脑'),
    ('/industrial_computers', '工控机'),
    ('/personnel', '人员列表'),
    ('/admin/users', '用户管理'),
    ('/security', '保密管理'),
    ('/case/', '案件管理'),
    ('/case/collections', '案例集'),
    ('/case/sop', '调查SOP'),
    ('/case/reports', '调查报告'),
    ('/emergency/', '应急管理'),
    ('/emergency/plans', '应急预案'),
    ('/emergency/drills', '应急演练'),
    ('/emergency/teams', '应急小组'),
]
for path, name in test_pages:
    try:
        r = s.get(f'{base}{path}', allow_redirects=True, timeout=5)
        final_url = r.url
        if r.status_code == 200:
            if 'login' in final_url and path not in final_url:
                print(f"   ❌ {name} ({path}) - 被重定向到登录页")
            else:
                print(f"   ✅ {name} ({path})")
        else:
            print(f"   ❌ {name} ({path}) - 状态码:{r.status_code} URL:{final_url}")
    except Exception as e:
        print(f"   ❌ {name} - 错误: {e}")

# Step 5: Logout
print("\n5. 测试登出...")
r = s.get(f'{base}/logout', allow_redirects=True)
print(f"   状态码: {r.status_code}, URL: {r.url}")
if 'login' in r.url:
    print("   ✅ 登出成功!")
else:
    print("   ⚠️ 登出异常")

print("\n" + "=" * 60)
print("测试完成!")
print("=" * 60)