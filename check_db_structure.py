from app import app
from sqlalchemy import text

with app.app_context():
    from app import db
    
    print('=== 直接查询数据库表结构 ===')
    
    # 查询 computer_info 表的结构
    result = db.session.execute(text('DESCRIBE computer_info'))
    print('\ncomputer_info 表结构:')
    for row in result:
        print('  {} - {} - NULL={}'.format(row[0], row[1], row[2]))
    
    # 查询前5条数据的所有字段
    print('\n=== computer_info 表数据样例 ===')
    result = db.session.execute(text('SELECT * FROM computer_info LIMIT 5'))
    columns = db.session.execute(text('DESCRIBE computer_info')).fetchall()
    col_names = [col[0] for col in columns]
    
    print('字段: {}'.format(col_names))
    print()
    
    for row in result:
        print('样例数据:')
        for i, col in enumerate(col_names):
            print('  {}: {}'.format(col, row[i]))