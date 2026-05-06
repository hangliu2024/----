from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 部门模型
class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=True)
    level = db.Column(db.Integer, nullable=False, default=1)  # 部门层级
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # 自关联 - 支持部门层级结构
    parent = db.relationship('Department', remote_side=[id], backref='sub_departments')
    # 关联用户
    users = db.relationship('User', backref='department', lazy=True)
    # 关联人员 - 移除错误的外键关系，因为Personnel.dept_code不是外键
    
    def __repr__(self):
        return f"Department('{self.name}', '{self.code}', level={self.level})"

# 用户模型
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # admin, department_admin, user
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=True)
    department_access = db.Column(db.Boolean, nullable=False, default=False)  # 是否只查看自己部门数据
    
    # 新增字段
    emp_id = db.Column(db.String(20), nullable=True)  # 工号
    phone = db.Column(db.String(20), nullable=True)  # 手机号
    real_name = db.Column(db.String(50), nullable=True)  # 真实姓名
    is_active = db.Column(db.Boolean, nullable=False, default=True)  # 账号状态
    last_login = db.Column(db.DateTime, nullable=True)  # 最后登录时间
    login_count = db.Column(db.Integer, default=0)  # 登录次数
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.role}', dept_id={self.department_id})"


# 登录日志模型
class LoginLog(db.Model):
    __tablename__ = 'login_log'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    username = db.Column(db.String(20), nullable=True)
    login_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    logout_time = db.Column(db.DateTime, nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    login_type = db.Column(db.String(20), default='login')  # login/logout
    
    user = db.relationship('User', backref='login_logs')


# 操作日志模型
class OperationLog(db.Model):
    __tablename__ = 'operation_log'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    username = db.Column(db.String(20), nullable=True)
    operation_type = db.Column(db.String(50), nullable=False)  # add/edit/delete/view/export/import
    module = db.Column(db.String(50), nullable=True)  # 模块名称
    description = db.Column(db.Text, nullable=True)  # 操作描述
    ip_address = db.Column(db.String(50), nullable=True)
    request_url = db.Column(db.String(255), nullable=True)
    request_method = db.Column(db.String(10), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    user = db.relationship('User', backref='operation_logs')

# 计算机资产模型（使用英文列名）
class ComputerInfo(db.Model):
    __tablename__ = 'computer_info'  # 指定表名
    
    id = db.Column(db.Integer, primary_key=True)
    computer_name = db.Column(db.String(42), nullable=True)  # 电脑名称
    employee_id = db.Column(db.String(50), nullable=True)  # 工号
    dept_code = db.Column(db.String(50), nullable=True)  # 部门代码
    dept_level2 = db.Column(db.String(50), nullable=True)  # 二级部门
    emp_name = db.Column(db.String(50), nullable=True)  # 员工姓名
    asset_id = db.Column(db.Integer, nullable=True)  # 资产ID
    network_address = db.Column(db.String(255), nullable=True)  # 网络地址
    ip_mac = db.Column(db.String(255), nullable=True)  # IP/MAC
    operating_system = db.Column(db.String(255), nullable=True)  # 操作系统
    last_login_user = db.Column(db.String(255), nullable=True)  # 最后登录用户
    
    def __repr__(self):
        return f"ComputerInfo('{self.computer_name}', '{self.asset_id}')"

# 工控机资产模型
class IndustrialComputer(db.Model):
    __tablename__ = 'industrial_computer'
    
    id = db.Column(db.Integer, primary_key=True)
    seq_no = db.Column(db.String(20), nullable=True)
    zone = db.Column(db.String(50), nullable=True)
    bu_dept = db.Column(db.String(50), nullable=True)
    factory = db.Column(db.String(50), nullable=True)
    building = db.Column(db.String(50), nullable=True)
    floor = db.Column(db.String(20), nullable=True)
    device_name = db.Column(db.String(100), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    device_vendor = db.Column(db.String(100), nullable=True)
    operating_system = db.Column(db.String(100), nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    mac_address = db.Column(db.String(50), nullable=True)
    all_mac = db.Column(db.String(100), nullable=True)
    third_party_antivirus = db.Column(db.String(10), nullable=True)
    antivirus_brand = db.Column(db.String(50), nullable=True)
    iep_installed = db.Column(db.String(10), nullable=True)
    whitelist_scan = db.Column(db.String(10), nullable=True)
    virus_scan = db.Column(db.String(10), nullable=True)
    remark = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f"IndustrialComputer('{self.device_name}', '{self.ip_address}')"

# 人员信息模型
class Personnel(db.Model):
    __tablename__ = 'employees_info'  # 指定表名
    
    id = db.Column(db.Integer, primary_key=True)
    # 部门信息
    company_dept = db.Column(db.String(21), nullable=True)
    factory_dept = db.Column(db.String(15), nullable=True)
    dept_code = db.Column(db.String(12), nullable=True)
    dept_full_name = db.Column(db.String(78), nullable=True)
    business_unit = db.Column(db.String(34), nullable=True)
    first_level_dept_abbr = db.Column(db.String(15), nullable=True)
    org_category = db.Column(db.String(7), nullable=True)
    job_family = db.Column(db.String(3), nullable=True)
    dept_level1 = db.Column(db.String(9), nullable=True)
    dept_level2 = db.Column(db.String(15), nullable=True)
    dept_level3 = db.Column(db.String(15), nullable=True)
    dept_level4 = db.Column(db.String(18), nullable=True)
    leaf_dept = db.Column(db.String(18), nullable=True)
    region_org = db.Column(db.String(9), nullable=True)
    work_location = db.Column(db.String(15), nullable=True)
    
    # 基本信息
    emp_id = db.Column(db.String(7), nullable=True)
    emp_name = db.Column(db.String(24), nullable=True)
    emp_status = db.Column(db.String(3), nullable=True)
    emp_gender = db.Column(db.String(1), nullable=True)
    emp_type = db.Column(db.String(9), nullable=True)
    group_hire_date = db.Column(db.String(15), nullable=True)
    hire_date = db.Column(db.String(15), nullable=True)
    is_probation = db.Column(db.String(1), nullable=True)
    probation_end_date = db.Column(db.String(15), nullable=True)
    regular_date = db.Column(db.String(15), nullable=True)
    
    # 职位信息
    position = db.Column(db.String(30), nullable=True)
    position_category = db.Column(db.String(3), nullable=True)
    position_grade = db.Column(db.String(6), nullable=True)
    job_type = db.Column(db.String(6), nullable=True)
    job_category = db.Column(db.String(16), nullable=True)
    job_sequence = db.Column(db.String(9), nullable=True)
    job_title = db.Column(db.String(10), nullable=True)
    acting_appointment = db.Column(db.String(6), nullable=True)
    project_job = db.Column(db.String(7), nullable=True)
    job_rank = db.Column(db.String(4), nullable=True)
    daily_salary_grade = db.Column(db.String(6), nullable=True)
    qualification_grade = db.Column(db.String(4), nullable=True)
    professional_grade = db.Column(db.String(4), nullable=True)
    job_level = db.Column(db.String(4), nullable=True)
    project_job_level = db.Column(db.String(4), nullable=True)
    talent_tag = db.Column(db.String(34), nullable=True)
    is_mentor = db.Column(db.String(1), nullable=True)
    
    # 汇报关系
    report_superior_id = db.Column(db.String(9), nullable=True)
    report_superior = db.Column(db.String(6), nullable=True)
    dept_head_id = db.Column(db.String(9), nullable=True)
    dept_head = db.Column(db.String(4), nullable=True)
    
    # 个人信息
    nationality = db.Column(db.String(6), nullable=True)
    birthplace = db.Column(db.String(12), nullable=True)
    ethnicity = db.Column(db.String(4), nullable=True)
    marital_status = db.Column(db.String(4), nullable=True)
    political_status = db.Column(db.String(9), nullable=True)
    
    # 教育信息
    highest_education_type = db.Column(db.String(6), nullable=True)
    highest_education_mode = db.Column(db.String(6), nullable=True)
    highest_education = db.Column(db.String(6), nullable=True)
    school = db.Column(db.String(28), nullable=True)
    major = db.Column(db.String(24), nullable=True)
    education_start_date = db.Column(db.String(15), nullable=True)
    education_end_date = db.Column(db.String(15), nullable=True)
    first_education = db.Column(db.String(6), nullable=True)
    second_education = db.Column(db.String(6), nullable=True)
    
    # 身份信息
    birth_date = db.Column(db.String(15), nullable=True)
    age = db.Column(db.String(3), nullable=True)
    id_type = db.Column(db.String(7), nullable=True)
    id_number = db.Column(db.String(27), nullable=True)
    id_address = db.Column(db.String(60), nullable=True)
    id_expiry = db.Column(db.String(28), nullable=True)
    
    # 合同信息
    legal_entity = db.Column(db.String(21), nullable=True)
    contract_entity = db.Column(db.String(28), nullable=True)
    contract_type = db.Column(db.String(6), nullable=True)
    contract_start_date = db.Column(db.String(15), nullable=True)
    contract_end_date = db.Column(db.String(28), nullable=True)
    labor_company = db.Column(db.String(4), nullable=True)
    
    # 联系信息
    current_residence = db.Column(db.String(70), nullable=True)
    registered_residence = db.Column(db.String(57), nullable=True)
    phone_number = db.Column(db.String(19), nullable=True)
    emergency_contact_name = db.Column(db.String(19), nullable=True)
    emergency_contact_phone = db.Column(db.String(19), nullable=True)
    
    # 财务信息
    bank_name = db.Column(db.String(13), nullable=True)
    bank_branch = db.Column(db.String(81), nullable=True)
    bank_account = db.Column(db.String(28), nullable=True)
    financial_code = db.Column(db.String(21), nullable=True)
    
    # 其他信息
    union_member = db.Column(db.String(1), nullable=True)
    is_veteran = db.Column(db.String(1), nullable=True)
    initial_social_insurance_unit = db.Column(db.String(4), nullable=True)
    has_fuel_card = db.Column(db.String(1), nullable=True)
    
    # 离职信息
    resignation_date = db.Column(db.String(15), nullable=True)
    last_pay_date = db.Column(db.String(15), nullable=True)
    resignation_type = db.Column(db.String(9), nullable=True)
    resignation_reason = db.Column(db.String(9), nullable=True)
    is_blacklisted = db.Column(db.String(1), nullable=True)
    resignation_reason_detail = db.Column(db.String(139), nullable=True)
    resignation_interview = db.Column(db.String(145), nullable=True)
    
    def __repr__(self):
        return f"Personnel('{self.emp_name}', '{self.emp_id}', '{self.dept_full_name}')"

# 权限矩阵模型
class PermissionMatrix(db.Model):
    __tablename__ = 'permission_matrix'
    
    id = db.Column(db.Integer, primary_key=True)
    dept_id = db.Column(db.String(20), nullable=True)
    dept_name = db.Column(db.String(100), nullable=True)
    permission_level = db.Column(db.String(20), nullable=True)
    description = db.Column(db.Text, nullable=True)
    permission_code = db.Column(db.String(50), nullable=True)
    permission_type = db.Column(db.String(20), default='view')
    resource_type = db.Column(db.String(50), nullable=True)
    resource_id = db.Column(db.String(100), nullable=True)
    action_list = db.Column(db.String(200), default='view')
    condition_expr = db.Column(db.Text, nullable=True)
    status = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, nullable=True)

# 系统角色模型
class SysRole(db.Model):
    __tablename__ = 'sys_role'
    
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), nullable=False)
    role_code = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.Integer, default=1)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, nullable=True)

# 系统功能模块模型
class SysModule(db.Model):
    __tablename__ = 'sys_module'
    
    id = db.Column(db.Integer, primary_key=True)
    module_name = db.Column(db.String(50), nullable=False)
    module_code = db.Column(db.String(50), nullable=False, unique=True)
    parent_id = db.Column(db.Integer, default=0)
    module_type = db.Column(db.String(20), default='menu')
    route_path = db.Column(db.String(200), nullable=True)
    icon = db.Column(db.String(50), nullable=True)
    sort_order = db.Column(db.Integer, default=0)
    status = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

# 系统权限配置模型
class SysPermission(db.Model):
    __tablename__ = 'sys_permission'
    
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('sys_role.id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('sys_module.id'), nullable=False)
    can_view = db.Column(db.Integer, default=0)
    can_add = db.Column(db.Integer, default=0)
    can_edit = db.Column(db.Integer, default=0)
    can_delete = db.Column(db.Integer, default=0)
    can_export = db.Column(db.Integer, default=0)
    can_import = db.Column(db.Integer, default=0)
    can_audit = db.Column(db.Integer, default=0)
    can_approve = db.Column(db.Integer, default=0)
    data_scope = db.Column(db.String(20), default='self')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    role = db.relationship('SysRole', backref='permissions')
    module = db.relationship('SysModule', backref='permissions')

# 用户角色关联模型
class SysUserRole(db.Model):
    __tablename__ = 'sys_user_role'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('sys_role.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    role = db.relationship('SysRole', backref='user_roles')

# 数据权限模型
class SysDataPermission(db.Model):
    __tablename__ = 'sys_data_permission'
    
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('sys_role.id'), nullable=False)
    dept_id = db.Column(db.String(50), nullable=False)
    permission_type = db.Column(db.String(20), default='view')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    role = db.relationship('SysRole', backref='data_permissions')

# 涉密人员模型
class ClassifiedPersonnel(db.Model):
    __tablename__ = 'classified_personnel'
    
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.String(20), nullable=True)
    emp_name = db.Column(db.String(50), nullable=True)
    dept_id = db.Column(db.String(20), nullable=True)
    dept_name = db.Column(db.String(100), nullable=True)
    agreement_type = db.Column(db.String(50), nullable=True)
    signing_date = db.Column(db.String(20), nullable=True)
    expiration_date = db.Column(db.String(20), nullable=True)
    status = db.Column(db.String(20), nullable=True)
    remark = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# 涉密存储介质模型
class ClassifiedMedia(db.Model):
    __tablename__ = 'classified_media'
    
    id = db.Column(db.Integer, primary_key=True)
    media_number = db.Column(db.String(50), nullable=True)
    media_type = db.Column(db.String(50), nullable=True)
    capacity = db.Column(db.String(20), nullable=True)
    dept_id = db.Column(db.String(20), nullable=True)
    dept_name = db.Column(db.String(100), nullable=True)
    responsible_name = db.Column(db.String(50), nullable=True)
    responsible_emp_id = db.Column(db.String(20), nullable=True)
    purpose = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), nullable=True)
    remark = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# 信息安全区域模型
class SecurityZone(db.Model):
    __tablename__ = 'security_zone'
    
    id = db.Column(db.Integer, primary_key=True)
    zone_code = db.Column(db.String(20), nullable=True)
    zone_name = db.Column(db.String(100), nullable=True)
    zone_level = db.Column(db.String(20), nullable=True)
    dept_id = db.Column(db.String(20), nullable=True)
    dept_name = db.Column(db.String(100), nullable=True)
    responsible_name = db.Column(db.String(50), nullable=True)
    responsible_emp_id = db.Column(db.String(20), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), nullable=True)
    remark = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# 电子涉密文件模型
class ElectronicDocument(db.Model):
    __tablename__ = 'electronic_document'
    
    id = db.Column(db.Integer, primary_key=True)
    doc_number = db.Column(db.String(50), nullable=True)
    doc_title = db.Column(db.String(200), nullable=True)
    doc_level = db.Column(db.String(20), nullable=True)
    dept_id = db.Column(db.String(20), nullable=True)
    dept_name = db.Column(db.String(100), nullable=True)
    responsible_name = db.Column(db.String(50), nullable=True)
    responsible_emp_id = db.Column(db.String(20), nullable=True)
    file_path = db.Column(db.String(200), nullable=True)
    doc_status = db.Column(db.String(20), nullable=True)
    remark = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# 纸质涉密文件模型
class PaperDocument(db.Model):
    __tablename__ = 'paper_document'
    
    id = db.Column(db.Integer, primary_key=True)
    doc_number = db.Column(db.String(50), nullable=True)
    doc_title = db.Column(db.String(200), nullable=True)
    doc_level = db.Column(db.String(20), nullable=True)
    dept_id = db.Column(db.String(20), nullable=True)
    dept_name = db.Column(db.String(100), nullable=True)
    responsible_name = db.Column(db.String(50), nullable=True)
    responsible_emp_id = db.Column(db.String(20), nullable=True)
    quantity = db.Column(db.Integer, nullable=True)
    storage_location = db.Column(db.String(100), nullable=True)
    doc_status = db.Column(db.String(20), nullable=True)
    remark = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

# 稽查任务模型
class AuditTask(db.Model):
    __tablename__ = 'audit_task'
    
    id = db.Column(db.Integer, primary_key=True)
    task_no = db.Column(db.String(50), nullable=False, unique=True)  # 任务编号
    task_title = db.Column(db.String(200), nullable=False)  # 任务标题
    task_type = db.Column(db.String(50), nullable=False)  # 任务类型：安全稽查/资产稽查/权限稽查/合规稽查
    task_content = db.Column(db.Text, nullable=False)  # 任务内容
    task_requirement = db.Column(db.Text, nullable=True)  # 任务要求
    priority = db.Column(db.String(20), default='normal')  # 优先级：urgent/high/normal/low
    assignee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 被分配人
    assigner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 分配人
    dept_id = db.Column(db.Integer, nullable=True)  # 部门ID
    dept_name = db.Column(db.String(100), nullable=True)  # 部门名称
    deadline = db.Column(db.DateTime, nullable=True)  # 截止时间
    status = db.Column(db.String(20), default='pending')  # 状态：pending/in_progress/completed/closed
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)  # 完成时间
    
    assignee = db.relationship('User', foreign_keys=[assignee_id], backref='assigned_tasks')
    assigner = db.relationship('User', foreign_keys=[assigner_id], backref='created_tasks')

# 稽查任务反馈模型
class AuditTaskFeedback(db.Model):
    __tablename__ = 'audit_task_feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('audit_task.id'), nullable=False)
    feedback_content = db.Column(db.Text, nullable=False)  # 反馈内容
    feedback_type = db.Column(db.String(20), default='report')  # 类型：report/supplement/reject
    attachment_path = db.Column(db.String(500), nullable=True)  # 附件路径
    feedback_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    task = db.relationship('AuditTask', backref='feedbacks')
    user = db.relationship('User', backref='audit_feedbacks')

# 稽查记录模型
class AuditRecord(db.Model):
    __tablename__ = 'audit_record'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('audit_task.id'), nullable=True)  # 关联任务（可选）
    audit_type = db.Column(db.String(50), nullable=False)  # 稽查类型
    audit_scope = db.Column(db.String(100), nullable=True)  # 稽查范围
    audit_content = db.Column(db.Text, nullable=False)  # 稽查内容
    audit_result = db.Column(db.Text, nullable=True)  # 稽查结果
    issue_found = db.Column(db.Text, nullable=True)  # 发现的问题
    suggestion = db.Column(db.Text, nullable=True)  # 整改建议
    audit_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    audit_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), default='draft')  # 状态：draft/submitted/reviewed
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    auditor = db.relationship('User', backref='audit_records')

# 人员系统权限矩阵模型（按人员-系统维度）
class PersonSystemPermissionMatrix(db.Model):
    __tablename__ = 'person_system_permission_matrix'
    
    id = db.Column(db.Integer, primary_key=True)
    emp_id = db.Column(db.String(20), nullable=True)
    emp_name = db.Column(db.String(50), nullable=True)
    dept_id = db.Column(db.String(20), nullable=True)
    dept_name = db.Column(db.String(100), nullable=True)
    system_name = db.Column(db.String(100), nullable=False)
    can_view = db.Column(db.Integer, default=0)
    can_add = db.Column(db.Integer, default=0)
    can_edit = db.Column(db.Integer, default=0)
    can_delete = db.Column(db.Integer, default=0)
    can_export = db.Column(db.Integer, default=0)
    can_import = db.Column(db.Integer, default=0)
    can_approve = db.Column(db.Integer, default=0)
    can_config = db.Column(db.Integer, default=0)
    permission_level = db.Column(db.String(20), default='basic')
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
