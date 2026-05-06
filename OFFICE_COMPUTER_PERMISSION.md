# 办公电脑数据隔离实现

## 修改日期
2026-04-16

## 实现目标
实现基于部门的办公电脑数据隔离，确保每个用户只能查看和管理自己配置的部门的数据。

---

## 修改内容

### 1. 修改办公电脑路由逻辑

**文件**: `app/routes/assets.py`

**主要修改**:
- 简化了部门权限过滤逻辑
- 直接使用 `computer_info.dept_code` 进行过滤
- 不再通过 `tangible_asset` 和 `personnel` 表的复杂关联

**新逻辑**:
```python
# 根据部门权限过滤 - 使用 dept_code 直接过滤
if current_user.department_access:
    from app.models import Department
    # 获取用户配置的部门
    user_department = Department.query.get(current_user.department_id)
    if user_department:
        # 使用部门的 dept_code 直接过滤 computer_info 表
        query = query.filter(ComputerInfo.dept_code == user_department.code)
```

**权限控制逻辑**:
- **管理员**: 可以查看所有办公电脑数据
- **部门管理员**: 只能查看配置部门（`department_id`）对应的 `dept_code` 的办公电脑
- **普通用户**: 如果配置了 `department_access`，也只能查看配置部门的数据

---

### 2. 更新办公电脑页面模板

**文件**: `app/templates/assets/office_computers.html`

**主要修改**:

1. **添加部门信息提示**
   ```html
   {% if current_user.department_access and current_user.department %}
   <div class="alert alert-info">
       <i class="bi bi-info-circle"></i> 您正在查看【{{ current_user.department.name }}】部门的数据
   </div>
   {% endif %}
   ```

2. **更新表格列**
   - 移除：资产ID、最后登录用户
   - 新增：部门代码、二级部门、员工姓名

3. **隐藏添加按钮**
   - 只有管理员可以看到"添加新办公电脑"按钮
   - 普通用户和部门管理员看不到此按钮

4. **增强搜索功能**
   - 搜索现在包含部门代码、二级部门、员工姓名字段

**新表格列**:
```
电脑名称 | 部门代码 | 二级部门 | 员工姓名 | 网络地址 | IP/MAC | 操作系统
```

---

## 数据流程

### 1. 用户登录系统
```
用户登录 → 读取用户配置 → 获取 department_id
```

### 2. 用户访问办公电脑页面
```
用户访问 /office_computers 
  ↓
检查 department_permission_required 装饰器
  ↓
如果 department_access = True:
  ├─ 获取用户的 department_id
  ├─ 查询 Department 表获取部门信息
  ├─ 使用部门的 code (dept_code) 过滤 computer_info 表
  └─ 返回该部门的数据
  ↓
如果 department_access = False (仅管理员):
  ├─ 返回所有 computer_info 数据
```

### 3. 数据展示
```
查询结果 
  ↓
显示部门信息提示 (如果是部门用户)
  ↓
显示办公电脑表格
  ↓
包含: 电脑名称、部门代码、二级部门、员工姓名等
```

---

## 权限验证

### 测试场景

#### 场景1: 管理员查看所有数据
- 用户: admin@example.com
- 角色: admin
- 权限: `department_access = False`
- 预期: 可以查看所有 18,000 条办公电脑数据

#### 场景2: 部门管理员查看本部门数据
- 用户: tech_admin@example.com
- 角色: department_admin
- 配置: `department_id = 25` (对应 dept_code = "DP000027", 部门名 = "总裁办公室")
- 权限: `department_access = True`
- 预期: 只能查看 1,500 条办公电脑数据（属于"总裁办公室"部门的）

#### 场景3: 普通用户查看本部门数据
- 用户: user1@example.com
- 角色: user
- 配置: `department_id = 30` (对应 dept_code = "DP001547", 部门名 = "制造中心")
- 权限: `department_access = True`
- 预期: 只能查看 800 条办公电脑数据（属于"制造中心"部门的）

---

## 数据库关联

### computer_info 表
```sql
- dept_code: 部门代码 (关联到 Department 表的 code 字段)
- dept_level2: 二级部门名称
- emp_name: 员工姓名
```

### Department 表
```sql
- id: 部门ID
- code: 部门代码 (用于过滤 computer_info)
- name: 部门名称 (用于显示)
```

### User 表
```sql
- department_id: 关联的部门ID
- department_access: 是否启用部门访问限制
```

---

## 关键优势

### 1. **简单高效**
- 直接使用 `dept_code` 过滤，无需复杂关联查询
- 减少数据库查询次数

### 2. **清晰明确**
- 权限控制逻辑简单易懂
- 用户知道自己只能查看哪些数据

### 3. **安全可靠**
- 管理员可以查看所有数据
- 部门用户只能查看本部门数据
- 无法访问未授权的部门数据

### 4. **易于维护**
- 代码结构清晰
- 权限逻辑集中管理
- 便于后续扩展

---

## 注意事项

### 1. 部门配置
- 确保用户的 `department_id` 已正确配置
- 部门的 `code` 字段必须与 `computer_info.dept_code` 匹配

### 2. 数据质量
- 确保 `computer_info.dept_code` 已正确填充
- 如果 dept_code 为空，用户将看不到该记录

### 3. 管理员权限
- 管理员不受部门限制
- 管理员可以查看所有部门的数据

---

## 状态

✅ **已完成**
- [OK] 办公电脑路由实现部门数据隔离
- [OK] 办公电脑页面显示部门信息
- [OK] 搜索功能包含部门字段
- [OK] 添加按钮权限控制
- [OK] 部门信息提示

---

## 相关文件

1. **app/routes/assets.py** - 办公电脑路由逻辑
2. **app/templates/assets/office_computers.html** - 办公电脑页面模板
3. **app/models.py** - ComputerInfo 模型定义
4. **app/decorators.py** - 部门权限装饰器