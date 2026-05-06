"""
验证部门数据同步结果
"""
from app import app
from app.models import Department, User

with app.app_context():
    print('=== 部门数据验证 ===\n')
    
    # 检查部门总数
    total_departments = Department.query.count()
    level1_departments = Department.query.filter_by(level=1).count()
    level2_departments = Department.query.filter_by(level=2).count()
    
    print(f'部门总数: {total_departments}')
    print(f'一级部门数量: {level1_departments}')
    print(f'二级部门数量: {level2_departments}')
    
    # 显示所有二级部门
    print('\n所有二级部门列表:')
    print('-' * 60)
    for dept in Department.query.filter_by(level=2).all():
        print(f'ID: {dept.id:3d} | 部门名称: {dept.name:20s} | 部门代码: {dept.code}')
    print('-' * 60)
    
    print('\n=== 用户数据验证 ===\n')
    
    # 检查用户总数
    total_users = User.query.count()
    print(f'用户总数: {total_users}')
    
    # 显示所有用户及其部门配置
    print('\n所有用户列表:')
    print('-' * 80)
    for user in User.query.all():
        dept_name = '未分配'
        dept_code = 'N/A'
        if user.department_id:
            dept = Department.query.get(user.department_id)
            if dept:
                dept_name = dept.name
                dept_code = dept.code
        access_text = '是' if user.department_access else '否'
        print(f'用户: {user.username:15s} | 邮箱: {user.email:30s} | 部门: {dept_name:20s} | 仅本部门: {access_text}')
    print('-' * 80)