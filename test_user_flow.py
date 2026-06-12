import requests, re

base = 'http://10.5.192.253:5001'
s = requests.Session()
results = []

# 1. 登录
r = s.get(f'{base}/login'); r.encoding='utf-8'
csrf = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', r.text).group(1)
r = s.post(f'{base}/login', data={'email':'admin@example.com','password':'Admin123!','csrf_token':csrf})
results.append(('登录', '正常' if r.status_code==200 else '失败'))

# 2. 仪表盘
r = s.get(f'{base}/'); r.encoding='utf-8'
has_kpi = '办公电脑' in r.text and '人数' in r.text
has_modules = '系统模块' in r.text
results.append(('仪表盘', '正常' if has_kpi and has_modules else '异常'))

# 3. 人员管理
r = s.get(f'{base}/personnel'); r.encoding='utf-8'
results.append(('人员管理', '正常' if '员工' in r.text else '异常'))

# 4. 办公电脑（分页）
r = s.get(f'{base}/office_computers?per_page=20'); r.encoding='utf-8'
results.append(('办公电脑', '正常' if '电脑名称' in r.text else '异常'))

# 5. 涉密人员
r = s.get(f'{base}/security/classified_personnel'); r.encoding='utf-8'
results.append(('涉密人员', '正常' if '涉密' in r.text else '异常'))

# 6. 安全区域
r = s.get(f'{base}/security/security_zone'); r.encoding='utf-8'
results.append(('安全区域', '正常' if '区域' in r.text else '异常'))

# 7. AI助手页面
r = s.get(f'{base}/ai-assistant'); r.encoding='utf-8'
results.append(('AI助手页面', '正常' if '数据问答' in r.text and '发送' in r.text else '异常'))

# 8. AI数据问答
r = s.post(f'{base}/api/ai/query/stream', json={'question':'公司有多少员工','mode':'query'}, stream=True)
data = ''
for line in r.iter_lines():
    if line: data += line.decode(errors='replace') + ' '
results.append(('AI数据问答', '正常' if 'done' in data else '无响应'))

# 9. AI一般对话
r = s.post(f'{base}/api/ai/query/stream', json={'question':'你好','mode':'chat'}, stream=True)
data = ''
for line in r.iter_lines():
    if line: data += line.decode(errors='replace') + ' '
results.append(('AI一般对话', '正常' if 'done' in data else '无响应'))

# 10. 稽查
r = s.get(f'{base}/audit/tasks'); r.encoding='utf-8'
results.append(('稽查管理', '正常' if '任务' in r.text else '异常'))

# 11. 用户管理
r = s.get(f'{base}/admin/users'); r.encoding='utf-8'
results.append(('用户管理', '正常' if '用户' in r.text else '异常'))

# 12. 保密首页
r = s.get(f'{base}/security/index'); r.encoding='utf-8'
results.append(('保密首页', '正常' if '涉密' in r.text or '保密' in r.text else '异常'))

# 打印结果
sep = '=' * 60
print(sep)
print('  ' + '\u7528\u6237\u89c6\u89d2\u6d4b\u8bd5\u62a5\u544a')
print('  ' + '\u6d4b\u8bd5\u5730\u5740: ' + base)
print(sep)
print()

h1 = '\u6a21\u5757'
h2 = '\u7ed3\u679c'
h3 = '\u72b6\u6001'
print(f'{h1:<16} {h2:<8} {h3}')
print('-' * 40)
ok = 0
for name, status in results:
    mark = '[OK]' if status == '正常' else '[FAIL]'
    if status == '正常': ok += 1
    print(f'{name:<16} {mark:<6} {status}')

print('-' * 40)
print(f'\u5408\u8ba1: {ok}/{len(results)} \u6a21\u5757\u6b63\u5e38')
print(sep)
if ok == len(results):
    print('ALL PASS - \u5168\u90e8\u6d4b\u8bd5\u901a\u8fc7')
else:
    print('SOME FAILED - \u8bf7\u68c0\u67e5\u5f02\u5e38\u6a21\u5757')
print(sep)
