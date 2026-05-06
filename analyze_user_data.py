"""
分析所有唯一用户数据
"""
from app import app
from sqlalchemy import text
import re

with app.app_context():
    from app import db
    
    print('=== 分析所有唯一用户数据 ===\n')
    
    # 查询所有唯一值
    result = db.session.execute(text('''
        SELECT DISTINCT last_login_user 
        FROM computer_info 
        WHERE last_login_user IS NOT NULL 
        ORDER BY last_login_user
    '''))
    
    all_users = [row[0] for row in result]
    
    print('总共有 {} 个唯一用户\n'.format(len(all_users)))
    
    # 分类统计
    chinese_only = []  # 纯中文姓名
    has_numbers = []   # 包含数字
    starts_with_eve = []  # 以EVE开头
    
    for user in all_users:
        if re.match(r'^[\u4e00-\u9fa5]+$', user):
            chinese_only.append(user)
        elif user.upper().startswith('EVE'):
            starts_with_eve.append(user)
        elif re.search(r'\d', user):
            has_numbers.append(user)
    
    print('数据分类统计:')
    print('=' * 80)
    print('1. 纯中文姓名: {} 个'.format(len(chinese_only)))
    print('2. 以EVE开头的: {} 个'.format(len(starts_with_eve)))
    print('3. 包含数字的其他: {} 个'.format(len([u for u in has_numbers if u not in starts_with_eve])))
    print('=' * 80)
    
    print('\n以EVE开头的用户示例 (前20个):')
    print('-' * 80)
    for user in starts_with_eve[:20]:
        print('  {}'.format(user))
    
    print('\n包含数字的其他用户 (前20个):')
    print('-' * 80)
    other_with_numbers = [u for u in has_numbers if u not in starts_with_eve]
    for user in other_with_numbers[:20]:
        print('  {}'.format(user))
    
    print('\n工号提取示例 (从EVE开头的用户中):')
    print('-' * 80)
    for user in starts_with_eve[:10]:
        print('\n原始: {}'.format(user))
        
        # 去除 EVE
        cleaned = re.sub(r'\bEVE\b', '', user, flags=re.IGNORECASE)
        print('  去除EVE后: {}'.format(cleaned.strip()))
        
        # 提取数字
        numbers = re.findall(r'\d+', cleaned)
        if numbers:
            print('  提取的数字: {}'.format(numbers))
            print('  最终工号: {}'.format(numbers[0] if numbers else cleaned.strip()))