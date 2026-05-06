"""
为computer_info表添加工号列并清洗数据
"""
from app import app
from sqlalchemy import text
import re

with app.app_context():
    from app import db
    
    print('=== 为computer_info表添加工号列 ===\n')
    
    # 1. 检查列是否已存在
    print('1. 检查现有表结构...')
    columns = db.session.execute(text('DESCRIBE computer_info')).fetchall()
    column_names = [col[0] for col in columns]
    
    if 'employee_id' in column_names:
        print('   employee_id 列已存在')
    else:
        print('   employee_id 列不存在，正在添加...')
        try:
            db.session.execute(text('''
                ALTER TABLE computer_info 
                ADD COLUMN employee_id VARCHAR(50) NULL
                COMMENT '工号'
                AFTER computer_name
            '''))
            db.session.commit()
            print('   [OK] 成功添加 employee_id 列')
        except Exception as e:
            print('   [FAIL] 添加列失败: {}'.format(e))
            db.session.rollback()
    
    # 2. 定义工号提取函数
    def extract_employee_id(last_login_user):
        """
        从最后登录用户提取工号
        规则：
        1. 如果是纯中文姓名，返回原值或标记为"无工号"
        2. 如果包含"EVE"或"LUBAN"，去除后提取数字部分
        3. 其他情况，清理后返回
        """
        if not last_login_user:
            return None
        
        original = last_login_user.strip()
        
        # 检查是否是纯中文姓名
        if re.match(r'^[\u4e00-\u9fa5]+$', original):
            # 纯中文姓名，保留原值作为工号
            return original
        
        # 去除 EVE (不区分大小写)
        cleaned = re.sub(r'\bEVE\b', '', original, flags=re.IGNORECASE)
        # 去除 LUBAN (不区分大小写)
        cleaned = re.sub(r'\bLUBAN\b', '', cleaned, flags=re.IGNORECASE)
        # 去除连字符和特殊字符，但保留数字和字母
        cleaned = re.sub(r'[^a-zA-Z0-9]', '', cleaned)
        
        # 如果清洗后为空或太短，返回原值
        if not cleaned or len(cleaned) < 2:
            return original
        
        return cleaned
    
    # 3. 查看需要清洗的数据样例
    print('\n2. 查看需要清洗的数据...')
    sample_query = db.session.execute(text('''
        SELECT DISTINCT last_login_user 
        FROM computer_info 
        WHERE last_login_user IS NOT NULL 
        LIMIT 10
    '''))
    
    print('\n数据清洗示例:')
    print('-' * 80)
    for row in sample_query:
        original = row[0]
        extracted = extract_employee_id(original)
        print('原始: {:20s} -> 清洗后: {}'.format(original, extracted))
    
    # 4. 更新所有数据
    print('\n3. 开始清洗并更新数据...')
    
    # 获取所有记录
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
        employee_id = extract_employee_id(last_login_user)
        
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
        
        # 每1000条打印一次进度
        if total % 1000 == 0:
            print('  已处理 {} / {} 条记录...'.format(total, all_records.rowcount if hasattr(all_records, 'rowcount') else '未知'))
    
    db.session.commit()
    print('[OK] 数据更新完成！共处理 {} 条记录'.format(updated))
    
    # 5. 验证结果
    print('\n4. 验证更新结果...')
    result = db.session.execute(text('''
        SELECT last_login_user, employee_id 
        FROM computer_info 
        WHERE employee_id IS NOT NULL 
        LIMIT 10
    '''))
    
    print('\n更新后的数据示例:')
    print('-' * 80)
    for row in result:
        print('最后登录用户: {:20s} -> 工号: {}'.format(row[0], row[1]))
    
    # 6. 统计信息
    print('\n5. 统计信息...')
    stats = db.session.execute(text('''
        SELECT 
            COUNT(*) as total,
            COUNT(employee_id) as with_employee_id,
            COUNT(last_login_user) - COUNT(employee_id) as without_employee_id
        FROM computer_info
    ''')).fetchone()
    
    print('  总记录数: {}'.format(stats[0]))
    print('  有工号的记录: {}'.format(stats[1]))
    print('  无工号的记录: {}'.format(stats[2]))
    
    # 显示工号分布
    print('\n6. 工号格式分布...')
    pattern_stats = db.session.execute(text('''
        SELECT 
            CASE 
                WHEN employee_id REGEXP '^[A-Z]{2,}[0-9]+$' THEN '大写字母开头+数字'
                WHEN employee_id REGEXP '^[a-z]+[0-9]+$' THEN '小写字母开头+数字'
                WHEN employee_id REGEXP '^[0-9]+$' THEN '纯数字'
                WHEN employee_id REGEXP '^[0-9]+-[0-9]+$' THEN '数字-数字'
                ELSE '其他'
            END as pattern,
            COUNT(*) as count
        FROM computer_info
        WHERE employee_id IS NOT NULL
        GROUP BY pattern
        ORDER BY count DESC
    '''))
    
    print('-' * 80)
    for row in pattern_stats:
        print('  {:20s}: {} 条'.format(row[0], row[1]))
    
    print('\n' + '=' * 80)
    print('[OK] 工号列添加和数据清洗完成！')