-- 初始化数据库表结构
-- 创建基础表

-- 用户表
CREATE TABLE IF NOT EXISTS user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(20) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password VARCHAR(60) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    department_id INT,
    department_access BOOLEAN DEFAULT FALSE,
    emp_id VARCHAR(20),
    phone VARCHAR(20),
    real_name VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    last_login DATETIME,
    login_count INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 部门表
CREATE TABLE IF NOT EXISTS department (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    parent_id INT,
    level INT DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES department(id)
);

-- 登录日志表
CREATE TABLE IF NOT EXISTS login_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    username VARCHAR(20),
    login_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    logout_time DATETIME,
    ip_address VARCHAR(50),
    user_agent VARCHAR(255),
    login_type VARCHAR(20) DEFAULT 'login',
    FOREIGN KEY (user_id) REFERENCES user(id)
);

-- 操作日志表
CREATE TABLE IF NOT EXISTS operation_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    username VARCHAR(20),
    operation_type VARCHAR(50) NOT NULL,
    module VARCHAR(50),
    description TEXT,
    ip_address VARCHAR(50),
    request_url VARCHAR(255),
    request_method VARCHAR(10),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id)
);

-- 电脑信息表
CREATE TABLE IF NOT EXISTS computer_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    computer_name VARCHAR(42),
    employee_id VARCHAR(50),
    dept_code VARCHAR(50),
    dept_level2 VARCHAR(50),
    emp_name VARCHAR(50),
    asset_id INT,
    network_address VARCHAR(255),
    ip_mac VARCHAR(255),
    operating_system VARCHAR(255),
    last_login_user VARCHAR(255)
);

-- 工控机表
CREATE TABLE IF NOT EXISTS industrial_computer (
    id INT AUTO_INCREMENT PRIMARY KEY,
    seq_no VARCHAR(20),
    zone VARCHAR(50),
    bu_dept VARCHAR(50),
    factory VARCHAR(50),
    building VARCHAR(50),
    floor VARCHAR(20),
    device_name VARCHAR(100),
    location VARCHAR(100),
    device_vendor VARCHAR(100),
    operating_system VARCHAR(100),
    ip_address VARCHAR(50),
    mac_address VARCHAR(50),
    all_mac VARCHAR(100),
    third_party_antivirus VARCHAR(10),
    antivirus_brand VARCHAR(50),
    iep_installed VARCHAR(10),
    whitelist_scan VARCHAR(10),
    virus_scan VARCHAR(10),
    remark TEXT
);

-- 员工信息表
CREATE TABLE IF NOT EXISTS employees_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_dept VARCHAR(21),
    factory_dept VARCHAR(15),
    dept_code VARCHAR(12),
    dept_full_name VARCHAR(78),
    business_unit VARCHAR(34),
    first_level_dept_abbr VARCHAR(15),
    org_category VARCHAR(7),
    job_family VARCHAR(3),
    dept_level1 VARCHAR(9),
    dept_level2 VARCHAR(15),
    dept_level3 VARCHAR(15),
    dept_level4 VARCHAR(18),
    leaf_dept VARCHAR(18),
    region_org VARCHAR(9),
    work_location VARCHAR(15),
    emp_id VARCHAR(7),
    emp_name VARCHAR(24),
    emp_status VARCHAR(3),
    emp_gender VARCHAR(1),
    emp_type VARCHAR(9),
    group_hire_date VARCHAR(15),
    hire_date VARCHAR(15),
    is_probation VARCHAR(1),
    probation_end_date VARCHAR(15),
    regular_date VARCHAR(15),
    position VARCHAR(30),
    position_category VARCHAR(3),
    position_grade VARCHAR(6),
    job_type VARCHAR(6),
    job_category VARCHAR(16),
    job_sequence VARCHAR(9),
    job_title VARCHAR(10),
    acting_appointment VARCHAR(6),
    project_job VARCHAR(7),
    job_rank VARCHAR(4),
    daily_salary_grade VARCHAR(6),
    qualification_grade VARCHAR(4),
    professional_grade VARCHAR(4),
    job_level VARCHAR(4),
    project_job_level VARCHAR(4),
    talent_tag VARCHAR(34),
    is_mentor VARCHAR(1),
    report_superior_id VARCHAR(9),
    report_superior VARCHAR(6),
    dept_head_id VARCHAR(9),
    dept_head VARCHAR(4),
    nationality VARCHAR(6),
    birthplace VARCHAR(12),
    ethnicity VARCHAR(4),
    marital_status VARCHAR(4),
    political_status VARCHAR(9),
    highest_education_type VARCHAR(6),
    highest_education_mode VARCHAR(6),
    highest_education VARCHAR(6),
    school VARCHAR(28),
    major VARCHAR(24),
    education_start_date VARCHAR(15),
    education_end_date VARCHAR(15),
    first_education VARCHAR(6),
    second_education VARCHAR(6),
    birth_date VARCHAR(15),
    age VARCHAR(3),
    id_type VARCHAR(7),
    id_number VARCHAR(27),
    id_address VARCHAR(60),
    id_expiry VARCHAR(28),
    legal_entity VARCHAR(21),
    contract_entity VARCHAR(28),
    contract_type VARCHAR(6),
    contract_start_date VARCHAR(15),
    contract_end_date VARCHAR(28),
    labor_company VARCHAR(4),
    current_residence VARCHAR(70),
    registered_residence VARCHAR(57),
    phone_number VARCHAR(19),
    emergency_contact_name VARCHAR(19),
    emergency_contact_phone VARCHAR(19),
    bank_name VARCHAR(13),
    bank_branch VARCHAR(81),
    bank_account VARCHAR(28),
    financial_code VARCHAR(21),
    union_member VARCHAR(1),
    is_veteran VARCHAR(1),
    initial_social_insurance_unit VARCHAR(4),
    has_fuel_card VARCHAR(1),
    resignation_date VARCHAR(15),
    last_pay_date VARCHAR(15),
    resignation_type VARCHAR(9),
    resignation_reason VARCHAR(9),
    is_blacklisted VARCHAR(1),
    resignation_reason_detail VARCHAR(139),
    resignation_interview VARCHAR(145)
);

-- 创建默认管理员账号
INSERT INTO user (username, email, password, role, real_name, is_active) 
VALUES ('admin', 'admin@example.com', 'pbkdf2:sha256:600000$admin$e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', 'admin', '系统管理员', TRUE)
ON DUPLICATE KEY UPDATE username=username;

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_emp_name ON employees_info(emp_name);
CREATE INDEX IF NOT EXISTS idx_emp_id ON employees_info(emp_id);
CREATE INDEX IF NOT EXISTS idx_emp_status ON employees_info(emp_status);
CREATE INDEX IF NOT EXISTS idx_dept_full_name ON employees_info(dept_full_name);
CREATE INDEX IF NOT EXISTS idx_computer_emp_name ON computer_info(emp_name);
CREATE INDEX IF NOT EXISTS idx_computer_emp_id ON computer_info(employee_id);