# -*- coding: utf-8 -*-
from app import app, db
from app.models import User

with app.app_context():
    with app.test_client() as client:
        with client.session_transaction() as sess:
            user = User.query.filter_by(username='admin').first()
            if user:
                sess['_user_id'] = str(user.id)
                print('已设置管理员登录状态')
        
        response = client.get('/security/permissions')
        print('Status:', response.status_code)
        
        if response.status_code == 200:
            data_str = str(response.data, 'utf-8', errors='ignore')
            
            print('Length:', len(response.data))
            
            if '权限矩阵' in data_str:
                print('OK - page contains permission matrix title')
            else:
                print('FAIL - no permission matrix title')
            
            if '角色' in data_str:
                print('OK - page contains roles info')
            else:
                print('FAIL - no roles info')
            
            print('\n--- Page preview (lines 100-150) ---')
            lines = data_str.split('\n')
            count = 0
            for line in lines:
                if 'class=' in line or '<th' in line or '<td' in line:
                    print(line.strip()[:120])
                    count += 1
                    if count > 30:
                        break
        else:
            print('Page not accessible, status:', response.status_code)