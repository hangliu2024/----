from app import app
from app.models import ComputerInfo, TangibleAsset

with app.app_context():
    print('=== ComputerInfo 表结构 ===')
    print('字段列表:')
    for col in ComputerInfo.__table__.columns:
        print(f'  - {col.name}: {col.type}')
    
    print('\n=== ComputerInfo 数据样例 (前5条) ===')
    computer_infos = ComputerInfo.query.limit(5).all()
    for i, comp in enumerate(computer_infos, 1):
        print(f'\n电脑 {i}:')
        print(f'  ID: {comp.id}')
        print(f'  asset_id: {comp.asset_id}')
        print(f'  network_address: {comp.network_address}')
        print(f'  ip_mac: {comp.ip_mac}')
        print(f'  operating_system: {comp.operating_system}')
        print(f'  last_login_user: {comp.last_login_user}')
    
    print('\n=== TangibleAsset 表结构 ===')
    print('字段列表:')
    for col in TangibleAsset.__table__.columns:
        print(f'  - {col.name}: {col.type}')
    
    print('\n=== 检查 computer_info 和 tangible_asset 的关联 ===')
    # 尝试通过 asset_id 关联
    sample = ComputerInfo.query.first()
    if sample and sample.asset_id:
        related_asset = TangibleAsset.query.get(sample.asset_id)
        if related_asset:
            print(f'找到关联的有形资产:')
            print(f'  资产名称: {related_asset.name}')
            print(f'  资产类别: {related_asset.category}')
            print(f'  资产位置: {related_asset.location}')
        else:
            print(f'未找到 asset_id={sample.asset_id} 的有形资产')