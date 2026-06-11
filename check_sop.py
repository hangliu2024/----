"""检查SOP是否已导入数据库"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from app.models import InvestigationSOP

with app.app_context():
    sops = InvestigationSOP.query.all()
    print(f'=== 数据库中SOP总数: {len(sops)} ===')
    for s in sops:
        print(f'  ID:{s.id} | 编号:{s.sop_no} | 标题:{s.sop_title} | 类型:{s.sop_type} | 版本:{s.sop_version} | 状态:{s.status}')
        print(f'    适用范围: {(s.applicable_scope or "")[:80]}...')
        print(f'    责任角色: {s.responsible_role}')
    
    if not sops:
        print('\n⚠️  数据库中没有任何SOP记录！案件调查SOP尚未导入。')
    else:
        # 检查是否有匿名举报案件调查SOP
        target = InvestigationSOP.query.filter_by(sop_no='SOP-NJ-001').first()
        if target:
            print(f'\n✅ 匿名举报案件调查SOP已导入 (编号: {target.sop_no})')
        else:
            print('\n⚠️  未找到编号为SOP-NJ-001的记录，匿名举报案件调查SOP可能未导入。')