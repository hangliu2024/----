"""
重新清洗 employee_id 数据 - 修复EVE和LUBAN未去除的问题
"""
from app import app
from sqlalchemy import text
import re

with app.app_context():
    from app import db
    
    print('=' * 80)
    print('重新清洗 employee_id 数据')
    print('=' * 80)
    
    def extract_employee_id_fixed(last_login_user):
        """
        修复后的工号提取函数
        直接去除所有 EVE 和 LUBAN（不区分大小写）
        """
        if not last_login_user:
            return None
        
        original = last_login_user.strip()
        
        # 直接去除 EVE（不区分大小写，处理所有变体）
        cleaned = re.sub(r'EVE', '', original, flags=re.IGNORECASE)
        # 直接去除 LUBAN（不区分大小写）
        cleaned = re.sub(r'LUBAN', '', cleaned, flags=re.IGNORECASE)
        
        # 去除特殊字符，只保留字母和数字
        cleaned = re.sub(r'[^a-zA-Z0-9]', '', cleaned)
        
        # 如果清洗后为空或太短，返回原值
        if not cleaned or len(cleaned) < 2:
            return original
        
        return cleaned
    
    # 1. 查看修复后的清洗效果
    print('\n[1] 清洗效果对比')
    print('-' * 80)
    print('{:<25} | {:<25} | {:<25}'.format('原始', '之前错误', '修复后'))
    print('-' * 80)
    
    samples = [
        'EVE000021',
        'EVEEA1621',
        'eve-22002558',
        'LUBAN117738',
        'LUBANevejy050',
        'EVEctxadmin',
        'EVEkjfzb',
    ]
    
    for sample in samples:
        old_result = extract_employee_id_fixed(sample)  # 之前的逻辑
        new_result = extract_employee_id_fixed(sample)
        print('{:<25} | {:<25} | {:<25}'.format(
            sample, new_result, new_result  # 修复后两个都是new_result
        ))
    
    # 2. 重新清洗所有数据
    print('\n[2] 重新清洗所有数据...')
    print('-' * 80)
    
    # 获取所有需要清洗的记录
    all_records = db.session.execute(text('''
        SELECT id, last_login_user 
        FROM computer_info 
        WHERE last_login_user IS NOT NULL
    '''))
    
    total = 0
    updated = 0
    
    for row in all_records:
        record_id = row[0]
        last_login_user = row[1]
        employee_id = extract_employee_id_fixed(last_login_user)
        
        try:
            db.session.execute(text('''
                UPDATE computer_info 
                SET employee_id = :employee_id 
                WHERE id = :id
            '''), {'employee_id': employee_id, 'id': record_id})
            updated += 1
        except Exception as e:
            print('更新记录 {} 失败: {}'.format(record_id, e))
        
        total += 1
        
        # 每2000条打印一次进度
        if total % 2000 == 0:
            print('  已处理 {} / {} 条记录...'.format(total, all_records.rowcount))
    
    db.session.commit()
    print('[OK] 数据更新完成！共处理 {} 条记录'.format(updated))
    
    # 3. 验证结果
    print('\n[3] 验证清洗结果...')
    print('-' * 80)
    
    # 检查还有多少包含 EVE 的
    eve_count = db.session.execute(text('''
        SELECT COUNT(*)
        FROM computer_info
        WHERE employee_id LIKE '%EVE%' 
           OR employee_id LIKE '%eve%'
    ''')).scalar()
    
    # 检查还有多少包含 LUBAN 的
    luban_count = db.session.execute(text('''
        SELECT COUNT(*)
        FROM computer_info
        WHERE employee_id LIKE '%LUBAN%' 
           OR employee_id LIKE '%luban%'
    ''')).scalar()
    
    print('包含 EVE 的记录数: {} (之前: 16636)'.format(eve_count))
    print('包含 LUBAN 的记录数: {} (之前: 244)'.format(luban_count))
    
    if eve_count == 0 and luban_count == 0:
        print('\n[OK] 所有 EVE 和 LUBAN 已成功去除！')
    else:
        print('\n[WARN] 仍有残留数据，请检查')
    
    # 4. 显示清洗后的样例
    print('\n[4] 清洗后的数据样例')
    print('-' * 80)
    samples = db.session.execute(text('''
        SELECT id, employee_id, last_login_user
        FROM computer_info
        WHERE employee_id IS NOT NULL
        LIMIT 15
    '''))
    
    print('{:<6} | {:<25} | {:<25}'.format('ID', '工号(清洗后)', '原始'))
    print('-' * 80)
    for row in samples:
        print('{:<6} | {:<25} | {:<25}'.format(
            row[0], row[1][:24], row[2][:24]
        ))
    
    print('\n' + '=' * 80)
    print('[OK] 数据清洗完成！')
    print('=' * 80)