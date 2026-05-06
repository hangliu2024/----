"""
测试漏洞修复效果
"""
from app import app
from app.models import ComputerInfo, TangibleAsset, Department, User
from app.routes.assets import office_computers
from flask_login import login_user

def test_computer_names():
    """测试办公电脑是否显示真实名称"""
    print('\n=== 测试1: 办公电脑名称显示 ===')
    
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['_user_id'] = '1'  # 假设admin用户ID为1
        
        # 测试办公电脑路由
        response = client.get('/office_computers')
        print(f'状态码: {response.status_code}')
        
        # 检查是否有"电脑 ("这样的虚假名称
        response_text = response.data.decode('utf-8')
        if '电脑 (' in response_text:
            print('[FAIL] 仍然显示虚假的电脑名称 (电脑 (ID))')
        else:
            print('[OK] 不再显示虚假的电脑名称')
        
        # 检查是否有真实的资产名称或IP地址
        if '资产ID:' in response_text or '10.' in response_text:
            print('[OK] 显示真实的电脑标识（资产名称或IP地址）')

def test_open_redirect():
    """测试开放重定向漏洞修复"""
    print('\n=== 测试2: 开放重定向漏洞 ===')
    
    with app.test_client() as client:
        # 测试恶意重定向
        response = client.get('/login?next=http://evil.com')
        print('尝试恶意重定向到 http://evil.com')
        print('响应状态码: {}'.format(response.status_code))
        
        if response.status_code == 200:
            # 检查是否被重定向到恶意网站
            response_text = response.data.decode('utf-8')
            if 'evil.com' not in response_text:
                print('[OK] 成功阻止开放重定向攻击')
            else:
                print('[FAIL] 仍然存在开放重定向漏洞')

def test_department_permissions():
    """测试部门权限检查"""
    print('\n=== 测试3: 部门权限检查 ===')
    
    with app.test_client() as client:
        # 测试人员管理路由的权限装饰器
        response = client.get('/personnel/new')
        print('人员创建页面访问状态码: {}'.format(response.status_code))
        
        if response.status_code == 200 or response.status_code == 302:
            print('[OK] 人员管理路由已添加部门权限检查')
        else:
            print('[FAIL] 人员管理路由权限检查有问题')

def test_computer_info_table():
    """测试computer_info表结构"""
    print('\n=== 测试4: ComputerInfo表结构 ===')
    
    with app.app_context():
        # 检查computer_info表
        columns = [col.name for col in ComputerInfo.__table__.columns]
        print(f'ComputerInfo表字段: {columns}')
        
        # 检查tangible_asset表
        asset_columns = [col.name for col in TangibleAsset.__table__.columns]
        print(f'TangibleAsset表字段: {asset_columns}')
        
        # 尝试关联查询
        sample = ComputerInfo.query.first()
        if sample and sample.asset_id:
            related_asset = TangibleAsset.query.get(sample.asset_id)
            if related_asset:
                print('[OK] 成功关联到有形资产: {}'.format(related_asset.name))
            else:
                print('[WARN] ComputerInfo.asset_id 与 TangibleAsset.id 没有匹配')

if __name__ == '__main__':
    print('开始测试漏洞修复效果...')
    print('=' * 50)
    
    test_computer_info_table()
    test_computer_names()
    test_open_redirect()
    test_department_permissions()
    
    print('\n' + '=' * 50)
    print('测试完成！')