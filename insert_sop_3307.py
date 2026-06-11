"""插入SOP数据到3307端口的MySQL"""
import pymysql

# 连接应用使用的数据库 (3307端口)
conn = pymysql.connect(
    host='10.5.192.253',
    port=3307,
    user='nocobase',
    password='nocobase',
    database='nocobase',
    charset='utf8mb4'
)

cursor = conn.cursor()

# 检查表是否存在
cursor.execute("SHOW TABLES LIKE 'investigation_sop'")
table_exists = cursor.fetchone()
print(f"investigation_sop表存在: {bool(table_exists)}")

if not table_exists:
    print("创建表...")
    cursor.execute("""
        CREATE TABLE investigation_sop (
            id INT AUTO_INCREMENT PRIMARY KEY,
            sop_no VARCHAR(50) NOT NULL UNIQUE,
            sop_title VARCHAR(200) NOT NULL,
            sop_type VARCHAR(50),
            sop_version VARCHAR(20),
            applicable_scope TEXT,
            investigation_steps TEXT,
            evidence_requirements TEXT,
            timeline_requirements TEXT,
            responsible_role VARCHAR(100),
            approval_process TEXT,
            status VARCHAR(20) DEFAULT 'draft',
            remark TEXT,
            full_content LONGTEXT,
            created_by INT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    print("✅ 表已创建")
else:
    # 检查full_content列
    cursor.execute("SHOW COLUMNS FROM investigation_sop LIKE 'full_content'")
    if not cursor.fetchone():
        print("添加full_content列...")
        cursor.execute("ALTER TABLE investigation_sop ADD COLUMN full_content LONGTEXT AFTER remark")
        conn.commit()
        print("✅ full_content列已添加")
    else:
        print("✅ full_content列已存在")

# 检查是否已有SOP数据
cursor.execute("SELECT id, sop_no, sop_title FROM investigation_sop WHERE sop_no='SOP-NJ-001'")
existing = cursor.fetchone()

# 读取完整HTML内容
with open(r'd:\资产管理\insert_sop_direct.py', 'r', encoding='utf-8') as f:
    content = f.read()
    # 提取full_content变量
    start = content.find('full_content = """') + len('full_content = """')
    end = content.find('"""', start)
    full_content = content[start:end]

if existing:
    print(f"更新现有记录 id={existing[0]}...")
    cursor.execute("""
        UPDATE investigation_sop SET 
            sop_title=%s, sop_type=%s, sop_version=%s,
            applicable_scope=%s, investigation_steps=%s,
            evidence_requirements=%s, timeline_requirements=%s,
            responsible_role=%s, approval_process=%s,
            status=%s, remark=%s, full_content=%s
        WHERE sop_no=%s
    """, (
        '匿名举报案件调查工作标准操作规程', '信息安全', '1.0',
        '惠州亿纬锂能股份有限公司（含下属子公司及关联基地）全体员工及相关利益方涉及的匿名举报情形',
        '举报受理与登记 → 初步评估与分级 → 正式启动调查 → 调查实施 → 结案与处置 → 存档与整理闭环',
        '1.举报原始材料统一编号 2.电话举报需录音 3.电子举报截屏保存 4.问询笔录须签字确认 5.实地核定拍照留痕',
        '1.举报受理后即时登记 2.初步评估应及时完成 3.调查方案经审批后启动 4.定期汇报机制',
        '保卫部/监察部（归口管理）、调查人员（执行）、公司领导（审批）',
        '1.保卫部归口管理 2.普通员工举报报管理层审批 3.高管举报逐级上报 4.调查方案经分管领导审批',
        'published', '来源文件：匿名举报案件调查SOP.docx',
        full_content, 'SOP-NJ-001'
    ))
    conn.commit()
    print(f'✅ 已更新SOP-NJ-001')
else:
    cursor.execute("""
        INSERT INTO investigation_sop (
            sop_no, sop_title, sop_type, sop_version,
            applicable_scope, investigation_steps,
            evidence_requirements, timeline_requirements,
            responsible_role, approval_process,
            status, remark, full_content, created_by
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        'SOP-NJ-001', '匿名举报案件调查工作标准操作规程', '信息安全', '1.0',
        '惠州亿纬锂能股份有限公司（含下属子公司及关联基地）全体员工及相关利益方涉及的匿名举报情形',
        '举报受理与登记 → 初步评估与分级 → 正式启动调查 → 调查实施 → 结案与处置 → 存档与整理闭环',
        '1.举报原始材料统一编号 2.电话举报需录音 3.电子举报截屏保存 4.问询笔录须签字确认 5.实地核定拍照留痕',
        '1.举报受理后即时登记 2.初步评估应及时完成 3.调查方案经审批后启动 4.定期汇报机制',
        '保卫部/监察部（归口管理）、调查人员（执行）、公司领导（审批）',
        '1.保卫部归口管理 2.普通员工举报报管理层审批 3.高管举报逐级上报 4.调查方案经分管领导审批',
        'published', '来源文件：匿名举报案件调查SOP.docx',
        full_content, 1
    ))
    conn.commit()
    print(f'✅ 已插入SOP-NJ-001')

# 验证
cursor.execute("SELECT id, sop_no, sop_title, LENGTH(full_content) as content_len FROM investigation_sop WHERE sop_no='SOP-NJ-001'")
row = cursor.fetchone()
if row:
    print(f'验证: id={row[0]}, sop_no={row[1]}, title={row[2]}, content_len={row[3]}')
else:
    print('❌ 验证失败：未找到记录')

cursor.close()
conn.close()
print('✅ 完成！')