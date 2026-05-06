"""
测试电脑名称显示修复
"""
from app import app
from app.models import ComputerInfo

with app.app_context():
    print('=== 测试电脑名称显示 ===\n')
    
    # 获取前5条电脑信息
    computer_infos = ComputerInfo.query.limit(5).all()
    
    print('办公电脑列表:')
    print('-' * 80)
    
    for i, comp in enumerate(computer_infos, 1):
        print('\n电脑 {}:'.format(i))
        print('  电脑名称: {}'.format(comp.computer_name if comp.computer_name else '[无]'))
        print('  资产ID: {}'.format(comp.asset_id))
        print('  网络地址: {}'.format(comp.network_address if comp.network_address else '[无]'))
        print('  最后登录用户: {}'.format(comp.last_login_user if comp.last_login_user else '[无]'))
        
        # 模拟显示名称
        if comp.computer_name:
            display_name = comp.computer_name
        else:
            display_name = '资产ID: {}'.format(comp.asset_id) if comp.asset_id else '未知电脑'
        
        print('  [显示名称]: {}'.format(display_name))
    
    print('\n' + '-' * 80)
    print('测试完成！')