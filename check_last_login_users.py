"""
检查最后登录用户的数据格式
"""
from app import app
from sqlalchemy import text

with app.app_context():
    from app import db
    
    print('=== 检查最后登录用户数据 ===\n')
    
    # 查询所有唯一值
    result = db.session.execute(text('''
        SELECT DISTINCT last_login_user 
        FROM computer_info 
        WHERE last_login_user IS NOT NULL 
        LIMIT 50
    '''))
    
    print('最后登录用户的样例数据 (前50条唯一值):')
    print('-' * 80)
    
    users = []
    for row in result:
        user = row[0]
        users.append(user)
        print('  {}'.format(user))
    
    print('\n' + '-' * 80)
    print('\n统计信息:')
    print('  总共唯一值: {}'.format(len(users)))
    
    # 分析工号格式
    print('\n工号格式分析:')
    print('  可能的工号格式:')
    print('    - 纯数字工号: 如 10001')
    print('    - 字母+数字: 如 E12345, L12345')
    print('    - 带括号的姓名: 如 (张三)')
    
    # 尝试提取工号
    print('\n工号提取示例:')
    import re
    
    for user in users[:10]:
        print('\n原始: {}'.format(user))
        
        # 去除 EVE 或 LUBAN
        cleaned = re.sub(r'\bEVE\b', '', user, flags=re.IGNORECASE)
        cleaned = re.sub(r'\bLUBAN\b', '', cleaned, flags=re.IGNORECASE)
        cleaned = cleaned.strip()
        
        print('  清洗后: {}'.format(cleaned))
        
        # 尝试提取纯数字工号
        numbers = re.findall(r'\d+', cleaned)
        if numbers:
            print('  提取到的数字: {}'.format(numbers))