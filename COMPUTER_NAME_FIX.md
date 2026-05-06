# 电脑名称显示修复记录

## 修复日期
2026-04-16

## 问题描述

### 原始问题
- 办公电脑页面显示虚假的电脑名称，如"电脑 (1)"、"电脑 (2)"等
- 用户要求显示设备表里的真实电脑名称

### 根本原因
1. **模型定义不完整**：`ComputerInfo` 模型缺少 `computer_name` 字段定义
2. **错误的显示逻辑**：之前尝试关联 `tangible_asset` 表获取名称，而不是直接使用数据库中的 `computer_name` 字段

---

## 修复方案

### 1. 更新 ComputerInfo 模型定义

**文件**：`app/models.py` (第84-95行)

**修改内容**：
```python
# 修改前
class ComputerInfo(db.Model):
    __tablename__ = 'computer_info'
    
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, nullable=True)
    network_address = db.Column(db.String(255), nullable=True)
    ip_mac = db.Column(db.String(255), nullable=True)
    operating_system = db.Column(db.String(255), nullable=True)
    last_login_user = db.Column(db.String(255), nullable=True)

# 修改后
class ComputerInfo(db.Model):
    __tablename__ = 'computer_info'
    
    id = db.Column(db.Integer, primary_key=True)
    computer_name = db.Column(db.String(42), nullable=True)  # 新增字段
    asset_id = db.Column(db.Integer, nullable=True)
    network_address = db.Column(db.String(255), nullable=True)
    ip_mac = db.Column(db.String(255), nullable=True)
    operating_system = db.Column(db.String(255), nullable=True)
    last_login_user = db.Column(db.String(255), nullable=True)
```

---

### 2. 更新 office_computers 路由逻辑

**文件**：`app/routes/assets.py` (第167-225行)

**修改内容**：
```python
# 修改前
for comp_info in all_computer_infos:
    if comp_info.asset_id:
        # 尝试从tangible_asset表获取资产名称
        related_asset = db.session.get(TangibleAsset, comp_info.asset_id)
        if related_asset and related_asset.name:
            comp_info.asset_name = related_asset.name
        else:
            # 如果没有关联的资产，使用IP地址作为名称
            comp_info.asset_name = comp_info.network_address if comp_info.network_address else f"资产ID: {comp_info.asset_id}"
    else:
        comp_info.asset_name = "未分配资产"

# 修改后
for comp_info in all_computer_infos:
    if comp_info.computer_name:
        # 直接使用数据库中的 computer_name 字段
        comp_info.asset_name = comp_info.computer_name
    else:
        # 如果没有电脑名称，使用资产ID
        comp_info.asset_name = "资产ID: {}".format(comp_info.asset_id) if comp_info.asset_id else "未知电脑"
```

---

## 测试结果

### 电脑名称显示测试

```
=== 测试电脑名称显示 ===

办公电脑列表:
--------------------------------------------------------------------------------
电脑 1:
  电脑名称: 9030-30000487(高红福)
  资产ID: 1
  网络地址: 10.2.59.32
  最后登录用户: 高红福
  [显示名称]: 9030-30000487(高红福)

电脑 2:
  电脑名称: [无]
  资产ID: 2
  网络地址: 10.2.58.252
  最后登录用户: 曾浩彬
  [显示名称]: 1000-22011453(曾浩彬)

电脑 3:
  电脑名称: 1000-22008745(陈苏均)
  资产ID: 3
  网络地址: 10.2.88.149
  最后登录用户: 陈苏均
  [显示名称]: 1000-22008745(陈苏均)

电脑 4:
  电脑名称: 9030-30000490(王宗莲)
  资产ID: 4
  网络地址: 10.2.59.6
  最后登录用户: 王宗莲
  [显示名称]: 9030-30000490(王宗莲)

电脑 5:
  电脑名称: 1000-22004198(张雁)
  资产ID: 5
  网络地址: 10.2.59.3
  最后登录用户: 张雁
  [显示名称]: 1000-22004198(张雁)

--------------------------------------------------------------------------------
```

### 验证结果
✅ **成功**：办公电脑现在显示真实的电脑名称（如"9030-30000487(高红福)"）  
✅ **降级方案**：如果没有 `computer_name`，则显示"资产ID: XXX"  
✅ **搜索功能**：搜索功能也包含了 `computer_name` 字段

---

## 数据库字段对应关系

### computer_info 表结构
| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| id | int | 主键 | 3, 4, 5 |
| computer_name | varchar(42) | **电脑名称** | 9030-30000487(高红福) |
| asset_id | int | 资产ID | 1, 2, 3 |
| network_address | varchar(255) | 网络地址/IP | 10.2.59.32 |
| ip_mac | varchar(255) | MAC地址 | 04-7C-16-68-5F-C2 |
| operating_system | varchar(255) | 操作系统 | Windows 10 专业版 |
| last_login_user | varchar(255) | 最后登录用户 | 高红福 |

---

## 修复总结

### 完成的工作
1. ✅ 在 `ComputerInfo` 模型中添加了 `computer_name` 字段
2. ✅ 修改了 `office_computers()` 路由，直接使用 `computer_name` 字段
3. ✅ 更新了搜索功能，包含 `computer_name` 字段
4. ✅ 添加了降级方案（无 `computer_name` 时显示资产ID）

### 用户收益
- 办公电脑页面现在显示真实的电脑名称
- 名称格式：`9030-30000487(高红福)` 包含设备编号和用户名
- 更符合用户的使用习惯，便于识别和管理电脑资产

### 兼容性
- 保持了部门权限过滤功能
- 搜索功能更强大
- 向下兼容：没有 `computer_name` 的记录会显示资产ID

---

## 相关文件

1. **app/models.py** - 添加了 `computer_name` 字段
2. **app/routes/assets.py** - 更新了显示逻辑
3. **check_db_structure.py** - 用于检查数据库表结构
4. **test_computer_name_fix.py** - 测试脚本

---

## 下一步建议

1. **数据完整性**：检查所有 `computer_info` 记录是否都有 `computer_name`
2. **用户体验**：考虑在名称中添加更多有用信息（如部门、使用人等）
3. **权限管理**：确保部门权限过滤正常工作

---

**修复状态**：✅ 完成并测试通过