from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, FloatField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('用户名', 
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('邮箱', 
                        validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    confirm_password = PasswordField('确认密码', 
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('注册')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('该用户名已被使用，请选择其他用户名。')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('该邮箱已被注册，请选择其他邮箱。')

class LoginForm(FlaskForm):
    email = StringField('邮箱', 
                        validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember = BooleanField('记住我')
    submit = SubmitField('登录')

# 资产表单
class TangibleAssetForm(FlaskForm):
    name = StringField('名称', validators=[DataRequired()])
    category = SelectField('类别', validators=[DataRequired()], choices=[
        ('办公电脑', '办公电脑'),
        ('工控机', '工控机'),
        ('工作站', '工作站')
    ])
    description = StringField('描述')
    value = StringField('价值', validators=[DataRequired()])
    purchase_date = StringField('购买日期', validators=[DataRequired()])
    location = StringField('位置', validators=[DataRequired()])
    status = StringField('状态', validators=[DataRequired()])
    assigned_to = StringField('分配给')
    submit = SubmitField('提交')

class IntangibleAssetForm(FlaskForm):
    name = StringField('名称', validators=[DataRequired()])
    category = StringField('类别', validators=[DataRequired()])
    description = StringField('描述')
    value = StringField('价值')
    registration_date = StringField('注册日期', validators=[DataRequired()])
    expiration_date = StringField('到期日期')
    status = StringField('状态', validators=[DataRequired()])
    submit = SubmitField('提交')

# 部门表单
class DepartmentForm(FlaskForm):
    name = StringField('部门名称', validators=[DataRequired()])
    code = StringField('部门代码', validators=[DataRequired()])
    description = StringField('部门描述')
    parent_id = SelectField('上级部门', choices=[], coerce=int)
    submit = SubmitField('提交')

# 用户部门表单
class UserDepartmentForm(FlaskForm):
    department_id = SelectField('部门', choices=[], coerce=int)
    department_access = BooleanField('只查看本部门数据')
    submit = SubmitField('保存')

# 人员表单
class PersonnelForm(FlaskForm):
    # 部门信息
    company_dept = StringField('公司部门')
    factory_dept = StringField('工厂部门')
    dept_code = StringField('部门代码')
    dept_full_name = StringField('部门全称')
    business_unit = StringField('业务单元')
    first_level_dept_abbr = StringField('一级部门简称')
    org_category = StringField('组织类别')
    job_family = StringField('职位族')
    dept_level1 = StringField('一级部门')
    dept_level2 = StringField('二级部门')
    dept_level3 = StringField('三级部门')
    dept_level4 = StringField('四级部门')
    leaf_dept = StringField('末级部门')
    region_org = StringField('区域组织')
    work_location = StringField('工作地点')
    
    # 基本信息
    emp_id = StringField('员工ID')
    emp_name = StringField('员工姓名')
    emp_status = StringField('员工状态')
    emp_gender = StringField('性别')
    emp_type = StringField('员工类型')
    group_hire_date = StringField('集团入职日期')
    hire_date = StringField('入职日期')
    is_probation = StringField('是否试用期')
    probation_end_date = StringField('试用期结束日期')
    regular_date = StringField('转正日期')
    
    # 职位信息
    position = StringField('职位')
    position_category = StringField('职位类别')
    position_grade = StringField('职位等级')
    job_type = StringField('岗位类型')
    job_category = StringField('岗位类别')
    job_sequence = StringField('岗位序列')
    job_title = StringField('岗位名称')
    acting_appointment = StringField('代职情况')
    project_job = StringField('项目岗位')
    job_rank = StringField('职级')
    daily_salary_grade = StringField('日薪等级')
    qualification_grade = StringField('资格等级')
    professional_grade = StringField('专业等级')
    job_level = StringField('岗位级别')
    project_job_level = StringField('项目岗位级别')
    talent_tag = StringField('人才标签')
    is_mentor = StringField('是否导师')
    
    # 汇报关系
    report_superior_id = StringField('汇报上级ID')
    report_superior = StringField('汇报上级')
    dept_head_id = StringField('部门负责人ID')
    dept_head = StringField('部门负责人')
    
    # 个人信息
    nationality = StringField('国籍')
    birthplace = StringField('出生地')
    ethnicity = StringField('民族')
    marital_status = StringField('婚姻状况')
    political_status = StringField('政治面貌')
    
    # 教育信息
    highest_education_type = StringField('最高学历类型')
    highest_education_mode = StringField('最高学历方式')
    highest_education = StringField('最高学历')
    school = StringField('学校')
    major = StringField('专业')
    education_start_date = StringField('教育开始日期')
    education_end_date = StringField('教育结束日期')
    first_education = StringField('第一学历')
    second_education = StringField('第二学历')
    
    # 身份信息
    birth_date = StringField('出生日期')
    age = StringField('年龄')
    id_type = StringField('证件类型')
    id_number = StringField('证件号码')
    id_address = StringField('证件地址')
    id_expiry = StringField('证件有效期')
    
    # 合同信息
    legal_entity = StringField('法人实体')
    contract_entity = StringField('合同实体')
    contract_type = StringField('合同类型')
    contract_start_date = StringField('合同开始日期')
    contract_end_date = StringField('合同结束日期')
    labor_company = StringField('劳务公司')
    
    # 联系信息
    current_residence = StringField('现居住地址')
    registered_residence = StringField('户籍地址')
    phone_number = StringField('电话号码')
    emergency_contact_name = StringField('紧急联系人姓名')
    emergency_contact_phone = StringField('紧急联系人电话')
    
    # 财务信息
    bank_name = StringField('银行名称')
    bank_branch = StringField('银行分行')
    bank_account = StringField('银行账号')
    financial_code = StringField('财务编码')
    
    # 其他信息
    union_member = StringField('是否工会会员')
    is_veteran = StringField('是否退役军人')
    initial_social_insurance_unit = StringField('初始社保单位')
    has_fuel_card = StringField('是否有油卡')
    
    # 离职信息
    resignation_date = StringField('离职日期')
    last_pay_date = StringField('最后薪资日期')
    resignation_type = StringField('离职类型')
    resignation_reason = StringField('离职原因')
    is_blacklisted = StringField('是否黑名单')
    resignation_reason_detail = StringField('离职原因详情')
    resignation_interview = StringField('离职访谈记录')
    
    submit = SubmitField('提交')
