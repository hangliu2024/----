from app import app
from app.models import ComputerInfo

with app.app_context():
    print('=== ComputerInfo 表完整结构 ===')
    print('字段列表:')
    for col in ComputerInfo.__table__.columns:
        print('  - {}: {}'.format(col.name, col.type))
    
    print('\n=== ComputerInfo 数据样例 (前5条) ===')
    computer_infos = ComputerInfo.query.limit(5).all()
    for i, comp in enumerate(computer_infos, 1):
        print('\n电脑 {}:'.format(i))
        print('  id: {}'.format(comp.id))
        print('  asset_id: {}'.format(comp.asset_id))
        print('  network_address: {}'.format(comp.network_address))
        print('  ip_mac: {}'.format(comp.ip_mac))
        print('  operating_system: {}'.format(comp.operating_system))
        print('  last_login_user: {}'.format(comp.last_login_user))
        
        # 检查是否有 computer_name 属性
        if hasattr(comp, 'computer_name'):
            print('  computer_name: {}'.format(comp.computer_name))
        else:
            print('  [注意] 没有 computer_name 属性')