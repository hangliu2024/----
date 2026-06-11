"""插入安全模块测试数据"""
import sys
sys.path.insert(0, '.')
from app import app, db
from datetime import datetime

with app.app_context():
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # classified_personnel
    db.session.execute(db.text(f"""INSERT INTO classified_personnel 
        (emp_id, emp_name, dept_id, dept_name, position, classification_level, training_record, 
         agreement_type, agreement_sign_date, status, signing_date, expiration_date, remark, created_at) VALUES
        ('000001', '张伟', 1, '技术研发部', '高级工程师', '机密', '已培训', '保密协议', '2024-01-15', '在职', '2024-01-15', '2027-01-15', '核心技术人员', '{now}'),
        ('000002', '李娜', 2, '项目管理部', '项目经理', '秘密', '已培训', '保密协议', '2024-03-01', '在职', '2024-03-01', '2027-03-01', '', '{now}'),
        ('000003', '王强', 1, '技术研发部', '技术总监', '绝密', '已培训', '保密协议+竞业', '2023-06-10', '在职', '2023-06-10', '2026-06-10', '技术负责人', '{now}'),
        ('000004', '赵敏', 3, '质量保障部', '质量工程师', '机密', '已培训', '保密协议', '2024-02-20', '在职', '2024-02-20', '2027-02-20', '', '{now}'),
        ('000005', '刘洋', 4, '生产制造部', '工艺工程师', '秘密', '已培训', '保密协议', '2023-08-05', '在职', '2023-08-05', '2026-08-05', '已续签', '{now}')
    """))
    print('Inserted 5 classified_personnel')
    
    # classified_media
    db.session.execute(db.text(f"""INSERT INTO classified_media 
        (media_id, media_type, brand_model, serial_no, classification, custodian_id, custodian_name,
         dept_id, dept_name, purpose, status, media_number, capacity, responsible_name, responsible_emp_id, remark, created_at) VALUES
        ('SM001', 'U盘', '金士顿DTSE9', 'KIN20240001', '机密', '000001', '张伟', 1, '技术研发部', '数据传输', '在用', 'SM-2024-001', '64GB', '王强', '000003', '', '{now}'),
        ('SM002', '移动硬盘', '西部数据', 'WD20240002', '秘密', '000002', '李娜', 2, '项目管理部', '项目资料备份', '在用', 'SM-2024-002', '2TB', '李娜', '000002', '', '{now}'),
        ('SM003', '光盘', 'Verbatim', 'VB20240003', '绝密', '000003', '王强', 1, '技术研发部', '核心技术归档', '在库', 'SM-2024-003', '50GB', '王强', '000003', '双盘备份', '{now}'),
        ('SM004', 'U盘', 'SanDisk', 'SD20240004', '秘密', '000004', '赵敏', 3, '质量保障部', '测试数据传输', '在用', 'SM-2024-004', '128GB', '赵敏', '000004', '', '{now}'),
        ('SM005', '软盘', '3M', '3M20240005', '机密', '000005', '刘洋', 4, '生产制造部', '历史数据存档', '待销毁', 'SM-2024-005', '1.44MB', '刘洋', '000005', '待集中销毁', '{now}')
    """))
    print('Inserted 5 classified_media')
    
    # security_zone
    db.session.execute(db.text(f"""INSERT INTO security_zone 
        (zone_id, zone_name, zone_type, location, manager_id, manager_name,
         dept_id, dept_name, status, zone_code, zone_level, responsible_name, responsible_emp_id, remark, created_at) VALUES
        ('ZONE001', '核心机房', '机房', 'A栋3层301室', '000003', '王强', 1, '技术研发部', '正常', 'ZONE-001', '绝密', '王强', '000003', '24小时监控', '{now}'),
        ('ZONE002', '涉密档案室', '档案室', 'B栋1层102室', '000002', '李娜', 2, '项目管理部', '正常', 'ZONE-002', '机密', '李娜', '000002', '', '{now}'),
        ('ZONE003', '研发实验室', '实验室', 'A栋4层401室', '000001', '张伟', 1, '技术研发部', '正常', 'ZONE-003', '机密', '张伟', '000001', '需申请进入', '{now}'),
        ('ZONE004', '会议室A', '会议室', 'A栋2层201室', '000004', '赵敏', 3, '质量保障部', '正常', 'ZONE-004', '秘密', '赵敏', '000004', '涉密会议专用', '{now}')
    """))
    print('Inserted 4 security_zone')
    
    # electronic_document
    db.session.execute(db.text(f"""INSERT INTO electronic_document 
        (doc_id, doc_title, classification, file_format, drafter_id, drafter_name, draft_dept,
         storage_path, custodian_id, custodian_name, dept_id, dept_name, doc_status,
         doc_number, doc_level, responsible_name, responsible_emp_id, file_path, remark, created_at) VALUES
        ('ED001', '产品设计图纸V3.0', '绝密', 'DWG', '000001', '张伟', '技术研发部',
         '/server/secret/design', '000001', '张伟', 1, '技术研发部', '正常',
         'ED-2024-001', '绝密', '张伟', '000001', '/server/secret/design', '最新版本', '{now}'),
        ('ED002', '项目验收报告', '机密', 'PDF', '000002', '李娜', '项目管理部',
         '/server/secret/report', '000002', '李娜', 2, '项目管理部', '正常',
         'ED-2024-002', '机密', '李娜', '000002', '/server/secret/report', '', '{now}'),
        ('ED003', '测试方案文档', '秘密', 'DOCX', '000004', '赵敏', '质量保障部',
         '/server/secret/test', '000004', '赵敏', 3, '质量保障部', '正常',
         'ED-2024-003', '秘密', '赵敏', '000004', '/server/secret/test', '', '{now}'),
        ('ED004', '工艺流程参数表', '机密', 'XLSX', '000005', '刘洋', '生产制造部',
         '/server/secret/process', '000005', '刘洋', 4, '生产制造部', '正常',
         'ED-2024-004', '机密', '刘洋', '000005', '/server/secret/process', '', '{now}')
    """))
    print('Inserted 4 electronic_document')
    
    # paper_document
    db.session.execute(db.text(f"""INSERT INTO paper_document 
        (doc_id, doc_title, classification, copies, pages, drafter_id, drafter_name,
         holder_id, holder_name, storage_location, custodian_id, custodian_name,
         dept_id, dept_name, doc_status, doc_number, doc_level, responsible_name, responsible_emp_id, quantity, remark, created_at) VALUES
        ('PD001', '保密承诺书', '机密', 1, 3, '000001', '张伟',
         '000002', '李娜', '档案室A柜3层', '000002', '李娜',
         2, '项目管理部', '在库', 'PD-2024-001', '机密', '李娜', '000002', 1, '', '{now}'),
        ('PD002', '核心技术方案', '绝密', 2, 45, '000003', '王强',
         '000003', '王强', '核心机房保险柜', '000003', '王强',
         1, '技术研发部', '在库', 'PD-2024-002', '绝密', '王强', '000003', 2, '仅限授权查阅', '{now}'),
        ('PD003', '质量检测报告', '秘密', 3, 18, '000004', '赵敏',
         '000004', '赵敏', '档案室B柜1层', '000004', '赵敏',
         3, '质量保障部', '在库', 'PD-2024-003', '秘密', '赵敏', '000004', 3, '', '{now}'),
        ('PD004', '生产工序指导书', '秘密', 5, 22, '000005', '刘洋',
         '000005', '刘洋', '档案室C柜2层', '000005', '刘洋',
         4, '生产制造部', '借出', 'PD-2024-004', '秘密', '刘洋', '000005', 5, '借出给车间', '{now}')
    """))
    print('Inserted 4 paper_document')
    
    db.session.commit()
    
    for t in ['classified_personnel','classified_media','security_zone','electronic_document','paper_document']:
        r = db.session.execute(db.text(f'SELECT COUNT(*) FROM {t}'))
        print(f'  {t}: {r.scalar()} records')
    print('Done!')