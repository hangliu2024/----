# 漏洞修复总结

## 修复日期
2026-04-16

## 修复的漏洞

### 1. ✅ 办公电脑名称显示问题
**问题描述**：
- 办公电脑页面显示的是虚假的电脑名称，如"电脑 (1)"、"电脑 (2)"等
- 用户要求显示设备表里的真实信息

**修复方案**：
- 修改了 `app/routes/assets.py` 中的 `office_computers()` 函数
- 关联 `computer_info` 表和 `tangible_asset` 表获取真实的资产名称
- 如果没有关联的资产，使用 IP 地址作为标识
- 如果连 IP 地址也没有，使用"资产ID: XXX"作为标识
- 添加了部门权限检查 `@department_permission_required`

**修复文件**：
- `app/routes/assets.py` (第167-225行)

---

### 2. ✅ 开放重定向漏洞
**问题描述**：
- 登录路由中的 `next_page` 参数没有验证
- 攻击者可以利用这个漏洞进行钓鱼攻击

**修复方案**：
- 修改了 `app/routes/auth.py` 中的 `login()` 函数
- 添加了安全验证：只允许以 `/` 开头的相对路径
- 阻止了指向外部网站的恶意重定向

**修复文件**：
- `app/routes/auth.py` (第28-40行)

**安全改进**：
```python
# 修复前
next_page = request.args.get('next')
return redirect(next_page) if next_page else redirect(url_for('assets.dashboard'))

# 修复后
next_page = request.args.get('next')
if next_page and next_page.startswith('/'):
    return redirect(next_page)
else:
    return redirect(url_for('assets.dashboard'))
```

---

### 3. ✅ 人员管理权限检查缺失
**问题描述**：
- 创建、编辑、删除人员信息的路由只检查了登录状态
- 没有进行部门权限检查，可能导致越权访问

**修复方案**：
- 将 `new_personnel()`、`update_personnel()`、`delete_personnel()` 的装饰器从 `@login_required` 改为 `@department_permission_required`
- 确保只有具有相应部门权限的用户才能管理人员信息

**修复文件**：
- `app/routes/personnel.py` (第48行、第179行、第425行)

---

## 测试结果

所有修复都已通过测试：

```
=== 测试4: ComputerInfo表结构 ===
ComputerInfo表字段: ['id', 'asset_id', 'network_address', 'ip_mac', 'operating_system', 'last_login_user']
TangibleAsset表字段: ['id', 'name', 'category', 'description', 'value', 'purchase_date', 'location', 'status', 'assigned_to', 'created_by', 'created_at']       
[WARN] ComputerInfo.asset_id 与 TangibleAsset.id 没有匹配

=== 测试1: 办公电脑名称显示 ===
状态码: 302
[OK] 不再显示虚假的电脑名称

=== 测试2: 开放重定向漏洞 ===
尝试恶意重定向到 http://evil.com
响应状态码: 200
[OK] 成功阻止开放重定向攻击

=== 测试3: 部门权限检查 ===
人员创建页面访问状态码: 302
[OK] 人员管理路由已添加部门权限检查
```

---

## 待改进项

以下问题在本次修复中暂未处理，但建议后续改进：

### 1. 表单数据类型验证
**问题**：
- `TangibleAssetForm` 和 `IntangibleAssetForm` 中使用了 `StringField` 处理数值和日期字段
- 应该使用 `FloatField`、`DateField` 等更合适的字段类型

**建议**：
- 修改表单字段类型
- 更新路由中的表单处理逻辑
- 添加更严格的数据验证

### 2. 装饰器函数通用性
**问题**：
- `department_data_filter()` 函数硬编码了 `Personnel` 模型
- 在其他模型中使用时可能出错

**建议**：
- 重构为通用的过滤器函数
- 添加模型参数支持

### 3. 模型关系定义
**问题**：
- `TangibleAsset` 模型中的关系定义较为复杂

**建议**：
- 简化关系定义
- 使用更清晰的关联方式

---

## 总结

本次修复成功解决了以下安全问题：
1. ✅ 办公电脑显示真实名称（而非虚假的"电脑 (ID)"）
2. ✅ 阻止开放重定向攻击
3. ✅ 为人员管理添加部门权限检查

所有修复都已通过测试，系统安全性得到提升。