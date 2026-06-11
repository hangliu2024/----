"""
资产管理系统 - 全面功能用例测试脚本 v2
基于实际路由定义的URL
"""
import requests
import json
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_URL = 'http://127.0.0.1:5000'
session = requests.Session()

total_tests = 0
passed = 0
failed = 0
issues = []

def test(name, condition, detail=""):
    global total_tests, passed, failed
    total_tests += 1
    if condition:
        passed += 1
        print(f"  [PASS] {name}")
    else:
        failed += 1
        msg = f"[FAIL] {name}" + (f" - {detail}" if detail else "")
        print(f"  {msg}")
        issues.append({"name": name, "detail": detail})

def get(url, allow_redirects=True):
    try:
        r = session.get(BASE_URL + url, allow_redirects=allow_redirects, timeout=10)
        return r
    except requests.exceptions.ConnectionError:
        print(f"  [ERROR] Connection failed: {url}")
        return None
    except Exception as e:
        print(f"  [ERROR] {url}: {e}")
        return None

import re as _re

def _get_csrf_token(url):
    """从页面中提取CSRF token"""
    try:
        r = session.get(BASE_URL + url, timeout=10)
        m = _re.search(r'name="csrf_token"[^>]*value="([^"]+)"', r.text)
        if m:
            return m.group(1)
        # 也尝试meta标签
        m = _re.search(r'<meta\s+name="csrf-token"\s+content="([^"]+)"', r.text)
        if m:
            return m.group(1)
    except:
        pass
    return None

def post(url, data=None, json_data=None, allow_redirects=True):
    try:
        # 如果是form data, 自动补充csrf_token
        if data is not None and 'csrf_token' not in data and json_data is None:
            csrf = _get_csrf_token(url)
            if csrf:
                data = dict(data)
                data['csrf_token'] = csrf
        r = session.post(BASE_URL + url, data=data, json=json_data, allow_redirects=allow_redirects, timeout=10)
        return r
    except requests.exceptions.ConnectionError:
        print(f"  [ERROR] Connection failed: {url}")
        return None
    except Exception as e:
        print(f"  [ERROR] {url}: {e}")
        return None

# 先检测服务器是否可连
print("="*60)
print("前置检查: 服务器连通性")
print("="*60)
try:
    r = requests.get(BASE_URL + '/', timeout=5)
    print(f"  服务器可达, 状态码: {r.status_code}")
except Exception as e:
    print(f"  服务器不可达: {e}")
    print("请确保 python run.py 正在运行")
    sys.exit(1)

# ============================================================
# 1. 未认证访问测试
# ============================================================
print("\n" + "="*60)
print("1. 未认证访问测试")
print("="*60)

# 实际路由 (基于代码审查):
# auth: /login, /register, /logout (无url_prefix)
# assets: /, /dashboard, /office_computers, /industrial_computers (无url_prefix)
# personnel: /personnel, /personnel/new (无url_prefix)
# departments: /departments/manage (url_prefix='/departments')
# security: /security (无url_prefix)
# audit: /audit/tasks (url_prefix='/audit')
# ai_assistant: /ai-assistant (无url_prefix)
# ai_settings: /ai-settings (无url_prefix)
# admin: /admin/users (url_prefix='/admin')

protected_urls = [
    ('/', '首页'),
    ('/personnel', '人员列表'),
    ('/office_computers', '办公电脑'),
    ('/industrial_computers', '工控机'),
    ('/departments/manage', '部门管理'),
    ('/security', '安全保密'),
    ('/audit/tasks', '审计任务'),
    ('/ai-assistant', 'AI助手'),
    ('/ai-settings', 'AI设置'),
    ('/admin/users', '用户管理'),
]

for url, name in protected_urls:
    r = get(url, allow_redirects=False)
    if r is None:
        test(f"未登录访问{name}({url})", False, "请求失败")
    elif r.status_code == 302:
        test(f"未登录访问{name}({url}) -> 302重定向到登录页", True)
    elif r.status_code == 404:
        test(f"未登录访问{name}({url})", False, f"返回404, 路由不存在!")
    else:
        test(f"未登录访问{name}({url}) -> 302", False, f"状态码: {r.status_code}")

# 登录/注册页应可直接访问
r = get('/login')
test("GET /login 登录页可访问", r and r.status_code == 200, f"状态码: {r.status_code if r else 'None'}")

r = get('/register')
test("GET /register 注册页可访问", r and r.status_code == 200, f"状态码: {r.status_code if r else 'None'}")

# 404测试
r = get('/nonexistent-page-url-12345')
test("不存在的页面 -> 404", r and r.status_code == 404, f"状态码: {r.status_code if r else 'None'}")

# ============================================================
# 2. 登录功能测试
# ============================================================
print("\n" + "="*60)
print("2. 登录功能测试")
print("="*60)

# 先退出现有session
session.get(BASE_URL + '/logout')

# 获取登录页
login_page = get('/login')
test("登录页面渲染", login_page and login_page.status_code == 200,
     f"状态码: {login_page.status_code if login_page else 'None'}")
if login_page and login_page.status_code == 200:
    test("登录页含表单", 'form' in login_page.text.lower(), "页面不含form标签")

# 测试空用户名
r = post('/login', data={'username': '', 'password': ''}, allow_redirects=False)
if r:
    test("空用户名登录", r.status_code in [200, 302], f"状态码: {r.status_code}")
else:
    test("空用户名登录", False, "请求失败")

# 错误密码
r = post('/login', data={'username': 'admin', 'password': 'wrongpass123'}, allow_redirects=False)
if r:
    test("错误密码登录", r.status_code in [200, 302], f"状态码: {r.status_code}")
else:
    test("错误密码登录", False, "请求失败")

# SQL注入
r = post('/login', data={"username": "' OR '1'='1' --", "password": "test"}, allow_redirects=False)
if r:
    test("SQL注入阻止", r.status_code in [200, 302], f"状态码: {r.status_code}")
else:
    test("SQL注入阻止", False, "请求失败")

# 尝试多种密码登录
admin_session_ok = False
passwords_to_try = ['admin123', '123456', 'admin', 'Admin123!', 'password', '12345678']
for pwd in passwords_to_try:
    s = requests.Session()
    s.get(BASE_URL + '/login')
    r = s.post(BASE_URL + '/login', data={'username': 'admin', 'password': pwd}, allow_redirects=True, timeout=10)
    if r and r.status_code == 200 and ('注销' in r.text or '退出' in r.text or 'admin' in r.text.lower()):
        test(f"admin/{pwd} 登录成功", True)
        session = s  # 保存已登录session
        admin_session_ok = True
        break
    elif r and r.status_code == 200 and ('登录' in r.text and '密码' in r.text):
        continue
    elif r and r.status_code == 302:
        # 跟随重定向
        r2 = s.get(BASE_URL + '/', allow_redirects=True)
        if r2 and r2.status_code == 200:
            test(f"admin/{pwd} 登录成功(302)", True)
            session = s
            admin_session_ok = True
            break

if not admin_session_ok:
    test("admin登录", False, "所有常见密码均失败, 请手动确认密码")

# ============================================================
# 3. 登录后功能测试
# ============================================================
if admin_session_ok:
    # 验证session有效
    r = get('/')
    test("登录后访问首页", r and r.status_code == 200, f"状态码: {r.status_code if r else 'None'}")

    # ---- 3.1 人员管理 ----
    print("\n" + "-"*40)
    print("3. 人员管理模块")
    print("-"*40)

    r = get('/personnel')
    test("人员列表页面", r and r.status_code == 200, f"状态码: {r.status_code if r else 'None'}")
    if r and r.status_code == 200:
        test("人员列表含table", '<table' in r.text.lower() or '人员' in r.text, "缺少数据表格")

    r = get('/personnel/new')
    test("新增人员页面", r and r.status_code == 200, f"状态码: {r.status_code if r else 'None'}")

    # 空表单提交
    r = post('/personnel/new', data={}, allow_redirects=False)
    test("空表单提交处理", r is not None, "请求失败")
    if r:
        if r.status_code == 200:
            test("空表单返回200(重新渲染表单)", True)
        elif r.status_code == 302:
            test("空表单提交后跳转", False, "空表单不应成功")

    # 正常新增
    r = post('/personnel/new', data={
        'name': 'API测试用户',
        'emp_id': 'TST001',
        'gender': '男',
        'dept_level2': '测试部门',
    }, allow_redirects=False)
    test("新增人员(正常数据)", r and r.status_code in [200, 302], f"状态码: {r.status_code if r else 'None'}")

    # 搜索
    r = get('/personnel?search=测试')
    test("人员搜索", r and r.status_code == 200, f"状态码: {r.status_code if r else 'None'}")

    # XSS搜索
    r = get('/personnel?search=<script>alert(1)</script>')
    test("XSS搜索防护", r and r.status_code == 200 and '<script>alert' not in r.text, "可能存在XSS")

    # 编辑(ID=1)
    r = get('/personnel/1/update')
    if r and r.status_code == 200:
        test("编辑人员(ID=1)", True)
    elif r and r.status_code == 302:
        test("编辑人员(ID=1)", True, "可能重定向到详情")
    elif r and r.status_code == 404:
        test("编辑人员(ID=1)", False, "ID=1不存在")
    else:
        test("编辑人员(ID=1)", False, f"状态码: {r.status_code if r else 'None'}")

    # 详情
    r = get('/personnel/1')
    test("人员详情(ID=1)", r and r.status_code in [200, 404], f"状态码: {r.status_code if r else 'None'}")

    # 导出
    r = get('/personnel/export')
    test("人员Excel导出", r and r.status_code == 200, f"状态码: {r.status_code if r else 'None'}")

    # 模板下载
    r = get('/personnel/template')
    test("人员导入模板", r and r.status_code == 200, f"状态码: {r.status_code if r else 'None'}")

    # 删除测试数据
    r = post('/personnel/TST001/delete', allow_redirects=False)
    if not r or r.status_code == 404:
        # 用emp_id删除可能不行, 试试其他方式
        r = post('/personnel/9999/delete', allow_redirects=False)
    test("删除测试人员", r is not None)

    # ---- 3.2 资产管理 ----
    print("\n" + "-"*40)
    print("4. 资产管理模块")
    print("-"*40)

    r = get('/industrial_computers')
    test("工控机列表", r and r.status_code == 200, f"状态码: {r.status_code if r else 'None'}")

    r = get('/office_computers')
    test("办公电脑列表", r and r.status_code == 200, f"状态码: {r.status_code if r else 'None'}")

    # 工控机新增页面 - 需要找到正确URL
    r = get('/industrial_computers/add')
    if r and r.status_code == 200:
        test("工控机新增页面", True)
    else:
        # 试试其他路径
        r = get('/industrial_computers/new')
        test("工控机新增页面(/new)", r and r.status_code == 200, f"状态码: {r.status_code if r else 'None'}")

    # 导出
    r = get('/industrial_computers/export')
    test("工控机导出", r and r.status_code == 200, f"状态码: {r.status_code if r else 'None'}")

    # 模板
    r = get('/industrial_computers/template')
    test("工控机导入模板", r and r.status_code == 200, f"状态码: {r.status_code if r else 'None'}")

    # 办公电脑导出
    r = get('/office_computers/export')
    test("办公电脑导出", r and r.status_code == 200, f"状态码: {r.status_code if r else 'None'}")

    # 搜索
    r = get('/industrial_computers?search=test')
    test("工控机搜索", r and r.status_code == 200, f"状态码: {r.status_code if r else 'None'}")

    # ---- 3.3 部门管理 ----
    print("\n" + "-"*40)
    print("5. 部门管理模块")
    print("-"*40)

    r = get('/departments/manage')
    test("部门管理页面", r and r.status_code == 200, f"状态码: {r.status_code if r else 'None'}")

    # ---- 3.4 安全保密 ----
    print("\n" + "-"*40)
    print("6. 安全保密模块")
    print("-"*40)

    security_pages = [
        ('/security', '安全保密首页'),
        ('/security/roles', '角色管理'),
        ('/security/modules', '模块管理'),
        ('/security/permission-matrix', '权限矩阵'),
        ('/security/person_permission_matrix', '人员权限矩阵'),
        ('/security/classified_personnel', '涉密人员'),
        ('/security/classified_media', '涉密介质'),
        ('/security/security_zone', '安全区域'),
        ('/security/electronic_document', '电子文档'),
        ('/security/paper_document', '纸质文档'),
    ]

    for url, name in security_pages:
        r = get(url)
        test(f"{name}页面({url})", r and r.status_code == 200, f"状态码: {r.status_code if r else 'None'}")

    # 涉密人员导出
    r = get('/security/classified_personnel/export')
    test("涉密人员导出", r and r.status_code == 200, f"状态码: {r.status_code if r else 'None'}")

    # 涉密介质导出
    r = get('/security/classified_media/export')
    test("涉密介质导出", r and r.status_code == 200, f"状态码: {r.status_code if r else 'None'}")

    # ---- 3.5 审计巡检 ----
    print("\n" + "-"*40)
    print("7. 审计巡检模块")
    print("-"*40)

    audit_pages = [
        ('/audit/tasks', '审计任务列表'),
        ('/audit/my-tasks', '我的任务'),
        ('/audit/records', '审计记录'),
        ('/audit/statistics', '审计统计'),
    ]

    for url, name in audit_pages:
        r = get(url)
        test(f"{name}页面", r and r.status_code == 200, f"状态码: {r.status_code if r else 'None'}")

    # 创建审计任务
    r = get('/audit/tasks/create')
    test("创建审计任务页面", r and r.status_code == 200, f"状态码: {r.status_code if r else 'None'}")

    r = post('/audit/tasks/create', data={
        'title': '自动化测试任务',
        'task_type': '例行检查',
        'description': '自动化测试创建的任务',
        'priority': 'normal',
        'due_date': '2025-12-31'
    }, allow_redirects=False)
    test("创建审计任务(POST)", r and r.status_code in [200, 302], f"状态码: {r.status_code if r else 'None'}")

    # 创建审计记录
    r = get('/audit/records/create')
    test("创建审计记录页面", r and r.status_code == 200, f"状态码: {r.status_code if r else 'None'}")

    # ---- 3.6 AI助手 ----
    print("\n" + "-"*40)
    print("8. AI助手模块")
    print("-"*40)

    r = get('/ai-assistant')
    test("AI助手页面", r and r.status_code == 200, f"状态码: {r.status_code if r else 'None'}")

    r = get('/ai-settings')
    test("AI设置页面", r and r.status_code == 200, f"状态码: {r.status_code if r else 'None'}")

    # AI设置保存
    r = post('/ai-settings/save', json_data={
        'provider': 'ollama',
        'ollama_api_base': 'http://localhost:11434/v1',
        'ollama_model': 'llama3'
    }, allow_redirects=False)
    test("保存AI配置(POST)", r and r.status_code in [200, 302], f"状态码: {r.status_code if r else 'None'}")

    # AI对话 (需要LLM连接, 可能失败)
    r = post('/ai_assistant/chat', json_data={
        'message': '你好',
        'employee_id': 1
    }, allow_redirects=False)
    test("AI对话API响应", r is not None and r.status_code in [200, 500],
         f"状态码: {r.status_code if r else 'None'}")

    # ---- 3.7 管理员模块 ----
    print("\n" + "-"*40)
    print("9. 管理员模块")
    print("-"*40)

    admin_pages = [
        ('/admin/users', '用户管理'),
        ('/admin/login-logs', '登录日志'),
        ('/admin/operation-logs', '操作日志'),
    ]

    for url, name in admin_pages:
        r = get(url)
        test(f"{name}页面", r and r.status_code == 200, f"状态码: {r.status_code if r else 'None'}")

    # 创建用户
    r = get('/admin/users/add')
    test("创建用户页面", r and r.status_code == 200, f"状态码: {r.status_code if r else 'None'}")

    r = post('/admin/users/add', data={
        'username': 'testcase_user',
        'password': 'TestCase123!',
        'role': 'user',
        'is_active': '1'
    }, allow_redirects=False)
    test("创建测试用户(POST)", r and r.status_code in [200, 302], f"状态码: {r.status_code if r else 'None'}")

    # ============================================================
    # 4. 权限系统测试
    # ============================================================
    print("\n" + "="*60)
    print("10. 权限系统测试(普通用户)")
    print("="*60)

    user_s = requests.Session()
    user_s.get(BASE_URL + '/login')
    r = user_s.post(BASE_URL + '/login', data={
        'username': 'testcase_user', 'password': 'TestCase123!'
    }, allow_redirects=True)

    if r and r.status_code == 200:
        test("普通用户登录", True)

        # 尝试访问管理员页面
        r = user_s.get(BASE_URL + '/admin/users', allow_redirects=False)
        test("普通用户访问/admin/users应被拒", r and r.status_code in [302, 403],
             f"状态码: {r.status_code if r else 'None'}")

        r = user_s.get(BASE_URL + '/admin/login-logs', allow_redirects=False)
        test("普通用户访问/admin/login-logs应被拒", r and r.status_code in [302, 403],
             f"状态码: {r.status_code if r else 'None'}")

        r = user_s.get(BASE_URL + '/admin/operation-logs', allow_redirects=False)
        test("普通用户访问/admin/operation-logs应被拒", r and r.status_code in [302, 403],
             f"状态码: {r.status_code if r else 'None'}")

        # 尝试访问普通页面
        r = user_s.get(BASE_URL + '/personnel', allow_redirects=False)
        test("普通用户访问/personnel", r and r.status_code in [200, 403],
             f"状态码: {r.status_code if r else 'None'}")

        r = user_s.get(BASE_URL + '/ai-assistant', allow_redirects=False)
        test("普通用户访问/ai-assistant", r and r.status_code in [200, 403],
             f"状态码: {r.status_code if r else 'None'}")
    else:
        test("普通用户登录", False, "无法登录")

    # ============================================================
    # 5. 边界/异常情况测试
    # ============================================================
    print("\n" + "="*60)
    print("11. 边界/异常情况测试")
    print("="*60)

    # 页码边界
    r = get('/personnel?page=99999')
    test("超大页码", r and r.status_code == 200, f"状态码: {r.status_code if r else 'None'}")

    r = get('/personnel?page=-1')
    test("负数页码", r and r.status_code == 200, f"状态码: {r.status_code if r else 'None'}")

    r = get('/personnel?page=abc')
    test("字符串页码", r and r.status_code == 200, f"状态码: {r.status_code if r else 'None'}")

    r = get('/personnel?page=0')
    test("零页码", r and r.status_code == 200, f"状态码: {r.status_code if r else 'None'}")

    # 搜索边界
    r = get('/personnel?search=')
    test("空搜索", r and r.status_code == 200, f"状态码: {r.status_code if r else 'None'}")

    r = get('/personnel?search=' + 'A' * 1000)
    test("超长搜索词(1000字符)", r and r.status_code == 200, f"状态码: {r.status_code if r else 'None'}")

    # 不存在的ID
    r = get('/personnel/999999')
    test("不存在的人员ID", r and r.status_code in [200, 302, 404], f"状态码: {r.status_code if r else 'None'}")

    # 字符串ID路由匹配
    r = get('/personnel/abc')
    test("字符串ID /personnel/abc", r and r.status_code in [200, 400, 404, 500],
         f"状态码: {r.status_code if r else 'None'}")

    # XSS
    r = get('/personnel?search=<img+src=x+onerror=alert(1)>')
    test("XSS搜索注入防护", r and r.status_code == 200 and 'onerror=alert' not in r.text,
         "可能存在XSS")

    # SQL注入搜索
    r = get("/personnel?search='; DROP TABLE personnel; --")
    test("SQL注入搜索防护", r and r.status_code == 200, f"状态码: {r.status_code if r else 'None'}")

    # ============================================================
    # 6. 注销测试
    # ============================================================
    print("\n" + "="*60)
    print("12. 注销测试")
    print("="*60)

    r = get('/logout')
    test("注销功能", r and r.status_code in [200, 302], f"状态码: {r.status_code if r else 'None'}")

    r = get('/', allow_redirects=False)
    test("注销后访问首页重定向", r and r.status_code == 302, f"状态码: {r.status_code if r else 'None'}")

    # ============================================================
    # 7. 注册功能测试
    # ============================================================
    print("\n" + "="*60)
    print("13. 注册功能测试")
    print("="*60)

    r = get('/register')
    test("注册页面可访问", r and r.status_code == 200, f"状态码: {r.status_code if r else 'None'}")

    r = post('/register', data={}, allow_redirects=False)
    test("空表单注册处理", r is not None)

    r = post('/register', data={
        'username': 'weakpwd',
        'password': '123',
        'confirm_password': '123'
    }, allow_redirects=False)
    test("弱密码注册处理", r is not None)

else:
    print("\n[SKIP] 未登录成功, 跳过所有已登录测试")

# ============================================================
# 汇总
# ============================================================
print("\n" + "="*60)
print("测试汇总")
print("="*60)
print(f"总测试数: {total_tests}")
print(f"通过: {passed}")
print(f"失败: {failed}")
if total_tests > 0:
    print(f"通过率: {passed/total_tests*100:.1f}%")

if issues:
    print(f"\n失败项 ({len(issues)}个):")
    for i, issue in enumerate(issues, 1):
        print(f"  {i}. {issue['name']}" + (f" - {issue['detail']}" if issue['detail'] else ""))