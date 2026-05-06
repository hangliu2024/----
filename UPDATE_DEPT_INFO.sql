-- 将 computer_info 表的工号与 employee_info 表关联，提取部门信息
-- 创建时间: 2026-04-16

-- 1. 添加部门信息字段（如果还没有）
ALTER TABLE computer_info 
ADD COLUMN IF NOT EXISTS dept_code VARCHAR(50) NULL COMMENT '部门代码';

ALTER TABLE computer_info 
ADD COLUMN IF NOT EXISTS dept_level2 VARCHAR(50) NULL COMMENT '二级部门';

ALTER TABLE computer_info 
ADD COLUMN IF NOT EXISTS emp_name VARCHAR(50) NULL COMMENT '员工姓名';

-- 2. 更新部门信息（使用 JOIN）
UPDATE computer_info c
INNER JOIN employees_info e ON c.employee_id = e.emp_id
SET 
    c.dept_code = e.dept_code,
    c.dept_level2 = e.dept_level2,
    c.emp_name = e.emp_name;

-- 3. 验证更新结果
SELECT 
    COUNT(*) as 总记录数,
    SUM(CASE WHEN dept_code IS NOT NULL THEN 1 ELSE 0 END) as 已更新,
    SUM(CASE WHEN dept_code IS NULL AND employee_id IS NOT NULL THEN 1 ELSE 0 END) as 未匹配
FROM computer_info
WHERE employee_id IS NOT NULL;

-- 4. 查看更新后的样例数据
SELECT 
    employee_id as 工号,
    computer_name as 电脑名称,
    dept_code as 部门代码,
    dept_level2 as 二级部门,
    emp_name as 姓名
FROM computer_info
WHERE dept_code IS NOT NULL
LIMIT 20;
